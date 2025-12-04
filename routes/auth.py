"""
Rutas de autenticación de TechShop
Login, registro, logout, OAuth de Google, recuperación de contraseña
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from services.user_service import UserService
from utils.validators import validar_dni_nie
from routes.helpers import get_current_user

# Crear blueprint
auth_bp = Blueprint('auth', __name__)

# Inicializar servicios
user_service = UserService()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta para iniciar sesión.
    
    Returns:
        str: Página HTML de login o redirección después de la autenticación
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash("El nom d'usuari i la contrasenya són obligatoris", 'error')
            return render_template('login.html')
        
        # Autenticar mediante el servicio (siguiendo las reglas)
        success, user, message = user_service.authenticate_user(username, password)
        
        if success and user:
            session['user_id'] = user.id
            
            # Verificar si faltan datos obligatorios
            has_missing, missing_fields = user_service.check_missing_required_data(user.id)
            if has_missing:
                flash("Falten dades obligatòries al teu perfil. Si us plau, completa les teves dades.", 'warning')
                return redirect(url_for('profile.profile', section='edit'))
            
            flash(f"Benvingut de nou, {username}!", 'success')
            # Redirigir a la página de origen o a productos
            next_page = request.args.get('next', url_for('main.show_products'))
            return redirect(next_page)
        else:
            flash(message, 'error')
        
        return render_template('login.html')
    
    return render_template('login.html')


def get_google_oauth():
    """Obtener instancia de Google OAuth desde la app"""
    from flask import current_app
    
    # Obtener la instancia de OAuth almacenada en app.config
    oauth = current_app.config.get('OAUTH')
    if not oauth:
        raise RuntimeError("OAuth no está configurado. Verifica que GOOGLE_OAUTH_CLIENT_ID y GOOGLE_OAUTH_CLIENT_SECRET estén en .env")
    
    return oauth.google


@auth_bp.route('/auth/google')
def google_login():
    """
    Iniciar el proceso de autenticación con Google.
    Redirige a Google para autenticarse.
    """
    google = get_google_oauth()
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/google/callback')
def google_callback():
    """
    Callback de Google OAuth.
    Procesa la respuesta de Google y crea/inicia sesión del usuario.
    """
    try:
        google = get_google_oauth()
        token = google.authorize_access_token()
        
        # Obtener información del usuario desde Google
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user_info = resp.json()
        
        google_email = user_info.get('email')
        google_name = user_info.get('name', '')
        google_picture = user_info.get('picture', '')
        
        if not google_email:
            flash("No s'ha pogut obtenir l'email de Google", 'error')
            return redirect(url_for('auth.login'))
        
        # Buscar si el usuario ya existe por email usando el servicio (siguiendo las reglas)
        existing_user = user_service.get_user_by_email(google_email)
        
        if existing_user:
            # Usuario existente: iniciar sesión
            # Verificar que sea usuario común (no empresa)
            if existing_user.account_type == 'company':
                flash("Els comptes d'empresa no poden utilitzar l'inici de sessió amb Google", 'error')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = existing_user.id
            
            # Verificar si faltan datos obligatorios
            has_missing, missing_fields = user_service.check_missing_required_data(existing_user.id)
            if has_missing:
                flash("Falten dades obligatòries al teu perfil. Si us plau, completa les teves dades.", 'warning')
                return redirect(url_for('profile.profile', section='edit'))
            
            flash(f"Benvingut de nou, {existing_user.username}!", 'success')
            return redirect(url_for('main.show_products'))
        else:
            # Nuevo usuario: guardar datos de Google en la sesión y redirigir a completar datos
            session['google_email'] = google_email
            session['google_name'] = google_name
            session['google_picture'] = google_picture
            return redirect(url_for('auth.complete_google_profile'))
            
    except Exception as e:
        flash(f"Error en l'autenticació amb Google: {str(e)}", 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/complete-google-profile', methods=['GET', 'POST'])
def complete_google_profile():
    """
    Formulario para completar los datos faltantes después de la autenticación con Google.
    """
    # Verificar que hay datos de Google en la sesión
    google_email = session.get('google_email')
    google_name = session.get('google_name', '')
    
    if not google_email:
        flash("Sessió de Google no trobada. Si us plau, intenta iniciar sessió amb Google de nou.", 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        address = request.form.get('address', '').strip()
        dni = request.form.get('dni', '').strip().upper()
        accept_policies = request.form.get('accept_policies') == 'on'
        
        # Validaciones
        if not all([username, address]):
            flash("El nom d'usuari i l'adreça són obligatoris", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        if not accept_policies:
            flash("Has d'acceptar les polítiques de privacitat i condicions d'ús", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        # Validar nombre de usuario
        if len(username) < 4 or len(username) > 20:
            flash("El nom d'usuari ha de tenir entre 4 i 20 caràcters", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        # Validar DNI si se ha proporcionado
        if dni and not validar_dni_nie(dni):
            flash("DNI/NIE no vàlid", 'error')
            return render_template('complete_google_profile.html', 
                                 google_email=google_email, 
                                 google_name=google_name)
        
        # Crear usuario con Google (account_type siempre 'user' para OAuth)
        success, user, message = user_service.create_user_with_google(
            username, google_email, address, dni
        )
        
        if success and user:
            # Limpiar datos de Google de la sesión
            session.pop('google_email', None)
            session.pop('google_name', None)
            session.pop('google_picture', None)
            
            # Iniciar sesión
            session['user_id'] = user.id
            flash(f"Compte creat correctament amb Google! Benvingut, {username}!", 'success')
            return redirect(url_for('main.show_products'))
        else:
            flash(message, 'error')
    
    return render_template('complete_google_profile.html', 
                         google_email=google_email, 
                         google_name=google_name)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Ruta para recuperar contraseña mediante DNI y email.
    
    Returns:
        str: Página HTML de recuperación de contraseña
    """
    if request.method == 'POST':
        dni = request.form.get('dni', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        
        if not dni:
            flash("El DNI/NIE és obligatori", 'error')
            return render_template('forgot_password.html')
        
        if not email:
            flash("L'email és obligatori", 'error')
            return render_template('forgot_password.html')
        
        # Restablecer contraseña mediante el servicio
        success, message = user_service.reset_password_by_dni_and_email(dni, email)
        
        if success:
            flash(message, 'success')
            return render_template('forgot_password.html', success=True, message=message)
        else:
            flash(message, 'error')
    
    return render_template('forgot_password.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Ruta para registrar un nuevo usuario.
    
    Returns:
        str: Página HTML de registro o redirección después del registro
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        account_type = request.form.get('account_type', 'user').strip()
        dni = request.form.get('dni', '').strip()
        nif = request.form.get('nif', '').strip()
        accept_policies = request.form.get('accept_policies') == 'on'
        accept_newsletter = request.form.get('accept_newsletter') == 'on'
        
        # Validaciones del servidor
        if not all([username, password, email, address]):
            flash("Tots els camps són obligatoris", 'error')
            return render_template('register.html')
        
        # Validar que se acepten las políticas
        if not accept_policies:
            flash("Has d'acceptar les polítiques de privacitat i condicions d'ús per crear un compte", 'error')
            return render_template('register.html')
        
        # Validar nombre de usuario
        if len(username) < 4 or len(username) > 20:
            flash("El nom d'usuari ha de tenir entre 4 i 20 caràcters", 'error')
            return render_template('register.html')
        
        # Validar contraseña
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
        
        # Crear usuario mediante el servicio (siguiendo las reglas)
        success, user, message = user_service.create_user(
            username, password, email, address, account_type, dni, nif
        )
        
        if success and user:
            # Iniciar sesión automáticamente
            session['user_id'] = user.id
            flash(f"Compte creat correctament! Benvingut, {username}!", 'success')
            return redirect(url_for('main.show_products'))
        else:
            flash(message, 'error')
        
        return render_template('register.html')
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """
    Ruta para cerrar sesión.
    
    Returns:
        str: Redirección a la página de productos
    """
    username = None
    user = get_current_user()
    if user:
        username = user.username
    
    session.clear()
    
    if username:
        flash(f"Sessió tancada. Fins aviat, {username}!", 'info')
    else:
        flash("Sessió tancada", 'info')
    
    return redirect(url_for('main.show_products'))

