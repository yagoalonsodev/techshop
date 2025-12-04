"""
Rutas de la aplicación TechShop
Organizadas por funcionalidad siguiendo buenas prácticas
"""

from flask import Blueprint

# Importar todos los blueprints
from routes.main import main_bp
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.utils import utils_bp

# Lista de todos los blueprints para registrar
all_blueprints = [
    main_bp,
    auth_bp,
    profile_bp,
    admin_bp,
    company_bp,
    utils_bp
]


def register_routes(app):
    """
    Registrar todas las rutas en la aplicación Flask.
    
    Args:
        app: Instancia de Flask
    """
    for bp in all_blueprints:
        app.register_blueprint(bp)
