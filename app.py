"""
Aplicació principal TechShop
Aplicació web per gestionar un carretó de compres per a TechShop
"""

import os
import sqlite3
from decimal import Decimal
from pathlib import Path
from typing import Dict, List

# Intentar carregar dotenv, però no fallar si no està instal·lat (per tests)
try:
    from dotenv import load_dotenv
    # Carregar variables d'entorn des del fitxer .env si existeix
    load_dotenv()
except ImportError:
    # Si dotenv no està instal·lat, intentar carregar manualment el .env
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ[key] = value

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, make_response
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth

from models import Product, User
from services.cart_service import CartService
from services.order_service import OrderService
from services.recommendation_service import RecommendationService
from services.admin_service import AdminService
from services.user_service import UserService
from services.company_service import CompanyService
from services.product_service import ProductService
from utils.validators import validar_dni_nie, validar_cif_nif
from utils.translations import get_translation, get_available_languages, get_language_name
from functools import wraps


app = Flask(__name__)

# SECRET_KEY únicament des de variable d'entorn (.env)
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "SECRET_KEY no configurada. Afegeix SECRET_KEY al fitxer .env a la "
        "arrel del projecte, per exemple:\n\nSECRET_KEY=una-clau-molt-secreta"
    )
app.config["SECRET_KEY"] = secret_key

# Protecció CSRF per totes les peticions POST
csrf = CSRFProtect(app)

# Configurar OAuth de Google
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def get_current_language():
    """
    Obtener el idioma actual de la sesión.
    
    Returns:
        str: Código del idioma ('cat', 'esp', 'eng'), por defecto 'cat'
    """
    return session.get('language', 'cat')

@app.context_processor
def inject_language():
    """
    Inyectar funciones de traducción en todos los templates.
    """
    lang = get_current_language()
    return {
        '_': lambda key: get_translation(key, lang),
        'current_language': lang,
        'available_languages': get_available_languages(),
        'get_language_name': get_language_name
    }

def flash_translated(key: str, category: str = 'info'):
    """
    Mostrar un mensaje flash traducido.
    
    Args:
        key (str): Clave de traducción
        category (str): Categoría del mensaje ('success', 'error', 'warning', 'info')
    """
    lang = get_current_language()
    message = get_translation(key, lang)
    flash(message, category)

def get_current_user():
    """
    Obtenir l'usuari actual des de la sessió.
    
    Returns:
        User o None: L'usuari actual si està autenticat, None altrament
    """
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    # Obtenir usuari mitjançant el servei (seguint les regles)
    return user_service.get_user_by_id(user_id)


@app.context_processor
def inject_csrf_token():
    """Permet usar {{ csrf_token() }} als formularis HTML sense WTForms."""
    user = get_current_user()
    return dict(csrf_token=generate_csrf, current_user=user)

# Inicialitzar serveis
cart_service = CartService()
order_service = OrderService()
recommendation_service = RecommendationService()
admin_service = AdminService()
user_service = UserService()
product_service = ProductService()
# company_service s'inicialitzarà després de crear l'app


def require_admin(f):
    """
    Decorador per protegir rutes que requereixen permisos d'administrador.
    
    Args:
        f: Funció a decorar
        
    Returns:
        Funció decorada que verifica permisos d'admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin():
            flash("Accés denegat. Es requereixen permisos d'administrador.", 'error')
            return redirect(url_for('show_products'))
        return f(*args, **kwargs)
    return decorated_function


def require_company(f):
    """
    Decorador per protegir rutes que requereixen ser una empresa.
    
    Args:
        f: Funció a decorar
        
    Returns:
        Funció decorada que verifica que l'usuari és una empresa
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Has d'iniciar sessió per accedir a aquesta pàgina.", 'error')
            return redirect(url_for('login'))
        if user.account_type != 'company':
            flash("Accés denegat. Aquesta funcionalitat és només per empreses.", 'error')
            return redirect(url_for('show_products'))
        return f(*args, **kwargs)
    return decorated_function

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def _get_product_images(product_id: int, limit: int = 4) -> List[str]:
    """
    Construir les rutes d'imatge per a un producte determinat.
    
    Args:
        product_id (int): Identificador del producte.
        limit (int): Nombre màxim d'imatges a retornar.
        
    Returns:
        List[str]: Llista d'URLs relatives a les imatges del producte.
    """
    images_dir = Path(app.static_folder) / 'img' / 'products' / str(product_id)
    if not images_dir.exists():
        return []

    image_urls: List[str] = []
    for image_path in sorted(images_dir.iterdir()):
        if not image_path.is_file():
            continue
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        image_urls.append(
            url_for('static', filename=f'img/products/{product_id}/{image_path.name}')
        )
        if len(image_urls) >= limit:
            break

    return image_urls


