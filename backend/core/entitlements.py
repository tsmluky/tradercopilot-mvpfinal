from datetime import datetime
from typing import Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models_db import User, DailyUsage

# === 1. CONFIGURATION & DATA ===

# Aliases: Input -> Canonical
TOKEN_ALIASES = {
    "MATIC": "POL",
    "RNDR": "RENDER",
    "LUNA": "LUNC", # Often requested, mapped to classic if supported or handled
}

# Stablecoins (Blocked)
STABLECOINS = {
    "USDT", "USDC", "DAI", "FDUSD", "TUSD", "USDD", "BUSD", "USDE"
}

# Allow-lists (Canonical Symbols)
TOKENS_FREE = {
    "BTC", "ETH", "SOL"
}

TOKENS_TRADER = TOKENS_FREE.union({
    "BNB", "XRP", "ADA", "DOGE", "TON", "AVAX", "DOT", "LINK",
    "POL", "LTC", "BCH", "TRX", "ATOM", "NEAR", "SUI", "APT", "OP", "ARB", "UNI", "AAVE",
    "PENDLE", "RENDER"
})

# Full Pro List (Set for O(1) lookup)
TOKENS_PRO = TOKENS_TRADER.union({
    "FIL", "ICP", "XLM", "HBAR", "ALGO", "VET", "EGLD", "KAS", "XMR", "ETC", "XTZ", 
    "THETA", "EOS", "NEO", "IOTA", "DASH", "ZEC", "KSM", "FLOW", "FTM", "KLAY", "ZIL", 
    "HNT", "CHZ", "BAT", "APE", "SAND", "MANA", "AXS", "GALA", "GMT", "ILV", "IMX", 
    "ENJ", "LRC", "LPT", "MKR", "LDO", "COMP", "CRV", "CVX", "SNX", "DYDX", "GMX", 
    "1INCH", "BAL", "SUSHI", "YFI", "FXS", "RPL", "KAVA", "FET", "TAO", "ONDO", "INJ", 
    "TIA", "SEI", "STX", "RUNE", "AXL", "JUP", "JTO", "RAY", "ORCA", "BONK", "WIF", 
    "PEPE", "SHIB", "FLOKI", "PYTH", "BAND", "ROSE", "MINA", "AR", "CFX", "KDA", "JASMY", 
    "WOO", "WLD"
})

# Feature Quotas (Daily)
# Unlimited features get a high Hard-Cap for Fair Use protection
QUOTAS = {
    "FREE": {
        "ai_analysis": 2,
        "advisor_chat": 0
    },
    "TRADER": {
        "ai_analysis": 10,
        "advisor_chat": 20
    },
    "PRO": {
        "ai_analysis": 200,    # "Unlimited" Fair Use
        "advisor_chat": 500    # "Unlimited" Fair Use
    },
    "OWNER": {
        "ai_analysis": 9999,
        "advisor_chat": 9999
    }
}

# === 2. TOKEN CATALOG SERVICE ===

class TokenCatalog:
    @staticmethod
    def normalize(token: str) -> str:
        """
        Normaliza entrada: Trim, Upper, Resolve Alias.
        """
        if not token:
            return ""
        
        t = token.strip().upper()
        
        # 1. Alias Resolution
        if t in TOKEN_ALIASES:
            t = TOKEN_ALIASES[t]
            
        return t

    @staticmethod
    def is_stablecoin(token: str) -> bool:
        return token in STABLECOINS

    @staticmethod
    def get_allowed_tokens(plan: str) -> List[str]:
        p = plan.upper()
        if p == "FREE":
            return sorted(list(TOKENS_FREE))
        elif p == "TRADER":
            return sorted(list(TOKENS_TRADER))
        # PRO / OWNER
        return sorted(list(TOKENS_PRO))

    @staticmethod
    def check_access(plan: str, token: str) -> bool:
        """
        Verifica si el plan tiene acceso al token (CANONICAL).
        """
        p = plan.upper()
        
        # Owner bypass
        if p == "OWNER":
            return True
            
        if p == "FREE":
            return token in TOKENS_FREE
        if p == "TRADER":
            return token in TOKENS_TRADER
        if p == "PRO":
            return token in TOKENS_PRO
            
        return False # Unknown plan


# === 3. ENFORCEMENT FUNCTIONS ===

