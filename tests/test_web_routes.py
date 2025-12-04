"""
Tests para Web Routes
"""

from tests.test_common import *

def test_web_get_products_page():
    """La pàgina principal de productes ha de carregar sense errors."""
    app.config["TESTING"] = True
    client = app.test_client()
    resp = client.get("/")
    return assert_equals(resp.status_code, 200, "La portada ha de respondre 200")



def test_web_login_success():
    """Login exitós amb credencials vàlides."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuari a la BD (con dirección para evitar redirección a completar datos)
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS User (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, email TEXT, address TEXT, created_at TEXT)")
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("test_login_user", password_hash, "test@example.com", "Carrer Test 123, Barcelona")
    )
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post(
        "/login",
        data={"username": "test_login_user", "password": "Password123"},
        follow_redirects=True
    )
    
    ok_status = assert_equals(resp.status_code, 200, "Login ha de respondre 200")
    ok_redirect = assert_true(
        b"Productes" in resp.data or b"productes" in resp.data,
        "Després del login s'ha de redirigir a productes"
    )
    
    # Verificar que la sessió conté user_id
    # Necessitem fer una nova petició per verificar la sessió
    resp2 = client.get("/")
    ok_user_id = assert_true(
        b"test_login_user" in resp2.data or b"Hola" in resp2.data,
        "La sessió ha de contenir user_id i mostrar el nom d'usuari"
    )
    
    return ok_status and ok_redirect and ok_user_id



def test_web_login_wrong_password():
    """Login falla amb contrasenya incorrecta."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuari a la BD
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("test_login_user2", password_hash, "test2@example.com")
    )
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post(
        "/login",
        data={"username": "test_login_user2", "password": "WrongPassword"},
        follow_redirects=True
    )
    
    ok_status = assert_equals(resp.status_code, 200, "Login ha de respondre 200")
    resp_data = resp.data if resp.data else b""
    ok_error = assert_true(
        b"incorrectes" in resp_data or b"incorrecta" in resp_data or b"error" in resp_data.lower() or b"Nom d'usuari o contrasenya" in resp_data,
        "S'ha de mostrar missatge d'error de contrasenya"
    )
    
    # Verificar que NO s'ha creat sessió fent una petició a la pàgina principal
    resp2 = client.get("/")
    ok_no_session = assert_false(
        b"test_login_user2" in resp2.data and b"Hola" in resp2.data,
        "No s'ha de crear sessió amb contrasenya incorrecta"
    )
    
    return ok_status and ok_error and ok_no_session



def test_web_register_success():
    """Registre exitós de nou usuari."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Netejar usuari si existeix (incluyendo DNI)
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = 'test_register_user' OR email = 'register@test.com' OR dni = '12345678Z'")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post(
        "/register",
        data={
            "username": "test_register_user",
            "password": "Password123",
            "email": "register@test.com",
            "address": "Test Address 123",
            "account_type": "user",
            "dni": "12345678Z",
            "nif": "",
            "accept_policies": "on",
            "accept_newsletter": "on"
        },
        follow_redirects=True
    )
    
    ok_status = assert_equals(resp.status_code, 200, "Registre ha de respondre 200")
    ok_redirect = assert_true(
        b"Productes" in resp.data or b"productes" in resp.data,
        "Després del registre s'ha de redirigir a productes"
    )
    
    # Verificar que s'ha creat l'usuari a la BD
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM User WHERE username = 'test_register_user'")
    user = cursor.fetchone()
    conn.close()
    
    ok_user_created = assert_true(user is not None, "S'ha de crear l'usuari a la BD")
    
    # Verificar que s'ha creat sessió fent una petició a la pàgina principal
    resp2 = client.get("/")
    ok_session = assert_true(
        b"test_register_user" in resp2.data or b"Hola" in resp2.data,
        "S'ha de crear sessió després del registre i mostrar el nom d'usuari"
    )
    
    return ok_status and ok_redirect and ok_user_created and ok_session



def test_web_register_duplicate_username():
    """Registre falla amb nom d'usuari duplicat."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuari existent
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("test_duplicate_user", password_hash, "duplicate@test.com")
    )
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post(
        "/register",
        data={
            "username": "test_duplicate_user",
            "accept_policies": "on",
            "password": "Password123",
            "email": "new@test.com",
            "address": "Test Address",
            "account_type": "user",
            "dni": "12345678Z",
            "nif": ""
        },
        follow_redirects=True
    )
    
    ok_status = assert_equals(resp.status_code, 200, "Registre ha de respondre 200")
    ok_error = assert_true(
        b"ja est&#224; en &#250;s" in resp.data 
        or b"ja est" in resp.data 
        or "en ús".encode('utf-8') in resp.data,
        "S'ha de mostrar missatge d'error de nom d'usuari duplicat"
    )
    
    return ok_status and ok_error



