"""
Servei de gestió de productes
Implementa la lògica de negoci per a les operacions relacionades amb productes
"""

import sqlite3
from decimal import Decimal
from typing import List, Optional, Tuple
from models import Product


class ProductService:
    """Servei per gestionar productes"""
    
    def __init__(self, db_path: str = "techshop.db"):
        self.db_path = db_path
    
    def get_all_products(self) -> List[Product]:
        """
        Obtenir tots els productes disponibles.
        
        Returns:
            List[Product]: Llista de tots els productes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, price, stock FROM Product ORDER BY id")
                results = cursor.fetchall()
                
                products = []
                for row in results:
                    products.append(Product(
                        id=row[0],
                        name=row[1],
                        price=Decimal(str(row[2])),
                        stock=row[3]
                    ))
                return products
        except sqlite3.Error:
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtenir un producte per ID.
        
        Args:
            product_id (int): ID del producte
            
        Returns:
            Optional[Product]: Producte si existeix, None altrament
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, price, stock FROM Product WHERE id = ?",
                    (product_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return Product(
                        id=row[0],
                        name=row[1],
                        price=Decimal(str(row[2])),
                        stock=row[3]
                    )
        except sqlite3.Error:
            pass
        
        return None
    
    def get_products_by_ids(self, product_ids: List[int]) -> List[Tuple[Product, int]]:
        """
        Obtenir productes per una llista d'IDs amb quantitats.
        
        Args:
            product_ids: Llista de tuples (product_id, quantity) o dict {product_id: quantity}
            
        Returns:
            List[Tuple[Product, int]]: Llista de tuples (Product, quantity)
        """
        if not product_ids:
            return []
        
        # Convertir dict a llista de tuples si cal
        if isinstance(product_ids, dict):
            items = list(product_ids.items())
        else:
            items = product_ids
        
        products_with_quantities = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for product_id, quantity in items:
                    cursor.execute(
                        "SELECT id, name, price, stock FROM Product WHERE id = ?",
                        (product_id,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        product = Product(
                            id=row[0],
                            name=row[1],
                            price=Decimal(str(row[2])),
                            stock=row[3]
                        )
                        products_with_quantities.append((product, quantity))
        except sqlite3.Error:
            pass
        
        return products_with_quantities

