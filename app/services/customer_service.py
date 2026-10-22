from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional, Tuple
from app.schemas.customer import Customer, CustomerInput

# In-memory persistence simulation
customers_db: Dict[str, Customer] = {}

class CustomerService:
    @staticmethod
    def create_customer(data: CustomerInput) -> Customer:
        cust_id = f"cust_{uuid.uuid4().hex[:8]}"
        customer = Customer(
            id=cust_id,
            name=data.name,
            email=data.email,
            createdAt=datetime.now(timezone.utc)
        )
        customers_db[cust_id] = customer
        return customer

    @staticmethod
    def get_customer(cust_id: str) -> Optional[Customer]:
        return customers_db.get(cust_id)

    @staticmethod
    def list_customers(page: int = 1, limit: int = 10) -> Tuple[List[Customer], int]:
        all_customers = list(customers_db.values())
        total = len(all_customers)
        start = (page - 1) * limit
        end = start + limit
        return all_customers[start:end], total