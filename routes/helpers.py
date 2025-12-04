"""
Funciones auxiliares y decoradores para las rutas
"""

from functools import wraps
from flask import session, flash, redirect, url_for
from services.user_service import UserService

# Inicializar servicio
user_service = UserService()


def get_current_user():
    """
    Obtener el usuario actual desde la sesión.
    
    Returns:
        User o None: El usuario actual si está autenticado, None en caso contrario
    """
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    return user_service.get_user_by_id(user_id)


def require_admin(f):
    """
    Decorador para proteger rutas que requieren permisos de administrador.
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada que verifica permisos de admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin():
            flash("Accés denegat. Es requereixen permisos d'administrador.", 'error')
            return redirect(url_for('main.show_products'))
        return f(*args, **kwargs)
    return decorated_function


def require_company(f):
    """
    Decorador para proteger rutas que requieren ser una empresa.
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada que verifica que el usuario es una empresa
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Has d'iniciar sessió per accedir a aquesta pàgina.", 'error')
            return redirect(url_for('auth.login'))
        if user.account_type != 'company':
            flash("Accés denegat. Aquesta funcionalitat és només per empreses.", 'error')
            return redirect(url_for('main.show_products'))
        return f(*args, **kwargs)
    return decorated_function


def _get_product_images(product_id, limit=4):
    """
    Construir las rutas de imagen para un producto determinado.
    
    Args:
        product_id (int): Identificador del producto.
        limit (int): Número máximo de imágenes a retornar.
        
    Returns:
        List[str]: Lista de URLs relativas a las imágenes del producto.
    """
    from flask import url_for, current_app
    from pathlib import Path
    
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    
    images_dir = Path(current_app.static_folder) / 'img' / 'products' / str(product_id)
    if not images_dir.exists():
        return []

    image_urls = []
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

