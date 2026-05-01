from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import structlog
from app.core.config import settings

log = structlog.get_logger()
bearer = HTTPBearer(auto_error=False)


class CurrentUser:
    def __init__(self, user_id: str, email: str, role: str = "analyst"):
        self.user_id = user_id
        self.email = email
        self.role = role


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
) -> CurrentUser:
    # In dev mode without Cognito configured, allow bypass
    if settings.ENVIRONMENT != "prod" and not settings.COGNITO_USER_POOL_ID:
        return CurrentUser(user_id="dev-user", email="dev@example.com", role="admin")

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = jwt.get_unverified_claims(token)
        user_id = payload.get("sub", "unknown")
        email = payload.get("email", "")
        groups = payload.get("cognito:groups", [])
        role = "admin" if "admin" in groups else "analyst" if "analyst" in groups else "client"
        return CurrentUser(user_id=user_id, email=email, role=role)
    except JWTError as e:
        log.warning("jwt_error", error=str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_role(*roles: str):
    async def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

    return checker