def assert_token_allowed(user: User, raw_token: str):
    """
    Validación estricta de token por tier.
    Lanza 403 con JSON estructurado si falla.
    """
    # 0. Normalize
    token = TokenCatalog.normalize(raw_token)
    
    # 1. Stablecoin Check
    if TokenCatalog.is_stablecoin(token):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "STABLECOIN_NOT_SUPPORTED",
                "message": f"Stablecoins like {token} are not supported for analysis targets.",
                "tier": user.plan,
            }
        )

    # 2. Tier Access Check
    plan = (user.plan or "FREE").upper()
    if not TokenCatalog.check_access(plan, token):
         # Prepare standard response
        allowed = TokenCatalog.get_allowed_tokens(plan)
        # Summary for error message
        limit_msg = "3 (BTC, ETH, SOL)" if plan == "FREE" else f"{len(allowed)} curated tokens"
        
        raise HTTPException(
            status_code=403,
            detail={
                "code": "TOKEN_NOT_ALLOWED",
                "message": f"Your {plan} plan does not include access to {token}.",
                "tier": plan,
                "token_requested": token,
                "allowed_sample": allowed[:5],
                "upgrade_required": True
            }
        )
    
    # Return normalized token if needed by caller, but usually caller just re-normalizes
    return token


def can_use_advisor(user: User):
    """
    Verifica acceso base al Advisor Chat.
    """
    plan = (user.plan or "FREE").upper()
    
    # Access logic: Only PRO (and specific TRADER limits/features if any)
    # Based on prompt: TRADER has 20 chats/day. So they HAVE access, but capped.
    # FREE has 0.
    
    limits = QUOTAS.get(plan, QUOTAS["FREE"])
    chat_limit = limits.get("advisor_chat", 0)
    
    if chat_limit <= 0:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FEATURE_LOCKED",
                "message": f"Advisor Chat is not available on the {plan} plan.",
                "tier": plan,
                "upgrade_required": True
            }
        )


def check_and_increment_quota(db: Session, user: User, feature: str):
    """
    Verifica y consume cuota diaria.
    Lanza 429 con JSON estructurado si falla.
    """
    plan = (user.plan or "FREE").upper()
    
    # Get Limits
    limits = QUOTAS.get(plan, QUOTAS["FREE"])
    limit = limits.get(feature, 0)
    
    # Hard Block if 0 (Redundant if checking feature access first, but safe)
    if limit <= 0:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FEATURE_LOCKED",
                "message": f"Feature {feature} not enabled for {plan}.",
                "tier": plan,
                "upgrade_required": True
            }
        )
        
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # 1. Atomic DB Get/Create
    # We try to find the record first
    usage = db.query(DailyUsage).filter(
        DailyUsage.user_id == user.id,
        DailyUsage.feature == feature,
        DailyUsage.date == today_str
    ).with_for_update().first()
    
    if not usage:
        try:
            usage = DailyUsage(user_id=user.id, feature=feature, date=today_str, count=0)
            db.add(usage)
            db.commit()
            db.refresh(usage)
            # Re-lock
            usage = db.query(DailyUsage).filter(DailyUsage.id == usage.id).with_for_update().first()
        except IntegrityError:
            db.rollback()
            usage = db.query(DailyUsage).filter(
                DailyUsage.user_id == user.id,
                DailyUsage.feature == feature,
                DailyUsage.date == today_str
            ).with_for_update().first()

    # 2. Check Limit
    if usage.count >= limit:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "DAILY_QUOTA_EXCEEDED",
                "message": f"You have reached your daily limit of {limit} for {feature}.",
                "tier": plan,
                "limit": limit,
                "used": usage.count,
                "reset_at": "00:00 UTC",
                "upgrade_required": plan != "PRO" # Suggest upgrade if not Pro
            }
        )

    # 3. Increment
    usage.count += 1
    db.commit()
    
    return {
        "used": usage.count,
        "limit": limit,
        "remaining": limit - usage.count
    }


def get_user_entitlements(db: Session, user: User):
    """
    Retorna estado completo para UI.
    """
    plan = (user.plan or "FREE").upper()
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Get usage from DB
    usages = db.query(DailyUsage).filter(
        DailyUsage.user_id == user.id,
        DailyUsage.date == today_str
    ).all()
    
    usage_map = {u.feature: u.count for u in usages}
    limits = QUOTAS.get(plan, QUOTAS["FREE"])
    
    return {
        "tier": plan,
        "features": {
            "ai_analysis": {
                "limit": limits.get("ai_analysis", 0),
                "used": usage_map.get("ai_analysis", 0),
                "remaining": max(0, limits.get("ai_analysis", 0) - usage_map.get("ai_analysis", 0))
            },
            "advisor_chat": {
                "limit": limits.get("advisor_chat", 0),
                "used": usage_map.get("advisor_chat", 0),
                "remaining": max(0, limits.get("advisor_chat", 0) - usage_map.get("advisor_chat", 0))
            }
        },
        "allowed_tokens": TokenCatalog.get_allowed_tokens(plan),
        "server_time": datetime.utcnow().isoformat() + "Z"
    }
