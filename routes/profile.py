"""
Rutas de perfil de usuario de TechShop
Ver datos, editar datos, historial de compras, descargar facturas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response

from services.user_service import UserService
from services.order_service import OrderService
from utils.invoice_generator import generate_invoice_pdf
from routes.helpers import get_current_user

# Crear blueprint
profile_bp = Blueprint('profile', __name__)

# Inicializar servicios
user_service = UserService()
order_service = OrderService()


@profile_bp.route('/profile')
def profile():
    """
    Página de perfil del usuario con secciones: ver datos, editar datos, historial de compras.
    
    Returns:
        str: Página HTML del perfil
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per accedir al teu perfil", 'error')
        return redirect(url_for('auth.login'))
    
    # Obtener usuario completo con DNI/NIF
    full_user = user_service.get_user_by_id(user.id)
    if not full_user:
        flash("Error carregant les dades del perfil", 'error')
        return redirect(url_for('main.show_products'))
    
    # Obtener historial de compras
    orders_with_items = order_service.get_orders_by_user_id(user.id)
    
    section = request.args.get('section', 'view')  # view, edit, history
    
    return render_template('profile.html', 
                         user=full_user, 
                         orders_with_items=orders_with_items,
                         section=section)


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    """
    Editar el perfil del usuario.
    
    Returns:
        str: Formulario de edición o redirección después de actualizar
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per editar el teu perfil", 'error')
        return redirect(url_for('auth.login'))
    
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
            return redirect(url_for('profile.profile', section='view'))
        else:
            flash(message, 'error')
            full_user = user_service.get_user_by_id(user.id)
            return render_template('profile.html', user=full_user, section='edit', orders_with_items=[])
    
    # GET: mostrar formulario
    full_user = user_service.get_user_by_id(user.id)
    if not full_user:
        flash("Error carregant les dades del perfil", 'error')
        return redirect(url_for('profile.profile'))
    
    orders_with_items = order_service.get_orders_by_user_id(user.id)
    return render_template('profile.html', user=full_user, section='edit', orders_with_items=orders_with_items)


@profile_bp.route('/profile/delete', methods=['POST'])
def delete_account():
    """
    Eliminar la cuenta del usuario.
    
    Returns:
        str: Redirección después de eliminar la cuenta
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per eliminar el teu compte", 'error')
        return redirect(url_for('auth.login'))
    
    # Confirmar eliminación (podría añadirse un campo de confirmación)
    success, message = user_service.delete_user_account(user.id)
    
    if success:
        # Cerrar sesión
        session.clear()
        flash("El teu compte ha estat eliminat correctament", 'success')
        return redirect(url_for('main.show_products'))
    else:
        flash(message, 'error')
        return redirect(url_for('profile.profile'))


@profile_bp.route('/profile/invoice/<int:order_id>')
def download_invoice(order_id):
    """
    Generar y descargar la factura de una comanda en formato PDF.
    
    Args:
        order_id (int): ID de la comanda
        
    Returns:
        Response: PDF de la factura
    """
    user = get_current_user()
    if not user:
        flash("Has d'iniciar sessió per descarregar la factura", 'error')
        return redirect(url_for('auth.login'))
    
    # Verificar que la comanda pertenece al usuario
    success, message, order = order_service.get_order_by_id(order_id)
    if not success or order.user_id != user.id:
        flash("Comanda no trobada o no tens permís per accedir-hi", 'error')
        return redirect(url_for('profile.profile', section='history'))
    
    # Generar PDF
    print(f"🔍 Intentando generar factura para orden {order_id}, usuario {user.id}")
    pdf_data = generate_invoice_pdf(order_id, user.id)
    if not pdf_data:
        print(f" Error generant la factura {order_id}, 'error'")
        flash("Error generant la factura. Revisa els logs del servidor per més detalls.", 'error')
        return redirect(url_for('profile.profile', section='history'))
    
    print(f"✅ PDF generado correctamente para orden {order_id}")
    
    # Crear respuesta con el PDF
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=factura_{order_id}.pdf'
    
    return response

