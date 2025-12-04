"""
Rutas principales de TechShop
Productos, carrito, checkout y confirmación de pedidos
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from pathlib import Path
from typing import Dict, List

from services.cart_service import CartService
from services.order_service import OrderService
from services.recommendation_service import RecommendationService
from services.product_service import ProductService
from services.user_service import UserService
from utils.invoice_generator import generate_invoice_pdf
from utils.email_service import send_order_confirmation_email
from routes.helpers import get_current_user, _get_product_images
import sqlite3

# Crear blueprint
main_bp = Blueprint('main', __name__)

# Inicializar servicios
cart_service = CartService()
order_service = OrderService()
recommendation_service = RecommendationService()
product_service = ProductService()
user_service = UserService()


@main_bp.route('/')
def show_products():
    """
    Ruta que obtiene todos los productos de la base de datos y los pasa a la capa de presentación.
    
    Returns:
        str: Página HTML con la lista de productos
    """
    recommendations = recommendation_service.get_top_selling_products(limit=3)
    user_recommendations = []
    user_id = session.get('user_id')
    if user_id:
        user_recommendations = recommendation_service.get_top_products_for_user(user_id=user_id, limit=3)

    # Obtener productos mediante el servicio (siguiendo las reglas)
    products = product_service.get_all_products()
    
    # Obtener imágenes para cada producto
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


@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Ruta que muestra el detalle de un producto específico.
    
    Args:
        product_id (int): ID del producto
        
    Returns:
        str: Página HTML con el detalle del producto
    """
    # Obtener producto mediante el servicio
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        flash("Producte no trobat", 'error')
        return redirect(url_for('main.show_products'))
    
    # Obtener imágenes del producto
    product_images = _get_product_images(product_id)
    
    return render_template(
        'product_detail.html',
        product=product,
        product_images=product_images
    )


