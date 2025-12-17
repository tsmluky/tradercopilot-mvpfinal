from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize Limiter
# Using In-Memory fallback if no storage uri is provided
# key_func=get_remote_address uses the client IP
limiter = Limiter(key_func=get_remote_address)
