from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class CustomerInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Jane Doe")
    email: EmailStr = Field(..., example="jane.doe@example.com")

class Customer(CustomerInput):
    id: str = Field(..., example="cust_12345")
    createdAt: datetime