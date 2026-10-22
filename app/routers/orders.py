from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.common import ErrorResponse, PaginatedResponse
from app.schemas.order import Order, OrderInput
from app.services.order_service import OrderService

router = APIRouter(prefix="/v1/orders", tags=["Orders"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Order, responses={400: {"model": ErrorResponse}})
def create_order(payload: OrderInput):
    try:
        return OrderService.create_order(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Order, responses={404: {"model": ErrorResponse}})
def get_order(id: str):
    order = OrderService.get_order(id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("", response_model=PaginatedResponse[Order])
def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    items, total = OrderService.list_orders(page=page, limit=limit)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)