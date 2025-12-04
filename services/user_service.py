"""
Servei de gestió de perfil d'usuari
Implementa la lògica de negoci per gestionar el perfil de l'usuari
"""

import sqlite3
import secrets
import string
from typing import Tuple, Optional, List
from models import User
from datetime import datetime
from utils.validators import validar_dni_nie, validar_cif_nif
from werkzeug.security import generate_password_hash


class UserService:
    """Servei per gestionar el perfil de l'usuari"""
    
    def __init__(self, db_path: str = "techshop.db"):
        self.db_path = db_path
    
    def update_user_profile(self, user_id: int, username: str, email: str, 
                           address: str, dni: str = "", nif: str = "") -> Tuple[bool, str]:
        """
        Actualitzar el perfil de l'usuari.
        
        Args:
            user_id (int): ID de l'usuari
            username (str): Nou nom d'usuari
            email (str): Nou email
            address (str): Nova adreça
            dni (str): DNI per usuaris individuals
            nif (str): NIF per empreses
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        if not username or len(username.strip()) < 4 or len(username.strip()) > 20:
            return False, "El nom d'usuari ha de tenir entre 4 i 20 caràcters"
        
        if '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Adreça de correu electrònic no vàlida"
        
        # Validar DNI/NIF segons el tipus de compte
        cursor = None
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT account_type FROM User WHERE id = ?", (user_id,))
                result = cursor.fetchone()
                account_type = result[0] if result and result[0] else 'user'
                
                if account_type == 'company':
                    if nif and not validar_cif_nif(nif):
                        return False, "NIF no vàlid. Format esperat: lletra + 7 números + caràcter de control"
                else:
                    if dni and not validar_dni_nie(dni):
                        return False, "DNI/NIE no vàlid. Format esperat: 8 números + lletra (DNI) o X/Y/Z + 7 números + lletra (NIE)"
        except sqlite3.Error:
            pass  # Continuar amb la validació normal
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar si el username ya existe en otro usuario
                cursor.execute(
                    "SELECT id FROM User WHERE username = ? AND id != ?",
                    (username.strip(), user_id)
                )
                if cursor.fetchone():
                    return False, "Aquest nom d'usuari ja està en ús"
                
                # Verificar si el email ya existe en otro usuario
                cursor.execute(
                    "SELECT id FROM User WHERE email = ? AND id != ?",
                    (email.strip(), user_id)
                )
                if cursor.fetchone():
                    return False, "Aquest email ja està en ús"
                
                # Verificar si el DNI ya existe en otro usuario (si se proporciona)
                if dni:
                    try:
                        cursor.execute(
                            "SELECT id FROM User WHERE dni = ? AND id != ?",
                            (dni.strip().upper(), user_id)
                        )
                        if cursor.fetchone():
                            return False, "Aquest DNI/NIE ja està registrat en un altre compte"
                    except sqlite3.OperationalError:
                        pass  # Si la columna DNI no existe, continuar
                
                # Verificar si el NIF ya existe en otro usuario (si se proporciona)
                if nif:
                    try:
                        cursor.execute(
                            "SELECT id FROM User WHERE nif = ? AND id != ?",
                            (nif.strip().upper(), user_id)
                        )
                        if cursor.fetchone():
                            return False, "Aquest NIF/CIF ja està registrat en un altre compte"
                    except sqlite3.OperationalError:
                        pass  # Si la columna NIF no existe, continuar
                
                # Obtener account_type del usuario
                cursor.execute("SELECT account_type FROM User WHERE id = ?", (user_id,))
                result = cursor.fetchone()
                account_type = result[0] if result and result[0] else 'user'
                
                # Actualizar según las columnas disponibles
                try:
                    if account_type == 'company':
                        cursor.execute(
                            "UPDATE User SET username = ?, email = ?, address = ?, nif = ? WHERE id = ?",
                            (username.strip(), email.strip(), address.strip(), nif.strip(), user_id)
                        )
                    else:
                        cursor.execute(
                            "UPDATE User SET username = ?, email = ?, address = ?, dni = ? WHERE id = ?",
                            (username.strip(), email.strip(), address.strip(), dni.strip(), user_id)
                        )
                except sqlite3.OperationalError:
                    # Si las columnas DNI/NIF no existen, actualizar sin ellas
                    cursor.execute(
                        "UPDATE User SET username = ?, email = ?, address = ? WHERE id = ?",
                        (username.strip(), email.strip(), address.strip(), user_id)
                    )
                
                if cursor.rowcount == 0:
                    return False, "Usuari no trobat"
                conn.commit()
                return True, "Perfil actualitzat correctament"
        except sqlite3.Error as e:
            return False, f"Error actualitzant el perfil: {str(e)}"
    
    def check_missing_required_data(self, user_id: int) -> Tuple[bool, List[str]]:
        """
        Verificar si a l'usuari li falten dades obligatòries.
        
        Args:
            user_id (int): ID de l'usuari
            
        Returns:
            Tuple[bool, List[str]]: (hi ha dades faltants, llista de camps faltants)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener datos del usuario
                try:
                    cursor.execute(
                        "SELECT account_type, email, address, dni, nif FROM User WHERE id = ?",
                        (user_id,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        return True, ["usuari_no_trobat"]
                    
                    account_type = result[0] or "user"
                    email = result[1]
                    address = result[2]
                    dni = result[3]
                    nif = result[4]
                except sqlite3.OperationalError:
                    # Si las columnas no existen, verificar solo campos básicos
                    cursor.execute(
                        "SELECT email, address FROM User WHERE id = ?",
                        (user_id,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        return True, ["usuari_no_trobat"]
                    email = result[0]
                    address = result[1]
                    account_type = "user"
                    dni = ""
                    nif = ""
                
                missing_fields = []
                
                # Verificar campos obligatorios comunes
                if not email or email.strip() == "":
                    missing_fields.append("email")
                
                if not address or address.strip() == "":
                    missing_fields.append("address")
                
                # Verificar campos según tipo de cuenta
                if account_type == 'company':
                    if not nif or nif.strip() == "":
                        missing_fields.append("nif")
                else:
                    # Para usuarios comunes, DNI es opcional pero recomendado
                    # No lo marcamos como faltante obligatorio
                    pass
                
                return len(missing_fields) > 0, missing_fields
                
        except sqlite3.Error:
            return True, ["error_verificacio"]
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtenir un usuari per ID amb totes les dades.
        
        Args:
            user_id (int): ID de l'usuari
            
        Returns:
            User o None: L'usuari si existeix, None altrament
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "SELECT id, username, email, address, role, account_type, dni, nif, created_at FROM User WHERE id = ?",
                        (user_id,)
                    )
                    result = cursor.fetchone()
                    if result and len(result) >= 9:
                        return User(
                            id=result[0],
                            username=result[1],
                            email=result[2] if result[2] else "",
                            address=result[3] if result[3] else "",
                            role=result[4] if result[4] else "common",
                            account_type=result[5] if result[5] else "user",
                            dni=result[6] if result[6] else "",
                            nif=result[7] if result[7] else "",
                            password_hash="",
                            created_at=datetime.fromisoformat(result[8]) if result[8] else datetime.now()
                        )
                except sqlite3.OperationalError:
                    # Sin DNI/NIF
                    cursor.execute(
                        "SELECT id, username, email, address, role, account_type, created_at FROM User WHERE id = ?",
                        (user_id,)
                    )
                    result = cursor.fetchone()
                    if result and len(result) >= 7:
                        return User(
                            id=result[0],
                            username=result[1],
                            email=result[2] if result[2] else "",
                            address=result[3] if result[3] else "",
                            role=result[4] if result[4] else "common",
                            account_type=result[5] if result[5] else "user",
                            password_hash="",
                            created_at=datetime.fromisoformat(result[6]) if result[6] else datetime.now()
                        )
        except sqlite3.Error:
            pass
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obtenir un usuari per email amb totes les dades.
        
        Args:
            email (str): Email de l'usuari
            
        Returns:
            User o None: L'usuari si existeix, None altrament
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "SELECT id, username, email, address, role, account_type, dni, nif, created_at FROM User WHERE email = ?",
                        (email.lower(),)
                    )
                    result = cursor.fetchone()
                    if result and len(result) >= 9:
                        return User(
                            id=result[0],
                            username=result[1],
                            email=result[2] if result[2] else "",
                            address=result[3] if result[3] else "",
                            role=result[4] if result[4] else "common",
                            account_type=result[5] if result[5] else "user",
                            dni=result[6] if result[6] else "",
                            nif=result[7] if result[7] else "",
                            password_hash="",
                            created_at=datetime.fromisoformat(result[8]) if result[8] else datetime.now()
                        )
                except sqlite3.OperationalError:
                    # Sin DNI/NIF
                    cursor.execute(
                        "SELECT id, username, email, address, role, account_type, created_at FROM User WHERE email = ?",
                        (email.lower(),)
                    )
                    result = cursor.fetchone()
                    if result and len(result) >= 7:
                        return User(
                            id=result[0],
                            username=result[1],
                            email=result[2] if result[2] else "",
                            address=result[3] if result[3] else "",
                            role=result[4] if result[4] else "common",
                            account_type=result[5] if result[5] else "user",
                            password_hash="",
                            created_at=datetime.fromisoformat(result[6]) if result[6] else datetime.now()
                        )
        except sqlite3.Error:
            pass
        
        return None
    
    def reset_password_by_dni_and_email(self, dni: str, email: str) -> Tuple[bool, str]:
        """
        Restablir contrasenya d'un usuari mitjançant el seu DNI i email, i enviar-la per email.
        
        Args:
            dni (str): DNI de l'usuari
            email (str): Email de l'usuari
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        from utils.email_service import send_password_reset_email
        
        # Validar DNI
        if not dni or not validar_dni_nie(dni):
            return False, "DNI/NIE no vàlid"
        
        # Validar email
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Email no vàlid"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar usuari per DNI i email (han de coincidir)
                try:
                    cursor.execute(
                        "SELECT id, username, email FROM User WHERE dni = ? AND email = ?",
                        (dni.upper(), email.strip().lower())
                    )
                except sqlite3.OperationalError:
                    # Si la columna DNI no existe, retornar error
                    return False, "El sistema no suporta la recuperació de contrasenya per DNI"
                
                result = cursor.fetchone()
                
                if not result:
                    return False, "No s'ha trobat cap usuari amb aquest DNI/NIE i email. Verifica que ambdós coincideixin amb el teu compte."
                
                user_id, username, user_email = result
                
                if not user_email:
                    return False, "L'usuari no té un email registrat. Contacta amb l'administrador."
                
                # Generar nova contrasenya aleatòria
                alphabet = string.ascii_letters + string.digits
                new_password = ''.join(secrets.choice(alphabet) for i in range(12))
                
                # Actualitzar contrasenya
                password_hash = generate_password_hash(new_password)
                cursor.execute(
                    "UPDATE User SET password_hash = ? WHERE id = ?",
                    (password_hash, user_id)
                )
                conn.commit()
                
                # Enviar email amb la nova contrasenya
                email_success, email_message = send_password_reset_email(user_email, username, new_password)
                
                if email_success:
                    return True, f"S'ha enviat un email a {user_email} amb la teva nova contrasenya. Si no el veus, revisa la carpeta de spam."
                else:
                    # Si falla l'email, revertir el canvi de contrasenya (opcional)
                    # Por ahora solo retornamos el error
                    return False, f"Contrasenya restablida però error enviant l'email: {email_message}"
                
        except sqlite3.Error as e:
            return False, f"Error restablint la contrasenya: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Autenticar un usuari amb nom d'usuari i contrasenya.
        
        Args:
            username (str): Nom d'usuari
            password (str): Contrasenya en text pla
            
        Returns:
            Tuple[bool, Optional[User], str]: (èxit, usuari, missatge)
        """
        from werkzeug.security import check_password_hash
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "SELECT id, username, password_hash, email, address, role, account_type, dni, nif, created_at FROM User WHERE username = ?",
                        (username,)
                    )
                    result = cursor.fetchone()
                except sqlite3.OperationalError:
                    cursor.execute(
                        "SELECT id, username, password_hash, email, address, role, account_type, created_at FROM User WHERE username = ?",
                        (username,)
                    )
                    result = cursor.fetchone()
                
                if not result:
                    return False, None, "Nom d'usuari o contrasenya incorrectes"
                
                user_id = result[0]
                stored_hash = result[2]
                
                if not check_password_hash(stored_hash, password):
                    return False, None, "Nom d'usuari o contrasenya incorrectes"
                
                # Construir objecte User
                try:
                    user = User(
                        id=result[0],
                        username=result[1],
                        email=result[3] if result[3] else "",
                        address=result[4] if result[4] else "",
                        role=result[5] if result[5] else "common",
                        account_type=result[6] if result[6] else "user",
                        dni=result[7] if len(result) > 7 and result[7] else "",
                        nif=result[8] if len(result) > 8 and result[8] else "",
                        password_hash="",
                        created_at=datetime.fromisoformat(result[9] if len(result) > 9 and result[9] else datetime.now().isoformat())
                    )
                except (IndexError, ValueError):
                    user = User(
                        id=result[0],
                        username=result[1],
                        email=result[3] if len(result) > 3 and result[3] else "",
                        address=result[4] if len(result) > 4 and result[4] else "",
                        role=result[5] if len(result) > 5 and result[5] else "common",
                        account_type=result[6] if len(result) > 6 and result[6] else "user",
                        password_hash="",
                        created_at=datetime.fromisoformat(result[7] if len(result) > 7 and result[7] else datetime.now().isoformat())
                    )
                
                return True, user, "Autenticació correcta"
        except sqlite3.Error as e:
            return False, None, f"Error d'autenticació: {str(e)}"
    
    def create_or_get_user(self, username: str, password: str, email: str, address: str) -> Tuple[bool, Optional[User], str]:
        """
        Crear un nou usuari o obtenir-lo si ja existeix.
        Utilitzat en el checkout com a convidat.
        
        Args:
            username (str): Nom d'usuari
            password (str): Contrasenya en text pla
            email (str): Email
            address (str): Adreça
            
        Returns:
            Tuple[bool, Optional[User], str]: (èxit, usuari, missatge)
        """
        from werkzeug.security import generate_password_hash
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Comprovar si l'usuari ja existeix
                cursor.execute("SELECT id, password_hash FROM User WHERE username = ?", (username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    user_id, stored_hash = existing_user
                    from werkzeug.security import check_password_hash
                    if not check_password_hash(stored_hash, password):
                        return False, None, "Contrasenya incorrecta per a l'usuari indicat"
                    
                    # Actualitzar dades de contacte
                    try:
                        cursor.execute(
                            "UPDATE User SET email = ?, address = ? WHERE id = ?",
                            (email, address, user_id)
                        )
                    except sqlite3.OperationalError:
                        pass
                    conn.commit()
                    
                    # Obtenir usuari actualitzat
                    user = self.get_user_by_id(user_id)
                    return True, user, "Usuari existent actualitzat"
                else:
                    # Registrar nou usuari
                    password_hash = generate_password_hash(password, method="pbkdf2:sha256")
                    try:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, role, account_type, created_at) "
                            "VALUES (?, ?, ?, ?, 'common', 'user', datetime('now'))",
                            (username, password_hash, email, address)
                        )
                    except sqlite3.OperationalError:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, created_at) "
                            "VALUES (?, ?, ?, ?, datetime('now'))",
                            (username, password_hash, email, address)
                        )
                    
                    user_id = cursor.lastrowid
                    conn.commit()
                    
                    user = self.get_user_by_id(user_id)
                    return True, user, "Usuari creat correctament"
        except sqlite3.Error as e:
            return False, None, f"Error creant usuari: {str(e)}"
    
    def create_user(self, username: str, password: str, email: str, address: str, 
                   account_type: str = 'user', dni: str = "", nif: str = "") -> Tuple[bool, Optional[User], str]:
        """
        Crear un nou usuari (per registre).
        
        Args:
            username (str): Nom d'usuari
            password (str): Contrasenya en text pla
            email (str): Email
            address (str): Adreça
            account_type (str): Tipus de compte ('user' o 'company')
            dni (str): DNI per usuaris individuals
            nif (str): NIF per empreses
            
        Returns:
            Tuple[bool, Optional[User], str]: (èxit, usuari, missatge)
        """
        from werkzeug.security import generate_password_hash
        
        # Validacions
        if not username or len(username.strip()) < 4 or len(username.strip()) > 20:
            return False, None, "El nom d'usuari ha de tenir entre 4 i 20 caràcters"
        
        if not password or len(password) < 8:
            return False, None, "La contrasenya ha de tenir mínim 8 caràcters"
        
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            return False, None, "La contrasenya ha de contenir almenys una lletra i un número"
        
        if '@' not in email or '.' not in email.split('@')[-1]:
            return False, None, "Adreça de correu electrònic no vàlida"
        
        # Validar DNI/NIF segons el tipus de compte
        if account_type == 'company':
            if not nif or not validar_cif_nif(nif):
                return False, None, "NIF no vàlid. Format esperat: lletra + 7 números + caràcter de control"
        else:
            if not dni or not validar_dni_nie(dni):
                return False, None, "DNI/NIE no vàlid. Format esperat: 8 números + lletra (DNI) o X/Y/Z + 7 números + lletra (NIE)"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Comprovar si l'usuari ja existeix
                cursor.execute("SELECT id FROM User WHERE username = ?", (username,))
                if cursor.fetchone():
                    return False, None, "Aquest nom d'usuari ja està en ús"
                
                # Comprovar si l'email ja existeix
                cursor.execute("SELECT id FROM User WHERE email = ?", (email,))
                if cursor.fetchone():
                    return False, None, "Aquest email ja està en ús"
                
                # Comprovar si el DNI ja existeix (si s'ha proporcionat)
                if dni:
                    try:
                        cursor.execute("SELECT id FROM User WHERE dni = ? AND id != ?", (dni.strip().upper(), 0))
                        if cursor.fetchone():
                            return False, None, "Aquest DNI/NIE ja està registrat en un altre compte"
                    except sqlite3.OperationalError:
                        pass  # Si la columna DNI no existe, continuar
                
                # Comprovar si el NIF ja existeix (si s'ha proporcionat)
                if nif:
                    try:
                        cursor.execute("SELECT id FROM User WHERE nif = ? AND id != ?", (nif.strip().upper(), 0))
                        if cursor.fetchone():
                            return False, None, "Aquest NIF/CIF ja està registrat en un altre compte"
                    except sqlite3.OperationalError:
                        pass  # Si la columna NIF no existe, continuar
                
                # Crear usuari
                password_hash = generate_password_hash(password, method="pbkdf2:sha256")
                try:
                    cursor.execute(
                        "INSERT INTO User (username, password_hash, email, address, role, account_type, dni, nif, created_at) "
                        "VALUES (?, ?, ?, ?, 'common', ?, ?, ?, datetime('now'))",
                        (username.strip(), password_hash, email.strip(), address.strip(), account_type, dni.strip(), nif.strip())
                    )
                except sqlite3.OperationalError:
                    # Si las columnas no existen, insertar sin ellas
                    try:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, role, account_type, created_at) "
                            "VALUES (?, ?, ?, ?, 'common', ?, datetime('now'))",
                            (username.strip(), password_hash, email.strip(), address.strip(), account_type)
                        )
                    except sqlite3.OperationalError:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, created_at) "
                            "VALUES (?, ?, ?, ?, datetime('now'))",
                            (username.strip(), password_hash, email.strip(), address.strip())
                        )
                
                user_id = cursor.lastrowid
                conn.commit()
                
                user = self.get_user_by_id(user_id)
                
                # Enviar email de benvinguda (no bloqueja si falla)
                try:
                    from utils.email_service import send_welcome_email
                    email_success, email_message = send_welcome_email(email, username)
                    if email_success:
                        print(f"✅ Email de benvinguda enviat correctament a {email}")
                    else:
                        # Log del error pero no fallar el registro
                        print(f"⚠️  Error enviant email de benvinguda a {email}: {email_message}")
                except Exception as e:
                    # Log del error pero no fallar el registro
                    print(f"⚠️  Excepció enviant email de benvinguda a {email}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                return True, user, "Usuari creat correctament"
        except sqlite3.Error as e:
            return False, None, f"Error creant usuari: {str(e)}"
    
    def create_user_with_google(self, username: str, email: str, address: str, dni: str = "") -> Tuple[bool, Optional[User], str]:
        """
        Crear un usuari amb Google OAuth (només usuaris comuns).
        
        Args:
            username (str): Nom d'usuari
            email (str): Email de Google
            address (str): Adreça d'enviament
            dni (str): DNI/NIE (opcional)
            
        Returns:
            Tuple[bool, Optional[User], str]: (èxit, usuari, missatge)
        """
        # Validacions bàsiques
        if not username or len(username) < 4 or len(username) > 20:
            return False, None, "El nom d'usuari ha de tenir entre 4 i 20 caràcters"
        
        if not address or len(address) < 10:
            return False, None, "L'adreça ha de tenir almenys 10 caràcters"
        
        # Validar DNI si s'ha proporcionat
        if dni and not validar_dni_nie(dni):
            return False, None, "DNI/NIE no vàlid"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Comprovar si l'usuari ja existeix
                cursor.execute("SELECT id FROM User WHERE username = ?", (username,))
                if cursor.fetchone():
                    return False, None, "Aquest nom d'usuari ja està en ús"
                
                # Comprovar si l'email ja existeix
                cursor.execute("SELECT id FROM User WHERE email = ?", (email.lower(),))
                if cursor.fetchone():
                    return False, None, "Aquest email ja està en ús"
                
                # Comprovar si el DNI ja existeix (si s'ha proporcionat)
                if dni:
                    try:
                        cursor.execute("SELECT id FROM User WHERE dni = ? AND id != ?", (dni.strip().upper(), 0))
                        if cursor.fetchone():
                            return False, None, "Aquest DNI/NIE ja està registrat en un altre compte"
                    except sqlite3.OperationalError:
                        pass  # Si la columna DNI no existe, continuar
                
                # Crear usuari sense contrasenya (OAuth)
                # Generar un hash aleatori per a la contrasenya (no s'utilitzarà)
                random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
                password_hash = generate_password_hash(random_password, method="pbkdf2:sha256")
                
                try:
                    if dni:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, role, account_type, dni, created_at) "
                            "VALUES (?, ?, ?, ?, 'common', 'user', ?, datetime('now'))",
                            (username.strip(), password_hash, email.strip().lower(), address.strip(), dni.strip().upper())
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO User (username, password_hash, email, address, role, account_type, created_at) "
                            "VALUES (?, ?, ?, ?, 'common', 'user', datetime('now'))",
                            (username.strip(), password_hash, email.strip().lower(), address.strip())
                        )
                except sqlite3.OperationalError:
                    # Si las columnas no existen, insertar sin ellas
                    cursor.execute(
                        "INSERT INTO User (username, password_hash, email, address, created_at) "
                        "VALUES (?, ?, ?, ?, datetime('now'))",
                        (username.strip(), password_hash, email.strip().lower(), address.strip())
                    )
                
                user_id = cursor.lastrowid
                conn.commit()
                
                user = self.get_user_by_id(user_id)
                
                # Enviar email de benvinguda (no bloqueja si falla)
                try:
                    from utils.email_service import send_welcome_email
                    email_success, email_message = send_welcome_email(email, username)
                    if email_success:
                        print(f"✅ Email de benvinguda enviat correctament a {email}")
                    else:
                        print(f"⚠️  Error enviant email de benvinguda a {email}: {email_message}")
                except Exception as e:
                    print(f"⚠️  Excepció enviant email de benvinguda a {email}: {str(e)}")
                
                return True, user, "Usuari creat correctament amb Google"
        except sqlite3.Error as e:
            return False, None, f"Error creant usuari: {str(e)}"
    
    def delete_user_account(self, user_id: int) -> Tuple[bool, str]:
        """
        Eliminar el compte de l'usuari.
        Elimina l'usuari i totes les seves dades associades.
        
        Args:
            user_id (int): ID de l'usuari a eliminar
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar que el usuario existe
                cursor.execute("SELECT id FROM User WHERE id = ?", (user_id,))
                if not cursor.fetchone():
                    return False, "Usuari no trobat"
                
                # Eliminar items de comandes associades
                cursor.execute("""
                    DELETE FROM OrderItem 
                    WHERE order_id IN (SELECT id FROM "Order" WHERE user_id = ?)
                """, (user_id,))
                
                # Eliminar comandes de l'usuari
                cursor.execute('DELETE FROM "Order" WHERE user_id = ?', (user_id,))
                
                # Eliminar l'usuari
                cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
                
                conn.commit()
                return True, "Compte eliminat correctament"
        except sqlite3.Error as e:
            return False, f"Error eliminant el compte: {str(e)}"

