from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreateRequest(BaseModel):
    email: str
    password: str
    full_name: str
    is_admin: bool = False


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None


class AccountResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    balance: float
    created_at: datetime


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    full_name: str
    is_admin: bool
    created_at: datetime


class PaymentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    transaction_id: str
    account_id: int
    amount: float
    created_at: datetime


class PaymentWebhookResponse(BaseModel):
    status: str
    transaction_id: str
    account_id: int
    amount: float
    balance: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
