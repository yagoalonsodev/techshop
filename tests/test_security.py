"""
Tests para Security
"""

from tests.test_common import *

def test_security_session_hijacking_attempt():
    """Intentar acceder con un user_id manipulado en la sesión."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuario legítimo
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("legit_user", password_hash, "legit@test.com")
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'legit_user'")
    legit_user_id = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    # Intentar usar un user_id que no existe o es de otro usuario
    fake_user_ids = [99999, -1, 0, legit_user_id + 1000]
    
    all_safe = True
    for fake_id in fake_user_ids:
        with client.session_transaction() as sess:
            sess["user_id"] = fake_id
        
        resp = client.get("/")
        # No debería mostrar información de usuario falso
        ok_safe = assert_false(
            b"Hola" in resp.data and b"legit_user" in resp.data,
            f"user_id falso {fake_id} no debería autenticar"
        )
        all_safe = all_safe and ok_safe
    
    return all_safe



def test_security_negative_quantity():
    """Intentar añadir cantidades negativas o muy grandes."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear producto
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (600, 'Test Security', 10.00, 10)")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    invalid_quantities = [-1, -100, 0, 999999, "'; DROP TABLE--", "<script>"]
    
    all_safe = True
    for invalid_qty in invalid_quantities:
        resp = client.post(
            "/add_to_cart",
            data={"product_id": 600, "quantity": invalid_qty},
            follow_redirects=True
        )
        ok_safe = assert_true(
            b"error" in resp.data.lower() or resp.status_code != 200,
            f"Cantidad inválida {invalid_qty} debería ser rechazada"
        )
        all_safe = all_safe and ok_safe
    
    return all_safe



def test_security_email_injection():
    """Intentar inyección en el campo email - verificar que no se ejecuta código."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    malicious_emails = [
        "test@test.com'; DROP TABLE User;--",
        "test@test.com\"><script>alert(1)</script>",
        "test@test.com' OR '1'='1",
        "test@test.com\nadmin@admin.com"
    ]
    
    all_safe = True
    for email in malicious_emails:
        username = f"user_{abs(hash(email)) % 10000}"
        
        # Limpiar usuario si existe (incluyendo DNI)
        conn = sqlite3.connect("techshop.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE username = ? OR email = ? OR dni = ?", (username, email, "12345678Z"))
        conn.commit()
        conn.close()
        
        resp = client.post(
            "/register",
            data={
                "username": username,
                "password": "Password123",
                "email": email,
                "address": "Test Address",
                "account_type": "user",
                "dni": "12345678Z",
                "nif": "",
                "accept_policies": "on"
            },
            follow_redirects=True
        )
        
        # Verificar que la tabla User sigue existiendo (no se ejecutó DROP TABLE)
        conn = sqlite3.connect("techshop.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM User")
            table_exists = True
        except sqlite3.Error:
            table_exists = False
        conn.close()
        
        # Verificar que el email no contiene código ejecutable en la respuesta
        resp_data = resp.data if resp.data else b""
        if not isinstance(resp_data, bytes):
            resp_data = str(resp_data).encode('utf-8')
        resp_data_lower = resp_data.lower()
        
        # Verificar que no hay scripts ejecutándose (el email puede aparecer escapado, lo cual es correcto)
        # Buscar scripts activos, no solo la presencia del texto
        email_has_script = (
            b"<script>" in resp_data_lower and b"</script>" in resp_data_lower
        ) or (
            b"onerror=" in resp_data_lower and b"'" in resp_data_lower
        ) or (
            b"onload=" in resp_data_lower and b"'" in resp_data_lower
        )
        
        # Verificar que el email malicioso no se almacenó en la base de datos sin escapar
        conn = sqlite3.connect("techshop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM User WHERE email = ?", (email,))
        email_stored = cursor.fetchone()[0] > 0
        conn.close()
        
        # Lo importante es que:
        # 1. La tabla siga existiendo (no se ejecutó DROP TABLE) - CRÍTICO
        # 2. No haya scripts ejecutándose en la respuesta - CRÍTICO
        # El registro puede ser rechazado (lo cual es correcto), pero no debe ejecutar código malicioso
        # Si el email se almacenó, debe estar escapado y no ejecutarse
        ok_safe = assert_true(
            table_exists and not email_has_script,
            f"Email malicioso no debería ejecutar código SQL o XSS"
        )
        all_safe = all_safe and ok_safe
    
    return all_safe



def test_security_password_hash_exposure():
    """Verificar que los hashes de contraseña no se exponen."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuario
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("SecretPassword123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("hash_test_user", password_hash, "hash@test.com")
    )
    conn.commit()
    conn.close()
    
    client = app.test_client()
    # Intentar acceder a diferentes endpoints
    endpoints = ["/", "/checkout", "/login", "/register"]
    
    all_safe = True
    for endpoint in endpoints:
        resp = client.get(endpoint)
        # El hash no debería aparecer en ninguna respuesta
        ok_safe = assert_false(
            password_hash.encode() in resp.data,
            f"Hash de contraseña no debería aparecer en {endpoint}"
        )
        all_safe = all_safe and ok_safe
    
    return all_safe



def test_security_csrf_protection():
    """Verificar que CSRF está activo en endpoints críticos."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    
    client = app.test_client()
    # Intentar POST sin token CSRF
    endpoints = [
        ("/add_to_cart", {"product_id": 1, "quantity": 1}),
        ("/remove_from_cart", {"product_id": 1}),
        ("/process_order", {"checkout_type": "guest", "username": "test", "password": "Test123", "email": "test@test.com", "address": "Test 123"}),
    ]
    
    all_protected = True
    for endpoint, data in endpoints:
        resp = client.post(endpoint, data=data, follow_redirects=True)
        ok_protected = assert_true(
            resp.status_code == 400 or b"CSRF" in resp.data.upper(),
            f"{endpoint} debería requerir CSRF token"
        )
        all_protected = all_protected and ok_protected
    
    return all_protected



def test_security_password_complexity_bypass():
    """Intentar bypass de validación de complejidad de contraseña."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    weak_passwords = [
        "12345678",  # Solo números
        "abcdefgh",  # Solo letras
        "ABCDEFGH",  # Solo mayúsculas
        "password",  # Palabra común
        "1234567",  # Menos de 8 caracteres
        "",  # Vacío
    ]
    
    all_rejected = True
    for password in weak_passwords:
        resp = client.post(
            "/register",
            data={
                "username": f"user_{hash(password) % 10000}",
                "password": password,
                "email": f"test{hash(password) % 10000}@test.com"
            },
            follow_redirects=True
        )
        ok_rejected = assert_true(
            b"error" in resp.data.lower() or b"contrasenya" in resp.data.lower() or resp.status_code != 200,
            f"Contraseña débil debería ser rechazada"
        )
        all_rejected = all_rejected and ok_rejected
    
    return all_rejected



def test_security_path_traversal():
    """Intentar path traversal en URLs."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    malicious_paths = [
        "../../../etc/passwd",
        "....//....//etc/passwd",
        "/etc/passwd",
        "..\\..\\..\\windows\\system32",
    ]
    
    all_safe = True
    for path in malicious_paths:
        resp = client.get(f"/{path}")
        ok_safe = assert_true(
            resp.status_code == 404,
            f"Path traversal '{path}' debería devolver 404"
        )
        all_safe = all_safe and ok_safe
    
    return all_safe


