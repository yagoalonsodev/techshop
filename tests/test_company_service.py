"""
Tests para Company Service
"""

from tests.test_common import *

def test_company_service_get_company_products():
    """Verificar que CompanyService obtiene productos de una empresa."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 2', 20.0, 10, 1))
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 3', 30.0, 15, 2))
    conn.commit()
    conn.close()
    
    service = CompanyService('test.db')
    products = service.get_company_products(1)
    
    return assert_equals(len(products), 2, "Debería obtener solo productos de la empresa 1")



def test_company_service_get_product_by_id():
    """Verificar que CompanyService obtiene un producto de la empresa."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = CompanyService('test.db')
    product = service.get_product_by_id(product_id, 1)
    
    return assert_true(product is not None and product.name == 'Product 1', "Debería obtener el producto de la empresa")



def test_company_service_get_product_by_id_wrong_company():
    """Verificar que CompanyService no obtiene producto de otra empresa."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = CompanyService('test.db')
    product = service.get_product_by_id(product_id, 2)
    
    return assert_true(product is None, "No debería obtener producto de otra empresa")



def test_company_service_create_product():
    """Verificar que CompanyService crea un producto."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    conn.commit()
    conn.close()
    
    service = CompanyService('test.db')
    success, message, product_id = service.create_product(1, 'New Product', Decimal('15.50'), 10)
    
    return assert_true(success and product_id is not None, "Debería crear el producto correctamente")



def test_company_service_update_product():
    """Verificar que CompanyService actualiza un producto."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = CompanyService('test.db')
    success, message = service.update_product(product_id, 1, 'Updated Product', Decimal('20.00'), 15)
    
    return assert_true(success, "Debería actualizar el producto correctamente")



def test_company_service_update_product_wrong_company():
    """Verificar que CompanyService no actualiza producto de otra empresa."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = CompanyService('test.db')
    success, message = service.update_product(product_id, 2, 'Updated Product', Decimal('20.00'), 15)
    
    return assert_false(success, "No debería actualizar producto de otra empresa")



def test_company_service_can_delete_product():
    """Verificar que CompanyService permite eliminar producto sin ventas."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS OrderItem (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = CompanyService('test.db')
    can_delete, message = service.can_delete_product(product_id, 1)
    
    return assert_true(can_delete, "Debería permitir eliminar producto sin ventas")



def test_company_service_cannot_delete_product_with_sales():
    """Verificar que CompanyService no permite eliminar producto con ventas."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS OrderItem (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    conn.commit()
    product_id = cursor.lastrowid
    cursor.execute('INSERT INTO OrderItem (order_id, product_id, quantity) VALUES (?, ?, ?)', (1, product_id, 2))
    conn.commit()
    conn.close()
    
    service = CompanyService('test.db')
    can_delete, message = service.can_delete_product(product_id, 1)
    
    return assert_false(can_delete, "No debería permitir eliminar producto con ventas")



def test_company_service_delete_product():
    """Verificar que CompanyService elimina un producto."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, company_id INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS OrderItem (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)', ('Product 1', 10.0, 5, 1))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = CompanyService('test.db')
    success, message = service.delete_product(product_id, 1)
    
    # Verificar que se eliminó
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Product WHERE id = ?', (product_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    return assert_true(success and count == 0, "Debería eliminar el producto")


# ========== TESTS DE EMPRESAS NO PUEDEN COMPRAR ==========


def test_company_cannot_checkout():
    """Verificar que empresas no pueden acceder al checkout."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear empresa
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, address, account_type, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
        ("company_user2", password_hash, "company2@test.com", "Address", "company")
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'company_user2'")
    user_id = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    resp = client.get("/checkout")
    
    return assert_true(
        resp.status_code == 302 or "no pots comprar".encode('utf-8') in resp.data.lower(),
        "Empresa no debería poder acceder al checkout"
    )


