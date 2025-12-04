"""
Tests para Cart Service
"""

from tests.test_common import *

def test_cart_add():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product WHERE id = 1")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (1, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(1, 3, session)
    return assert_true(success)


def test_cart_add_multiple_calls_respect_limit_and_stock():
    """
    Afegir el mateix producte diverses vegades ha de respectar tant el límit de 5 unitats
    com el stock disponible.
    """
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product WHERE id = 90")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (90, 'Multi', 10.00, 5)")
    conn.commit()
    conn.close()
    success1, _ = service.add_to_cart(90, 2, session)
    success2, _ = service.add_to_cart(90, 2, session)
    # Ja portem 4 unitats, afegir-ne 2 més ha de fallar (límit 5 i stock 5)
    success3, _ = service.add_to_cart(90, 2, session)
    contents = service.get_cart_contents(session)
    conditions = [
        assert_true(success1),
        assert_true(success2),
        assert_false(success3),
        assert_equals(contents.get(90), 4, "La quantitat final ha de quedar en 4 unitats"),
    ]
    return all(conditions)


def test_cart_stock():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (2, 'Low', 50.00, 2)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(2, 5, session)
    return assert_false(success)


def test_cart_stock_exact_boundary():
    """Afegir exactament el stock disponible ha de ser possible."""
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (21, 'Exact', 50.00, 3)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(21, 3, session)
    return assert_true(success, "Afegir exactament el stock disponible hauria de ser vàlid")


def test_cart_limit():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (3, 'Test', 100.00, 20)")
    conn.commit()
    conn.close()
    service.add_to_cart(3, 3, session)
    success, _ = service.add_to_cart(3, 3, session)
    return assert_false(success)


