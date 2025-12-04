"""
Script per crear un usuari administrador de prova
"""

import sqlite3
from werkzeug.security import generate_password_hash


def create_admin_user(username="admin", password="Admin123", email="admin@techshop.com"):
    """
    Crear un usuari administrador.
    
    Args:
        username (str): Nom d'usuari de l'admin
        password (str): Contrasenya de l'admin
        email (str): Email de l'admin
    """
    try:
        conn = sqlite3.connect('techshop.db')
        cursor = conn.cursor()
        
        # Verificar si l'usuari ja existeix
        cursor.execute("SELECT id FROM User WHERE username = ?", (username,))
        existing = cursor.fetchone()
        
        if existing:
            # Actualizar a admin si ya existe
            try:
                cursor.execute(
                    "UPDATE User SET role = 'admin', account_type = 'user', email = ? WHERE username = ?",
                    (email, username)
                )
                print(f"✅ Usuari '{username}' actualitzat a administrador")
            except sqlite3.OperationalError:
                print(f"⚠️  L'usuari '{username}' existeix però les columnes role/account_type no estan disponibles")
        else:
            # Crear nou usuari admin
            password_hash = generate_password_hash(password, method="pbkdf2:sha256")
            try:
                cursor.execute(
                    "INSERT INTO User (username, password_hash, email, address, role, account_type, created_at) "
                    "VALUES (?, ?, ?, ?, 'admin', 'user', datetime('now'))",
                    (username, password_hash, email, "Carrer Admin 1, Barcelona")
                )
            except sqlite3.OperationalError:
                # Si las columnas no existen, crear sin ellas
                cursor.execute(
                    "INSERT INTO User (username, password_hash, email, address, created_at) "
                    "VALUES (?, ?, ?, ?, datetime('now'))",
                    (username, password_hash, email, "Carrer Admin 1, Barcelona")
                )
                print(f"⚠️  Usuari '{username}' creat però les columnes role/account_type no estan disponibles")
                print("   Executa migrate_database.py per afegir les columnes")
            else:
                print(f"✅ Usuari administrador creat:")
                print(f"   Username: {username}")
                print(f"   Password: {password}")
                print(f"   Email: {email}")
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error creant l'usuari admin: {e}")
        return False


if __name__ == '__main__':
    create_admin_user()

