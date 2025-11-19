"""
Aplicació principal TechShop
Aplicació web per gestionar un carretó de compres per a TechShop
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from decimal import Decimal
from pathlib import Path
from typing import Dict, List
from werkzeug.security import generate_password_hash, check_password_hash
from models import Product, User
from services.cart_service import CartService
from services.order_service import OrderService
from services.recommendation_service import RecommendationService


app = Flask(__name__)
app.secret_key = 'techshop_secret_key'  # En producció, usar una clau segura

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
    
    success, message = cart_service.add_to_cart(product_id, quantity)
    
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
    
    success, message = cart_service.remove_from_cart(product_id)
    
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
    cart_contents = cart_service.get_cart_contents()
    cart_total = cart_service.get_cart_total()
    
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
    
    Returns:
        str: Redirecció a la pàgina de confirmació
    """
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    
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
    
    # Crear usuari amb contrasenya hashejada
    try:
        with sqlite3.connect('techshop.db') as conn:
            cursor = conn.cursor()
            
            # Generar hash segur de la contrasenya
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            cursor.execute(
                "INSERT INTO User (username, password_hash, email, address, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
                (username, password_hash, email, address)
            )
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            conn.commit()
            
            # Crear la comanda
            cart_contents = cart_service.get_cart_contents()
            success, message, order_id = order_service.create_order(cart_contents, user_id)
            
            if success:
                cart_service.clear_cart()
                flash(f"Comanda processada correctament! ID: {order_id}", 'success')
                return redirect(url_for('order_confirmation', order_id=order_id))
            else:
                flash(message, 'error')
                return redirect(url_for('checkout'))
                
    except sqlite3.Error as e:
        flash(f"Error processant la comanda: {str(e)}", 'error')
        return redirect(url_for('checkout'))


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


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)
