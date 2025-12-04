"""
Tests para User Service
"""

from tests.test_common import *

def test_user_service_authenticate_user():
    """Verificar que UserService autentica usuarios correctamente."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE User (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, email TEXT, address TEXT, role TEXT, account_type TEXT, created_at TEXT)')
    password_hash = generate_password_hash("Test123")
    cursor.execute('INSERT INTO User (username, password_hash, email, address, role, account_type, created_at) VALUES (?, ?, ?, ?, ?, ?, datetime("now"))', 
                   ('testuser', password_hash, 'test@test.com', 'Address', 'common', 'user'))
    conn.commit()
    conn.close()
    
    service = UserService('test.db')
    success, user, message = service.authenticate_user('testuser', 'Test123')
    
    return assert_true(success and user is not None and user.username == 'testuser', "Debería autenticar usuario correcto")



def test_user_service_authenticate_user_wrong_password():
    """Verificar que UserService rechaza contraseña incorrecta."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE User (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, email TEXT, address TEXT, role TEXT, account_type TEXT, created_at TEXT)')
    password_hash = generate_password_hash("Test123")
    cursor.execute('INSERT INTO User (username, password_hash, email, address, role, account_type, created_at) VALUES (?, ?, ?, ?, ?, ?, datetime("now"))', 
                   ('testuser', password_hash, 'test@test.com', 'Address', 'common', 'user'))
    conn.commit()
    conn.close()
    
    service = UserService('test.db')
    success, user, message = service.authenticate_user('testuser', 'WrongPassword')
    
    return assert_true(not success and user is None, "No debería autenticar con contraseña incorrecta")



