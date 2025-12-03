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
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash

from models import Product, User
from services.cart_service import CartService
from services.order_service import OrderService
from services.recommendation_service import RecommendationService


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


def get_current_user():
    """
    Obtenir l'usuari actual des de la sessió.
    
    Returns:
        User o None: L'usuari actual si està autenticat, None altrament
    """
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    try:
        with sqlite3.connect('techshop.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email, address FROM User WHERE id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2] if len(result) > 2 else "",
                    password_hash="",  # No retornem el hash
                )
    except sqlite3.Error:
        pass
    
    return None


@app.context_processor
def inject_csrf_token():
    """Permet usar {{ csrf_token() }} als formularis HTML sense WTForms."""
    user = get_current_user()
    return dict(csrf_token=generate_csrf, current_user=user)

# Inicialitzar serveis
cart_service = CartService()
order_service = OrderService()
recommendation_service = RecommendationService()

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

    try:
        with sqlite3.connect('techshop.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, stock FROM Product")
            products_data = cursor.fetchall()
            
            products = []
            product_images: Dict[int, List[str]] = {}
            for row in products_data:
                product = Product(
                    id=row[0],
                    name=row[1],
                    price=Decimal(str(row[2])),
                    stock=row[3]
                )
                products.append(product)
                product_images[product.id] = _get_product_images(product.id)
            
            return render_template(
                'products.html',
                products=products,
                recommendations=recommendations,
                user_recommendations=user_recommendations,
                product_images=product_images
            )
            
    except sqlite3.Error as e:
        flash(f"Error carregant productes: {str(e)}", 'error')
        return render_template(
            'products.html',
            products=[],
            recommendations=recommendations,
            user_recommendations=user_recommendations,
            product_images={}
        )


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Afegir producte al carretó des de la interfície web.
    
    Returns:
        str: Redirecció a la pàgina de productes
    """
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
    cart_contents = cart_service.get_cart_contents(session)
    cart_total = cart_service.get_cart_total(session)
    
    # Obtenir informació dels productes del carretó
    cart_products = []
    try:
        with sqlite3.connect('techshop.db') as conn:
            cursor = conn.cursor()
            for product_id, quantity in cart_contents.items():
                cursor.execute(
                    "SELECT id, name, price FROM Product WHERE id = ?",
                    (product_id,)
                )
                result = cursor.fetchone()
                if result:
                    product = Product(
                        id=result[0],
                        name=result[1],
                        price=Decimal(str(result[2]))
                    )
                    cart_products.append(
                        (product, quantity, _get_product_images(product.id))
                    )
                    
    except sqlite3.Error as e:
        flash(f"Error carregant productes del carretó: {str(e)}", 'error')
        cart_products = []
    
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
        
        # Actualitzar adreça de l'usuari si cal
        try:
            with sqlite3.connect('techshop.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE User SET address = ? WHERE id = ?",
                    (address, user_id)
                )
                conn.commit()
        except sqlite3.Error:
            pass  # No és crític si falla l'actualització
        
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
        
        # Autenticació / registre d'usuari i creació de comanda en una única transacció
        conn = None
        try:
            conn = sqlite3.connect('techshop.db')
            cursor = conn.cursor()

            # Comprovar si l'usuari ja existeix
            cursor.execute(
                "SELECT id, password_hash FROM User WHERE username = ?",
                (username,),
            )
            existing_user = cursor.fetchone()

            if existing_user:
                user_id, stored_hash = existing_user

                # Verificar la contrasenya de l'usuari existent
                if not check_password_hash(stored_hash, password):
                    conn.rollback()
                    flash("Contrasenya incorrecta per a l'usuari indicat", "error")
                    return redirect(url_for("checkout"))

                # Opcional: actualitzar dades de contacte
                cursor.execute(
                    "UPDATE User SET email = ?, address = ? WHERE id = ?",
                    (email, address, user_id),
                )
            else:
                # Registrar un nou usuari amb contrasenya hashejada
                password_hash = generate_password_hash(password, method="pbkdf2:sha256")
                cursor.execute(
                    "INSERT INTO User (username, password_hash, email, address, created_at) "
                    "VALUES (?, ?, ?, ?, datetime('now'))",
                    (username, password_hash, email, address),
                )
                user_id = cursor.lastrowid

            # Desa l'usuari a la sessió un cop validat / creat
            session["user_id"] = user_id

            # Crear la comanda utilitzant el servei, dins de la mateixa transacció
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
        
        try:
            with sqlite3.connect('techshop.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, password_hash FROM User WHERE username = ?",
                    (username,)
                )
                result = cursor.fetchone()
                
                if result:
                    user_id, stored_hash = result
                    if check_password_hash(stored_hash, password):
                        session['user_id'] = user_id
                        flash(f"Benvingut de nou, {username}!", 'success')
                        # Redirigir a la pàgina d'origen o a productes
                        next_page = request.args.get('next', url_for('show_products'))
                        return redirect(next_page)
                    else:
                        flash("Contrasenya incorrecta", 'error')
                else:
                    flash("Nom d'usuari no trobat", 'error')
        except sqlite3.Error as e:
            flash(f"Error d'autenticació: {str(e)}", 'error')
        
        return render_template('login.html')
    
    return render_template('login.html')


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
        
        # Validacions del servidor
        if not all([username, password, email]):
            flash("Tots els camps són obligatoris", 'error')
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
        
        try:
            with sqlite3.connect('techshop.db') as conn:
                cursor = conn.cursor()
                
                # Comprovar si l'usuari ja existeix
                cursor.execute("SELECT id FROM User WHERE username = ?", (username,))
                if cursor.fetchone():
                    flash("Aquest nom d'usuari ja està en ús", 'error')
                    return render_template('register.html')
                
                # Registrar nou usuari
                password_hash = generate_password_hash(password, method="pbkdf2:sha256")
                cursor.execute(
                    "INSERT INTO User (username, password_hash, email, created_at) "
                    "VALUES (?, ?, ?, datetime('now'))",
                    (username, password_hash, email)
                )
                user_id = cursor.lastrowid
                conn.commit()
                
                # Iniciar sessió automàticament
                session['user_id'] = user_id
                flash(f"Compte creat correctament! Benvingut, {username}!", 'success')
                return redirect(url_for('show_products'))
                
        except sqlite3.Error as e:
            flash(f"Error creant el compte: {str(e)}", 'error')
        
        return render_template('register.html')
    
    return render_template('register.html')


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


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)