@app.route('/')
def show_products():
    """
    Ruta que obté tots els productes de la base de dades i els passa a la capa de presentació.
    
    Returns:
        str: Pàgina HTML amb la llista de productes
    """
    recommendations = recommendation_service.get_top_selling_products(limit=3)
    user_recommendations = []
    user_id = session.get('user_id')
    if user_id:
        user_recommendations = recommendation_service.get_top_products_for_user(user_id=user_id, limit=3)

    # Obtenir productes mitjançant el servei (seguint les regles)
    products = product_service.get_all_products()
    
    # Obtenir imatges per a cada producte
    product_images: Dict[int, List[str]] = {}
    for product in products:
        product_images[product.id] = _get_product_images(product.id)
    
    return render_template(
        'products.html',
        products=products,
        recommendations=recommendations,
        user_recommendations=user_recommendations,
        product_images=product_images
    )
            

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Ruta que mostra el detall d'un producte específic.
    
    Args:
        product_id (int): ID del producte
        
    Returns:
        str: Pàgina HTML amb el detall del producte
    """
    # Obtenir producte mitjançant el servei
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        flash("Producte no trobat", 'error')
        return redirect(url_for('show_products'))
    
    # Obtenir imatges del producte
    product_images = _get_product_images(product_id)
    
    return render_template(
        'product_detail.html',
        product=product,
        product_images=product_images
    )


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Afegir producte al carretó des de la interfície web.
    
    Returns:
        str: Redirecció a la pàgina de productes
    """
    # Verificar que no sigui una empresa (les empreses no poden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('show_products'))
    
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not product_id or not quantity:
        flash("Dades invàlides", 'error')
        return redirect(url_for('show_products'))
    
    success, message = cart_service.add_to_cart(product_id, quantity, session)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('show_products'))


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """
    Eliminar producte del carretó des de la interfície web.
    
    Returns:
        str: Redirecció a la pàgina de checkout
    """
    # Verificar que no sigui una empresa (les empreses no poden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('show_products'))
    
    product_id = request.form.get('product_id', type=int)
    
    if not product_id:
        flash("Producte no especificat", 'error')
        return redirect(url_for('checkout'))
    
    success, message = cart_service.remove_from_cart(product_id, session)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('checkout'))


@app.route('/checkout')
def checkout():
    """
    Ruta que mostra el resum del carretó i un formulari per introduir dades de l'usuari.
    
    Returns:
        str: Pàgina HTML del checkout
    """
    # Verificar que no sigui una empresa (les empreses no poden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('show_products'))
    
    cart_contents = cart_service.get_cart_contents(session)
    cart_total = cart_service.get_cart_total(session)
    
    # Obtenir informació dels productes del carretó mitjançant el servei
    products_with_quantities = product_service.get_products_by_ids(cart_contents)
    
    # Construir llista amb imatges
    cart_products = []
    for product, quantity in products_with_quantities:
                    cart_products.append(
                        (product, quantity, _get_product_images(product.id))
                    )
    
    return render_template('checkout.html', 
                         cart_products=cart_products, 
                         cart_total=cart_total)


