"""
Tests para Admin Service
"""

from tests.test_common import *

def test_admin_service_get_dashboard_stats():
    """Verificar que AdminService obtiene estadísticas del dashboard."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    cursor.execute('CREATE TABLE User (id INTEGER PRIMARY KEY, username TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS "Order" (id INTEGER PRIMARY KEY, total REAL, user_id INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Product 1', 10.0, 5))
    cursor.execute('INSERT INTO User (username) VALUES (?)', ('user1',))
    cursor.execute('INSERT INTO "Order" (total, user_id) VALUES (?, ?)', (100.0, 1))
    conn.commit()
    conn.close()
    
    service = AdminService('test.db')
    product_count, user_count, order_count, revenue = service.get_dashboard_stats()
    
    return assert_true(
        product_count == 1 and user_count == 1 and order_count == 1,
        "Debería obtener estadísticas correctas"
    )


# ========== TESTS DE USER SERVICE ==========