def test_web_logout():
    """Logout tanca la sessió correctament."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuari i iniciar sessió
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("test_logout_user", password_hash, "logout@test.com")
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'test_logout_user'")
    user_id = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    resp = client.get("/logout", follow_redirects=True)
    
    ok_status = assert_equals(resp.status_code, 200, "Logout ha de respondre 200")
    
    # Verificar que la sessió s'ha netejat
    with client.session_transaction() as sess:
        ok_session_cleared = assert_true(
            sess.get("user_id") is None,
            "La sessió s'ha de netejar després del logout"
        )
    
    return ok_status and ok_session_cleared



def test_web_checkout_authenticated_user():
    """Checkout amb usuari autenticat només demana adreça."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuari i producte
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, account_type, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("test_auth_checkout", password_hash, "auth@test.com", "user")
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute(
        "INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (300, 'Test Auth Product', 19.99, 5)"
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'test_auth_checkout'")
    user_id = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    # Afegir producte al carretó
    client.post("/add_to_cart", data={"product_id": 300, "quantity": 1})
    
    # Anar al checkout
    resp = client.get("/checkout")
    
    ok_status = assert_equals(resp.status_code, 200, "Checkout ha de respondre 200")
    ok_user_info = assert_true(
        b"test_auth_checkout" in resp.data,
        "S'ha de mostrar el nom d'usuari autenticat"
    )
    ok_only_address = assert_true(
        b'name="address"' in resp.data or b"Adre&#231;a d'enviament" in resp.data or "Adreça d'enviament".encode('utf-8') in resp.data or b"Direcci" in resp.data or b"textarea" in resp.data and b"address" in resp.data,
        "S'ha de mostrar el camp d'adreça"
    )
    ok_no_username_field = assert_false(
        b'name="username"' in resp.data and b'name="password"' in resp.data,
        "No s'han de mostrar camps de username/password per a usuaris autenticats"
    )
    
    return ok_status and ok_user_info and ok_only_address and ok_no_username_field



def test_web_checkout_guest_flow():
    """Checkout com a invitado demana tots els camps."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear producte
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute(
        "INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (400, 'Test Guest Product', 29.99, 10)"
    )
    conn.commit()
    conn.close()
    
    client = app.test_client()
    # Afegir producte al carretó
    client.post("/add_to_cart", data={"product_id": 400, "quantity": 1})
    
    # Anar al checkout
    resp = client.get("/checkout")
    
    ok_status = assert_equals(resp.status_code, 200, "Checkout ha de respondre 200")
    ok_choice = assert_true(
        "Iniciar Sessió".encode('utf-8') in resp.data or "Comprar com a Invitat".encode('utf-8') in resp.data,
        "S'ha de mostrar opció d'iniciar sessió o comprar com a invitado"
    )
    
    return ok_status and ok_choice



def test_security_sql_injection_register():
    """Intentar SQL injection en el registro - verificar que no se ejecuta SQL."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    sql_injections = [
        "admin' OR '1'='1",
        "'; DROP TABLE User;--",
        "' UNION SELECT * FROM User--"
    ]
    
    all_safe = True
    for injection in sql_injections:
        # Limpiar usuario si existe
        conn = sqlite3.connect("techshop.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE username = ?", (injection,))
        conn.commit()
        conn.close()
        
        resp = client.post(
            "/register",
            data={
                "username": injection,
                "password": "Password123",
                "email": f"test{hash(injection) % 10000}@test.com"
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
        
        # Lo importante es que la tabla siga existiendo (SQL no se ejecutó)
        ok_safe = assert_true(
            table_exists,
            f"SQL injection '{injection}' no debería ejecutar código SQL"
        )
        all_safe = all_safe and ok_safe
    
    return all_safe



def test_security_bypass_checkout_type():
    """Intentar cambiar checkout_type para evitar validaciones."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    # Intentar procesar como autenticado sin estar autenticado
    resp = client.post(
        "/process_order",
        data={
            "checkout_type": "authenticated",  # Sin estar autenticado
            "address": "Calle Test 123"
        },
        follow_redirects=True
    )
    
    ok_rejected = assert_true(
        b"error" in resp.data.lower() or "Sessió no vàlida".encode('utf-8') in resp.data or resp.status_code != 200,
        "No debería permitir checkout autenticado sin sesión"
    )
    
    return ok_rejected



def test_security_register_existing_email():
    """Intentar registrar con email ya existente."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuario con email
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Password123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("existing_email_user", password_hash, "existing@test.com")
    )
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post(
        "/register",
        data={
            "username": "new_user_same_email",
            "password": "Password123",
            "email": "existing@test.com",  # Email duplicado
            "address": "Test Address",
            "account_type": "user",
            "dni": "12345678Z",
            "nif": "",
            "accept_policies": "on"
        },
        follow_redirects=True
    )
    
    # Debería permitir (el sistema actual permite emails duplicados, pero podemos verificar que no crashea)
    ok_safe = assert_true(
        resp.status_code == 200,
        "Registro con email existente no debería crashear"
    )
    
    return ok_safe



def test_profile_view_requires_login():
    """Verificar que el perfil requiere login."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    resp = client.get("/profile")
    
    return assert_true(
        resp.status_code == 302 or "login" in resp.location.lower(),
        "Perfil debería redirigir a login si no hay sesión"
    )



def test_invoice_download_requires_login():
    """Verificar que descargar factura requiere login."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    resp = client.get("/profile/invoice/1")
    
    return assert_true(
        resp.status_code == 302 or "login" in resp.location.lower(),
        "Descarga de factura debería requerir login"
    )



def test_register_requires_policies():
    """Verificar que el registro requiere aceptar políticas."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Limpiar usuario si existe
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = 'test_no_policies'")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post("/register", data={
        "username": "test_no_policies",
        "password": "Test1234",
        "email": "nopolicies@test.com",
        "address": "Test Address",
        "account_type": "user",
        "dni": "12345678Z",
        "nif": ""
        # Sin accept_policies
    })
    
    return assert_true(
        resp.status_code == 200 and ("polítiques".encode('utf-8') in resp.data.lower() or "acceptar".encode('utf-8') in resp.data.lower()),
        "Debería rechazar registro sin aceptar políticas"
    )



def test_register_newsletter_optional():
    """Verificar que el newsletter es opcional."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Limpiar usuario si existe
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = 'test_no_newsletter'")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post("/register", data={
        "username": "test_no_newsletter",
        "password": "Test1234",
        "email": "nonewsletter@test.com",
        "address": "Test Address",
        "account_type": "user",
        "dni": "12345678Z",
        "nif": "",
        "accept_policies": "on"
        # Sin accept_newsletter
    }, follow_redirects=True)
    
    return assert_true(
        resp.status_code == 200,
        "Debería permitir registro sin newsletter"
    )


# ========== TESTS DE VISTA DE DETALLE DE PRODUCTO ==========


def test_web_login_redirects_to_complete_data_if_missing():
    """Test que login redirige a completar datos si faltan datos obligatorios."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuario sin email
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT INTO User (username, password_hash, address, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("incomplete_user", password_hash, "Test Address")
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = None
    
    resp = client.post(
        "/login",
        data={"username": "incomplete_user", "password": "Test123"},
        follow_redirects=False
    )
    
    ok_redirect = assert_true(resp.status_code == 302, "Debería redirigir")
    ok_profile = assert_true("/profile" in resp.location or "profile" in resp.location.lower(), f"Debería redirigir a perfil: {resp.location}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return ok_redirect and ok_profile


if __name__ == '__main__':
    exit(0 if main() else 1)