@app.route('/process_order', methods=['POST'])
def process_order():
    """
    Processar la comanda quan l'usuari confirma la compra.
    Maneja dos flujos: usuari autenticat (solo dirección) o invitado (todos los campos).
    
    Returns:
        str: Redirecció a la pàgina de confirmació
    """
    # Verificar que no sigui una empresa (les empreses no poden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('show_products'))
    
    checkout_type = request.form.get('checkout_type', 'guest')
    address = request.form.get('address', '').strip()
    
    # Si l'usuari està autenticat, només necessitem l'adreça
    if checkout_type == 'authenticated':
        user_id = session.get('user_id')
        if not user_id:
            flash("Sessió no vàlida. Si us plau, inicia sessió de nou.", 'error')
            return redirect(url_for('login'))
        
        # Validar adreça
        if not address or len(address) < 10:
            flash("L'adreça d'enviament ha de tenir almenys 10 caràcters", 'error')
            return redirect(url_for('checkout'))
        
        # Actualitzar adreça de l'usuari si cal (mitjançant el servei)
        user = user_service.get_user_by_id(user_id)
        if user:
            user_service.update_user_profile(user_id, user.username, user.email, address, 
                                            user.dni if hasattr(user, 'dni') else "", 
                                            user.nif if hasattr(user, 'nif') else "")
        
        # Crear la comanda
        conn = None
        try:
            conn = sqlite3.connect('techshop.db')
            cart_contents = cart_service.get_cart_contents(session)
            success, message, order_id = order_service.create_order_in_transaction(
                conn, cart_contents, user_id
            )
            
            if not success:
                conn.rollback()
                flash(message, "error")
                return redirect(url_for("checkout"))
            
            conn.commit()
            cart_service.clear_cart(session)
            flash(f"Comanda processada correctament! ID: {order_id}", "success")
            return redirect(url_for("order_confirmation", order_id=order_id))
            
        except sqlite3.Error as e:
            if conn is not None:
                conn.rollback()
            flash(f"Error processant la comanda: {str(e)}", "error")
            return redirect(url_for("checkout"))
        finally:
            if conn is not None:
                conn.close()
    
    # Flujo d'invitado: demanar tots els camps
    else:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validacions del servidor
        if not all([username, password, email, address]):
            flash("Tots els camps són obligatoris", 'error')
            return redirect(url_for('checkout'))
        
        # Validar nom d'usuari
        if len(username) < 4 or len(username) > 20:
            flash("El nom d'usuari ha de tenir entre 4 i 20 caràcters", 'error')
            return redirect(url_for('checkout'))
        
        # Validar contrasenya (mínim 8 caràcters, almenys una lletra i un número)
        if len(password) < 8:
            flash("La contrasenya ha de tenir mínim 8 caràcters", 'error')
            return redirect(url_for('checkout'))
        
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            flash("La contrasenya ha de contenir almenys una lletra i un número", 'error')
            return redirect(url_for('checkout'))
        
        # Validar email: ha de contenir un @ i un . després de l'arroba
        if '@' not in email or '.' not in email.split('@')[-1]:
            flash("Adreça de correu electrònic no vàlida", 'error')
            return redirect(url_for('checkout'))
        
        # Validar adreça
        if len(address) < 10:
            flash("L'adreça d'enviament ha de tenir almenys 10 caràcters", 'error')
            return redirect(url_for('checkout'))
        
        # Crear o obtenir usuari mitjançant el servei (seguint les regles)
        success_user, user, message_user = user_service.create_or_get_user(username, password, email, address)
        
        if not success_user:
            flash(message_user, "error")
            return redirect(url_for("checkout"))

        user_id = user.id
        session["user_id"] = user_id

        # Crear la comanda utilitzant el servei
        conn = None
        try:
            conn = sqlite3.connect('techshop.db')
            cart_contents = cart_service.get_cart_contents(session)
            success, message, order_id = order_service.create_order_in_transaction(
                conn, cart_contents, user_id
            )

            if not success:
                conn.rollback()
                flash(message, "error")
                return redirect(url_for("checkout"))

            # Tot correcte: confirmar canvis i netejar el carretó
            conn.commit()
            cart_service.clear_cart(session)
            flash(f"Comanda processada correctament! ID: {order_id}", "success")
            return redirect(url_for("order_confirmation", order_id=order_id))

        except sqlite3.Error as e:
            if conn is not None:
                conn.rollback()
            flash(f"Error processant la comanda: {str(e)}", "error")
            return redirect(url_for("checkout"))
        finally:
            if conn is not None:
                conn.close()


