"""
Script de migració per afegir el camp company_id a la taula Product
"""

import sqlite3

def migrate():
    """Afegir camp company_id a la taula Product"""
    try:
        conn = sqlite3.connect('techshop.db')
        cursor = conn.cursor()
        
        # Verificar si la columna ja existeix
        cursor.execute("PRAGMA table_info(Product)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'company_id' not in columns:
            # Afegir columna company_id (NULL per productes existents, que pertanyen a l'admin)
            cursor.execute("ALTER TABLE Product ADD COLUMN company_id INTEGER")
            conn.commit()
            print("✅ Columna company_id afegida a la taula Product")
        else:
            print("ℹ️  La columna company_id ja existeix")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error en la migració: {str(e)}")
        return False

if __name__ == "__main__":
    migrate()

