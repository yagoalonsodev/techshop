"""
Rutas de administración de TechShop
Panel de administración, CRUD de productos, usuarios y órdenes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from decimal import Decimal

from services.admin_service import AdminService
from services.user_service import UserService
from routes.helpers import get_current_user, require_admin

# Crear blueprint
admin_bp = Blueprint('admin', __name__)

# Inicializar servicios
admin_service = AdminService()
user_service = UserService()


@admin_bp.route('/admin')
@require_admin
def admin_dashboard():
    """
    Dashboard de administración.
    
    Returns:
        str: Página HTML del dashboard de admin
    """
    # Obtener estadísticas mediante el servicio (siguiendo las reglas)
    total_products, total_users, total_orders, total_revenue = admin_service.get_dashboard_stats()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_users=total_users,
                         total_orders=total_orders,
                         total_revenue=total_revenue)


# ========== CRUD PRODUCTOS ==========

@admin_bp.route('/admin/products')
@require_admin
def admin_products():
    """
    Lista de productos para administrar.
    
    Returns:
        str: Página HTML con lista de productos
    """
    products = admin_service.get_all_products()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/admin/products/create', methods=['GET', 'POST'])
@require_admin
def admin_create_product():
    """
    Crear un nuevo producto.
    
    Returns:
        str: Formulario de creación o redirección después de crear
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
            return redirect(url_for('admin.admin_products'))
        else:
            flash(message, 'error')
            return render_template('admin/product_form.html', product=None)
    
    return render_template('admin/product_form.html', product=None)


@admin_bp.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@require_admin
def admin_edit_product(product_id):
    """
    Editar un producto existente.
    
    Args:
        product_id (int): ID del producto
        
    Returns:
        str: Formulario de edición o redirección después de actualizar
    """
    product = admin_service.get_product_by_id(product_id)
    if not product:
        flash("Producte no trobat", 'error')
        return redirect(url_for('admin.admin_products'))
    
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
            return redirect(url_for('admin.admin_products'))
        else:
            flash(message, 'error')
            return render_template('admin/product_form.html', product=product)
    
    return render_template('admin/product_form.html', product=product)


@admin_bp.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@require_admin
def admin_delete_product(product_id):
    """
    Eliminar un producto.
    
    Args:
        product_id (int): ID del producto
        
    Returns:
        str: Redirección a la lista de productos
    """
    success, message = admin_service.delete_product(product_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_products'))


# ========== CRUD USUARIOS ==========

@admin_bp.route('/admin/users')
@require_admin
def admin_users():
    """
    Lista de usuarios para administrar.
    
    Returns:
        str: Página HTML con lista de usuarios
    """
    users = admin_service.get_all_users()
    return render_template('admin/users.html', users=users, current_user=get_current_user())


@admin_bp.route('/admin/users/create', methods=['GET', 'POST'])
@require_admin
def admin_create_user():
    """
    Crear un nuevo usuario con contraseña generada automáticamente.
    
    Returns:
        str: Formulario de creación o redirección después de crear
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
            return redirect(url_for('admin.admin_users'))
        else:
            flash(message, 'error')
            return render_template('admin/user_create_form.html')
    
    return render_template('admin/user_create_form.html')


@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@require_admin
def admin_edit_user(user_id):
    """
    Editar un usuario existente.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        str: Formulario de edición o redirección después de actualizar
    """
    user = admin_service.get_user_by_id(user_id)
    if not user:
        flash("Usuari no trobat", 'error')
        return redirect(url_for('admin.admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        role = request.form.get('role', 'common').strip()
        # account_type no es modificable, mantener el valor existente
        account_type = user.account_type if user.account_type else 'user'
        
        success, message = admin_service.update_user(user_id, username, email, address, role, account_type)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.admin_users'))
        else:
            flash(message, 'error')
            return render_template('admin/user_form.html', user=user)
    
    return render_template('admin/user_form.html', user=user)


@admin_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@require_admin
def admin_reset_user_password(user_id):
    """
    Restablecer la contraseña de un usuario con una nueva contraseña generada automáticamente.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        str: Redirección a la lista de usuarios
    """
    success, message, new_password = admin_service.reset_user_password(user_id)
    
    if success:
        flash(f"{message}. Nova contrasenya: {new_password}", 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@require_admin
def admin_delete_user(user_id):
    """
    Eliminar un usuario.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        str: Redirección a la lista de usuarios
    """
    success, message = admin_service.delete_user(user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_users'))


# ========== CRUD ÓRDENES ==========

@admin_bp.route('/admin/orders')
@require_admin
def admin_orders():
    """
    Lista de comandas para administrar.
    
    Returns:
        str: Página HTML con lista de comandas
    """
    orders = admin_service.get_all_orders()
    
    # Obtener información de los usuarios e items por cada comanda
    orders_data = []
    for order in orders:
        # Obtener usuario mediante el servicio (siguiendo las reglas)
        user = user_service.get_user_by_id(order.user_id)
        username = user.username if user else "Usuari eliminat"
        email = user.email if user else ""
        
        # Obtener items
        items = admin_service.get_order_items(order.id)
        orders_data.append((order, username, email, items))
    
    return render_template('admin/orders.html', orders_data=orders_data)


@admin_bp.route('/admin/orders/<int:order_id>/delete', methods=['POST'])
@require_admin
def admin_delete_order(order_id):
    """
    Eliminar una comanda.
    
    Args:
        order_id (int): ID de la comanda
        
    Returns:
        str: Redirección a la lista de comandas
    """
    success, message = admin_service.delete_order(order_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.admin_orders'))

