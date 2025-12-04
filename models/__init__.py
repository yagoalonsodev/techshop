"""
Modelos de datos para TechShop
Defineix les classes de dades seguint l'esquema de la base de dades
"""

from models.product import Product
from models.user import User
from models.order import Order
from models.order_item import OrderItem

__all__ = ['Product', 'User', 'Order', 'OrderItem']

