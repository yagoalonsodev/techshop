"""
Modelos de datos para TechShop
Defineix les classes de dades seguint l'esquema de la base de dades
"""

from datetime import datetime
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


class User:
    """Model per gestionar la informació de l'usuari que fa la compra"""
    
    def __init__(self, id: Optional[int] = None, username: str = "", 
                 password_hash: str = "", email: str = "", 
                 address: str = "",
                 role: str = "common",
                 account_type: str = "user",
                 dni: str = "",
                 nif: str = "",
                 created_at: Optional[datetime] = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.address = address
        self.role = role  # 'common' o 'admin'
        self.account_type = account_type  # 'user' o 'company'
        self.dni = dni  # DNI per usuaris individuals
        self.nif = nif  # NIF per empreses
        self.created_at = created_at or datetime.now()
    
    def is_admin(self) -> bool:
        """Verificar si l'usuari és administrador."""
        return self.role == "admin"
    
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}', account_type='{self.account_type}')"


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
