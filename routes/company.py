"""
Rutas de gestión de productos para empresas de TechShop
CRUD de productos para usuarios tipo empresa
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from decimal import Decimal

from services.company_service import CompanyService
from routes.helpers import get_current_user, require_company

# Crear blueprint
company_bp = Blueprint('company', __name__)


@company_bp.route('/company/products')
@require_company
def company_products():
    """
    Lista de productos de la empresa.
    
    Returns:
        str: Página HTML con lista de productos de la empresa
    """
    user = get_current_user()
    # Inicializar company_service con static_folder
    from flask import current_app
    company_service = CompanyService(static_folder=current_app.static_folder)
    products = company_service.get_company_products(user.id)
    return render_template('company/products.html', products=products)


@company_bp.route('/company/products/create', methods=['GET', 'POST'])
@require_company
def company_create_product():
    """
    Crear un nuevo producto para la empresa.
    
    Returns:
        str: Formulario de creación o redirección después de crear
    """
    user = get_current_user()
    from flask import current_app
    company_service = CompanyService(static_folder=current_app.static_folder)
    
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
        
        # Crear producto
        success, message, product_id = company_service.create_product(user.id, name, price, stock)
        
        if success:
            # Guardar imágenes si hay
            files = request.files.getlist('images')
            if files and any(f.filename for f in files):
                img_success, img_message = company_service.save_product_images(product_id, files)
                if not img_success:
                    flash(f"Producte creat però error amb imatges: {img_message}", 'warning')
                else:
                    flash(f"{message}. {img_message}", 'success')
            else:
                flash(message, 'success')
            return redirect(url_for('company.company_products'))
        else:
            flash(message, 'error')
            return render_template('company/product_form.html', product=None)
    
    return render_template('company/product_form.html', product=None)


@company_bp.route('/company/products/<int:product_id>/edit', methods=['GET', 'POST'])
@require_company
def company_edit_product(product_id):
    """
    Editar un producto existente de la empresa.
    
    Args:
        product_id (int): ID del producto
        
    Returns:
        str: Formulario de edición o redirección después de actualizar
    """
    user = get_current_user()
    from flask import current_app
    company_service = CompanyService(static_folder=current_app.static_folder)
    product = company_service.get_product_by_id(product_id, user.id)
    
    if not product:
        flash("Producte no trobat o no tens permís per editar-lo", 'error')
        return redirect(url_for('company.company_products'))
    
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
            # Guardar nuevas imágenes si hay
            files = request.files.getlist('images')
            if files and any(f.filename for f in files):
                img_success, img_message = company_service.save_product_images(product_id, files)
                if not img_success:
                    flash(f"{message}. Error amb imatges: {img_message}", 'warning')
                else:
                    flash(f"{message}. {img_message}", 'success')
            else:
                flash(message, 'success')
            return redirect(url_for('company.company_products'))
        else:
            flash(message, 'error')
            return render_template('company/product_form.html', product=product)
    
    return render_template('company/product_form.html', product=product)


@company_bp.route('/company/products/<int:product_id>/delete', methods=['POST'])
@require_company
def company_delete_product(product_id):
    """
    Eliminar un producto de la empresa (solo si no tiene ventas).
    
    Args:
        product_id (int): ID del producto
        
    Returns:
        str: Redirección a la lista de productos
    """
    user = get_current_user()
    from flask import current_app
    company_service = CompanyService(static_folder=current_app.static_folder)
    success, message = company_service.delete_product(product_id, user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('company.company_products'))

