"""
Rutas de utilidades de TechShop
Cambio de idioma, políticas de privacidad
"""

from flask import Blueprint, render_template, request, redirect, url_for, session

from utils.translations import get_available_languages

# Crear blueprint
utils_bp = Blueprint('utils', __name__)


@utils_bp.route('/policies')
def show_policies():
    """
    Ruta para mostrar las políticas de privacidad y condiciones de uso.
    
    Returns:
        str: Página HTML con las políticas
    """
    return_to = request.args.get('return_to', 'register')
    return render_template('policies.html', return_to=return_to)


@utils_bp.route('/set_language/<lang>')
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
    next_page = request.referrer or url_for('main.show_products')
    return redirect(next_page)