@main_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Añadir producto al carrito desde la interfaz web.
    
    Returns:
        str: Redirección a la página de productos
    """
    # Verificar que no sea una empresa (las empresas no pueden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('main.show_products'))
    
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not product_id or not quantity:
        flash("Dades invàlides", 'error')
        return redirect(url_for('main.show_products'))
    
    success, message = cart_service.add_to_cart(product_id, quantity, session)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('main.show_products'))


@main_bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """
    Eliminar producto del carrito desde la interfaz web.
    
    Returns:
        str: Redirección a la página de checkout
    """
    # Verificar que no sea una empresa (las empresas no pueden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('main.show_products'))
    
    product_id = request.form.get('product_id', type=int)
    
    if not product_id:
        flash("Producte no especificat", 'error')
        return redirect(url_for('main.checkout'))
    
    success, message = cart_service.remove_from_cart(product_id, session)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('main.checkout'))


@main_bp.route('/checkout')
def checkout():
    """
    Ruta que muestra el resumen del carrito y un formulario para introducir datos del usuario.
    
    Returns:
        str: Página HTML del checkout
    """
    # Verificar que no sea una empresa (las empresas no pueden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('main.show_products'))
    
    cart_contents = cart_service.get_cart_contents(session)
    cart_total = cart_service.get_cart_total(session)
    
    # Obtener información de los productos del carrito mediante el servicio
    products_with_quantities = product_service.get_products_by_ids(cart_contents)
    
    # Construir lista con imágenes
    cart_products = []
    for product, quantity in products_with_quantities:
        cart_products.append(
            (product, quantity, _get_product_images(product.id))
        )
    
    return render_template('checkout.html', 
                         cart_products=cart_products, 
                         cart_total=cart_total)


@main_bp.route('/process_order', methods=['POST'])
def process_order():
    """
    Procesar la comanda cuando el usuario confirma la compra.
    Maneja dos flujos: usuario autenticado (solo dirección) o invitado (todos los campos).
    
    Returns:
        str: Redirección a la página de confirmación
    """
    # Verificar que no sea una empresa (las empresas no pueden comprar)
    user = get_current_user()
    if user and user.account_type == 'company':
        flash("Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.", 'error')
        return redirect(url_for('main.show_products'))
    
    checkout_type = request.form.get('checkout_type', 'guest')
    address = request.form.get('address', '').strip()
    
    # Si el usuario está autenticado, solo necesitamos la dirección
    if checkout_type == 'authenticated':
        user_id = session.get('user_id')
        if not user_id:
            flash("Sessió no vàlida. Si us plau, inicia sessió de nou.", 'error')
            return redirect(url_for('auth.login'))
        
        # Validar dirección
        if not address or len(address) < 10:
            flash("L'adreça d'enviament ha de tenir almenys 10 caràcters", 'error')
            return redirect(url_for('main.checkout'))
        
        # Actualizar dirección del usuario si es necesario (mediante el servicio)
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
                return redirect(url_for("main.checkout"))
            
            conn.commit()
            cart_service.clear_cart(session)
            
            # Enviar email de confirmación con factura (usando servicios, siguiendo arquitectura de 3 capas)
            user_obj = user_service.get_user_by_id(user_id)
            if user_obj and user_obj.email:
                # Obtener datos de la orden usando el servicio (no acceso directo a BD)
                success_order, message_order, order = order_service.get_order_by_id(order_id)
                if success_order and order:
                    # Obtener items de la orden usando el servicio
                    success_items, message_items, order_items = order_service.get_order_items_for_email(order_id)
                    if success_items:
                        # Generar factura PDF
                        from utils.invoice_generator import generate_invoice_pdf
                        invoice_pdf = generate_invoice_pdf(order_id, user_id)
                        # Enviar email con datos ya procesados por servicios
                        from utils.email_service import send_order_confirmation_email
                        email_success, email_message = send_order_confirmation_email(
                            user_obj.email, 
                            user_obj.username, 
                            order_id,
                            float(order.total),
                            order.created_at.strftime('%d/%m/%Y %H:%M') if order.created_at else 'N/A',
                            order_items,
                            invoice_pdf
                        )
                        if not email_success:
                            print(f"⚠️ No se pudo enviar el email de confirmación: {email_message}")
            
            flash(f"Comanda processada correctament! ID: {order_id}", "success")
            return redirect(url_for("main.order_confirmation", order_id=order_id))
            
        except sqlite3.Error as e:
            if conn is not None:
                conn.rollback()
            flash(f"Error processant la comanda: {str(e)}", "error")
            return redirect(url_for("main.checkout"))
        finally:
            if conn is not None:
                conn.close()
    
    # Flujo de invitado: pedir todos los campos
    else:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validaciones del servidor
        if not all([username, password, email, address]):
            flash("Tots els camps són obligatoris", 'error')
            return redirect(url_for('main.checkout'))
        
        # Validar nombre de usuario
        if len(username) < 4 or len(username) > 20:
            flash("El nom d'usuari ha de tenir entre 4 i 20 caràcters", 'error')
            return redirect(url_for('main.checkout'))
        
        # Validar contraseña (mínimo 8 caracteres, al menos una letra y un número)
        if len(password) < 8:
            flash("La contrasenya ha de tenir mínim 8 caràcters", 'error')
            return redirect(url_for('main.checkout'))
        
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            flash("La contrasenya ha de contenir almenys una lletra i un número", 'error')
            return redirect(url_for('main.checkout'))
        
        # Validar email: debe contener un @ y un . después del arroba
        if '@' not in email or '.' not in email.split('@')[-1]:
            flash("Adreça de correu electrònic no vàlida", 'error')
            return redirect(url_for('main.checkout'))
        
        # Validar dirección
        if len(address) < 10:
            flash("L'adreça d'enviament ha de tenir almenys 10 caràcters", 'error')
            return redirect(url_for('main.checkout'))
        
        # Crear o obtener usuario mediante el servicio (siguiendo las reglas)
        success_user, user, message_user = user_service.create_or_get_user(username, password, email, address)
        
        if not success_user:
            flash(message_user, "error")
            return redirect(url_for("main.checkout"))

        user_id = user.id
        session["user_id"] = user_id

        # Crear la comanda utilizando el servicio
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
                return redirect(url_for("main.checkout"))

            # Todo correcto: confirmar cambios y limpiar el carrito
            conn.commit()
            cart_service.clear_cart(session)
            
            # Enviar email de confirmación con factura (usando servicios, siguiendo arquitectura de 3 capas)
            if user and user.email:
                # Obtener datos de la orden usando el servicio (no acceso directo a BD)
                success_order, message_order, order = order_service.get_order_by_id(order_id)
                if success_order and order:
                    # Obtener items de la orden usando el servicio
                    success_items, message_items, order_items = order_service.get_order_items_for_email(order_id)
                    if success_items:
                        # Generar factura PDF
                        from utils.invoice_generator import generate_invoice_pdf
                        invoice_pdf = generate_invoice_pdf(order_id, user_id)
                        # Enviar email con datos ya procesados por servicios
                        from utils.email_service import send_order_confirmation_email
                        email_success, email_message = send_order_confirmation_email(
                            user.email, 
                            user.username, 
                            order_id,
                            float(order.total),
                            order.created_at.strftime('%d/%m/%Y %H:%M') if order.created_at else 'N/A',
                            order_items,
                            invoice_pdf
                        )
                        if not email_success:
                            print(f"⚠️ No se pudo enviar el email de confirmación: {email_message}")
            
            flash(f"Comanda processada correctament! ID: {order_id}", "success")
            return redirect(url_for("main.order_confirmation", order_id=order_id))

        except sqlite3.Error as e:
            if conn is not None:
                conn.rollback()
            flash(f"Error processant la comanda: {str(e)}", "error")
            return redirect(url_for("main.checkout"))
        finally:
            if conn is not None:
                conn.close()


@main_bp.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    """
    Mostrar confirmación de comanda.
    
    Args:
        order_id (int): ID de la comanda
        
    Returns:
        str: Página HTML de confirmación
    """
    success, message, order = order_service.get_order_by_id(order_id)
    
    if success:
        return render_template('order_confirmation.html', order=order)
    else:
        flash(message, 'error')
        return redirect(url_for('main.show_products'))

