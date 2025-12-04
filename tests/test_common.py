"""
Utilidades comunes para todos los tests
"""
import sqlite3
import os
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash

from app import app  # para tests de integración Flask
from models import Product, User, Order, OrderItem
from services.cart_service import CartService
from services.order_service import OrderService
from services.recommendation_service import RecommendationService
from utils.validators import validar_dni, validar_nie, validar_cif, validar_dni_nie, validar_cif_nif
from services.user_service import UserService
from services.admin_service import AdminService
from services.product_service import ProductService
from services.company_service import CompanyService


class MockSession:
    """Clase mock para simular una sesión de Flask en los tests unitarios."""
    def __init__(self):
        self._data = {}
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __contains__(self, key):
        return key in self._data
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]
    
    def clear(self):
        self._data.clear()
    
    @property
    def modified(self):
        return True
    
    @modified.setter
    def modified(self, value):
        pass


class Colors:
    """Colores para output en terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


# Contadores globales para tests
test_count = 0
passed_count = 0
failed_count = 0


def run_test(name, test_func):
    """Ejecuta un test y actualiza contadores globales"""
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
    """Assert que una condición es True"""
    if not condition:
        if msg: 
            print(f"  {Colors.YELLOW}⚠️  {msg}{Colors.END}")
        return False
    return True


def assert_false(condition, msg=""):
    """Assert que una condición es False"""
    if condition:
        if msg: 
            print(f"  {Colors.YELLOW}⚠️  {msg}{Colors.END}")
        return False
    return True


def assert_equals(actual, expected, msg=""):
    """Assert que dos valores son iguales"""
    if actual != expected:
        if msg: 
            print(f"  {Colors.YELLOW}⚠️  {msg}: esperado={expected}, actual={actual}{Colors.END}")
        return False
    return True


def reset_test_counters():
    """Resetea los contadores globales de tests"""
    global test_count, passed_count, failed_count
    test_count = 0
    passed_count = 0
    failed_count = 0


def get_test_stats():
    """Retorna estadísticas de tests"""
    global test_count, passed_count, failed_count
    return {
        'total': test_count,
        'passed': passed_count,
        'failed': failed_count,
        'success_rate': (passed_count / test_count * 100) if test_count > 0 else 0
    }


def init_test_db():
    """Inicializa una base de datos de prueba"""
    if os.path.exists('test.db'):
        os.remove('test.db')
    
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(20) NOT NULL UNIQUE,
            password_hash VARCHAR(60) NOT NULL,
            email VARCHAR(100) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            role VARCHAR(20) DEFAULT 'common',
            account_type VARCHAR(20) DEFAULT 'user',
            address TEXT,
            dni VARCHAR(20),
            nif VARCHAR(20),
            company_name VARCHAR(100),
            newsletter BOOLEAN DEFAULT 0,
            policies_accepted BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "Order" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total DECIMAL(10,2) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES User(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderItem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES "Order"(id),
            FOREIGN KEY (product_id) REFERENCES Product(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    return 'test.db'


def cleanup_test_db():
    """Limpia la base de datos de prueba"""
    if os.path.exists('test.db'):
        os.remove('test.db')


def _reset_sales_data(conn):
    """Resetea datos de ventas para tests de recomendaciones"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM OrderItem")
    cursor.execute('DELETE FROM "Order"')
    conn.commit()


def _insert_sale(conn, order_id, user_id, product_id, quantity, price, stock=100):
    """Inserta una venta para tests de recomendaciones"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO "Order" (id, total, created_at, user_id)
        VALUES (?, ?, datetime('now'), ?)
    ''', (order_id, price * quantity, user_id))
    cursor.execute('''
        INSERT INTO OrderItem (order_id, product_id, quantity)
        VALUES (?, ?, ?)
    ''', (order_id, product_id, quantity))
    cursor.execute('''
        UPDATE Product SET stock = ? WHERE id = ?
    ''', (stock, product_id))
    conn.commit()

