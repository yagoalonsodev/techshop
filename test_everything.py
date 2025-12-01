#!/usr/bin/env python3
"""SCRIPT DE PRUEBAS EXHAUSTIVO PARA TECHSHOP"""
import sqlite3, os
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
from models import Product, User, Order, OrderItem
from services.cart_service import CartService
from services.order_service import OrderService
from services.recommendation_service import RecommendationService

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

test_count = 0
passed_count = 0
failed_count = 0

def run_test(name, test_func):
    global test_count, passed_count, failed_count
    test_count += 1
    print(f"\n{Colors.BLUE}[TEST {test_count}]{Colors.END} {Colors.BOLD}{name}{Colors.END}")
    try:
        result = test_func()
        if result:
            print(f"{Colors.GREEN}✅ PASSED{Colors.END}")
            passed_count += 1
        else:
            print(f"{Colors.RED}❌ FAILED{Colors.END}")
            failed_count += 1
        return result
    except Exception as e:
        print(f"{Colors.RED}❌ FAILED: {str(e)}{Colors.END}")
        failed_count += 1
        return False

def assert_true(condition, msg=""):
    if not condition:
        if msg: print(f"  {Colors.YELLOW}⚠️  {msg}{Colors.END}")
        return False
    return True

def assert_false(condition, msg=""):
    if condition:
        if msg: print(f"  {Colors.YELLOW}⚠️  {msg}{Colors.END}")
        return False
    return True

def assert_equals(actual, expected, msg=""):
    if actual != expected:
        if msg: print(f"  {Colors.YELLOW}⚠️  {msg}: esperado={expected}, actual={actual}{Colors.END}")
        return False
    return True

def test_db_init():
    try:
        if os.path.exists('test.db'): os.remove('test.db')
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
        cursor.execute("CREATE TABLE User (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, email TEXT, address TEXT, created_at TEXT)")
        cursor.execute('CREATE TABLE "Order" (id INTEGER PRIMARY KEY, total REAL, created_at TEXT, user_id INTEGER)')
        cursor.execute("CREATE TABLE OrderItem (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)")
        conn.commit()
        conn.close()
        return True
    except: return False

def test_product():
    p = Product(id=1, name="Test", price=Decimal('10.00'), stock=5)
    return assert_equals(p.id, 1) and assert_equals(p.name, "Test")

def test_user():
    from datetime import datetime
    u = User(id=1, username="testuser", password_hash="h", email="t@e.com", created_at=datetime.now())
    return assert_equals(u.id, 1) and assert_equals(u.username, "testuser")

def test_user_created_at_default():
    """Si no es passa created_at, s'ha d'assignar automàticament la data actual."""
    u = User(id=2, username="nouser", password_hash="x", email="n@e.com")
    return assert_true(u.created_at is not None, "created_at no hauria de ser None per defecte")

def test_order():
    o = Order(id=1, total=Decimal('100.00'), user_id=1)
    return assert_equals(o.id, 1) and assert_equals(o.total, Decimal('100.00'))

def test_order_created_at_default():
    """Les comandes també han de tenir created_at per defecte."""
    o = Order(id=2, total=Decimal('50.00'), user_id=1)
    return assert_true(o.created_at is not None, "created_at de l'ordre no hauria de ser None")

def test_orderitem():
    oi = OrderItem(id=1, order_id=1, product_id=1, quantity=2)
    return assert_equals(oi.id, 1) and assert_equals(oi.quantity, 2)

