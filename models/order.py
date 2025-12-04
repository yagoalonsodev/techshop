"""
Modelo Order para TechShop
Representa cada comanda realitzada
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional


class Order:
    """Model per representar cada comanda realitzada"""
    
    def __init__(self, id: Optional[int] = None, total: Decimal = Decimal('0.00'), 
                 created_at: Optional[datetime] = None, user_id: Optional[int] = None):
        self.id = id
        self.total = total
        self.created_at = created_at or datetime.now()
        self.user_id = user_id
    
    def __repr__(self):
        return f"Order(id={self.id}, total={self.total}, user_id={self.user_id})"

