from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.firebase import verify_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    try:
        decoded = verify_token(token)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_role(*roles: str):
    """
    Roles match UI exactly: 'Team Member', 'Admin', 'Super Admin'
    """
    def checker(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role", "Team Member")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required: {list(roles)}",
            )
        return user
    return checker


AnyUser        = Depends(get_current_user)
AdminOnly      = Depends(require_role("Admin", "Super Admin"))
SuperAdminOnly = Depends(require_role("Super Admin"))
