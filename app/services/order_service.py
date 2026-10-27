from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional, Tuple
from app.schemas.order import Order, OrderInput, OrderItem, OrderStatus
from app.services.customer_service import CustomerService

orders_db: Dict[str, Order] = {}

# Mock product pricing table
MOCK_PRICES = {"prod_99": 120.00, "prod_100": 45.50}

class OrderService:
    @staticmethod
    def create_order(data: OrderInput) -> Order:
        # Business logic validation: Ensure customer exists
        customer = CustomerService.get_customer(data.customerId)
        if not customer:
            raise ValueError(f"Customer with ID '{data.customerId}' does not exist.")

        order_items: List[OrderItem] = []
        total_amount = 0.0

        for item in data.items:
            unit_price = MOCK_PRICES.get(item.productId, 50.00)  # Default fallback price
            item_total = unit_price * item.quantity
            total_amount += item_total
            
            order_items.append(
                OrderItem(
                    productId=item.productId,
                    quantity=item.quantity,
                    unitPrice=unit_price
                )
            )

        order_id = f"ord_{uuid.uuid4().hex[:8]}"
        order = Order(
            id=order_id,
            customerId=data.customerId,
            status=OrderStatus.PENDING,
            items=order_items,
            totalAmount=round(total_amount, 2),
            createdAt=datetime.now(timezone.utc)
        )
        orders_db[order_id] = order
        return order

    @staticmethod
    def get_order(order_id: str) -> Optional[Order]:
        return orders_db.get(order_id)

    @staticmethod
    def list_orders(page: int = 1, limit: int = 10) -> Tuple[List[Order], int]:
        all_orders = list(orders_db.values())
        total = len(all_orders)
        start = (page - 1) * limit
        end = start + limit
        return all_orders[start:end], total

    @staticmethod
    def list_orders_for_customer(customer_id: str, page: int = 1, limit: int = 10) -> Tuple[List[Order], int]:
        customer_orders = [o for o in order_db.values() if o.customerId == customer_id]
        total = len(customer_orders)
        start = (page - 1) * limit
        end = start + limit
        return customer_orders[start:end], total