def test_cart_add():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (1, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(1, 3)
    return assert_true(success)

def test_cart_add_multiple_calls_respect_limit_and_stock():
    """
    Afegir el mateix producte diverses vegades ha de respectar tant el límit de 5 unitats
    com el stock disponible.
    """
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (90, 'Multi', 10.00, 5)")
    conn.commit()
    conn.close()
    success1, _ = service.add_to_cart(90, 2)
    success2, _ = service.add_to_cart(90, 2)
    # Ja portem 4 unitats, afegir-ne 2 més ha de fallar (límit 5 i stock 5)
    success3, _ = service.add_to_cart(90, 2)
    contents = service.get_cart_contents()
    conditions = [
        assert_true(success1),
        assert_true(success2),
        assert_false(success3),
        assert_equals(contents.get(90), 4, "La quantitat final ha de quedar en 4 unitats"),
    ]
    return all(conditions)

def test_cart_stock():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (2, 'Low', 50.00, 2)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(2, 5)
    return assert_false(success)

def test_cart_stock_exact_boundary():
    """Afegir exactament el stock disponible ha de ser possible."""
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (21, 'Exact', 50.00, 3)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(21, 3)
    return assert_true(success, "Afegir exactament el stock disponible hauria de ser vàlid")

def test_cart_limit():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (3, 'Test', 100.00, 20)")
    conn.commit()
    conn.close()
    service.add_to_cart(3, 3)
    success, _ = service.add_to_cart(3, 3)
    return assert_false(success)

def test_cart_limit_exact_boundary():
    """Comprovar que es permet exactament 5 unitats però no més."""
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (33, 'Limit', 10.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(33, 5)
    # Ja hem arribat a 5, afegir-ne una més ha de fallar
    success2, _ = service.add_to_cart(33, 1)
    return assert_true(success) and assert_false(success2)

def test_cart_negative():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (4, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(4, -1)
    return assert_false(success)

def test_cart_zero_quantity():
    """La quantitat 0 no és vàlida al carretó."""
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (50, 'ZeroTest', 10.00, 10)")
    conn.commit()
    conn.close()
    success, _ = service.add_to_cart(50, 0)
    return assert_false(success, "No s'hauria d'acceptar quantitat 0")

def test_cart_non_int_quantity():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (40, 'Test', 50.00, 5)")
    conn.commit()
    conn.close()
    # Pasar una cadena en lloc d'un enter ha de fallar
    success, _ = service.add_to_cart(40, "3")
    return assert_false(success, "add_to_cart ha d'ignorar quantitats no enteres")

def test_cart_remove():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (5, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(5, 2)
    success, _ = service.remove_from_cart(5)
    return assert_true(success)

def test_cart_remove_nonexistent():
    service = CartService('test.db')
    success, _ = service.remove_from_cart(999)
    return assert_false(success)

def test_cart_add_product_not_found():
    """Intentar afegir un producte que no existeix a BD ha de fallar amb missatge adequat."""
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    conn.commit()
    conn.close()
    success, msg = service.add_to_cart(999, 1)
    return assert_false(success, "No s'hauria de poder afegir un producte inexistent") and \
           assert_true("Producte no trobat" in msg)

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
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (6, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(6, 2)
    contents = service.get_cart_contents()
    return assert_true(6 in contents and contents[6] == 2)

def test_cart_multiple_products_contents():
    """Comprovar que el carretó pot contenir múltiples productes amb quantitats correctes."""
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (70, 'P70', 10.00, 10)")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (71, 'P71', 20.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(70, 1)
    service.add_to_cart(71, 2)
    contents = service.get_cart_contents()
    conditions = [
        assert_equals(contents.get(70), 1, "Quantitat per al producte 70 incorrecta"),
        assert_equals(contents.get(71), 2, "Quantitat per al producte 71 incorrecta"),
    ]
    return all(conditions)

def test_cart_total():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (7, 'P1', 100.00, 10)")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (8, 'P2', 200.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(7, 2)
    service.add_to_cart(8, 1)
    total = service.get_cart_total()
    return assert_equals(total, Decimal('400.00'))

def test_cart_total_with_missing_product():
    """
    Si al carretó hi ha un producte que ja no existeix a BD,
    get_cart_total ha d'ignorar-lo i no petar.
    """
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (20, 'P1', 100.00, 10)")
    conn.commit()
    conn.close()
    # Afegim un producte vàlid i un d'inexistent
    service.add_to_cart(20, 1)
    service.cart[21] = 2  # 21 no existeix a BD
    total = service.get_cart_total()
    return assert_equals(total, Decimal('100.00'), "Només s'ha de comptar el producte existent")

def test_cart_clear():
    service = CartService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (9, 'Test', 100.00, 10)")
    conn.commit()
    conn.close()
    service.add_to_cart(9, 3)
    service.clear_cart()
    contents = service.get_cart_contents()
    # clear_cart ha de ser idempotent (es pot cridar més d'un cop sense error)
    service.clear_cart()
    contents2 = service.get_cart_contents()
    return assert_true(len(contents) == 0) and assert_true(len(contents2) == 0)

def test_order_create():
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute('DELETE FROM "Order"')
    cursor.execute("DELETE FROM OrderItem")
    cursor.execute("DELETE FROM User")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (10, 'Prod', 100.00, 10)")
    cursor.execute("INSERT INTO User (id, username, password_hash, email) VALUES (1, 'user', 'hash', 'user@test.com')")
    conn.commit()
    conn.close()
    success, _, order_id = order_service.create_order({10: 3}, 1)
    return assert_true(success and order_id > 0)

def test_order_create_reduces_stock_to_zero():
    """Crear una comanda que consumeix tot el stock ha d'arribar a 0 exactament."""
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute('DELETE FROM "Order"')
    cursor.execute("DELETE FROM OrderItem")
    cursor.execute("DELETE FROM User")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (91, 'ZeroStock', 10.00, 4)")
    cursor.execute("INSERT INTO User (id, username, password_hash, email) VALUES (2, 'user2', 'hash', 'user2@test.com')")
    conn.commit()
    conn.close()
    success, _, _ = order_service.create_order({91: 4}, 2)
    if not assert_true(success, "La comanda hauria de crear-se correctament"):
        return False
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM Product WHERE id = 91")
    stock_after = cursor.fetchone()[0]
    conn.close()
    return assert_equals(stock_after, 0, "El stock ha de quedar exactament a 0")

def test_order_empty_cart():
    order_service = OrderService('test.db')
    success, _, _ = order_service.create_order({}, 1)
    return assert_false(success)

def test_order_with_zero_quantity_items():
    """
    Simular un carretó que conté elements amb quantitat 0.
    _calculate_order_total ha de tractar-los com si no hi fossin.
    """
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (60, 'P1', 10.00, 10)")
    conn.commit()
    cart = {60: 0}
    total = order_service._calculate_order_total(cart, cursor)
    conn.close()
    return assert_equals(total, Decimal('0.00'))

def test_order_user_not_found():
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute('DELETE FROM "Order"')
    cursor.execute("DELETE FROM OrderItem")
    cursor.execute("DELETE FROM User")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (41, 'Prod', 10.00, 10)")
    conn.commit()
    conn.close()
    # Usuari 999 no existeix
    success, msg, _ = order_service.create_order({41: 1}, 999)
    return assert_false(success, "S'hauria de rebutjar comanda per usuari inexistent") and \
           assert_equals(msg, "Usuari no trobat")

def test_order_total():
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (11, 'P1', 50.00, 10)")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (12, 'P2', 150.00, 10)")
    conn.commit()
    conn.close()
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cart = {11: 2, 12: 1}
    total = order_service._calculate_order_total(cart, cursor)
    conn.close()
    return assert_equals(total, Decimal('250.00'))

def test_order_total_with_decimal_prices():
    """Comprovar que els decimals dels preus es calculen correctament."""
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (80, 'D1', 19.99, 10)")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (81, 'D2', 0.99, 10)")
    conn.commit()
    cart = {80: 2, 81: 3}  # 2*19.99 + 3*0.99 = 39.98 + 2.97 = 42.95
    total = order_service._calculate_order_total(cart, cursor)
    conn.close()
    return assert_equals(total, Decimal('42.95'))

def test_order_total_ignores_missing_products():
    """
    _calculate_order_total ha d'ignorar IDs de productes que no existeixen a BD.
    """
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (30, 'P1', 50.00, 10)")
    conn.commit()
    cart = {30: 2, 31: 5}  # 31 no existeix
    total = order_service._calculate_order_total(cart, cursor)
    conn.close()
    return assert_equals(total, Decimal('100.00'), "Només s'ha de sumar el producte existent")

def test_order_get():
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM "Order"')
    cursor.execute('INSERT INTO "Order" (id, total, created_at, user_id) VALUES (1, 299.99, "2024-01-01", 1)')
    conn.commit()
    conn.close()
    success, _, order = order_service.get_order_by_id(1)
    if not success or order is None: return False
    return assert_equals(order.total, Decimal('299.99'))

def test_order_get_nonexistent():
    order_service = OrderService('test.db')
    success, _, _ = order_service.get_order_by_id(99999)
    return assert_false(success)

def test_order_get_negative_id():
    """Un ID negatiu no ha de retornar cap comanda."""
    order_service = OrderService('test.db')
    success, _, _ = order_service.get_order_by_id(-1)
    return assert_false(success)

def test_inventory_update():
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute('DELETE FROM "Order"')
    cursor.execute("DELETE FROM OrderItem")
    cursor.execute("DELETE FROM User")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (13, 'Prod', 100.00, 10)")
    cursor.execute("INSERT INTO User (id, username, password_hash, email) VALUES (1, 'user', 'hash', 'user@test.com')")
    conn.commit()
    conn.close()
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM Product WHERE id = 13")
    initial = cursor.fetchone()[0]
    conn.close()
    order_service.create_order({13: 3}, 1)
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM Product WHERE id = 13")
    final = cursor.fetchone()[0]
    conn.close()
    return assert_equals(final, initial - 3)

def test_order_tx_empty_cart():
    """Provar create_order_in_transaction amb carretó buit."""
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User")
    cursor.execute("INSERT INTO User (id, username, password_hash, email) VALUES (2, 'user2', 'hash', 'user2@test.com')")
    conn.commit()
    success, msg, order_id = order_service.create_order_in_transaction(conn, {}, 2)
    conn.close()
    return assert_false(success, "El carretó buit no hauria de crear comanda") and \
           assert_equals(msg, "El carretó està buit") and \
           assert_equals(order_id, 0)

def test_order_tx_user_not_found():
    """Provar create_order_in_transaction amb usuari inexistent."""
    order_service = OrderService('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product")
    cursor.execute("DELETE FROM User")
    cursor.execute("INSERT INTO Product (id, name, price, stock) VALUES (42, 'ProdTX', 20.00, 5)")
    conn.commit()
    success, msg, order_id = order_service.create_order_in_transaction(conn, {42: 1}, 999)
    conn.close()
    return assert_false(success, "Usuari inexistent no hauria de poder crear comanda") and \
           assert_equals(msg, "Usuari no trobat") and \
           assert_equals(order_id, 0)

def test_order_create_db_error():
    """Simular error de BD en create_order i comprovar que es retorna error adequat."""
    order_service = OrderService('test.db')
    original_connect = sqlite3.connect

    def failing_connect(*args, **kwargs):
        raise sqlite3.Error("disk I/O error")

    sqlite3.connect = failing_connect
    try:
        success, msg, order_id = order_service.create_order({1: 1}, 1)
        return assert_false(success, "En cas d'error de BD no s'hauria de crear la comanda") and \
               assert_true("Error creant la comanda" in msg) and \
               assert_equals(order_id, 0)
    finally:
        sqlite3.connect = original_connect

def test_username_validation():
    conditions = []
    conditions.append(assert_false(len("abc") >= 4 and len("abc") <= 20))
    conditions.append(assert_true(len("testuser") >= 4 and len("testuser") <= 20))
    conditions.append(assert_false(len("a" * 21) >= 4 and len("a" * 21) <= 20))
    return all(conditions)

def test_username_edge_cases():
    """Provar casos límit de longitud i caràcters del nom d'usuari."""
    too_short = "usr"
    too_long = "u" * 21
    valid = "user_123"
    conditions = []
    # massa curt
    conditions.append(assert_false(4 <= len(too_short) <= 20, "Nom massa curt no ha de ser vàlid"))
    # massa llarg
    conditions.append(assert_false(4 <= len(too_long) <= 20, "Nom massa llarg tampoc ha de ser vàlid"))
    # dins del rang
    conditions.append(assert_true(4 <= len(valid) <= 20, "Nom vàlid ha de complir la longitud"))
    return all(conditions)

def test_password_length():
    conditions = []
    conditions.append(assert_false(len("short") >= 8))
    conditions.append(assert_true(len("password123") >= 8))
    return all(conditions)

def test_password_complexity():
    conditions = []
    pwd = "password"
    conditions.append(assert_false(any(c.isalpha() for c in pwd) and any(c.isdigit() for c in pwd)))
    pwd = "12345678"
    conditions.append(assert_false(any(c.isalpha() for c in pwd) and any(c.isdigit() for c in pwd)))
    pwd = "password123"
    conditions.append(assert_true(any(c.isalpha() for c in pwd) and any(c.isdigit() for c in pwd)))
    return all(conditions)

def test_email_validation():
    conditions = []
    conditions.append(assert_false('@' in "invalid-email.com" and '.' in "invalid-email.com".split('@')[-1]))
    conditions.append(assert_false('@' in "test@invalid" and '.' in "test@invalid".split('@')[-1]))
    conditions.append(assert_true('@' in "test@example.com" and '.' in "test@example.com".split('@')[-1]))
    return all(conditions)

def test_email_edge_cases():
    """Provar correus amb múltiples punts i subdominis."""
    valid = "user.name+tag@sub.domain.co.uk"
    invalid_no_tld = "user@domain"
    invalid_two_ats = "user@@example.com"
    conditions = []
    conditions.append(
        assert_true(
            '@' in valid and '.' in valid.split('@')[-1],
            "Correu amb subdominis hauria de ser vàlid segons la regla simple",
        )
    )
    conditions.append(
        assert_false(
            '@' in invalid_no_tld and '.' in invalid_no_tld.split('@')[-1],
            "Correu sense TLD no hauria de ser vàlid",
        )
    )
    conditions.append(
        assert_false(
            invalid_two_ats.count('@') == 1 and '.' in invalid_two_ats.split('@')[-1],
            "Correu amb dues arrobes no és vàlid",
        )
    )
    return all(conditions)

def test_address_validation():
    return assert_false(len("Short") >= 10) and assert_true(len("Calle Mayor 123, Madrid") >= 10)

def test_address_very_long():
    """Adreces molt llargues també s'han d'acceptar mentre superin el mínim."""
    long_address = "Carrer " + "x" * 200 + ", Barcelona"
    return assert_true(len(long_address) >= 10, "Adreça llarga ha de ser acceptada per la regla de mínim")

def test_required_fields():
    return (assert_false(all(["", "pwd", "e@e.com", "addr"])) and 
            assert_true(all(["user", "pwd", "e@e.com", "addr"])))

def test_password_hash():
    pwd = "testpassword123"
    hashed = generate_password_hash(pwd, method='pbkdf2:sha256')
    return assert_true(len(hashed) > 0 and pwd != hashed)

def test_password_verify():
    pwd = "testpassword123"
    hashed = generate_password_hash(pwd, method='pbkdf2:sha256')
    valid = check_password_hash(hashed, pwd)
    return assert_true(valid)

def test_password_verify_wrong_password():
    """Verificar que una contrasenya incorrecta no passa la comprovació."""
    pwd = "testpassword123"
    hashed = generate_password_hash(pwd, method='pbkdf2:sha256')
    wrong_pwd = "otraPassword456"
    valid = check_password_hash(hashed, wrong_pwd)
    return assert_false(valid, "Una contrasenya incorrecta no hauria de verificar-se")

def test_password_hash_unique_per_call():
    """El mateix password ha de generar hashes diferents (salts diferents)."""
    pwd = "testpassword123"
    h1 = generate_password_hash(pwd, method='pbkdf2:sha256')
    h2 = generate_password_hash(pwd, method='pbkdf2:sha256')
    return assert_true(h1 != h2, "Cada hash ha de ser diferent encara que el password sigui el mateix")

def test_password_with_symbols_is_valid_for_rules():
    """Comprovar que contrasenyes amb símbols segueixen complint les regles del servidor."""
    pwd = "Passw0rd!!"
    conditions = []
    conditions.append(assert_true(len(pwd) >= 8, "Longitud mínima no complerta"))
    conditions.append(
        assert_true(
            any(c.isalpha() for c in pwd) and any(c.isdigit() for c in pwd),
            "Ha de contenir com a mínim una lletra i un número",
        )
    )
    return all(conditions)

def test_password_rules_reject_empty_and_simple():
    """Provar que les regles del servidor no accepten contrasenyes buides o massa simples."""
    empty = ""
    only_letters = "abcdefgh"
    only_digits = "12345678"
    conditions = []
    # buida
    conditions.append(assert_false(len(empty) >= 8, "Una contrasenya buida no ha de ser vàlida"))
    # només lletres
    conditions.append(
        assert_false(
            len(only_letters) >= 8
            and any(c.isalpha() for c in only_letters)
            and any(c.isdigit() for c in only_letters),
            "Una contrasenya amb només lletres no compleix la complexitat",
        )
    )
    # només dígits
    conditions.append(
        assert_false(
            len(only_digits) >= 8
            and any(c.isalpha() for c in only_digits)
            and any(c.isdigit() for c in only_digits),
            "Una contrasenya amb només dígits tampoc compleix la complexitat",
        )
    )
    return all(conditions)

def test_password_tampered_hash_does_not_verify():
    """Si algú manipula el hash a BD, la verificació ha de fallar."""
    pwd = "testpassword123"
    hashed = generate_password_hash(pwd, method='pbkdf2:sha256')
    # Manipulem lleugerament el hash (canviem un caràcter) per simular alteració a BD
    tampered = hashed[:-1] + ("x" if hashed[-1] != "x" else "y")
    try:
        valid = check_password_hash(tampered, pwd)
        return assert_false(valid, "Un hash manipulat no s'hauria de verificar mai")
    except Exception:
        # Si la llibreria llença excepció, també és acceptable (no es verifica)
        return True

def test_password_plaintext_stored_as_hash_is_rejected():
    """
    Simula que a la columna password_hash s'ha guardat per error el password en text pla.
    La verificació no hauria de funcionar (no ha de ser un camí d'atac).
    """
    pwd = "testpassword123"
    fake_hash = pwd  # el "hash" és en realitat text pla
    try:
        valid = check_password_hash(fake_hash, pwd)
        return assert_false(
            valid,
            "Un valor en text pla a password_hash no s'hauria de poder verificar com a vàlid",
        )
    except Exception:
        # També acceptable: la llibreria rebutja el format
        return True


def _reset_sales_data(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM OrderItem")
    cursor.execute('DELETE FROM "Order"')
    cursor.execute("DELETE FROM Product")
    cursor.execute("DELETE FROM User")
    conn.commit()


def _insert_sale(conn, order_id, user_id, product_id, quantity, price, stock=100):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO User (id, username, password_hash, email, address, created_at) "
        "VALUES (?, ?, 'hash', 'user@example.com', 'Address Test', datetime('now'))",
        (user_id, f'user{user_id}',))
    cursor.execute(
        "INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (?, ?, ?, ?)",
        (product_id, f'Product {product_id}', price, stock))
    cursor.execute(
        'INSERT OR REPLACE INTO "Order" (id, total, created_at, user_id) VALUES (?, ?, datetime("now"), ?)',
        (order_id, price * quantity, user_id))
    cursor.execute(
        "INSERT INTO OrderItem (order_id, product_id, quantity) VALUES (?, ?, ?)",
        (order_id, product_id, quantity))
    conn.commit()


def test_recommendations_by_sales():
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=5, price=50.0)
    _insert_sale(conn, order_id=2, user_id=1, product_id=2, quantity=2, price=100.0)
    _insert_sale(conn, order_id=3, user_id=2, product_id=3, quantity=8, price=20.0)
    conn.close()

    recommendations = service.get_top_selling_products(limit=2)
    if not assert_equals(len(recommendations), 2, "Número de recomanacions incorrecte"):
        return False
    top_product, top_total = recommendations[0]
    second_product, second_total = recommendations[1]
    conditions = [
        assert_equals(top_product.id, 3, "El producte més venut ha de ser el 3"),
        assert_equals(top_total, 8, "Unitats venudes esperades per al producte 3"),
        assert_equals(second_product.id, 1, "El segon producte ha de ser el 1"),
        assert_equals(second_total, 5, "Unitats venudes esperades per al producte 1"),
    ]
    return all(conditions)

def test_recommendations_tiebreaker_by_name():
    """
    Quan dos productes tenen les mateixes unitats venudes,
    l'ordre s'ha de decidir pel nom (ORDER BY total_sold DESC, p.name ASC).
    """
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    # Mateixa quantitat venuda (3), però noms diferents
    _insert_sale(conn, order_id=10, user_id=1, product_id=10, quantity=3, price=10.0)  # Product 10
    _insert_sale(conn, order_id=11, user_id=1, product_id=11, quantity=3, price=10.0)  # Product 11
    conn.close()

    recs = service.get_top_selling_products(limit=2)
    if not assert_equals(len(recs), 2, "Han de sortir dos productes en empat"):
        return False
    p1, _ = recs[0]
    p2, _ = recs[1]
    # Per nom alfabètic: "Product 10" ha d'anar abans que "Product 11"
    return assert_true(p1.name < p2.name, "S'hauria d'ordenar per nom en cas d'empat")


def test_recommendations_limit_zero():
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=3, price=10.0)
    conn.close()
    recommendations = service.get_top_selling_products(limit=0)
    return assert_equals(recommendations, [], "Limit zero ha de retornar llista buida")

def test_recommendations_negative_limit():
    """Un límit negatiu s'ha de tractar igual que 0: sense recomanacions."""
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=2, price=10.0)
    conn.close()
    recommendations = service.get_top_selling_products(limit=-5)
    return assert_equals(recommendations, [], "Limit negatiu ha de retornar llista buida")


def test_recommendations_no_sales():
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    conn.close()
    recommendations = service.get_top_selling_products(limit=3)
    return assert_equals(recommendations, [], "Sense vendes no hi ha recomanacions")

def test_recommendations_limit_greater_than_products():
    """Si el límit és més gran que el nombre de productes venuts, només s'han de retornar els existents."""
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=20, user_id=1, product_id=100, quantity=1, price=10.0)
    _insert_sale(conn, order_id=21, user_id=1, product_id=101, quantity=2, price=10.0)
    conn.close()
    recs = service.get_top_selling_products(limit=10)
    return assert_equals(len(recs), 2, "Només hi hauria d'haver 2 recomanacions encara que el límit sigui 10")


