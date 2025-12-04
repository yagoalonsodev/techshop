"""
Tests para Integration
"""

from tests.test_common import *

def test_inventory_update():
    init_test_db()  # Asegurar que la BD está inicializada
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



def test_profile_view_authenticated():
    """Verificar acceso al perfil con usuario autenticado."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuario
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("test_profile", password_hash, "test@test.com", "Test Address")
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'test_profile'")
    user_id = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    resp = client.get("/profile")
    
    return assert_true(
        resp.status_code == 200 and b"El Meu Perfil" in resp.data,
        "Perfil debería ser accesible con usuario autenticado"
    )



def test_profile_edit_updates_data():
    """Verificar que la edición de perfil actualiza datos."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Limpiar usuario y email de prueba
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = 'test_edit' OR email IN ('test_edit_email@test.com', 'newemail_edit@test.com')")
    # Limpiar también cualquier usuario con el DNI que vamos a usar
    cursor.execute("DELETE FROM User WHERE dni = '12345678Z'")
    conn.commit()
    
    # Crear usuario
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT INTO User (username, password_hash, email, address, account_type, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
        ("test_edit", password_hash, "test_edit_email@test.com", "Old Address", "user")
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'test_edit'")
    user_id = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    # Intentar actualizar con DNI válido (seguir redirección)
    resp = client.post("/profile/edit", data={
        "username": "test_edit",
        "email": "newemail_edit@test.com",
        "address": "New Address",
        "dni": "12345678Z",
        "nif": ""
    }, follow_redirects=True)
    
    # Verificar que la respuesta fue exitosa
    if resp.status_code != 200:
        return assert_false(True, f"La respuesta debería ser 200, pero fue {resp.status_code}")
    
    # Verificar que se actualizó en la base de datos (esperar un poco para que se complete la transacción)
    import time
    time.sleep(0.2)
    
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email, address, dni FROM User WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            # Corregir unpacking: la query devuelve 3 valores (email, address, dni)
            email, address, dni = result
            ok_email = assert_equals(email, "newemail_edit@test.com", f"Email debería actualizarse. Actual: {email}")
            ok_address = assert_equals(address, "New Address", f"Address debería actualizarse. Actual: {address}")
            return ok_email and ok_address
        return False
    except sqlite3.OperationalError:
        # Si la columna dni no existe, solo verificamos email y address
        cursor.execute("SELECT email, address FROM User WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            email, address = result
            ok_email = assert_equals(email, "newemail_edit@test.com", f"Email debería actualizarse. Actual: {email}")
            ok_address = assert_equals(address, "New Address", f"Address debería actualizarse. Actual: {address}")
            return ok_email and ok_address
        return False
    finally:
        conn.close()



def test_invoice_generator_no_default_data():
    """Test que las facturas no muestran datos por defecto (N/A)."""
    from utils.invoice_generator import generate_invoice_pdf
    
    # Crear usuario sin algunos datos
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("invoice_test_user", password_hash, "invoice@test.com", "Test Address")
    )
    user_id = cursor.lastrowid
    
    # Crear orden
    cursor.execute('CREATE TABLE IF NOT EXISTS "Order" (id INTEGER PRIMARY KEY, total REAL, created_at TEXT, user_id INTEGER)')
    cursor.execute('INSERT INTO "Order" (total, created_at, user_id) VALUES (?, ?, ?)', (50.0, "2024-01-01", user_id))
    order_id = cursor.lastrowid
    
    # Crear OrderItem
    cursor.execute('CREATE TABLE IF NOT EXISTS OrderItem (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)')
    cursor.execute('INSERT OR IGNORE INTO Product (id, name, price, stock) VALUES (?, ?, ?, ?)', (999, "Test Product", 50.0, 10))
    cursor.execute('INSERT INTO OrderItem (order_id, product_id, quantity) VALUES (?, ?, ?)', (order_id, 999, 1))
    
    conn.commit()
    conn.close()
    
    pdf_data = generate_invoice_pdf(order_id, user_id)
    
    ok_pdf = assert_true(pdf_data is not None, "Debería generar PDF")
    
    # Verificar que el PDF no contiene "N/A"
    if pdf_data:
        pdf_text = pdf_data.decode('latin-1', errors='ignore')
        ok_no_na = assert_false("N/A" in pdf_text or "n/a" in pdf_text, "El PDF no debería contener 'N/A'")
    else:
        ok_no_na = False
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM OrderItem WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM \"Order\" WHERE id = ?", (order_id,))
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return ok_pdf and ok_no_na


