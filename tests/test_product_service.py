"""
Tests para Product Service
"""

from tests.test_common import *

def test_product_service_get_all_products():
    """Verificar que ProductService obtiene todos los productos."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Product 1', 10.0, 5))
    cursor.execute('INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Product 2', 20.0, 10))
    conn.commit()
    conn.close()
    
    service = ProductService('test.db')
    products = service.get_all_products()
    
    return assert_equals(len(products), 2, "Debería obtener 2 productos")



def test_product_service_get_product_by_id():
    """Verificar que ProductService obtiene un producto por ID."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Product 1', 10.0, 5))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = ProductService('test.db')
    product = service.get_product_by_id(product_id)
    
    return assert_true(product is not None and product.name == 'Product 1', "Debería obtener el producto correcto")



def test_product_service_get_product_by_id_nonexistent():
    """Verificar que ProductService retorna None para producto inexistente."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    conn.commit()
    conn.close()
    
    service = ProductService('test.db')
    product = service.get_product_by_id(999)
    
    return assert_true(product is None, "Debería retornar None para producto inexistente")



def test_product_service_get_products_by_ids():
    """Verificar que ProductService obtiene productos por lista de IDs."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Product 1', 10.0, 5))
    cursor.execute('INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Product 2', 20.0, 10))
    conn.commit()
    product_id1 = cursor.lastrowid - 1
    product_id2 = cursor.lastrowid
    conn.close()
    
    service = ProductService('test.db')
    products = service.get_products_by_ids([(product_id1, 2), (product_id2, 3)])
    
    return assert_equals(len(products), 2, "Debería obtener 2 productos con cantidades")



def test_product_service_get_products_by_ids_dict():
    """Verificar que ProductService acepta dict como entrada."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    cursor.execute('INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)', ('Product 1', 10.0, 5))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    service = ProductService('test.db')
    products = service.get_products_by_ids({product_id: 2})
    
    return assert_equals(len(products), 1, "Debería obtener 1 producto desde dict")


# ========== TESTS DE COMPANY SERVICE ==========

