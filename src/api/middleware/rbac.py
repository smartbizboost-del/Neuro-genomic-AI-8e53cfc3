from functools import wraps
from fastapi import HTTPException, Depends, status
from src.api.middleware.auth import get_current_user


def require_role(allowed_roles: list):
    """Decorator for role-based access control"""
    def decorator(func):
        @wraps(func)
        async def wrapper(
                *args, current_user=Depends(get_current_user), **kwargs):
            if current_user.get('role') not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
