"""
Script per afegir les columnes DNI i NIF a la taula User
"""

import sqlite3
import sys


def migrate_add_dni_nif():
    """
    Afegir les columnes DNI i NIF a la taula User si no existeixen.
    """
    try:
        conn = sqlite3.connect('techshop.db')
        cursor = conn.cursor()
        
        # Verificar si les columnes ja existeixen
        cursor.execute("PRAGMA table_info(User)")
        columns = [column[1] for column in cursor.fetchall()]
        
        changes_made = False
        
        # Afegir columna DNI si no existeix
        if 'dni' not in columns:
            try:
                cursor.execute("ALTER TABLE User ADD COLUMN dni VARCHAR(20)")
                print("✅ Columna 'dni' afegida correctament")
                changes_made = True
            except sqlite3.OperationalError as e:
                print(f"⚠️  Error afegint columna 'dni': {e}")
        
        # Afegir columna NIF si no existeix
        if 'nif' not in columns:
            try:
                cursor.execute("ALTER TABLE User ADD COLUMN nif VARCHAR(20)")
                print("✅ Columna 'nif' afegida correctament")
                changes_made = True
            except sqlite3.OperationalError as e:
                print(f"⚠️  Error afegint columna 'nif': {e}")
        
        if not changes_made:
            print("ℹ️  Les columnes DNI i NIF ja existeixen")
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error en la migració: {e}")
        return False


if __name__ == '__main__':
    success = migrate_add_dni_nif()
    sys.exit(0 if success else 1)

