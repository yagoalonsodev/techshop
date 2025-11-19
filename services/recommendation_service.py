"""
Servei de recomanacions de productes basat en les vendes històriques.
Implementa la lògica per obtenir els productes més venuts sense barrejar cap codi de presentació.
"""

import sqlite3
from decimal import Decimal
from typing import List, Tuple

from models import Product


class RecommendationService:
    """Servei per calcular recomanacions a partir de les vendes registrades."""

    def __init__(self, db_path: str = "techshop.db"):
        """
        Inicialitza el servei.

        Args:
            db_path (str): Ruta a la base de dades SQLite.
        """
        self.db_path = db_path

    def get_top_selling_products(self, limit: int = 3) -> List[Tuple[Product, int]]:
        """
        Obtenir una llista dels productes més venuts.

        Args:
            limit (int): Nombre màxim de productes recomanats a retornar.

        Returns:
            List[Tuple[Product, int]]: Llista de tuples amb el producte i la quantitat venuda.
        """
        if limit <= 0:
            return []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT p.id, p.name, p.price, p.stock, SUM(oi.quantity) AS total_sold
                    FROM OrderItem oi
                    INNER JOIN Product p ON p.id = oi.product_id
                    GROUP BY oi.product_id
                    ORDER BY total_sold DESC, p.name ASC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()

                recommendations: List[Tuple[Product, int]] = []
                for row in rows:
                    product = Product(
                        id=row[0],
                        name=row[1],
                        price=Decimal(str(row[2])),
                        stock=row[3],
                    )
                    total_sold = int(row[4]) if row[4] is not None else 0
                    recommendations.append((product, total_sold))

                return recommendations

        except sqlite3.Error:
            return []

    def get_top_products_for_user(self, user_id: int, limit: int = 3) -> List[Tuple[Product, int]]:
        """
        Obtenir una llista dels productes més venuts per a un usuari específic.

        Args:
            user_id (int): Identificador de l'usuari.
            limit (int): Nombre màxim de productes recomanats a retornar.

        Returns:
            List[Tuple[Product, int]]: Llista de tuples amb el producte i la quantitat venuda per l'usuari.
        """
        if limit <= 0 or user_id is None:
            return []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT p.id, p.name, p.price, p.stock, SUM(oi.quantity) AS total_sold
                    FROM "Order" o
                    INNER JOIN OrderItem oi ON oi.order_id = o.id
                    INNER JOIN Product p ON p.id = oi.product_id
                    WHERE o.user_id = ?
                    GROUP BY oi.product_id
                    ORDER BY total_sold DESC, p.name ASC
                    LIMIT ?
                    """,
                    (user_id, limit,),
                )
                rows = cursor.fetchall()

                recommendations: List[Tuple[Product, int]] = []
                for row in rows:
                    product = Product(
                        id=row[0],
                        name=row[1],
                        price=Decimal(str(row[2])),
                        stock=row[3],
                    )
                    total_sold = int(row[4]) if row[4] is not None else 0
                    recommendations.append((product, total_sold))

                return recommendations

        except sqlite3.Error:
            return []

