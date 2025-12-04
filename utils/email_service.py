"""
Servei d'enviament d'emails
Implementa la lògica per enviar emails utilitzant SMTP de Gmail
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple
from pathlib import Path

# Carregar variables d'entorn si no estan carregades
def _load_env_if_needed():
    """Carregar variables d'entorn des del .env si no estan carregades"""
    # Intentar carregar amb dotenv primer
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Si encara no estan carregades, carregar manualment
    if not os.environ.get('EMAIL') or not os.environ.get('GOOGLE_PASSWORD_APP'):
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        # Eliminar comillas simples y dobles
                        value = value.strip().strip('"').strip("'")
                        if key and value:
                            os.environ[key] = value


def send_password_reset_email(email_to: str, username: str, new_password: str) -> Tuple[bool, str]:
    """
    Enviar email amb la nova contrasenya restablida.
    
    Args:
        email_to (str): Email del destinatari
        username (str): Nom d'usuari
        new_password (str): Nova contrasenya generada
        
    Returns:
        Tuple[bool, str]: (èxit, missatge)
    """
    # Carregar variables d'entorn si cal
    _load_env_if_needed()
    
    # Obtenir credencials des de variables d'entorn (acceptar EMAIL o CORREO)
    email_from = os.environ.get('EMAIL') or os.environ.get('CORREO')
    password_app = os.environ.get('GOOGLE_PASSWORD_APP')
    
    if not email_from or not password_app:
        return False, f"Configuració d'email no trobada. EMAIL/CORREO={'OK' if email_from else 'FALTANT'}, GOOGLE_PASSWORD_APP={'OK' if password_app else 'FALTANT'}"
    
    try:
        # Crear missatge
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = "TechShop - Nova Contrasenya"
        
        # Cos del missatge
        body = f"""
Hola {username},

S'ha sol·licitat la recuperació de la teva contrasenya a TechShop.

La teva nova contrasenya és:

{new_password}

Si no has sol·licitat aquest canvi, si us plau contacta amb nosaltres immediatament.

Per seguretat, et recomanem canviar aquesta contrasenya després d'iniciar sessió.

Salutacions,
L'equip de TechShop
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Conectar amb el servidor SMTP de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Habilitar encriptació
        server.login(email_from, password_app)
        
        # Enviar email
        text = msg.as_string()
        result = server.sendmail(email_from, [email_to], text)
        server.quit()
        
        # Verificar si hi ha errors en l'enviament
        if result:
            return False, f"Error enviant l'email. Destinataris rebutjats: {result}"
        
        return True, "Email enviat correctament"
        
    except smtplib.SMTPAuthenticationError as e:
        return False, f"Error d'autenticació amb el servidor d'email. Verifica les credencials (EMAIL i GOOGLE_PASSWORD_APP al .env). Error: {str(e)}"
    except smtplib.SMTPRecipientsRefused as e:
        return False, f"L'adreça de correu {email_to} no és vàlida o ha estat rebutjada. Error: {str(e)}"
    except smtplib.SMTPSenderRefused as e:
        return False, f"L'adreça de correu remitent {email_from} ha estat rebutjada. Error: {str(e)}"
    except smtplib.SMTPDataError as e:
        return False, f"Error enviant les dades de l'email. Error: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"Error SMTP enviant l'email: {str(e)}"
    except Exception as e:
        return False, f"Error inesperat enviant l'email: {str(e)}"


def send_welcome_email(email_to: str, username: str) -> Tuple[bool, str]:
    """
    Enviar email de benvinguda quan un usuari es registra.
    
    Args:
        email_to (str): Email del destinatari
        username (str): Nom d'usuari
        
    Returns:
        Tuple[bool, str]: (èxit, missatge)
    """
    # Carregar variables d'entorn si cal
    _load_env_if_needed()
    
    # Obtenir credencials des de variables d'entorn (acceptar EMAIL o CORREO)
    email_from = os.environ.get('EMAIL') or os.environ.get('CORREO')
    password_app = os.environ.get('GOOGLE_PASSWORD_APP')
    
    if not email_from or not password_app:
        return False, f"Configuració d'email no trobada. EMAIL/CORREO={'OK' if email_from else 'FALTANT'}, GOOGLE_PASSWORD_APP={'OK' if password_app else 'FALTANT'}"
    
    try:
        # Crear missatge
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = "Benvingut/da a TechShop!"
        
        # Cos del missatge
        body = f"""
Hola {username},

Gràcies per crear un compte a TechShop!

Estem encantats de tenir-te amb nosaltres. Ara pots:

- Explorar el nostre catàleg de productes electrònics
- Afegir productes al teu carretó de compra
- Realitzar compres de forma segura
- Gestionar el teu perfil i veure el teu historial de compres

Si tens alguna pregunta o necessites ajuda, no dubtis a contactar-nos.

Benvingut/da a la família TechShop!

Salutacions,
L'equip de TechShop
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Conectar amb el servidor SMTP de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Habilitar encriptació
        server.login(email_from, password_app)
        
        # Enviar email
        text = msg.as_string()
        result = server.sendmail(email_from, [email_to], text)
        server.quit()
        
        # Verificar si hi ha errors en l'enviament
        if result:
            return False, f"Error enviant l'email. Destinataris rebutjats: {result}"
        
        return True, "Email de benvinguda enviat correctament"
        
    except smtplib.SMTPAuthenticationError as e:
        return False, f"Error d'autenticació amb el servidor d'email. Verifica les credencials (EMAIL i GOOGLE_PASSWORD_APP al .env). Error: {str(e)}"
    except smtplib.SMTPRecipientsRefused as e:
        return False, f"L'adreça de correu {email_to} no és vàlida o ha estat rebutjada. Error: {str(e)}"
    except smtplib.SMTPSenderRefused as e:
        return False, f"L'adreça de correu remitent {email_from} ha estat rebutjada. Error: {str(e)}"
    except smtplib.SMTPDataError as e:
        return False, f"Error enviant les dades de l'email. Error: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"Error SMTP enviant l'email: {str(e)}"
    except Exception as e:
        return False, f"Error inesperat enviant l'email: {str(e)}"

