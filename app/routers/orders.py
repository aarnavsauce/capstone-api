from fastapi import APIRouter, HTTPException, Query, status, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth import get_current_customer_id
from app.schemas.common import ErrorResponse, PaginatedResponse
from app.schemas.order import Order, OrderInput
from app.services.order_service import OrderService

#limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/v1/orders", tags=["Orders"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Order, responses={400: {"model": ErrorResponse}})
@limiter.limit("5/minute") # rate limit order creating to 5 req/min
def create_order(request: Request, payload: OrderInput, current_customer_id: str = Depends(get_current_customer_id)):
    # scope enforcement: users cannot create orders for someone else
    if payload.customerId != current_customer_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Forbidden: You can only place orders for your own account."
        )
    try:
        return OrderService.create_order(payload)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail = str(e))
    

@router.get("/{id}", response_model=Order, responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
def get_order(id: str, current_customer_id: str = Depends(get_current_customer_id)):
    order = OrderService.get_order(id)
    
    # 1. First check if order exists (404)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    # 2. Check ownership (403)
    if order.customerId != current_customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this order."
        )
        
    return order

@router.get("", response_model=PaginatedResponse[Order])
def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_customer_id: str = Depends(get_current_customer_id)
):
    # Only return orders belonging to the authenticated user
    items, total = OrderService.list_orders_for_customer(customer_id=current_customer_id, page=page, limit=limit)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)