@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    """
    Mostrar confirmació de comanda.
    
    Args:
        order_id (int): ID de la comanda
        
    Returns:
        str: Pàgina HTML de confirmació
    """
    success, message, order = order_service.get_order_by_id(order_id)
    
    if success:
        return render_template('order_confirmation.html', order=order)
    else:
        flash(message, 'error')
        return redirect(url_for('show_products'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta per iniciar sessió.
    
    Returns:
        str: Pàgina HTML de login o redirecció després de l'autenticació
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash("El nom d'usuari i la contrasenya són obligatoris", 'error')
            return render_template('login.html')
        
        # Autenticar mitjançant el servei (seguint les regles)
        success, user, message = user_service.authenticate_user(username, password)
        
        if success and user:
            session['user_id'] = user.id
            
            # Verificar si faltan datos obligatorios
            has_missing, missing_fields = user_service.check_missing_required_data(user.id)
            if has_missing:
                flash("Falten dades obligatòries al teu perfil. Si us plau, completa les teves dades.", 'warning')
                return redirect(url_for('profile', section='edit'))
            
            flash(f"Benvingut de nou, {username}!", 'success')
            # Redirigir a la pàgina d'origen o a productes
            next_page = request.args.get('next', url_for('show_products'))
            return redirect(next_page)
        else:
            flash(message, 'error')
        
        return render_template('login.html')
    
    return render_template('login.html')


@app.route('/auth/google')
def google_login():
    """
    Iniciar el procés d'autenticació amb Google.
    Redirigeix a Google per autenticar-se.
    """
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def google_callback():
    """
    Callback de Google OAuth.
    Processa la resposta de Google i crea/inicia sessió de l'usuari.
    """
    try:
        token = google.authorize_access_token()
        
        # Obtener información del usuario desde Google
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user_info = resp.json()
        
        google_email = user_info.get('email')
        google_name = user_info.get('name', '')
        google_picture = user_info.get('picture', '')
        
        if not google_email:
            flash("No s'ha pogut obtenir l'email de Google", 'error')
            return redirect(url_for('login'))
        
        # Buscar si l'usuari ja existeix per email
        conn = sqlite3.connect('techshop.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, account_type, role, dni, address FROM User WHERE email = ?", (google_email.lower(),))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Usuari existent: iniciar sessió
            user_id, username, email, account_type, role, dni, address = existing_user
            
            # Verificar que sigui usuari comú (no empresa)
            if account_type == 'company':
                flash("Els comptes d'empresa no poden utilitzar l'inici de sessió amb Google", 'error')
                conn.close()
                return redirect(url_for('login'))
            
            session['user_id'] = user_id
            
            # Verificar si faltan datos obligatorios
            has_missing, missing_fields = user_service.check_missing_required_data(user_id)
            if has_missing:
                flash("Falten dades obligatòries al teu perfil. Si us plau, completa les teves dades.", 'warning')
                conn.close()
                return redirect(url_for('profile', section='edit'))
            
            flash(f"Benvingut de nou, {username}!", 'success')
            conn.close()
            return redirect(url_for('show_products'))
        else:
            # Nou usuari: guardar dades de Google a la sessió i redirigir a completar dades
            session['google_email'] = google_email
            session['google_name'] = google_name
            session['google_picture'] = google_picture
            conn.close()
            return redirect(url_for('complete_google_profile'))
            
    except Exception as e:
        flash(f"Error en l'autenticació amb Google: {str(e)}", 'error')
        return redirect(url_for('login'))


@app.route('/complete-google-profile', methods=['GET', 'POST'])
def complete_google_profile():
    """
    Formulari per completar les dades faltants després de l'autenticació amb Google.
    """
    # Verificar que hi ha dades de Google a la sessió
    google_email = session.get('google_email')
    google_name = session.get('google_name', '')
    
    if not google_email:
        flash("Sessió de Google no trobada. Si us plau, intenta iniciar sessió amb Google de nou.", 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        address = request.form.get('address', '').strip()
        dni = request.form.get('dni', '').strip().upper()
        accept_policies = request.form.get('accept_policies') == 'on'
        
        # Validacions
        if not all([username, address]):
            flash("El nom d'usuari i l'adreça són obligatoris", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        if not accept_policies:
            flash("Has d'acceptar les polítiques de privacitat i condicions d'ús", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        # Validar nom d'usuari
        if len(username) < 4 or len(username) > 20:
            flash("El nom d'usuari ha de tenir entre 4 i 20 caràcters", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        # Validar DNI si s'ha proporcionat
        if dni and not validar_dni_nie(dni):
            flash("DNI/NIE no vàlid", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        # Crear usuari amb Google (account_type sempre 'user' per OAuth)
        success, user, message = user_service.create_user_with_google(
            username, google_email, address, dni
        )
        
        if success and user:
            # Netejar dades de Google de la sessió
            session.pop('google_email', None)
            session.pop('google_name', None)
            session.pop('google_picture', None)
            
            # Iniciar sessió
            session['user_id'] = user.id
            flash(f"Compte creat correctament amb Google! Benvingut, {username}!", 'success')
            return redirect(url_for('show_products'))
        else:
            flash(message, 'error')
    
    return render_template('complete_google_profile.html', 
                         google_email=google_email, 
                         google_name=google_name)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Ruta per recuperar contrasenya mitjançant DNI i email.
    
    Returns:
        str: Pàgina HTML de recuperació de contrasenya
    """
    if request.method == 'POST':
        dni = request.form.get('dni', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        
        if not dni:
            flash("El DNI/NIE és obligatori", 'error')
            return render_template('forgot_password.html')
        
        if not email:
            flash("L'email és obligatori", 'error')
            return render_template('forgot_password.html')
        
        # Restablir contrasenya mitjançant el servei
        success, message = user_service.reset_password_by_dni_and_email(dni, email)
        
        if success:
            flash(message, 'success')
            return render_template('forgot_password.html', success=True, message=message)
        else:
            flash(message, 'error')
    
    return render_template('forgot_password.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Ruta per registrar un nou usuari.
    
    Returns:
        str: Pàgina HTML de registre o redirecció després del registre
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        account_type = request.form.get('account_type', 'user').strip()
        dni = request.form.get('dni', '').strip()
        nif = request.form.get('nif', '').strip()
        accept_policies = request.form.get('accept_policies') == 'on'
        accept_newsletter = request.form.get('accept_newsletter') == 'on'
        
        # Validacions del servidor
        if not all([username, password, email, address]):
            flash("Tots els camps són obligatoris", 'error')
            return render_template('register.html')
        
        # Validar que s'acceptin les polítiques
        if not accept_policies:
            flash("Has d'acceptar les polítiques de privacitat i condicions d'ús per crear un compte", 'error')
            return render_template('register.html')
        
        # Validar nom d'usuari
        if len(username) < 4 or len(username) > 20:
            flash("El nom d'usuari ha de tenir entre 4 i 20 caràcters", 'error')
            return render_template('register.html')
        
        # Validar contrasenya
        if len(password) < 8:
            flash("La contrasenya ha de tenir mínim 8 caràcters", 'error')
            return render_template('register.html')
        
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            flash("La contrasenya ha de contenir almenys una lletra i un número", 'error')
            return render_template('register.html')
        
        # Validar email
        if '@' not in email or '.' not in email.split('@')[-1]:
            flash("Adreça de correu electrònic no vàlida", 'error')
            return render_template('register.html')
        
        # Crear usuari mitjançant el servei (seguint les regles)
        success, user, message = user_service.create_user(
            username, password, email, address, account_type, dni, nif
        )
        
        if success and user:
            # Iniciar sessió automàticament
            session['user_id'] = user.id
            flash(f"Compte creat correctament! Benvingut, {username}!", 'success')
            return redirect(url_for('show_products'))
        else:
            flash(message, 'error')
        
        return render_template('register.html')
    
    return render_template('register.html')


@app.route('/policies')
def show_policies():
    """
    Ruta per mostrar les polítiques de privacitat i condicions d'ús.
    
    Returns:
        str: Pàgina HTML amb les polítiques
    """
    return_to = request.args.get('return_to', 'register')
    return render_template('policies.html', return_to=return_to)


@app.route('/set_language/<lang>')
def set_language(lang):
    """
    Cambiar el idioma de la aplicación.
    
    Args:
        lang (str): Código del idioma ('cat', 'esp', 'eng')
        
    Returns:
        redirect: Redirección a la página anterior o a productos
    """
    if lang in get_available_languages():
        session['language'] = lang
    
    # Redirigir a la página anterior o a productos
    next_page = request.referrer or url_for('show_products')
    return redirect(next_page)

@app.route('/logout')
def logout():
    """
    Ruta per tancar sessió.
    
    Returns:
        str: Redirecció a la pàgina de productes
    """
    username = None
    user = get_current_user()
    if user:
        username = user.username
    
    session.clear()
    if username:
        flash(f"Sessió tancada. Fins aviat, {username}!", 'success')
    else:
        flash("Sessió tancada", 'success')
    
    return redirect(url_for('show_products'))


# ============================================================================
# RUTES D'ADMINISTRACIÓ (requereixen permisos d'admin)
# ============================================================================

@app.route('/admin')
@require_admin
def admin_dashboard():
    """
    Dashboard d'administració.
    
    Returns:
        str: Pàgina HTML del dashboard d'admin
    """
    # Obtenir estadístiques mitjançant el servei (seguint les regles)
    total_products, total_users, total_orders, total_revenue = admin_service.get_dashboard_stats()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_users=total_users,
                         total_orders=total_orders,
                         total_revenue=total_revenue)


# ========== CRUD PRODUCTES ==========

@app.route('/admin/products')
@require_admin
def admin_products():
    """
    Llista de productes per administrar.
    
    Returns:
        str: Pàgina HTML amb llista de productes
    """
    products = admin_service.get_all_products()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/create', methods=['GET', 'POST'])
@require_admin
def admin_create_product():
    """
    Crear un nou producte.
    
    Returns:
        str: Formulari de creació o redirecció després de crear
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '').strip()
        stock_str = request.form.get('stock', '').strip()
        
        try:
            price = Decimal(price_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            flash("El preu i el stock han de ser números vàlids", 'error')
            return render_template('admin/product_form.html', product=None)
        
        success, message, product_id = admin_service.create_product(name, price, stock)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_products'))
        else:
            flash(message, 'error')
            return render_template('admin/product_form.html', product=None)
    
    return render_template('admin/product_form.html', product=None)


@app.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@require_admin
def admin_edit_product(product_id):
    """
    Editar un producte existent.
    
    Args:
        product_id (int): ID del producte
        
    Returns:
        str: Formulari d'edició o redirecció després d'actualitzar
    """
    product = admin_service.get_product_by_id(product_id)
    if not product:
        flash("Producte no trobat", 'error')
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '').strip()
        stock_str = request.form.get('stock', '').strip()
        
        try:
            price = Decimal(price_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            flash("El preu i el stock han de ser números vàlids", 'error')
            return render_template('admin/product_form.html', product=product)
        
        success, message = admin_service.update_product(product_id, name, price, stock)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_products'))
        else:
            flash(message, 'error')
            return render_template('admin/product_form.html', product=product)
    
    return render_template('admin/product_form.html', product=product)


@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@require_admin
def admin_delete_product(product_id):
    """
    Eliminar un producte.
    
    Args:
        product_id (int): ID del producte
        
    Returns:
        str: Redirecció a la llista de productes
    """
    success, message = admin_service.delete_product(product_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin_products'))


# ========== CRUD USUARIS ==========

@app.route('/admin/users')
@require_admin
def admin_users():
    """
    Llista d'usuaris per administrar.
    
    Returns:
        str: Pàgina HTML amb llista d'usuaris
    """
    users = admin_service.get_all_users()
    return render_template('admin/users.html', users=users, current_user=get_current_user())


@app.route('/admin/users/create', methods=['GET', 'POST'])
@require_admin
def admin_create_user():
    """
    Crear un nou usuari amb contrasenya generada automàticament.
    
    Returns:
        str: Formulari de creació o redirecció després de crear
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        role = request.form.get('role', 'common').strip()
        account_type = request.form.get('account_type', 'user').strip()
        dni = request.form.get('dni', '').strip()
        nif = request.form.get('nif', '').strip()
        
        success, message, generated_password, user_id = admin_service.create_user(
            username, email, address, role, account_type, dni, nif
        )
        
        if success:
            flash(f"{message}. Contrasenya generada: {generated_password}", 'success')
            return redirect(url_for('admin_users'))
        else:
            flash(message, 'error')
            return render_template('admin/user_create_form.html')
    
    return render_template('admin/user_create_form.html')


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@require_admin
def admin_edit_user(user_id):
    """
    Editar un usuari existent.
    
    Args:
        user_id (int): ID de l'usuari
        
    Returns:
        str: Formulari d'edició o redirecció després d'actualitzar
    """
    user = admin_service.get_user_by_id(user_id)
    if not user:
        flash("Usuari no trobat", 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        role = request.form.get('role', 'common').strip()
        # account_type no es modifiable, mantenir el valor existent
        account_type = user.account_type if user.account_type else 'user'
        
        success, message = admin_service.update_user(user_id, username, email, address, role, account_type)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin_users'))
        else:
            flash(message, 'error')
            return render_template('admin/user_form.html', user=user)
    
    return render_template('admin/user_form.html', user=user)


@app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@require_admin
def admin_reset_user_password(user_id):
    """
    Restablir la contrasenya d'un usuari amb una nova contrasenya generada automàticament.
    
    Args:
        user_id (int): ID de l'usuari
        
    Returns:
        str: Redirecció a la llista d'usuaris
    """
    success, message, new_password = admin_service.reset_user_password(user_id)
    
    if success:
        flash(f"{message}. Nova contrasenya: {new_password}", 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@require_admin
def admin_delete_user(user_id):
    """
    Eliminar un usuari.
    
    Args:
        user_id (int): ID de l'usuari
        
    Returns:
        str: Redirecció a la llista d'usuaris
    """
    success, message = admin_service.delete_user(user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin_users'))


# ========== CRUD ORDENES ==========

@app.route('/admin/orders')
@require_admin
def admin_orders():
    """
    Llista de comandes per administrar.
    
    Returns:
        str: Pàgina HTML amb llista de comandes
    """
    orders = admin_service.get_all_orders()
    
    # Obtenir informació dels usuaris i items per cada comanda
    orders_data = []
    for order in orders:
        # Obtenir usuari mitjançant el servei (seguint les regles)
        user = user_service.get_user_by_id(order.user_id)
        username = user.username if user else "Usuari eliminat"
        email = user.email if user else ""
        
        # Obtenir items
        items = admin_service.get_order_items(order.id)
        orders_data.append((order, username, email, items))
    
    return render_template('admin/orders.html', orders_data=orders_data)


@app.route('/admin/orders/<int:order_id>/delete', methods=['POST'])
@require_admin
def admin_delete_order(order_id):
    """
    Eliminar una comanda.
    
    Args:
        order_id (int): ID de la comanda
        
    Returns:
        str: Redirecció a la llista de comandes
    """
    success, message = admin_service.delete_order(order_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin_orders'))


# ========== PERFIL D'USUARI ==========

@app.route('/profile')
def profile():
    """
    Pàgina de perfil de l'usuari amb seccions: veure dades, editar dades, historial de compres.
    
    Returns:
        str: Pàgina HTML del perfil
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per accedir al teu perfil", 'error')
        return redirect(url_for('login'))
    
    # Obtenir usuari complet amb DNI/NIF
    full_user = user_service.get_user_by_id(user.id)
    if not full_user:
        flash("Error carregant les dades del perfil", 'error')
        return redirect(url_for('show_products'))
    
    # Obtenir historial de compres
    orders_with_items = order_service.get_orders_by_user_id(user.id)
    
    section = request.args.get('section', 'view')  # view, edit, history
    
    return render_template('profile.html', 
                         user=full_user, 
                         orders_with_items=orders_with_items,
                         section=section)


@app.route('/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    """
    Editar el perfil de l'usuari.
    
    Returns:
        str: Formulari d'edició o redirecció després d'actualitzar
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per editar el teu perfil", 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        dni = request.form.get('dni', '').strip()
        nif = request.form.get('nif', '').strip()
        
        success, message = user_service.update_user_profile(
            user.id, username, email, address, dni, nif
        )
        
        if success:
            flash(message, 'success')
            # Actualizar sesión
            session['user_id'] = user.id
            return redirect(url_for('profile', section='view'))
        else:
            flash(message, 'error')
            full_user = user_service.get_user_by_id(user.id)
            return render_template('profile.html', user=full_user, section='edit', orders_with_items=[])
    
    # GET: mostrar formulario
    full_user = user_service.get_user_by_id(user.id)
    if not full_user:
        flash("Error carregant les dades del perfil", 'error')
        return redirect(url_for('profile'))
    
    orders_with_items = order_service.get_orders_by_user_id(user.id)
    return render_template('profile.html', user=full_user, section='edit', orders_with_items=orders_with_items)


@app.route('/profile/delete', methods=['POST'])
def delete_account():
    """
    Eliminar el compte de l'usuari.
    
    Returns:
        str: Redirecció després d'eliminar el compte
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per eliminar el teu compte", 'error')
        return redirect(url_for('login'))
    
    # Confirmar eliminación (podría añadirse un campo de confirmación)
    success, message = user_service.delete_user_account(user.id)
    
    if success:
        # Cerrar sesión
        session.clear()
        flash("El teu compte ha estat eliminat correctament", 'success')
        return redirect(url_for('show_products'))
    else:
        flash(message, 'error')
        return redirect(url_for('profile'))


@app.route('/profile/invoice/<int:order_id>')
def download_invoice(order_id):
    """
    Generar i descarregar la factura d'una comanda en format PDF.
    
    Args:
        order_id (int): ID de la comanda
        
    Returns:
        Response: PDF de la factura
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per descarregar la factura", 'error')
        return redirect(url_for('login'))
    
    # Verificar que la comanda pertany a l'usuari
    success, message, order = order_service.get_order_by_id(order_id)
    if not success or order.user_id != user.id:
        flash("Comanda no trobada o no tens permís per accedir-hi", 'error')
        return redirect(url_for('profile', section='history'))
    
    # Generar PDF
    from utils.invoice_generator import generate_invoice_pdf
    
    print(f"🔍 Intentando generar factura para orden {order_id}, usuario {user.id}")
    pdf_data = generate_invoice_pdf(order_id, user.id)
    if not pdf_data:
        print(f" Error generant la factura {order_id}, 'error'")
        flash("Error generant la factura. Revisa els logs del servidor per més detalls.", 'error')
        return redirect(url_for('profile', section='history'))
    
    print(f"✅ PDF generado correctamente para orden {order_id}")
    
    # Crear respuesta con el PDF
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=factura_{order_id}.pdf'
    
    return response


# ========== GESTIÓ DE PRODUCTES PER EMPRESES ==========

# Inicialitzar company_service després de crear l'app
company_service = CompanyService(static_folder=app.static_folder)

@app.route('/company/products')
@require_company
def company_products():
    """
    Llista de productes de l'empresa.
    
    Returns:
        str: Pàgina HTML amb llista de productes de l'empresa
    """
    user = get_current_user()
    products = company_service.get_company_products(user.id)
    return render_template('company/products.html', products=products)


@app.route('/company/products/create', methods=['GET', 'POST'])
@require_company
def company_create_product():
    """
    Crear un nou producte per l'empresa.
    
    Returns:
        str: Formulari de creació o redirecció després de crear
    """
    user = get_current_user()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '').strip()
        stock_str = request.form.get('stock', '').strip()
        
        try:
            price = Decimal(price_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            flash("El preu i el stock han de ser números vàlids", 'error')
            return render_template('company/product_form.html', product=None)
        
        # Crear producte
        success, message, product_id = company_service.create_product(user.id, name, price, stock)
        
        if success:
            # Guardar imatges si hi ha
            files = request.files.getlist('images')
            if files and any(f.filename for f in files):
                img_success, img_message = company_service.save_product_images(product_id, files)
                if not img_success:
                    flash(f"Producte creat però error amb imatges: {img_message}", 'warning')
                else:
                    flash(f"{message}. {img_message}", 'success')
            else:
                flash(message, 'success')
            return redirect(url_for('company_products'))
        else:
            flash(message, 'error')
            return render_template('company/product_form.html', product=None)
    
    return render_template('company/product_form.html', product=None)


@app.route('/company/products/<int:product_id>/edit', methods=['GET', 'POST'])
@require_company
def company_edit_product(product_id):
    """
    Editar un producte existent de l'empresa.
    
    Args:
        product_id (int): ID del producte
        
    Returns:
        str: Formulari d'edició o redirecció després d'actualitzar
    """
    user = get_current_user()
    product = company_service.get_product_by_id(product_id, user.id)
    
    if not product:
        flash("Producte no trobat o no tens permís per editar-lo", 'error')
        return redirect(url_for('company_products'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '').strip()
        stock_str = request.form.get('stock', '').strip()
        
        try:
            price = Decimal(price_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            flash("El preu i el stock han de ser números vàlids", 'error')
            return render_template('company/product_form.html', product=product)
        
        success, message = company_service.update_product(product_id, user.id, name, price, stock)
        
        if success:
            # Guardar noves imatges si hi ha
            files = request.files.getlist('images')
            if files and any(f.filename for f in files):
                img_success, img_message = company_service.save_product_images(product_id, files)
                if not img_success:
                    flash(f"{message}. Error amb imatges: {img_message}", 'warning')
                else:
                    flash(f"{message}. {img_message}", 'success')
            else:
                flash(message, 'success')
            return redirect(url_for('company_products'))
        else:
            flash(message, 'error')
            return render_template('company/product_form.html', product=product)
    
    return render_template('company/product_form.html', product=product)


@app.route('/company/products/<int:product_id>/delete', methods=['POST'])
@require_company
def company_delete_product(product_id):
    """
    Eliminar un producte de l'empresa (només si no té vendes).
    
    Args:
        product_id (int): ID del producte
        
    Returns:
        str: Redirecció a la llista de productes
    """
    user = get_current_user()
    success, message = company_service.delete_product(product_id, user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('company_products'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)
