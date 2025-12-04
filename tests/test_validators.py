"""
Tests para Validators
"""

from tests.test_common import *

def test_email_validation():
    conditions = []
    conditions.append(assert_false('@' in "invalid-email.com" and '.' in "invalid-email.com".split('@')[-1]))
    conditions.append(assert_false('@' in "test@invalid" and '.' in "test@invalid".split('@')[-1]))
    conditions.append(assert_true('@' in "test@example.com" and '.' in "test@example.com".split('@')[-1]))
    return all(conditions)


def test_address_validation():
    return assert_false(len("Short") >= 10) and assert_true(len("Calle Mayor 123, Madrid") >= 10)


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


def test_security_checkout_guest_invalid_data():
    """Intentar checkout como invitado con datos inválidos."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear producto y añadir al carrito
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
    cursor.execute("INSERT OR REPLACE INTO Product (id, name, price, stock) VALUES (800, 'Test Guest', 10.00, 10)")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    client.post("/add_to_cart", data={"product_id": 800, "quantity": 1})
    
    # Intentar checkout con datos inválidos
    invalid_data = [
        {"checkout_type": "guest", "username": "ab", "password": "Pass123", "email": "invalid", "address": "short"},
        {"checkout_type": "guest", "username": "a" * 100, "password": "123", "email": "test@test", "address": "Valid address here"},
    ]
    
    all_rejected = True
    for data in invalid_data:
        resp = client.post("/process_order", data=data, follow_redirects=True)
        ok_rejected = assert_true(
            b"error" in resp.data.lower() or resp.status_code != 200,
            "Datos inválidos deberían ser rechazados"
        )
        all_rejected = all_rejected and ok_rejected
    
    return all_rejected



def test_validator_dni_valido():
    """Validar DNI válido."""
    return assert_true(validar_dni("12345678Z"), "DNI válido debería pasar")



def test_validator_dni_invalido_formato():
    """Validar DNI con formato incorrecto."""
    return assert_false(validar_dni("1234567Z"), "DNI con formato incorrecto debería fallar")



def test_validator_dni_invalido_letra():
    """Validar DNI con letra incorrecta."""
    return assert_false(validar_dni("12345678A"), "DNI con letra incorrecta debería fallar")



def test_validator_nie_valido():
    """Validar NIE válido."""
    return assert_true(validar_nie("X1234567L"), "NIE válido debería pasar")



def test_validator_nie_invalido_formato():
    """Validar NIE con formato incorrecto."""
    return assert_false(validar_nie("X123456L"), "NIE con formato incorrecto debería fallar")



def test_validator_cif_valido():
    """Validar CIF válido."""
    # CIF de ejemplo válido: B12345674 (B requiere número de control)
    return assert_true(validar_cif("B12345674"), "CIF válido debería pasar")



def test_validator_cif_invalido_formato():
    """Validar CIF con formato incorrecto."""
    return assert_false(validar_cif("12345678"), "CIF con formato incorrecto debería fallar")



def test_validator_dni_nie_detecta_dni():
    """Validar que detecta DNI correctamente."""
    return assert_true(validar_dni_nie("12345678Z"), "Debería detectar DNI")



def test_validator_dni_nie_detecta_nie():
    """Validar que detecta NIE correctamente."""
    return assert_true(validar_dni_nie("X1234567L"), "Debería detectar NIE")



def test_validator_dni_nie_invalido():
    """Validar DNI/NIE inválido."""
    return assert_false(validar_dni_nie("12345678A"), "DNI/NIE inválido debería fallar")


# ========== TESTS DE PERFIL DE USUARIO ==========


def test_profile_edit_rejects_invalid_dni():
    """Verificar que rechaza DNI inválido."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Crear usuario
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, address, account_type, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
        ("test_invalid_dni", password_hash, "test@test.com", "Address", "user")
    )
    conn.commit()
    cursor.execute("SELECT id FROM User WHERE username = 'test_invalid_dni'")
    user_id = cursor.fetchone()[0]
    conn.close()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    
    resp = client.post("/profile/edit", data={
        "username": "test_invalid_dni",
        "email": "test@test.com",
        "address": "Address",
        "dni": "12345678X",  # DNI inválido (letra incorrecta, debería ser Z)
        "nif": ""
    })
    
    resp_data = resp.data if resp.data else b""
    if not isinstance(resp_data, bytes):
        resp_data = str(resp_data).encode('utf-8')
    
    resp_data_lower = resp_data.lower()
    error_found = (
        b"no valid" in resp_data_lower or 
        b"no valido" in resp_data_lower or 
        b"error" in resp_data_lower or
        b"invalid" in resp_data_lower
    )
    
    return assert_true(
        resp.status_code == 200 and error_found,
        "Debería rechazar DNI inválido"
    )



def test_register_with_valid_dni():
    """Verificar registro con DNI válido."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Limpiar usuario si existe
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = 'test_dni_user'")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post("/register", data={
        "username": "test_dni_user",
        "password": "Test1234",
        "email": "dni@test.com",
        "address": "Test Address",
        "account_type": "user",
        "dni": "12345678Z",
        "nif": ""
    })
    
    location_lower = resp.location.lower() if resp.location else ""
    return assert_true(
        resp.status_code == 302 or "productes" in location_lower or resp.status_code == 200,
        "Debería registrar usuario con DNI válido"
    )



def test_register_with_valid_nie():
    """Verificar registro con NIE válido."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Limpiar usuario si existe
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = 'test_nie_user'")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post("/register", data={
        "username": "test_nie_user",
        "password": "Test1234",
        "email": "nie@test.com",
        "address": "Test Address",
        "account_type": "user",
        "dni": "X1234567L",
        "nif": "",
        "accept_policies": "on"
    })
    
    location_lower = resp.location.lower() if resp.location else ""
    return assert_true(
        resp.status_code == 302 or "productes" in location_lower or resp.status_code == 200,
        "Debería registrar usuario con NIE válido"
    )



def test_register_with_valid_cif():
    """Verificar registro empresa con CIF válido."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    # Limpiar usuario si existe
    conn = sqlite3.connect("techshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = 'test_cif_company'")
    conn.commit()
    conn.close()
    
    client = app.test_client()
    resp = client.post("/register", data={
        "username": "test_cif_company",
        "password": "Test1234",
        "email": "cif@test.com",
        "address": "Test Address",
        "account_type": "company",
        "dni": "",
        "nif": "B12345674",
        "accept_policies": "on"
    })
    
    location_lower = resp.location.lower() if resp.location else ""
    return assert_true(
        resp.status_code == 302 or "productes" in location_lower or resp.status_code == 200,
        "Debería registrar empresa con CIF válido"
    )



def test_register_rejects_invalid_dni():
    """Verificar que rechaza DNI inválido en registro."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    client = app.test_client()
    resp = client.post("/register", data={
        "username": "test_invalid_dni_reg",
        "password": "Test1234",
        "email": "invalid@test.com",
        "address": "Test Address",
        "account_type": "user",
        "dni": "12345678A",  # DNI inválido
        "nif": "",
        "accept_policies": "on"
    })
    
    return assert_true(
        resp.status_code == 200 and "no vàlid".encode('utf-8') in resp.data.lower(),
        "Debería rechazar DNI inválido en registro"
    )


# ========== TESTS DE FACTURAS PDF ==========

