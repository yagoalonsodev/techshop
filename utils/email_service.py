"""
Servei d'enviament d'emails
Implementa la lògica per enviar emails utilitzant SMTP de Gmail
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Tuple, Optional
from pathlib import Path
import base64

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


def send_order_confirmation_email(
    email_to: str, 
    username: str, 
    order_id: int, 
    order_total: float,
    order_date: str,
    order_items: list,
    invoice_pdf: Optional[bytes] = None
) -> Tuple[bool, str]:
    """
    Enviar email de confirmación de compra con foto del producto y factura adjunta.
    
    Esta función NO accede directamente a la base de datos. Recibe los datos ya procesados
    desde la capa de servicios, siguiendo la arquitectura de 3 capas.
    
    Args:
        email_to (str): Email del destinatario
        username (str): Nombre de usuario
        order_id (int): ID de la orden
        order_total (float): Total de la orden
        order_date (str): Fecha de la orden
        order_items (list): Lista de items con formato [{'product_id': int, 'quantity': int, 'name': str, 'price': Decimal}, ...]
        invoice_pdf (bytes, optional): PDF de la factura para adjuntar
        
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    _load_env_if_needed()
    
    email_from = os.environ.get('EMAIL') or os.environ.get('CORREO')
    password_app = os.environ.get('GOOGLE_PASSWORD_APP')
    
    if not email_from or not password_app:
        return False, f"Configuració d'email no trobada. EMAIL/CORREO={'OK' if email_from else 'FALTANT'}, GOOGLE_PASSWORD_APP={'OK' if password_app else 'FALTANT'}"
    
    try:
        # Obtener primera imagen de cada producto (acceso a archivos, no BD)
        product_images = {}
        for item in order_items:
            product_id = item['product_id']
            # Buscar imagen del producto
            images_dir = Path('static/img/products') / str(product_id)
            if images_dir.exists():
                for img_file in sorted(images_dir.glob('*.jpg')) + sorted(images_dir.glob('*.png')):
                    product_images[product_id] = str(img_file)
                    break
        
        # Crear mensaje HTML
        msg = MIMEMultipart('related')
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = f"TechShop - Confirmación de Compra #{order_id}"
        
        # Construir HTML del email
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .product-card {{ background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .product-image {{ max-width: 200px; height: auto; border-radius: 8px; margin: 10px 0; }}
                .product-name {{ font-size: 18px; font-weight: bold; color: #0d6efd; margin: 10px 0; }}
                .order-info {{ background: white; border-radius: 8px; padding: 20px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Gracias por tu compra, {username}!</h1>
                </div>
                <div class="content">
                    <p>Tu pedido ha sido procesado correctamente. Aquí tienes los detalles:</p>
                    
                    <div class="order-info">
                        <h3>Detalles del Pedido</h3>
                        <p><strong>Número de Pedido:</strong> #{order_id}</p>
                        <p><strong>Total:</strong> {order_total:.2f}€</p>
                        <p><strong>Fecha:</strong> {order_date}</p>
                    </div>
                    
                    <h3>Productos Comprados:</h3>
        """
        
        # Agregar productos con imágenes
        for item in order_items:
            product_id = item['product_id']
            quantity = item['quantity']
            name = item['name']
            price = item['price']
            image_path = product_images.get(product_id)
            if image_path and os.path.exists(image_path):
                # Leer imagen y convertir a base64 para incrustar en HTML
                with open(image_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    img_ext = Path(image_path).suffix[1:].lower()
                    img_mime = 'image/jpeg' if img_ext in ['jpg', 'jpeg'] else 'image/png'
                    html_body += f"""
                    <div class="product-card">
                        <img src="data:{img_mime};base64,{img_data}" alt="{name}" class="product-image">
                        <div class="product-name">{name}</div>
                        <p><strong>Cantidad:</strong> {quantity}</p>
                        <p><strong>Precio unitario:</strong> {price:.2f}€</p>
                        <p><strong>Subtotal:</strong> {float(price) * quantity:.2f}€</p>
                    </div>
                    """
            else:
                html_body += f"""
                    <div class="product-card">
                        <div class="product-name">{name}</div>
                        <p><strong>Cantidad:</strong> {quantity}</p>
                        <p><strong>Precio unitario:</strong> {price:.2f}€</p>
                        <p><strong>Subtotal:</strong> {float(price) * quantity:.2f}€</p>
                    </div>
                """
        
        html_body += f"""
                    <p style="margin-top: 20px;"><strong>La factura está adjunta a este correo.</strong></p>
                </div>
                <div class="footer">
                    <p>TechShop - Tu tienda de tecnología de confianza</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Adjuntar HTML
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Adjuntar factura PDF si está disponible
        if invoice_pdf:
            part = MIMEBase('application', 'pdf')
            part.set_payload(invoice_pdf)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename=factura_{order_id}.pdf')
            msg.attach(part)
        
        # Enviar email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_from, password_app)
        text = msg.as_string()
        result = server.sendmail(email_from, [email_to], text)
        server.quit()
        
        if result:
            return False, f"Error enviant l'email. Destinataris rebutjats: {result}"
        
        return True, "Email de confirmación enviado correctamente"
        
    except Exception as e:
        return False, f"Error inesperat enviant l'email: {str(e)}"
