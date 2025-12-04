"""
Servei de gestió de comandes
Implementa la lògica de negoci per crear comandes sense barrejar amb presentació o accés a dades
"""

import sqlite3
from decimal import Decimal
from datetime import datetime
from typing import Dict, Tuple
from models import Order, OrderItem


class OrderService:
    """Servei per gestionar les comandes"""
    
    def __init__(self, db_path: str = "techshop.db"):
        self.db_path = db_path

    def create_order_in_transaction(
        self, conn: sqlite3.Connection, cart: Dict[int, int], user_id: int
    ) -> Tuple[bool, str, int]:
        """
        Crear una nova comanda utilitzant una connexió existent.

        Aquesta funció NO fa commit/rollback: és responsabilitat del codi
        que la crida (permetent transaccions que inclouen usuari + comanda).
        """
        if not cart:
            return False, "El carretó està buit", 0

        cursor = conn.cursor()

        # Verificar que l'usuari existeix
        cursor.execute("SELECT id FROM User WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False, "Usuari no trobat", 0

        # Calcular total de la comanda
        total = self._calculate_order_total(cart, cursor)
        if total == Decimal("0.00"):
            return False, "Error calculant el total de la comanda", 0

        # Crear la comanda
        cursor.execute(
            'INSERT INTO "Order" (total, created_at, user_id) VALUES (?, ?, ?)',
            (float(total), datetime.now(), user_id),
        )
        order_id = cursor.lastrowid

        # Crear les línies de comanda i actualitzar inventari
        for product_id, quantity in cart.items():
            # Crear OrderItem
            cursor.execute(
                "INSERT INTO OrderItem (order_id, product_id, quantity) VALUES (?, ?, ?)",
                (order_id, product_id, quantity),
            )

            # Actualitzar inventari
            cursor.execute(
                "UPDATE Product SET stock = stock - ? WHERE id = ?",
                (quantity, product_id),
            )

        return True, f"Comanda creada correctament. Total: {total}", order_id

    def create_order(self, cart: Dict[int, int], user_id: int) -> Tuple[bool, str, int]:
        """
        Versió compatible que crea una nova comanda obrint la seva pròpia connexió.
        Es manté per compatibilitat amb els tests i altres usos.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                return self.create_order_in_transaction(conn, cart, user_id)
        except sqlite3.Error as e:
            return False, f"Error creant la comanda: {str(e)}", 0
    
    def _calculate_order_total(self, cart: Dict[int, int], cursor) -> Decimal:
        """
        Calcular el total de la comanda sumant price * quantity de cada producte.
        
        Args:
            cart (Dict[int, int]): Carretó amb {product_id: quantity}
            cursor: Cursor de la base de dades
            
        Returns:
            Decimal: Total de la comanda
        """
        total = Decimal('0.00')
        
        for product_id, quantity in cart.items():
            cursor.execute("SELECT price FROM Product WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            if result:
                price = Decimal(str(result[0]))
                total += price * quantity
        
        return total
    
    def get_order_by_id(self, order_id: int) -> Tuple[bool, str, Order]:
        """
        Obtenir una comanda per ID.
        
        Args:
            order_id (int): ID de la comanda
            
        Returns:
            Tuple[bool, str, Order]: (èxit, missatge, comanda)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, total, created_at, user_id FROM \"Order\" WHERE id = ?",
                    (order_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return False, "Comanda no trobada", None
                
                order = Order(
                    id=result[0],
                    total=Decimal(str(result[1])),
                    created_at=datetime.fromisoformat(result[2]),
                    user_id=result[3]
                )
                
                return True, "Comanda trobada", order
                
        except sqlite3.Error as e:
            return False, f"Error accedint a la comanda: {str(e)}", None
    
    def get_orders_by_user_id(self, user_id: int) -> list:
        """
        Obtenir totes les comandes d'un usuari específic.
        
        Args:
            user_id (int): ID de l'usuari
            
        Returns:
            list: Llista de tuples (Order, items) on items és una llista de OrderItem amb informació del producte
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Obtenir totes les comandes de l'usuari
                cursor.execute(
                    'SELECT id, total, created_at, user_id FROM "Order" WHERE user_id = ? ORDER BY created_at DESC',
                    (user_id,)
                )
                orders_data = cursor.fetchall()
                
                orders_with_items = []
                for row in orders_data:
                    order = Order(
                        id=row[0],
                        total=Decimal(str(row[1])),
                        created_at=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                        user_id=row[3]
                    )
                    
                    # Obtenir items de la comanda amb informació del producte
                    cursor.execute("""
                        SELECT oi.id, oi.order_id, oi.product_id, oi.quantity, p.name, p.price
                        FROM OrderItem oi
                        JOIN Product p ON oi.product_id = p.id
                        WHERE oi.order_id = ?
                    """, (order.id,))
                    items_data = cursor.fetchall()
                    
                    items = []
                    for item_row in items_data:
                        items.append({
                            'id': item_row[0],
                            'order_id': item_row[1],
                            'product_id': item_row[2],
                            'quantity': item_row[3],
                            'product_name': item_row[4],
                            'product_price': Decimal(str(item_row[5]))
                        })
                    
                    orders_with_items.append((order, items))
                
                return orders_with_items
        except sqlite3.Error as e:
            return []