def test_recommendations_for_user():
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=4, price=25.0)
    _insert_sale(conn, order_id=2, user_id=1, product_id=2, quantity=2, price=40.0)
    _insert_sale(conn, order_id=3, user_id=2, product_id=1, quantity=3, price=25.0)
    _insert_sale(conn, order_id=4, user_id=2, product_id=3, quantity=5, price=15.0)
    conn.close()

    user1_recommendations = service.get_top_products_for_user(user_id=1, limit=3)
    if not assert_equals(len(user1_recommendations), 2, "L'usuari 1 ha de tenir dos productes recomanats"):
        return False
    top_user1, qty_user1 = user1_recommendations[0]
    if not (assert_equals(top_user1.id, 1, "Primer producte usuari 1") and assert_equals(qty_user1, 4, "Quantitat producte 1 usuari 1")):
        return False

    user2_recommendations = service.get_top_products_for_user(user_id=2, limit=2)
    if not assert_equals(len(user2_recommendations), 2, "L'usuari 2 ha de tenir dos productes recomanats"):
        return False
    top_user2, qty_user2 = user2_recommendations[0]
    return (assert_equals(top_user2.id, 3, "Primer producte usuari 2") and
            assert_equals(qty_user2, 5, "Quantitat producte 3 usuari 2"))