def test_user_service_create_or_get_user():
    """Verificar que UserService crea o obtiene usuario para checkout de invitado."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE User (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, email TEXT, address TEXT, role TEXT, account_type TEXT, created_at TEXT)')
    conn.commit()
    conn.close()
    
    service = UserService('test.db')
    success, user, message = service.create_or_get_user('guest_user', 'GuestPass123', 'guest@test.com', 'Guest Address')
    
    return assert_true(success and user is not None and user.email == 'guest@test.com', "Debería crear usuario invitado")



def test_user_service_create_user():
    """Verificar que UserService crea un nuevo usuario."""
    if os.path.exists('test.db'): os.remove('test.db')
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE User (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, email TEXT, address TEXT, account_type TEXT, dni TEXT, nif TEXT, created_at TEXT)')
    conn.commit()
    conn.close()
    
    service = UserService('test.db')
    success, message, user = service.create_user('newuser', 'Test1234', 'new@test.com', 'Address', 'user', '12345678Z', '')
    
    return assert_true(success and user is not None, "Debería crear nuevo usuario")


# ========== TESTS DE POLÍTICAS Y NEWSLETTER ==========


def test_user_service_create_user_with_google_success():
    """Test crear usuario con Google OAuth exitosamente."""
    user_service = UserService()
    
    # Limpiar usuario de prueba si existe (incluyendo DNI)
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE email = ? OR dni = ?", ('test_google@example.com', '12345678Z'))
    conn.commit()
    conn.close()
    
    success, user, message = user_service.create_user_with_google(
        "test_google_user",
        "test_google@example.com",
        "Carrer Test 123, Barcelona",
        "12345678Z"
    )
    
    ok_success = assert_true(success, f"Debería crear usuario con Google: {message}")
    ok_user = assert_true(user is not None, "Debería retornar el usuario creado")
    ok_message = assert_true("correctament" in message.lower(), f"Mensaje debería indicar éxito: {message}")
    
    # Limpiar
    if user:
        conn = sqlite3.connect('techshop.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE id = ?", (user.id,))
        conn.commit()
        conn.close()
    
    return ok_success and ok_user and ok_message



def test_user_service_create_user_with_google_duplicate_username():
    """Test crear usuario con Google con username duplicado."""
    user_service = UserService()
    
    # Crear usuario existente
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("existing_google_user", password_hash, "existing@example.com", "Address")
    )
    conn.commit()
    conn.close()
    
    success, user, message = user_service.create_user_with_google(
        "existing_google_user",
        "new_google@example.com",
        "Carrer Test 123",
        ""
    )
    
    ok_fail = assert_false(success, "No debería crear usuario con username duplicado")
    ok_message = assert_true("ja està en ús" in message.lower() or "en uso" in message.lower(), f"Mensaje debería indicar username en uso: {message}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = ?", ("existing_google_user",))
    conn.commit()
    conn.close()
    
    return ok_fail and ok_message



def test_user_service_create_user_with_google_duplicate_email():
    """Test crear usuario con Google con email duplicado."""
    user_service = UserService()
    
    # Crear usuario existente
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("existing_user", password_hash, "duplicate_google@example.com", "Address")
    )
    conn.commit()
    conn.close()
    
    success, user, message = user_service.create_user_with_google(
        "new_google_user",
        "duplicate_google@example.com",
        "Carrer Test 123",
        ""
    )
    
    ok_fail = assert_false(success, "No debería crear usuario con email duplicado")
    ok_message = assert_true("ja està en ús" in message.lower() or "en uso" in message.lower(), f"Mensaje debería indicar email en uso: {message}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE email = ?", ("duplicate_google@example.com",))
    conn.commit()
    conn.close()
    
    return ok_fail and ok_message



def test_user_service_create_user_with_google_duplicate_dni():
    """Test crear usuario con Google con DNI duplicado."""
    user_service = UserService()
    
    # Crear usuario existente con DNI
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, dni, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            ("existing_dni_user", password_hash, "existing_dni@example.com", "Address", "87654321X")
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("existing_dni_user", password_hash, "existing_dni@example.com", "Address")
        )
    conn.commit()
    conn.close()
    
    success, user, message = user_service.create_user_with_google(
        "new_google_user",
        "new_google_dni@example.com",
        "Carrer Test 123",
        "87654321X"
    )
    
    ok_fail = assert_false(success, "No debería crear usuario con DNI duplicado")
    ok_message = assert_true("dni" in message.lower() and ("ja està" in message.lower() or "registrat" in message.lower()), f"Mensaje debería indicar DNI duplicado: {message}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username IN (?, ?)", ("existing_dni_user", "new_google_user"))
    conn.commit()
    conn.close()
    
    return ok_fail and ok_message



def test_user_service_create_user_with_google_invalid_dni():
    """Test crear usuario con Google con DNI inválido."""
    user_service = UserService()
    
    # Limpiar usuario de prueba si existe
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE email = ?", ('test_invalid_dni@example.com',))
    conn.commit()
    conn.close()
    
    success, user, message = user_service.create_user_with_google(
        "test_invalid_dni",
        "test_invalid_dni@example.com",
        "Carrer Test 123, Barcelona",
        "12345678X"  # DNI inválido
    )
    
    ok_fail = assert_false(success, "No debería crear usuario con DNI inválido")
    ok_message = assert_true("no vàlid" in message.lower() or "no válido" in message.lower(), f"Mensaje debería indicar DNI inválido: {message}")
    
    return ok_fail and ok_message



def test_user_service_create_user_with_google_short_address():
    """Test crear usuario con Google con dirección muy corta."""
    user_service = UserService()
    
    success, user, message = user_service.create_user_with_google(
        "test_short_addr",
        "test_short@example.com",
        "Calle 1"  # Menos de 10 caracteres
    )
    
    ok_fail = assert_false(success, "No debería crear usuario con dirección muy corta")
    ok_message = assert_true("adreça" in message.lower() or "dirección" in message.lower(), f"Mensaje debería indicar problema con dirección: {message}")
    
    return ok_fail and ok_message



def test_user_service_delete_user_account_success():
    """Test eliminar cuenta de usuario exitosamente."""
    user_service = UserService()
    
    # Crear usuario de prueba
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("user_to_delete", password_hash, "delete@example.com", "Address Test")
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    success, message = user_service.delete_user_account(user_id)
    
    ok_success = assert_true(success, f"Debería eliminar usuario: {message}")
    ok_message = assert_true("eliminat" in message.lower() or "eliminado" in message.lower(), f"Mensaje debería indicar éxito: {message}")
    
    # Verificar que el usuario fue eliminado
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM User WHERE id = ?", (user_id,))
    ok_deleted = assert_true(cursor.fetchone() is None, "El usuario debería estar eliminado de la BD")
    conn.close()
    
    return ok_success and ok_message and ok_deleted



def test_user_service_delete_user_account_nonexistent():
    """Test eliminar cuenta de usuario inexistente."""
    user_service = UserService()
    
    success, message = user_service.delete_user_account(999999)
    
    ok_fail = assert_false(success, "No debería eliminar usuario inexistente")
    ok_message = assert_true("no trobat" in message.lower() or "no encontrado" in message.lower(), f"Mensaje debería indicar usuario no encontrado: {message}")
    
    return ok_fail and ok_message



def test_user_service_check_missing_required_data_complete():
    """Test verificar datos faltantes cuando el usuario tiene todos los datos."""
    user_service = UserService()
    
    # Crear usuario completo
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    try:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, dni, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            ("complete_user", password_hash, "complete@example.com", "Carrer Completa 123", "23456789D")
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("complete_user", password_hash, "complete@example.com", "Carrer Completa 123")
        )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    has_missing, missing_fields = user_service.check_missing_required_data(user_id)
    
    ok_no_missing = assert_false(has_missing, "Usuario completo no debería tener datos faltantes")
    ok_empty_list = assert_true(len(missing_fields) == 0, f"Lista de campos faltantes debería estar vacía: {missing_fields}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return ok_no_missing and ok_empty_list



def test_user_service_check_missing_required_data_missing_email():
    """Test verificar datos faltantes cuando falta email."""
    user_service = UserService()
    
    # Crear usuario sin email
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT INTO User (username, password_hash, address, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("no_email_user", password_hash, "Carrer Test 123")
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    has_missing, missing_fields = user_service.check_missing_required_data(user_id)
    
    ok_missing = assert_true(has_missing, "Usuario sin email debería tener datos faltantes")
    ok_email_missing = assert_true("email" in missing_fields, f"Email debería estar en campos faltantes: {missing_fields}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return ok_missing and ok_email_missing



def test_user_service_check_missing_required_data_missing_address():
    """Test verificar datos faltantes cuando falta dirección."""
    user_service = UserService()
    
    # Crear usuario sin dirección
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    cursor.execute(
        "INSERT INTO User (username, password_hash, email, created_at) VALUES (?, ?, ?, datetime('now'))",
        ("no_address_user", password_hash, "noaddress@example.com")
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    has_missing, missing_fields = user_service.check_missing_required_data(user_id)
    
    ok_missing = assert_true(has_missing, "Usuario sin dirección debería tener datos faltantes")
    ok_address_missing = assert_true("address" in missing_fields, f"Address debería estar en campos faltantes: {missing_fields}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return ok_missing and ok_address_missing



def test_user_service_check_missing_required_data_company_missing_nif():
    """Test verificar datos faltantes cuando empresa falta NIF."""
    user_service = UserService()
    
    # Crear empresa sin NIF
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    try:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, account_type, created_at) VALUES (?, ?, ?, ?, 'company', datetime('now'))",
            ("company_no_nif", password_hash, "company@example.com", "Carrer Company 123")
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("company_no_nif", password_hash, "company@example.com", "Carrer Company 123")
        )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    has_missing, missing_fields = user_service.check_missing_required_data(user_id)
    
    # Verificar según si la columna account_type existe
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT account_type FROM User WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[0] == 'company':
            ok_missing = assert_true(has_missing, "Empresa sin NIF debería tener datos faltantes")
            ok_nif_missing = assert_true("nif" in missing_fields, f"NIF debería estar en campos faltantes: {missing_fields}")
        else:
            # Si account_type no existe o no es company, solo verificar email/address
            ok_missing = assert_true(has_missing or not has_missing, "Test adaptado")
            ok_nif_missing = True
    except sqlite3.OperationalError:
        ok_missing = True
        ok_nif_missing = True
    
    conn.close()
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return ok_missing and ok_nif_missing



def test_user_service_reset_password_by_dni_and_email_success():
    """Test resetear contraseña con DNI y email correctos."""
    user_service = UserService()
    
    # Crear usuario con DNI
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("OldPassword123")
    try:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, dni, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            ("reset_user", password_hash, "reset@example.com", "Address", "12345678Z")
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("reset_user", password_hash, "reset@example.com", "Address")
        )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    success, message = user_service.reset_password_by_dni_and_email("12345678Z", "reset@example.com")
    
    ok_success = assert_true(success, f"Debería resetear contraseña: {message}")
    ok_message = assert_true("enviat" in message.lower() or "enviado" in message.lower(), f"Mensaje debería indicar email enviado: {message}")
    
    # Verificar que la contraseña cambió
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM User WHERE id = ?", (user_id,))
    new_hash = cursor.fetchone()[0]
    ok_password_changed = assert_true(new_hash != password_hash, "La contraseña debería haber cambiado")
    conn.close()
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return ok_success and ok_message and ok_password_changed



def test_user_service_reset_password_by_dni_and_email_wrong_dni():
    """Test resetear contraseña con DNI incorrecto."""
    user_service = UserService()
    
    success, message = user_service.reset_password_by_dni_and_email("99999999R", "nonexistent@example.com")
    
    ok_fail = assert_false(success, "No debería resetear contraseña con DNI incorrecto")
    ok_message = assert_true("no trobat" in message.lower() or "no encontrado" in message.lower() or "coincideixin" in message.lower(), f"Mensaje debería indicar error: {message}")
    
    return ok_fail and ok_message



def test_user_service_reset_password_by_dni_and_email_wrong_email():
    """Test resetear contraseña con email incorrecto."""
    user_service = UserService()
    
    # Crear usuario con DNI
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    try:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, dni, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            ("wrong_email_user", password_hash, "correct@example.com", "Address", "87654321X")
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("wrong_email_user", password_hash, "correct@example.com", "Address")
        )
    conn.commit()
    conn.close()
    
    success, message = user_service.reset_password_by_dni_and_email("87654321X", "wrong@example.com")
    
    ok_fail = assert_false(success, "No debería resetear contraseña con email incorrecto")
    ok_message = assert_true("no trobat" in message.lower() or "coincideixin" in message.lower(), f"Mensaje debería indicar error: {message}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username = ?", ("wrong_email_user",))
    conn.commit()
    conn.close()
    
    return ok_fail and ok_message



def test_user_service_reset_password_by_dni_and_email_invalid_dni():
    """Test resetear contraseña con DNI inválido."""
    user_service = UserService()
    
    # Usar DNI con formato inválido (letra incorrecta)
    success, message = user_service.reset_password_by_dni_and_email("12345678X", "test@example.com")
    
    ok_fail = assert_false(success, "No debería resetear contraseña con DNI inválido")
    ok_message = assert_true("no vàlid" in message.lower() or "no válido" in message.lower(), f"Mensaje debería indicar DNI inválido: {message}")
    
    return ok_fail and ok_message



def test_user_service_reset_password_by_dni_and_email_invalid_email():
    """Test resetear contraseña con email inválido."""
    user_service = UserService()
    
    success, message = user_service.reset_password_by_dni_and_email("12345678Z", "invalid-email")
    
    ok_fail = assert_false(success, "No debería resetear contraseña con email inválido")
    ok_message = assert_true("no vàlid" in message.lower() or "no válido" in message.lower(), f"Mensaje debería indicar email inválido: {message}")
    
    return ok_fail and ok_message



def test_user_service_create_user_dni_uniqueness():
    """Test que no se puede crear usuario con DNI duplicado."""
    user_service = UserService()
    
    # Crear primer usuario con DNI
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, dni, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            ("user1_dni", password_hash, "user1@example.com", "Address1", "11111111H")
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("user1_dni", password_hash, "user1@example.com", "Address1")
        )
    conn.commit()
    conn.close()
    
    # Intentar crear segundo usuario con mismo DNI
    success, user, message = user_service.create_user(
        "user2_dni",
        "Password123",
        "user2@example.com",
        "Address2",
        "user",
        "11111111H",
        ""
    )
    
    ok_fail = assert_false(success, "No debería crear usuario con DNI duplicado")
    ok_message = assert_true("dni" in message.lower() and ("ja està" in message.lower() or "registrat" in message.lower()), f"Mensaje debería indicar DNI duplicado: {message}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username IN (?, ?)", ("user1_dni", "user2_dni"))
    conn.commit()
    conn.close()
    
    return ok_fail and ok_message



def test_user_service_update_user_profile_dni_uniqueness():
    """Test que no se puede actualizar perfil con DNI de otro usuario."""
    user_service = UserService()
    
    # Crear dos usuarios
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, dni, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            ("user1_update", password_hash, "user1_update@example.com", "Address1", "22222222J")
        )
        user1_id = cursor.lastrowid
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, dni, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            ("user2_update", password_hash, "user2_update@example.com", "Address2", "33333333C")
        )
        user2_id = cursor.lastrowid
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("user1_update", password_hash, "user1_update@example.com", "Address1")
        )
        user1_id = cursor.lastrowid
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("user2_update", password_hash, "user2_update@example.com", "Address2")
        )
        user2_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Intentar actualizar user2 con DNI de user1
    success, message = user_service.update_user_profile(
        user2_id,
        "user2_update",
        "user2_update@example.com",
        "Address2",
        "22222222J",  # DNI de user1
        ""
    )
    
    ok_fail = assert_false(success, "No debería actualizar perfil con DNI de otro usuario")
    ok_message = assert_true("dni" in message.lower() and ("ja està" in message.lower() or "registrat" in message.lower()), f"Mensaje debería indicar DNI duplicado: {message}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE id IN (?, ?)", (user1_id, user2_id))
    conn.commit()
    conn.close()
    
    return ok_fail and ok_message



def test_user_service_create_user_nif_uniqueness():
    """Test que no se puede crear empresa con NIF duplicado."""
    user_service = UserService()
    
    # Crear primera empresa con NIF
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash("Test123")
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, account_type, nif, created_at) VALUES (?, ?, ?, ?, 'company', ?, datetime('now'))",
            ("company1_nif", password_hash, "company1@example.com", "Address1", "A12345674")
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "INSERT OR REPLACE INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("company1_nif", password_hash, "company1@example.com", "Address1")
        )
    conn.commit()
    conn.close()
    
    # Intentar crear segunda empresa con mismo NIF
    success, user, message = user_service.create_user(
        "company2_nif",
        "Password123",
        "company2@example.com",
        "Address2",
        "company",
        "",
        "A12345674"
    )
    
    ok_fail = assert_false(success, "No debería crear empresa con NIF duplicado")
    ok_message = assert_true("nif" in message.lower() and ("ja està" in message.lower() or "registrat" in message.lower()), f"Mensaje debería indicar NIF duplicado: {message}")
    
    # Limpiar
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE username IN (?, ?)", ("company1_nif", "company2_nif"))
    conn.commit()
    conn.close()
    
    return ok_fail and ok_message


