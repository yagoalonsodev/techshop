"""
Servei de gestió del carretó de compres
Implementa la lògica de negoci per gestionar el carretó sense barrejar amb presentació o accés a dades
"""

import sqlite3
from decimal import Decimal
from typing import Dict, List, Tuple
from models import Product


class CartService:
    """Servei per gestionar el carretó de compres"""
    
    def __init__(self, db_path: str = "techshop.db"):
        self.db_path = db_path
        self.cart = {}  # {product_id: quantity}
    
    def add_to_cart(self, product_id: int, quantity: int) -> Tuple[bool, str]:
        """
        Afegir un producte al carretó.
        
        Args:
            product_id (int): ID del producte a afegir
            quantity (int): Quantitat a afegir
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
            
        Raises:
            ValueError: Si la quantitat no és vàlida o supera el límit
        """
        if not isinstance(quantity, int) or quantity <= 0:
            return False, "La quantitat ha de ser un enter positiu"
        
        # Comprovar stock disponible
        stock_ok, stock_msg = self.validate_stock(product_id, quantity)
        if not stock_ok:
            return False, stock_msg
        
        # Comprovar límit de 5 unitats per producte
        current_quantity = self.cart.get(product_id, 0)
        total_quantity = current_quantity + quantity
        
        if total_quantity > 5:
            return False, f"No es pot superar el límit de 5 unitats per producte. Actual: {current_quantity}, intentant afegir: {quantity}"
        
        # Afegir al carretó
        self.cart[product_id] = total_quantity
        return True, f"Producte afegit al carretó. Quantitat total: {total_quantity}"
    
    def remove_from_cart(self, product_id: int) -> Tuple[bool, str]:
        """
        Eliminar un producte del carretó.
        
        Args:
            product_id (int): ID del producte a eliminar
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        if product_id in self.cart:
            del self.cart[product_id]
            return True, "Producte eliminat del carretó"
        else:
            return False, "Producte no trobat al carretó"
    
    def validate_stock(self, product_id: int, quantity: int) -> Tuple[bool, str]:
        """
        Comprovar que hi hagi prou stock disponible.
        
        Args:
            product_id (int): ID del producte
            quantity (int): Quantitat necessària
            
        Returns:
            Tuple[bool, str]: (disponible, missatge)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT stock FROM Product WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                
                if not result:
                    return False, "Producte no trobat"
                
                available_stock = result[0]
                if available_stock < quantity:
                    return False, f"Stock insuficient. Disponible: {available_stock}, Sol·licitat: {quantity}"
                
                return True, "Stock disponible"
                
        except sqlite3.Error as e:
            return False, f"Error accedint a la base de dades: {str(e)}"
    
    def get_cart_contents(self) -> Dict[int, int]:
        """
        Obtenir el contingut actual del carretó.
        
        Returns:
            Dict[int, int]: {product_id: quantity}
        """
        return self.cart.copy()
    
    def clear_cart(self):
        """Buida el carretó."""
        self.cart.clear()
    
    def get_cart_total(self) -> Decimal:
        """
        Calcular el total del carretó.
        
        Returns:
            Decimal: Total del carretó
        """
        total = Decimal('0.00')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for product_id, quantity in self.cart.items():
                    cursor.execute("SELECT price FROM Product WHERE id = ?", (product_id,))
                    result = cursor.fetchone()
                    if result:
                        price = Decimal(str(result[0]))
                        total += price * quantity
                        
        except sqlite3.Error:
            pass  # Retorna 0.00 en cas d'error
            
        return total