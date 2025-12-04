"""
Modelo Product para TechShop
Gestiona la llista de productes disponibles
"""

from decimal import Decimal
from typing import Optional


class Product:
    """Model per gestionar la llista de productes disponibles"""
    
    def __init__(self, id: Optional[int] = None, name: str = "", 
                 price: Decimal = Decimal('0.00'), stock: int = 0):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
    
    def __repr__(self):
        return f"Product(id={self.id}, name='{self.name}', price={self.price}, stock={self.stock})"

