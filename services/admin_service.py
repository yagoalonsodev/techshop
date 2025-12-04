"""
Servei de gestió administrativa
Implementa la lògica de negoci per a les operacions d'administració sense barrejar amb presentació o accés a dades
"""

import sqlite3
import secrets
import string
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from models import Product, User, Order, OrderItem
from datetime import datetime
from werkzeug.security import generate_password_hash
from utils.validators import validar_dni_nie, validar_cif_nif


class AdminService:
    """Servei per gestionar operacions administratives"""
    
    def __init__(self, db_path: str = "techshop.db"):
        self.db_path = db_path
    
    # ========== GESTIÓ DE PRODUCTES ==========
    
    def get_all_products(self) -> List[Product]:
        """
        Obtenir tots els productes.
        
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
            Product o None: El producte si existeix, None altrament
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, price, stock FROM Product WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                
                if result:
                    return Product(
                        id=result[0],
                        name=result[1],
                        price=Decimal(str(result[2])),
                        stock=result[3]
                    )
        except sqlite3.Error:
            pass
        
        return None
    
    def create_product(self, name: str, price: Decimal, stock: int) -> Tuple[bool, str, Optional[int]]:
        """
        Crear un nou producte.
        
        Args:
            name (str): Nom del producte
            price (Decimal): Preu del producte
            stock (int): Stock inicial
            
        Returns:
            Tuple[bool, str, Optional[int]]: (èxit, missatge, product_id)
        """
        if not name or len(name.strip()) == 0:
            return False, "El nom del producte és obligatori", None
        
        if price < 0:
            return False, "El preu no pot ser negatiu", None
        
        if stock < 0:
            return False, "El stock no pot ser negatiu", None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)",
                    (name.strip(), float(price), stock)
                )
                product_id = cursor.lastrowid
                conn.commit()
                return True, f"Producte creat correctament", product_id
        except sqlite3.Error as e:
            return False, f"Error creant el producte: {str(e)}", None
    
    def update_product(self, product_id: int, name: str, price: Decimal, stock: int) -> Tuple[bool, str]:
        """
        Actualitzar un producte existent.
        
        Args:
            product_id (int): ID del producte
            name (str): Nou nom
            price (Decimal): Nou preu
            stock (int): Nou stock
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        if not name or len(name.strip()) == 0:
            return False, "El nom del producte és obligatori"
        
        if price < 0:
            return False, "El preu no pot ser negatiu"
        
        if stock < 0:
            return False, "El stock no pot ser negatiu"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Product SET name = ?, price = ?, stock = ? WHERE id = ?",
                    (name.strip(), float(price), stock, product_id)
                )
                if cursor.rowcount == 0:
                    return False, "Producte no trobat"
                conn.commit()
                return True, "Producte actualitzat correctament"
        except sqlite3.Error as e:
            return False, f"Error actualitzant el producte: {str(e)}"
    
    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        """
        Eliminar un producte.
        
        Args:
            product_id (int): ID del producte
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Verificar si hi ha comandes amb aquest producte
                cursor.execute(
                    "SELECT COUNT(*) FROM OrderItem WHERE product_id = ?",
                    (product_id,)
                )
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return False, f"No es pot eliminar el producte perquè està associat a {count} comanda(s)"
                
                cursor.execute("DELETE FROM Product WHERE id = ?", (product_id,))
                if cursor.rowcount == 0:
                    return False, "Producte no trobat"
                conn.commit()
                return True, "Producte eliminat correctament"
        except sqlite3.Error as e:
            return False, f"Error eliminant el producte: {str(e)}"
    
    # ========== GESTIÓ D'USUARIS ==========
    
    def get_all_users(self) -> List[User]:
        """
        Obtenir tots els usuaris.
        
        Returns:
            List[User]: Llista de tots els usuaris
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Intentar obtener con las nuevas columnas
                try:
                    cursor.execute(
                        "SELECT id, username, email, address, role, account_type, created_at FROM User ORDER BY id"
                    )
                    results = cursor.fetchall()
                    
                    users = []
                    for row in results:
                        users.append(User(
                            id=row[0],
                            username=row[1],
                            email=row[2] if row[2] else "",
                            address=row[3] if row[3] else "",
                            role=row[4] if row[4] else "common",
                            account_type=row[5] if row[5] else "user",
                            password_hash="",
                            created_at=datetime.fromisoformat(row[6]) if row[6] else datetime.now()
                        ))
                    return users
                except sqlite3.OperationalError:
                    # Esquema antiguo
                    cursor.execute("SELECT id, username, email, address, created_at FROM User ORDER BY id")
                    results = cursor.fetchall()
                    users = []
                    for row in results:
                        users.append(User(
                            id=row[0],
                            username=row[1],
                            email=row[2] if row[2] else "",
                            address=row[3] if row[3] else "",
                            role="common",
                            account_type="user",
                            password_hash="",
                            created_at=datetime.fromisoformat(row[4]) if len(row) > 4 and row[4] else datetime.now()
                        ))
                    return users
        except sqlite3.Error:
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtenir un usuari per ID.
        
        Args:
            user_id (int): ID de l'usuari
            
        Returns:
            User o None: L'usuari si existeix, None altrament
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "SELECT id, username, email, address, role, account_type, created_at FROM User WHERE id = ?",
                        (user_id,)
                    )
                    result = cursor.fetchone()
                    if result and len(result) >= 7:
                        return User(
                            id=result[0],
                            username=result[1],
                            email=result[2] if result[2] else "",
                            address=result[3] if result[3] else "",
                            role=result[4] if result[4] else "common",
                            account_type=result[5] if result[5] else "user",
                            password_hash="",
                            created_at=datetime.fromisoformat(result[6]) if result[6] else datetime.now()
                        )
                except sqlite3.OperationalError:
                    cursor.execute(
                        "SELECT id, username, email, address, created_at FROM User WHERE id = ?",
                        (user_id,)
                    )
                    result = cursor.fetchone()
                    if result:
                        return User(
                            id=result[0],
                            username=result[1],
                            email=result[2] if result[2] else "",
                            address=result[3] if result[3] else "",
                            role="common",
                            account_type="user",
                            password_hash="",
                            created_at=datetime.fromisoformat(result[4]) if len(result) > 4 and result[4] else datetime.now()
                        )
        except sqlite3.Error:
            pass
        
        return None
    
    def update_user(self, user_id: int, username: str, email: str, address: str, 
                   role: str, account_type: str = None) -> Tuple[bool, str]:
        """
        Actualitzar un usuari.
        
        Args:
            user_id (int): ID de l'usuari
            username (str): Nou nom d'usuari
            email (str): Nou email
            address (str): Nova adreça
            role (str): Nou rol (common/admin)
            account_type (str, optional): Tipus de compte (user/company) - NO es modifica, només per validació
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        if not username or len(username.strip()) < 4 or len(username.strip()) > 20:
            return False, "El nom d'usuari ha de tenir entre 4 i 20 caràcters"
        
        if '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Adreça de correu electrònic no vàlida"
        
        if role not in ['common', 'admin']:
            return False, "El rol ha de ser 'common' o 'admin'"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Verificar si el username ya existe en otro usuario
                cursor.execute(
                    "SELECT id FROM User WHERE username = ? AND id != ?",
                    (username.strip(), user_id)
                )
                if cursor.fetchone():
                    return False, "Aquest nom d'usuari ja està en ús"
                
                # Obtener el account_type actual del usuario (no se modifica)
                try:
                    cursor.execute("SELECT account_type FROM User WHERE id = ?", (user_id,))
                    result = cursor.fetchone()
                    current_account_type = result[0] if result and result[0] else 'user'
                except (sqlite3.OperationalError, IndexError):
                    current_account_type = 'user'
                
                # Intentar actualizar con las nuevas columnas (sin modificar account_type)
                try:
                    cursor.execute(
                        "UPDATE User SET username = ?, email = ?, address = ?, role = ? WHERE id = ?",
                        (username.strip(), email.strip(), address.strip(), role, user_id)
                    )
                except sqlite3.OperationalError:
                    # Si las columnas no existen, actualizar sin ellas
                    cursor.execute(
                        "UPDATE User SET username = ?, email = ?, address = ? WHERE id = ?",
                        (username.strip(), email.strip(), address.strip(), user_id)
                    )
                
                if cursor.rowcount == 0:
                    return False, "Usuari no trobat"
                conn.commit()
                return True, "Usuari actualitzat correctament"
        except sqlite3.Error as e:
            return False, f"Error actualitzant l'usuari: {str(e)}"
    
    def create_user(self, username: str, email: str, address: str, 
                   role: str = 'common', account_type: str = 'user',
                   dni: str = "", nif: str = "") -> Tuple[bool, str, Optional[str], Optional[int]]:
        """
        Crear un nou usuari amb contrasenya generada automàticament.
        
        Args:
            username (str): Nom d'usuari
            email (str): Email de l'usuari
            address (str): Adreça de l'usuari
            role (str): Rol de l'usuari (common/admin)
            account_type (str): Tipus de compte (user/company)
            dni (str): DNI per usuaris individuals
            nif (str): NIF per empreses
            
        Returns:
            Tuple[bool, str, Optional[str], Optional[int]]: (èxit, missatge, contrasenya_generada, user_id)
        """
        if not username or len(username.strip()) < 4 or len(username.strip()) > 20:
            return False, "El nom d'usuari ha de tenir entre 4 i 20 caràcters", None, None
        
        if '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Adreça de correu electrònic no vàlida", None, None
        
        if role not in ['common', 'admin']:
            return False, "El rol ha de ser 'common' o 'admin'", None, None
        
        if account_type not in ['user', 'company']:
            return False, "El tipus de compte ha de ser 'user' o 'company'", None, None
        
        # Validar DNI/NIF segons el tipus de compte
        if account_type == 'company':
            if not nif or not validar_cif_nif(nif):
                return False, "NIF no vàlid. Format esperat: lletra + 7 números + caràcter de control", None, None
        else:
            if not dni or not validar_dni_nie(dni):
                return False, "DNI/NIE no vàlid. Format esperat: 8 números + lletra (DNI) o X/Y/Z + 7 números + lletra (NIE)", None, None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar si el username ya existe
                cursor.execute("SELECT id FROM User WHERE username = ?", (username.strip(),))
                if cursor.fetchone():
                    return False, "Aquest nom d'usuari ja està en ús", None, None
                
                # Verificar si el email ya existe
                cursor.execute("SELECT id FROM User WHERE email = ?", (email.strip(),))
                if cursor.fetchone():
                    return False, "Aquest email ja està en ús", None, None
                
                # Generar contrasenya segura automàticament
                # 12 caracteres: mayúsculas, minúsculas, dígitos
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for _ in range(12))
                password_hash = generate_password_hash(password, method="pbkdf2:sha256")
                
                # Intentar insertar con todas las columnas disponibles
                try:
                    if account_type == 'company':
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, role, account_type, nif, created_at) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                            (username.strip(), password_hash, email.strip(), address.strip(), role, account_type, nif.strip())
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, role, account_type, dni, created_at) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                            (username.strip(), password_hash, email.strip(), address.strip(), role, account_type, dni.strip())
                        )
                except sqlite3.OperationalError:
                    # Si las columnas DNI/NIF no existen, insertar sin ellas
                    try:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, role, account_type, created_at) "
                            "VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
                            (username.strip(), password_hash, email.strip(), address.strip(), role, account_type)
                        )
                    except sqlite3.OperationalError:
                        # Si las columnas role/account_type tampoco existen
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, created_at) "
                            "VALUES (?, ?, ?, ?, datetime('now'))",
                            (username.strip(), password_hash, email.strip(), address.strip())
                        )
                
                user_id = cursor.lastrowid
                conn.commit()
                return True, f"Usuari creat correctament", password, user_id
        except sqlite3.Error as e:
            return False, f"Error creant l'usuari: {str(e)}", None, None
    
    def reset_user_password(self, user_id: int) -> Tuple[bool, str, Optional[str]]:
        """
        Restablir la contrasenya d'un usuari amb una nova contrasenya generada automàticament.
        
        Args:
            user_id (int): ID de l'usuari
            
        Returns:
            Tuple[bool, str, Optional[str]]: (èxit, missatge, nova_contrasenya)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar que l'usuari existeix
                cursor.execute("SELECT id FROM User WHERE id = ?", (user_id,))
                if not cursor.fetchone():
                    return False, "Usuari no trobat", None
                
                # Generar nova contrasenya segura automàticament
                # 12 caracteres: mayúsculas, minúsculas, dígitos
                alphabet = string.ascii_letters + string.digits
                new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
                password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
                
                # Actualizar contrasenya
                cursor.execute(
                    "UPDATE User SET password_hash = ? WHERE id = ?",
                    (password_hash, user_id)
                )
                
                if cursor.rowcount == 0:
                    return False, "Error actualitzant la contrasenya", None
                
                conn.commit()
                return True, "Contrasenya restablida correctament", new_password
        except sqlite3.Error as e:
            return False, f"Error restablint la contrasenya: {str(e)}", None
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Eliminar un usuari.
        
        Args:
            user_id (int): ID de l'usuari
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Verificar si hi ha comandes associades
                cursor.execute('SELECT COUNT(*) FROM "Order" WHERE user_id = ?', (user_id,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return False, f"No es pot eliminar l'usuari perquè té {count} comanda(s) associada(s)"
                
                cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
                if cursor.rowcount == 0:
                    return False, "Usuari no trobat"
                conn.commit()
                return True, "Usuari eliminat correctament"
        except sqlite3.Error as e:
            return False, f"Error eliminant l'usuari: {str(e)}"
    
    # ========== GESTIÓ D'ORDENES ==========
    
    def get_all_orders(self) -> List[Order]:
        """
        Obtenir totes les comandes.
        
        Returns:
            List[Order]: Llista de totes les comandes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, total, created_at, user_id FROM "Order" ORDER BY created_at DESC')
                results = cursor.fetchall()
                
                orders = []
                for row in results:
                    orders.append(Order(
                        id=row[0],
                        total=Decimal(str(row[1])),
                        created_at=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                        user_id=row[3]
                    ))
                return orders
        except sqlite3.Error:
            return []
    
    def get_order_items(self, order_id: int) -> List[OrderItem]:
        """
        Obtenir els items d'una comanda.
        
        Args:
            order_id (int): ID de la comanda
            
        Returns:
            List[OrderItem]: Llista d'items de la comanda
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, order_id, product_id, quantity FROM OrderItem WHERE order_id = ?",
                    (order_id,)
                )
                results = cursor.fetchall()
                
                items = []
                for row in results:
                    items.append(OrderItem(
                        id=row[0],
                        order_id=row[1],
                        product_id=row[2],
                        quantity=row[3]
                    ))
                return items
        except sqlite3.Error:
            return []
    
    def delete_order(self, order_id: int) -> Tuple[bool, str]:
        """
        Eliminar una comanda.
        
        Args:
            order_id (int): ID de la comanda
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Eliminar items primero
                cursor.execute("DELETE FROM OrderItem WHERE order_id = ?", (order_id,))
                # Eliminar comanda
                cursor.execute('DELETE FROM "Order" WHERE id = ?', (order_id,))
                if cursor.rowcount == 0:
                    return False, "Comanda no trobada"
                conn.commit()
                return True, "Comanda eliminada correctament"
        except sqlite3.Error as e:
            return False, f"Error eliminant la comanda: {str(e)}"
    
    def get_dashboard_stats(self) -> Tuple[int, int, int, Decimal]:
        """
        Obtenir estadístiques per al dashboard d'administració.
        
        Returns:
            Tuple[int, int, int, Decimal]: (total_products, total_users, total_orders, total_revenue)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM Product")
                total_products = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM User")
                total_users = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM "Order"')
                total_orders = cursor.fetchone()[0]
                
                cursor.execute('SELECT SUM(total) FROM "Order"')
                total_revenue = Decimal(str(cursor.fetchone()[0] or 0))
                
                return total_products, total_users, total_orders, total_revenue
        except sqlite3.Error:
            return 0, 0, 0, Decimal('0.00')

