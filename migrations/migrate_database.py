"""
Script per migrar la base de dades existent afegint les noves columnes role i account_type
"""

import sqlite3
import os


def migrate_database():
    """
    Migra la base de dades afegint les columnes role i account_type a la taula User.
    """
    if not os.path.exists('techshop.db'):
        print("❌ No s'ha trobat techshop.db")
        return False
    
    try:
        conn = sqlite3.connect('techshop.db')
        cursor = conn.cursor()
        
        # Verificar si les columnes ja existeixen
        cursor.execute("PRAGMA table_info(User)")
        columns = [row[1] for row in cursor.fetchall()]
        
        has_role = 'role' in columns
        has_account_type = 'account_type' in columns
        
        if has_role and has_account_type:
            print("✅ La base de dades ja té les columnes role i account_type")
            conn.close()
            return True
        
        print("🔄 Migrant base de dades...")
        
        # Afegir columnes si no existeixen
        if not has_role:
            try:
                cursor.execute("ALTER TABLE User ADD COLUMN role VARCHAR(10) DEFAULT 'common'")
                # Actualizar valores existentes
                cursor.execute("UPDATE User SET role = 'common' WHERE role IS NULL")
                print("✅ Columna 'role' afegida")
            except sqlite3.Error as e:
                print(f"⚠️  Error afegint columna 'role': {e}")
        
        if not has_account_type:
            try:
                cursor.execute("ALTER TABLE User ADD COLUMN account_type VARCHAR(10) DEFAULT 'user'")
                # Actualizar valores existentes
                cursor.execute("UPDATE User SET account_type = 'user' WHERE account_type IS NULL")
                print("✅ Columna 'account_type' afegida")
            except sqlite3.Error as e:
                print(f"⚠️  Error afegint columna 'account_type': {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Migració completada correctament")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error durant la migració: {e}")
        return False


if __name__ == '__main__':
    migrate_database()

