from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

class OrderItemInput(BaseModel):
    productId: str = Field(..., example="prod_99")
    quantity: int = Field(..., ge=1, example=2)

class OrderItem(OrderItemInput):
    unitPrice: float = Field(..., example=120.00)

class OrderInput(BaseModel):
    customerId: str = Field(..., example="cust_12345")
    items: List[OrderItemInput] = Field(..., min_items=1)

class Order(BaseModel):
    id: str = Field(..., example="ord_88888")
    customerId: str
    status: OrderStatus
    items: List[OrderItem]
    totalAmount: float
    createdAt: datetime