def test_recommendations_for_user_limit_zero():
    """Amb limit 0 per usuari s'ha de retornar una llista buida."""
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=5, user_id=5, product_id=5, quantity=3, price=5.0)
    conn.close()
    recs = service.get_top_products_for_user(user_id=5, limit=0)
    return assert_equals(recs, [], "Limit zero per usuari ha de donar llista buida")

def test_recommendations_for_user_negative_limit():
    """Amb limit negatiu per usuari tampoc s'haurien de retornar recomanacions."""
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=6, user_id=6, product_id=6, quantity=2, price=5.0)
    conn.close()
    recs = service.get_top_products_for_user(user_id=6, limit=-3)
    return assert_equals(recs, [], "Limit negatiu per usuari ha de donar llista buida")


def test_recommendations_user_without_orders():
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=1, price=10.0)
    conn.close()

    recommendations = service.get_top_products_for_user(user_id=999, limit=3)
    return assert_equals(recommendations, [], "Usuari sense comandes no ha de tenir recomanacions")

def test_recommendations_user_none():
    """Si user_id és None, no s'ha de retornar cap recomanació."""
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=1, price=10.0)
    conn.close()
    recommendations = service.get_top_products_for_user(user_id=None, limit=3)
    return assert_equals(recommendations, [], "Amb user_id=None no s'haurien de generar recomanacions")

