"""
Tests para Order Service
"""

from tests.test_common import *

def test_web_process_order_missing_fields_no_order_created():
    """
    Si falten camps obligatoris al checkout (com a invitado), s'ha de redirigir al checkout
    i no s'ha de crear cap comanda nova.
    """
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # desactivem CSRF per provar només validacions
    client = app.test_client()

    # Comptar ordres actuals a la BD principal de l'aplicació
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS "Order" (id INTEGER PRIMARY KEY, total REAL, created_at TEXT, user_id INTEGER)')
    cursor.execute('SELECT COUNT(*) FROM "Order"')
    before_count = cursor.fetchone()[0]
    conn.close()

    # Intentar processar comanda com a invitado sense camps
    resp = client.post("/process_order", data={"checkout_type": "guest"}, follow_redirects=True)

    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM "Order"')
    after_count = cursor.fetchone()[0]
    conn.close()

    ok_redirect = assert_equals(resp.status_code, 200, "S'ha de redirigir al checkout (amb follow_redirects)")
    ok_no_new_order = assert_equals(
        before_count, after_count, "No s'ha de crear cap comanda si falten camps obligatoris"
    )
    ok_flash = assert_true(
        b"Tots els camps s&#243;n obligatoris" in resp.data
        or b"Tots els camps s\xc3\xb3n obligatoris" in resp.data,
        "S'ha de mostrar el missatge de camps obligatoris",
    )
    return ok_redirect and ok_no_new_order and ok_flash



def test_web_checkout_authenticated_creates_order():
    """Checkout amb usuari autenticat crea comanda correctament."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuari i producte
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("test_auth_order", password_hash, "authorder@test.com")
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute(
        "INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (500, 'Test Auth Order Product', 39.99, 10)"
    )
    cursor.execute('CREATE TABLE IF NOT EXISTS "Order" (id INTEGER PRIMARY KEY, total REAL, created_at TEXT, user_id INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS OrderItem (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)')
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'test_auth_order'")
    user_id = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM "Order"')
    before_orders = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    # Afegir producte al carretó
    client.post("/add_to_cart", data={"product_id": 500, "quantity": 2})
    
    # Processar comanda (només adreça)
    resp = client.post(
        "/process_order",
        data={
            "checkout_type": "authenticated",
            "address": "Carrer Autenticat 456, Barcelona"
        },
        follow_redirects=True
    )
    
    # Verificar que s'ha creat la comanda
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM "Order"')
    after_orders = cursor.fetchone()[0]
    conn.close()
    
    ok_status = assert_equals(resp.status_code, 200, "Processar comanda ha de respondre 200")
    ok_order_created = assert_true(
        after_orders == before_orders + 1,
        "S'ha de crear una nova comanda"
    )
    
    return ok_status and ok_order_created


# ============================================================================
# TESTS DE SEGURIDAD Y CASOS LÍMITE - INTENTAR "ROMPER" LA APLICACIÓN
# ============================================================================


def test_user_service_delete_user_account_with_orders():
    """Test eliminar cuenta de usuario que tiene órdenes."""
    user_service = UserService()
    
    # Crear usuario con orden
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("user_with_order", password_hash, "withorder@example.com", "Address")
    )
    user_id = cursor.lastrowid
    
    # Crear orden
    cursor.execute('CREATE TABLE IF NOT EXISTS "Order" (id INTEGER PRIMARY KEY, total REAL, created_at TEXT, user_id INTEGER)')
    cursor.execute('INSERT INTO "Order" (total, created_at, user_id) VALUES (?, ?, ?)', (100.0, "2024-01-01", user_id))
    order_id = cursor.lastrowid
    
    # Crear OrderItem
    cursor.execute('CREATE TABLE IF NOT EXISTS OrderItem (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)')
    cursor.execute('INSERT INTO OrderItem (order_id, product_id, quantity) VALUES (?, ?, ?)', (order_id, 1, 1))
    
    conn.commit()
    conn.close()
    
    success, message = user_service.delete_user_account(user_id)
    
    ok_success = assert_true(success, f"Debería eliminar usuario incluso con órdenes: {message}")
    
    # Verificar que todo fue eliminado
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM User WHERE id = ?", (user_id,))
    ok_user_deleted = assert_true(cursor.fetchone() is None, "Usuario debería estar eliminado")
    
    cursor.execute("SELECT id FROM \"Order\" WHERE user_id = ?", (user_id,))
    ok_orders_deleted = assert_true(cursor.fetchone() is None, "Órdenes deberían estar eliminadas")
    
    cursor.execute("SELECT id FROM OrderItem WHERE order_id = ?", (order_id,))
    ok_items_deleted = assert_true(cursor.fetchone() is None, "OrderItems deberían estar eliminados")
    
    conn.close()
    
    return ok_success and ok_user_deleted and ok_orders_deleted and ok_items_deleted


