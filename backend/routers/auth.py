from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database import get_db
from models_db import User
from core.security import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    """Verifica el token JWT y retorna el usuario actual."""
    from jose import JWTError, jwt
    from fastapi import status
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and Verify Token
        from core.security import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            print("[AUTH] Token missing 'sub' claim")
            raise credentials_exception
    except JWTError as e:
        print(f"[AUTH] JWT Decode Error: {e}")
        raise credentials_exception
        
    # Get User from DB
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if user is None:
        print(f"[AUTH] User {email} not found in DB")
        raise credentials_exception
        
    return user

from core.limiter import limiter

@router.post("/token")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request, # Required for SlowAPI
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """Endpoint estandar OAuth2 para login (email/password)."""
    # En OAuth2 'username' es el campo estándar, lo usamos para el email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "name": user.name,
            "role": user.role,
            "plan": user.plan,
            "plan_status": user.plan_status
        }
    }

@router.post("/register")
async def register_user(
    email: str, 
    password: str, 
    name: str = "Trader", 
    db: AsyncSession = Depends(get_db)
):
    """(Dev Helper) Registra un usuario inicial."""
    # Verificar si existe
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_pwd, name=name, role="user")
    
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email, "msg": "User created"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error creating user")

    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "plan": current_user.plan,
        "plan_status": current_user.plan_status,
        "avatar_url": f"https://ui-avatars.com/api/?name={current_user.name}&background=10b981&color=fff"
    }

# Entitlements Endpoint (Sync DB required for core logic)
from database import SessionLocal
from sqlalchemy.orm import Session
from core.entitlements import get_user_entitlements

def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me/entitlements")
def read_my_entitlements(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_sync_db)
):
    """
    Diagnóstico de límites y cuotas.
    """
    return get_user_entitlements(db, current_user)
