from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.common import ErrorResponse, PaginatedResponse
from app.schemas.customer import Customer, CustomerInput
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/v1/customers", tags=["Customers"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Customer, responses={400: {"model": ErrorResponse}})
def create_customer(payload: CustomerInput):
    return CustomerService.create_customer(payload)

@router.get("/{id}", response_model=Customer, responses={404: {"model": ErrorResponse}})
def get_customer(id: str):
    customer = CustomerService.get_customer(id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("", response_model=PaginatedResponse[Customer])
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    items, total = CustomerService.list_customers(page=page, limit=limit)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)