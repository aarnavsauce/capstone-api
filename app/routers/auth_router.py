from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.auth import create_access_token
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    customerId: str = Field(..., example="cust_12345")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    customer = CustomerService.get_customer(payload.customerId)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Customer not found")

    token = create_access_token(customer_id = customer.id)
    return TokenResponse(access_token=token)