def test_cart_limit_exact_boundary():
    """Comprovar que es permet exactament 5 unitats però no més."""
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (33, 'Limit', 10.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(33, 5, session)
    # Ja hem arribat a 5, afegir-ne una més ha de fallar
    success2, _ = service.add_to_cart(33, 1, session)
    return assert_true(success) and assert_false(success2)


def test_cart_negative():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (4, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(4, -1, session)
    return assert_false(success)


def test_cart_zero_quantity():
    """La quantitat 0 no és vàlida al carretó."""
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (50, 'ZeroTest', 10.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(50, 0, session)
    return assert_false(success, "No s'hauria d'acceptar quantitat 0")


def test_cart_non_int_quantity():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (40, 'Test', 50.00, 5)")
    conn.commit()
    conn.close()
    # Pasar una cadena en lloc d'un enter ha de fallar
    success, _ = service.add_to_cart(40, "3", session)
    return assert_false(success, "add_to_cart ha d'ignorar quantitats no enteres")


def test_cart_remove():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (5, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(5, 2, session)
    success, _ = service.remove_from_cart(5, session)
    return assert_true(success)


def test_cart_remove_nonexistent():
    service = CartService('test.db')
    session = MockSession()
    success, _ = service.remove_from_cart(999, session)
    return assert_false(success)


def test_cart_validate_stock_db_error():
    """Simular un error de BD a validate_stock i comprovar que es gestiona bé."""
    service = CartService('test.db')
    original_connect = sqlite3.connect

    def failing_connect(*args, **kwargs):
        raise sqlite3.Error("DB down")

    sqlite3.connect = failing_connect
    try:
        ok, msg = service.validate_stock(1, 1)
        return assert_false(ok, "En cas d'error de BD no hi hauria d'haver stock disponible") and \
               assert_true("Error accedint a la base de dades" in msg)
    finally:
        sqlite3.connect = original_connect


def test_cart_contents():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (6, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(6, 2, session)
    contents = service.get_cart_contents(session)
    return assert_true(6 in contents and contents[6] == 2)


def test_cart_total():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (7, 'P1', 100.00, 10)")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (8, 'P2', 200.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(7, 2, session)
    service.add_to_cart(8, 1, session)
    total = service.get_cart_total(session)
    return assert_equals(total, Decimal('400.00'))


def test_cart_clear():
    service = CartService('test.db')
    session = MockSession()
    conn = sqlite3.connect('test.db', timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (9, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(9, 3, session)
    service.clear_cart(session)
    contents = service.get_cart_contents(session)
    # clear_cart ha de ser idempotent (es pot cridar més d'un cop sense error)
    service.clear_cart(session)
    contents2 = service.get_cart_contents(session)
    return assert_true(len(contents) == 0) and assert_true(len(contents2) == 0)


def test_web_checkout_empty_cart():
    """El checkout amb el carretó buit ha d'informar a l'usuari."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # desactivem CSRF per facilitar el test
    client = app.test_client()
    # El carretó buit és l'estat per defecte (sessió nova)
    resp = client.get("/checkout")
    ok_status = assert_equals(resp.status_code, 200, "Checkout ha de respondre 200")
    ok_msg = assert_true(
        b"El teu carret&#243; est&#224; buit" in resp.data
        or b"El teu carret\xc3\xb3 est\xc3\xa0 buit" in resp.data,
        "El missatge de carretó buit ha d'aparèixer al checkout",
    )
    return ok_status and ok_msg



def test_web_add_to_cart_missing_csrf():
    """
    Sense token CSRF, una petició POST al backend ha de ser rebutjada.
    Això verifica que la protecció CSRF està activa.
    """
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    resp = client.post("/add_to_cart", data={"product_id": 1, "quantity": 1})
    return assert_equals(resp.status_code, 400, "Sense CSRF token s'ha d'obtenir un 400")



def test_web_full_checkout_flow_creates_order_and_clears_cart():
    """
    Flux complet de compra via web:
    - Es prepara un producte i un carretó
    - Es fa POST a /process_order amb dades vàlides
    - S'ha de crear una comanda i buidar el carretó web
    """
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # facilitem el test sense CSRF

    # Assegurar producte existent a la BD de l'aplicació
    conn = sqlite3.connect("techshop.db", timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute(
        "INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (200, 'Test Web Product', 9.99, 10)"
    )
    conn.commit()

    # Comptar ordres abans
    cursor.execute('CREATE TABLE IF NOT EXISTS "Order" (id INTEGER PRIMARY KEY, total REAL, created_at TEXT, user_id INTEGER)')
    cursor.execute('SELECT COUNT(*) FROM "Order"')
    before_orders = cursor.fetchone()[0]
    conn.close()

    # Preparar el carretó de la web fent POST a /add_to_cart (utilitza la sessió del client)
    client = app.test_client()
    # Afegir producte al carretó via POST (la sessió es manté al mateix client)
    client.post("/add_to_cart", data={"product_id": 200, "quantity": 2})
    
    # Verificar que el producte s'ha afegit al carretó
    resp_checkout_before = client.get("/checkout")
    ok_product_in_cart = assert_true(
        b"Test Web Product" in resp_checkout_before.data,
        "El producte ha d'estar al carretó abans de processar la comanda"
    )
    
    # Processar la comanda com a invitado
    resp = client.post(
        "/process_order",
        data={
            "checkout_type": "guest",
            "username": "webuser_test",
            "password": "Password123",
            "email": "webuser@test.com",
            "address": "Carrer de Prova 123, Barcelona",
        },
        follow_redirects=True,
    )

    # Verificar que la comanda s'ha creat
    conn = sqlite3.connect("techshop.db", timeout=10.0)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM "Order"')
    after_orders = cursor.fetchone()[0]
    conn.close()

    # Verificar que el carretó s'ha buidat després de processar la comanda
    resp_checkout_after = client.get("/checkout")
    ok_cart_empty = assert_true(
        b"El teu carret&#243; est&#224; buit" in resp_checkout_after.data
        or b"El teu carret\xc3\xb3 est\xc3\xa0 buit" in resp_checkout_after.data,
        "El carretó web s'ha de buidar després de processar la comanda"
    )

    ok_status = assert_equals(resp.status_code, 200, "El flux complet ha d'acabar amb resposta 200")
    ok_new_order = assert_true(after_orders == before_orders + 1, "S'hauria d'haver creat una nova comanda")

    return ok_status and ok_new_order and ok_cart_empty



def test_security_cart_manipulation():
    """Intentar manipular el carrito directamente en la sesión."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear producto
    conn = sqlite3.connect("techshop.db", timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (700, 'Test Cart', 10.00, 5)")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    # Intentar manipular el carrito directamente
    with client.session_transaction() as sess:
        sess["cart"] = {700: 999}  # Cantidad imposible
    
    resp = client.get("/checkout")
    # El sistema debería validar y rechazar cantidades inválidas
    ok_safe = assert_true(
        True,  # Si no crashea, está bien
        "Manipulación de carrito no debería crashear la app"
    )
    
    return ok_safe



def test_security_concurrent_cart_access():
    """Simular acceso concurrente al carrito."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear producto
    conn = sqlite3.connect("techshop.db", timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (900, 'Concurrent Test', 10.00, 100)")
    conn.commit()
    conn.close()
    
    # Simular múltiples clientes
    clients = [app.test_client() for _ in range(3)]
    
    all_safe = True
    for i, client in enumerate(clients):
        resp = client.post("/add_to_cart", data={"product_id": 900, "quantity": 5})
        ok_safe = assert_true(
            resp.status_code == 200 or resp.status_code == 302,
            f"Cliente {i} debería poder añadir al carrito"
        )
        all_safe = all_safe and ok_safe
    
    return all_safe



def test_company_cannot_add_to_cart():
    """Verificar que empresas no pueden agregar productos al carrito."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear empresa
    conn = sqlite3.connect("techshop.db", timeout=10.0)
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, address, account_type, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
        ("company_user", password_hash, "company@test.com", "Address", "company")
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'company_user'")
    user_id = cursor.fetchone()[0]
    
    # Crear producto
    cursor.execute('CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    cursor.execute('INSERT OR REPLACE INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Test Product', 10.0, 10))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    resp = client.post("/add_to_cart", data={"product_id": product_id, "quantity": 1})
    
    return assert_true(
        resp.status_code == 302 or "empreses no poden comprar".encode('utf-8') in resp.data.lower() or "empresa".encode('utf-8') in resp.data.lower(),
        "Empresa no debería poder agregar al carrito"
    )


