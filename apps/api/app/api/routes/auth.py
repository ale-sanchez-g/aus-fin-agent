from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.core.security import get_current_user, CurrentUser

router = APIRouter()


class UserInfoResponse(BaseModel):
    user_id: str
    email: str
    role: str


@router.get("/me", response_model=UserInfoResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    return UserInfoResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        role=current_user.role,
    )
