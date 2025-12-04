"""
Aplicación principal TechShop
Aplicación web para gestionar un carrito de compras para TechShop
"""

import os
from pathlib import Path

# Intentar cargar dotenv, pero no fallar si no está instalado (para tests)
try:
    from dotenv import load_dotenv
    # Cargar variables de entorno desde el archivo .env si existe
    load_dotenv()
except ImportError:
    # Si dotenv no está instalado, intentar cargar manualmente el .env
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

from flask import Flask, session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from authlib.integrations.flask_client import OAuth

from utils.translations import get_translation, get_available_languages, get_language_name
from routes import register_routes
from routes.helpers import get_current_user

app = Flask(__name__)

# SECRET_KEY únicamente desde variable de entorno (.env)
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "SECRET_KEY no configurada. Afegeix SECRET_KEY al fitxer .env a la "
        "arrel del projecte, per exemple:\n\nSECRET_KEY=una-clau-molt-secreta"
    )
app.config["SECRET_KEY"] = secret_key

# Protección CSRF para todas las peticiones POST
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

# Almacenar la instancia de OAuth en app.config para acceso desde blueprints
app.config['OAUTH'] = oauth


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


@app.context_processor
def inject_csrf_token():
    """Permite usar {{ csrf_token() }} en los formularios HTML sin WTForms."""
    user = get_current_user()
    return dict(csrf_token=generate_csrf, current_user=user)


# Registrar todas las rutas desde blueprints
register_routes(app)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)