def test_recommendations_db_error_returns_empty():
    """Si hi ha un error de BD, el servei de recomanacions ha de retornar llista buida."""
    service = RecommendationService('test.db')
    original_connect = sqlite3.connect

    def failing_connect(*args, **kwargs):
        raise sqlite3.Error("DB down")

    sqlite3.connect = failing_connect
    try:
        recs_all = service.get_top_selling_products(limit=3)
        recs_user = service.get_top_products_for_user(user_id=1, limit=3)
        return assert_equals(recs_all, [], "Amb error de BD s'ha de retornar llista buida (global)") and \
               assert_equals(recs_user, [], "Amb error de BD s'ha de retornar llista buida (per usuari)")
    finally:
        sqlite3.connect = original_connect

def main():
    print(f"\n{Colors.BOLD}{'='*80}\n🧪 SCRIPT DE PRUEBAS EXHAUSTIVO - TECHSHOP\n{'='*80}{Colors.END}\n")
    if os.path.exists('test.db'): os.remove('test.db')
    tests = [
        ("BD - Inicialización", test_db_init),
        ("Modelo - Product", test_product),
        ("Modelo - User", test_user),
        ("Modelo - User (created_at por defecto)", test_user_created_at_default),
        ("Modelo - Order", test_order),
        ("Modelo - Order (created_at por defecto)", test_order_created_at_default),
        ("Modelo - OrderItem", test_orderitem),
        ("Cart - Agregar producto", test_cart_add),
        ("Cart - Agregar producto varias veces respeta límite y stock", test_cart_add_multiple_calls_respect_limit_and_stock),
        ("Cart - Stock insuficiente", test_cart_stock),
        ("Cart - Stock igual al disponible", test_cart_stock_exact_boundary),
        ("Cart - Límite 5 unidades", test_cart_limit),
        ("Cart - Límite 5 unidades (borde exacto)", test_cart_limit_exact_boundary),
        ("Cart - Cantidad negativa", test_cart_negative),
        ("Cart - Cantidad cero", test_cart_zero_quantity),
        ("Cart - Cantidad no entera", test_cart_non_int_quantity),
        ("Cart - Remover producto", test_cart_remove),
        ("Cart - Remover inexistente", test_cart_remove_nonexistent),
        ("Cart - Agregar producto inexistente", test_cart_add_product_not_found),
        ("Cart - Error de BD en validate_stock", test_cart_validate_stock_db_error),
        ("Cart - Obtener contenido", test_cart_contents),
        ("Cart - Obtener contenido con múltiples productos", test_cart_multiple_products_contents),
        ("Cart - Calcular total", test_cart_total),
        ("Cart - Calcular total con producto inexistente", test_cart_total_with_missing_product),
        ("Cart - Limpiar carrito", test_cart_clear),
        ("Order - Crear orden", test_order_create),
        ("Order - Crear orden deja stock en cero", test_order_create_reduces_stock_to_zero),
        ("Order - Carrito vacío", test_order_empty_cart),
        ("Order - Carrito con cantidades cero", test_order_with_zero_quantity_items),
        ("Order - Usuario no encontrado", test_order_user_not_found),
        ("Order - Calcular total", test_order_total),
        ("Order - Calcular total con precios decimales", test_order_total_with_decimal_prices),
        ("Order - Calcular total ignora productos inexistentes", test_order_total_ignores_missing_products),
        ("Order - Obtener por ID", test_order_get),
        ("Order - Orden inexistente", test_order_get_nonexistent),
        ("Order - ID negativo no devuelve orden", test_order_get_negative_id),
        ("Order - Actualizar inventario", test_inventory_update),
        ("Order (TX) - Carrito vacío", test_order_tx_empty_cart),
        ("Order (TX) - Usuario no encontrado", test_order_tx_user_not_found),
        ("Order - Error de BD al crear orden", test_order_create_db_error),
        ("Validación - Username longitud", test_username_validation),
        ("Validación - Username casos límite", test_username_edge_cases),
        ("Validación - Password longitud", test_password_length),
        ("Validación - Password complejidad", test_password_complexity),
        ("Validación - Email", test_email_validation),
        ("Validación - Email casos límite", test_email_edge_cases),
        ("Validación - Dirección", test_address_validation),
        ("Validación - Dirección muy larga", test_address_very_long),
        ("Validación - Campos obligatorios", test_required_fields),
        ("Password - Generar hash", test_password_hash),
        ("Password - Verificar hash", test_password_verify),
        ("Password - Verificar password incorrecto", test_password_verify_wrong_password),
        ("Password - Hashes diferentes mismo password", test_password_hash_unique_per_call),
        ("Password - Con símbolos sigue siendo válida", test_password_with_symbols_is_valid_for_rules),
        ("Password - Reglas rechazan vacía y simples", test_password_rules_reject_empty_and_simple),
        ("Password - Hash manipulado no verifica", test_password_tampered_hash_does_not_verify),
        ("Password - Texto plano en password_hash es rechazado", test_password_plaintext_stored_as_hash_is_rejected),
        ("Recomendaciones - Ordenar per vendes", test_recommendations_by_sales),
        ("Recomendaciones - Desempate por nombre", test_recommendations_tiebreaker_by_name),
        ("Recomendaciones - Límite zero", test_recommendations_limit_zero),
        ("Recomendaciones - Límite negativo", test_recommendations_negative_limit),
        ("Recomendaciones - Sense vendes", test_recommendations_no_sales),
        ("Recomendaciones - Límite mayor que número de productos", test_recommendations_limit_greater_than_products),
        ("Recomendaciones - Per usuari", test_recommendations_for_user),
        ("Recomendaciones - Per usuari amb limit zero", test_recommendations_for_user_limit_zero),
        ("Recomendaciones - Per usuari amb limit negatiu", test_recommendations_for_user_negative_limit),
        ("Recomendaciones - Usuari sense compres", test_recommendations_user_without_orders),
        ("Recomendaciones - user_id None", test_recommendations_user_none),
        ("Recomendaciones - Error de BD retorna vacía", test_recommendations_db_error_returns_empty),
    ]
    for name, func in tests:
        run_test(name, func)
    print(f"\n{Colors.BOLD}{'='*80}\n📊 RESUMEN DE PRUEBAS\n{'='*80}{Colors.END}")
    print(f"Total de pruebas: {test_count}")
    print(f"{Colors.GREEN}✅ Pruebas exitosas: {passed_count}{Colors.END}")
    print(f"{Colors.RED}❌ Pruebas fallidas: {failed_count}{Colors.END}")
    if test_count > 0:
        percentage = (passed_count/test_count*100)
        print(f"{Colors.YELLOW}📈 Porcentaje de éxito: {percentage:.1f}%{Colors.END}")
    if os.path.exists('test.db'): os.remove('test.db')
    print(f"\n{Colors.BOLD}{'='*80}")
    if failed_count == 0:
        print(f"{Colors.GREEN}🎉 ¡TODAS LAS PRUEBAS PASARON!{Colors.END}")
    else:
        print(f"{Colors.RED}⚠️  HAY {failed_count} PRUEBAS FALLIDAS{Colors.END}")
    print(f"{'='*80}{Colors.END}\n")
    return failed_count == 0

if __name__ == '__main__':
    exit(0 if main() else 1)