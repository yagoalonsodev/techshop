"""
Modelo OrderItem para TechShop
Especifica els productes que formen part d'una comanda
"""

from typing import Optional


class OrderItem:
    """Model per especificar els productes que formen part d'una comanda"""
    
    def __init__(self, id: Optional[int] = None, order_id: Optional[int] = None, 
                 product_id: Optional[int] = None, quantity: int = 0):
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
    
    def __repr__(self):
        return f"OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})"

