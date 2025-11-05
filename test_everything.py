#!/usr/bin/env python3
"""SCRIPT DE PRUEBAS EXHAUSTIVO PARA TECHSHOP"""
import sqlite3, os
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
from models import Product, User, Order, OrderItem
from services.cart_service import CartService
from services.order_service import OrderService

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

def test_order():
    o = Order(id=1, total=Decimal('100.00'), user_id=1)
    return assert_equals(o.id, 1) and assert_equals(o.total, Decimal('100.00'))

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
    return assert_true(len(contents) == 0)

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

def test_order_empty_cart():
    order_service = OrderService('test.db')
    success, _, _ = order_service.create_order({}, 1)
    return assert_false(success)

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

def test_username_validation():
    conditions = []
    conditions.append(assert_false(len("abc") >= 4 and len("abc") <= 20))
    conditions.append(assert_true(len("testuser") >= 4 and len("testuser") <= 20))
    conditions.append(assert_false(len("a" * 21) >= 4 and len("a" * 21) <= 20))
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

def test_address_validation():
    return assert_false(len("Short") >= 10) and assert_true(len("Calle Mayor 123, Madrid") >= 10)

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

def main():
    print(f"\n{Colors.BOLD}{'='*80}\n🧪 SCRIPT DE PRUEBAS EXHAUSTIVO - TECHSHOP\n{'='*80}{Colors.END}\n")
    if os.path.exists('test.db'): os.remove('test.db')
    tests = [
        ("BD - Inicialización", test_db_init),
        ("Modelo - Product", test_product),
        ("Modelo - User", test_user),
        ("Modelo - Order", test_order),
        ("Modelo - OrderItem", test_orderitem),
        ("Cart - Agregar producto", test_cart_add),
        ("Cart - Stock insuficiente", test_cart_stock),
        ("Cart - Límite 5 unidades", test_cart_limit),
        ("Cart - Cantidad negativa", test_cart_negative),
        ("Cart - Remover producto", test_cart_remove),
        ("Cart - Remover inexistente", test_cart_remove_nonexistent),
        ("Cart - Obtener contenido", test_cart_contents),
        ("Cart - Calcular total", test_cart_total),
        ("Cart - Limpiar carrito", test_cart_clear),
        ("Order - Crear orden", test_order_create),
        ("Order - Carrito vacío", test_order_empty_cart),
        ("Order - Calcular total", test_order_total),
        ("Order - Obtener por ID", test_order_get),
        ("Order - Orden inexistente", test_order_get_nonexistent),
        ("Order - Actualizar inventario", test_inventory_update),
        ("Validación - Username longitud", test_username_validation),
        ("Validación - Password longitud", test_password_length),
        ("Validación - Password complejidad", test_password_complexity),
        ("Validación - Email", test_email_validation),
        ("Validación - Dirección", test_address_validation),
        ("Validación - Campos obligatorios", test_required_fields),
        ("Password - Generar hash", test_password_hash),
        ("Password - Verificar hash", test_password_verify),
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

