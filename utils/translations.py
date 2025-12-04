"""
Sistema de traducciones para TechShop
Soporta: Catalán (por defecto), Español, Inglés
"""

# Diccionarios de traducciones
TRANSLATIONS = {
    'cat': {
        # Navegación
        'products': 'Productes',
        'hello': 'Hola',
        'login': 'Iniciar Sessió',
        'logout': 'Tancar Sessió',
        'admin': 'Admin',
        'my_products': 'Els Meus Productes',
        'cart': 'Carretó',
        'profile': 'Perfil',
        'create_account': 'Crear Compte',
        'forgot_password': 'He oblidat la meva contrasenya',
        'back_to_products': 'Tornar a Productes',
        'continue_with_google': 'Continuar amb Google',
        
        # Títulos de páginas
        'page_products': 'Productes Disponibles',
        'page_login': 'Iniciar Sessió',
        'page_register': 'Crear Compte',
        'page_checkout': 'Finalitzar Compra',
        'page_profile': 'El Meu Perfil',
        'page_admin': 'Panell d\'Administració',
        
        # Formularios - Labels
        'label_username': 'Nom d\'usuari:',
        'label_password': 'Contrasenya:',
        'label_email': 'Correu electrònic:',
        'label_address': 'Adreça d\'enviament:',
        'label_account_type': 'Tipus de compte:',
        'label_dni': 'DNI/NIE:',
        'label_nif': 'NIF/CIF:',
        'label_name': 'Nom:',
        'label_price': 'Preu:',
        'label_stock': 'Stock:',
        'label_quantity': 'Quantitat:',
        'label_product_name': 'Nom del Producte:',
        
        # Formularios - Placeholders y ayuda
        'help_username': 'Entre 4 i 20 caràcters (només lletres, números i guions baixos)',
        'help_password': 'Mínim 8 caràcters, amb almenys una lletra i un número',
        'help_email': 'Introdueix una adreça de correu electrònic vàlida',
        'help_address': 'Mínim 10 caràcters',
        'help_dni': 'Format: 8 números + lletra (DNI) o X/Y/Z + 7 números + lletra (NIE)',
        'help_nif': 'Format: lletra + 7 números + caràcter de control',
        'help_username_placeholder': 'Escull un nom d\'usuari',
        'help_address_placeholder': 'Carrer, número, ciutat, codi postal',
        
        # Botones
        'btn_login': 'Iniciar Sessió',
        'btn_register': 'Crear Compte',
        'btn_submit': 'Enviar',
        'btn_save': 'Desar',
        'btn_cancel': 'Cancel·lar',
        'btn_delete': 'Eliminar',
        'btn_edit': 'Editar',
        'btn_create': 'Crear',
        'btn_add': 'Afegir',
        'btn_remove': 'Eliminar',
        'btn_confirm': 'Confirmar',
        'btn_back': 'Tornar',
        'btn_download_invoice': 'Descarregar Factura',
        'btn_delete_account': 'Eliminar Compte',
        'role_common': 'Common',
        'role_admin': 'Admin',
        'error_dni_invalid': 'DNI/NIE no vàlid. Format: 8 números + lletra (DNI) o X/Y/Z + 7 números + lletra (NIE)',
        'error_nif_invalid': 'NIF/CIF no vàlid. Format: lletra + 7 números + caràcter de control',
        'error_email_invalid': 'Format d\'email no vàlid. Exemple: exemple@correu.com',
        'help_price': 'en euros (ex: 19.99)',
        'help_stock': 'disponible en inventari',
        
        # Mensajes generales
        'welcome': 'Benvingut',
        'welcome_back': 'Benvingut de nou',
        'error': 'Error',
        'success': 'Èxit',
        'warning': 'Advertència',
        'info': 'Informació',
        
        # Autenticación
        'login_required': 'Has d\'iniciar sessió',
        'invalid_credentials': 'Credencials incorrectes',
        'logout_success': 'Sessió tancada',
        'register_success': 'Compte creat correctament',
        'password_reset_sent': 'Nova contrasenya enviada per correu',
        
        # Perfil
        'view_data': 'Veure les meves dades',
        'edit_data': 'Editar les meves dades',
        'purchase_history': 'Historial de compres',
        'no_purchases': 'No has fet cap compra encara',
        'order_date': 'Data',
        'order_total': 'Total',
        'delete_account_confirm': 'Estàs segur que vols eliminar el teu compte? Aquesta acció no es pot desfer.',
        
        # Carrito
        'cart_empty': 'El teu carretó està buit',
        'add_to_cart': 'Afegir al carretó',
        'add_products_to_cart': 'Afegix productes al carretó per continuar amb la compra',
        'remove_from_cart': 'Eliminar del carretó',
        'cart_total': 'Total del carretó',
        'cart_items': 'Articles al carretó',
        
        # Checkout
        'checkout': 'Finalitzar compra',
        'checkout_as_guest': 'Comprar com a convidat',
        'checkout_authenticated': 'Comprar com a usuari registrat',
        'order_confirmation': 'Confirmació de comanda',
        'order_processed': 'Comanda processada correctament',
        'order_id': 'ID de comanda',
        'order': 'Comanda',
        
        # Productos
        'available_products': 'Productes Disponibles',
        'recommended_for_you': 'Productes per a tu',
        'based_on_purchases': 'Basat en les teves compres recents',
        'popular_products': 'Productes Populars',
        'units_sold': 'unitats venudes',
        'in_stock': 'En estoc',
        'out_of_stock': 'Sense estoc',
        
        # Políticas
        'accept_policies': 'Accepto les polítiques de privacitat i condicions d\'ús',
        'accept_newsletter': 'Vull rebre ofertes i novetats per correu electrònic',
        'policies_title': 'Polítiques de Privacitat i Condicions d\'Ús',
        'policies_intro': 'Si us plau, llegeix atentament aquestes polítiques abans d\'acceptar-les.',
        'accept_policies_button': 'Acceptar Polítiques',
        
        # Admin
        'admin_dashboard': 'Panell d\'Administració',
        'admin_products': 'Productes',
        'admin_users': 'Usuaris',
        'admin_orders': 'Comandes',
        'create_user': 'Crear Nou Usuari',
        'reset_password': 'Restablir Contrasenya',
        'edit_product': 'Editar Producte',
        'create_product': 'Crear Nou Producte',
        
        # Company
        'my_products_title': 'Els Meus Productes',
        'create_product_title': 'Crear Nou Producte',
        'edit_product_title': 'Editar Producte',
        
        # Footer
        'footer_text': '© 2024 TechShop - Pràctica d\'Intel·ligència Artificial',
        
        # Google OAuth
        'complete_profile': 'Completar el Teu Perfil',
        'google_login_success': 'Has iniciat sessió amb Google!',
        'complete_profile_info': 'Per completar el registre, si us plau, proporciona les següents dades:',
        
        # Validaciones
        'validation_required': 'Aquest camp és obligatori',
        'validation_min_length': 'Ha de tenir almenys {min} caràcters',
        'validation_max_length': 'Ha de tenir com a màxim {max} caràcters',
        
        # Más textos comunes
        'trends': 'Tendències de TechShop',
        'most_sold': 'Els productes més venuts a la botiga',
        'cart_summary': 'Resum del Carretó',
        'user_data': 'Dades de l\'Usuari',
        'buying_as': 'Comprant com',
        'email_label': 'Correu:',
        'no_image': 'Sense imatge',
        'total': 'Total',
        'remove': 'Eliminar',
        'prefer_guest': 'Prefereixes comprar com a convidat o iniciant sessió?',
        'or': 'o',
        'all_fields_required': 'Tots els camps són obligatoris',
        'username_length_error': 'El nom d\'usuari ha de tenir entre 4 i 20 caràcters',
        'password_length_error': 'La contrasenya ha de tenir mínim 8 caràcters',
        'password_complexity_error': 'La contrasenya ha de contenir almenys una lletra i un número',
        'email_invalid': 'Adreça de correu electrònic no vàlida',
        'address_length_error': 'L\'adreça d\'enviament ha de tenir almenys 10 caràcters',
        'order_processed_success': 'Comanda processada correctament! ID: {order_id}',
        'order_error': 'Error processant la comanda',
        'company_cannot_buy': 'Les empreses no poden comprar productes. Aquesta funcionalitat és només per usuaris individuals.',
        'product_not_found': 'Producte no trobat',
        'invalid_data': 'Dades invàlides',
        'access_denied_admin': 'Accés denegat. Es requereixen permisos d\'administrador.',
        'access_denied_login': 'Has d\'iniciar sessió per accedir a aquesta pàgina.',
        'access_denied_company': 'Accés denegat. Aquesta funcionalitat és només per empreses.',
        'session_invalid': 'Sessió no vàlida. Si us plau, inicia sessió de nou.',
        'missing_required_data': 'Falten dades obligatòries al teu perfil. Si us plau, completa les teves dades.',
        
        # Más textos específicos de templates
        'account_type_user': 'Usuari Individual',
        'account_type_company': 'Empresa',
        'register_date': 'Data de registre',
        'my_data': 'Les Meves Dades',
        'save_changes': 'Guardar Canvis',
        'order_number': 'Comanda #{id}',
        'order_products': 'Productes:',
        'product_col': 'Producte',
        'quantity_col': 'Quantitat',
        'unit_price': 'Preu Unitari',
        'total_label': 'Total:',
        'view_products': 'Veure Productes',
        'no_purchases_yet': 'No has fet cap compra encara.',
        'email_sent': 'Email Enviat',
        'recovery_info': 'Introdueix el teu DNI/NIE i el teu correu electrònic per recuperar la teva contrasenya. Se\'t generarà una nova contrasenya que s\'enviarà al teu correu.',
        'recovery_tips': 'Consells:',
        'check_inbox': 'Revisa la teva bústia d\'entrada',
        'check_spam': 'Si no veus l\'email, comprova la carpeta de spam o correu no desitjat',
        'email_delay': 'L\'email pot trigar uns minuts en arribar',
        'change_password_after': 'Després d\'iniciar sessió, et recomanem canviar la contrasenya per una de la teva elecció',
        'go_to_login': 'Anar a Iniciar Sessió',
        'recover_password': 'Recuperar Contrasenya',
        'back_to_login': 'Tornar a Iniciar Sessió',
        'email_associated': 'Introdueix el correu electrònic associat al teu compte',
        'email_sent_message': 'Hem enviat un email amb la teva nova contrasenya a l\'adreça de correu associada al teu compte.',
        'select_account_type': 'Selecciona el tipus de compte',
        'policies_required': 'Obligatori per crear un compte. Has d\'obrir i llegir les polítiques per acceptar-les.',
        'newsletter_optional': 'Opcional',
        'already_have_account': 'Ja tinc compte',
        'complete_registration': 'Completar Registre',
        'dni_optional': 'DNI/NIE (opcional)',
        'dni_optional_help': 'Format: 8 números + lletra (DNI) o X/Y/Z + 7 números + lletra (NIE) - Opcional',
        'back_to_products': '← Tornar als productes',
        'price_label': 'Preu:',
        'stock_available': 'Stock disponible:',
        'units': 'unitats',
        'max_5_units': 'Màxim 5 unitats per producte',
        'product_out_of_stock': 'Producte esgotat',
        'order_processed_title': '✅ Comanda Processada Correctament',
        'order_details': 'Detalls de la Comanda',
        'order_id_label': 'ID de Comanda:',
        'date_label': 'Data:',
        'thanks_purchase': 'Gràcies per la teva compra! La teva comanda ha estat processada correctament.',
        'email_confirmation': 'Rebràs un correu de confirmació amb els detalls de l\'enviament.',
        'continue_shopping': 'Continuar Comprant',
        'admin_panel': 'Panel d\'Administració',
        'manage_products': 'Gestionar Productes',
        'manage_users': 'Gestionar Usuaris',
        'manage_orders': 'Gestionar',
        'total_revenue': 'Ingressos Totals',
        'back_to_dashboard': 'Tornar al Dashboard',
        'create_first_product': 'Crear Primer Producte',
        'no_products_available': 'No hi ha productes disponibles.',
        'no_users_registered': 'No hi ha usuaris registrats.',
        'confirm_delete_product': 'Estàs segur que vols eliminar aquest producte?',
        'confirm_delete_user': 'Estàs segur que vols eliminar aquest usuari?',
        'confirm_reset_password': 'Estàs segur que vols restablir la contrasenya d\'aquest usuari? Se generarà una nova contrasenya automàticament.',
        'confirm_delete_product_sales': 'Estàs segur que vols eliminar aquest producte? Només es pot eliminar si no té vendes.',
        'no_products_yet': 'No tens productes encara.',
        'create_first_product_link': 'Crea el teu primer producte',
        'manage_my_products': 'Gestionar Els Meus Productes',
        'table_id': 'ID',
        'table_name': 'Nom',
        'table_price': 'Preu',
        'table_stock': 'Stock',
        'table_actions': 'Accions',
        'table_username': 'Nom d\'Usuari',
        'table_email': 'Email',
        'table_role': 'Rol',
        'table_account_type': 'Tipus de Compte',
        'table_register_date': 'Data de Registre',
        'image_not_available': 'Imatge no disponible',
        'previous_product': 'Producte anterior',
        'next_product': 'Producte següent',
        'stock_label': 'Stock disponible:',
        'company_cannot_buy_message': 'Les empreses no poden comprar productes. Gestiona els teus productes des de',
        'image_main': 'Imatge principal de',
        'image_thumbnail': 'Miniatura de',
        'show_image': 'Mostrar imatge',
        'max_units_per_product': 'Màxim 5 unitats per producte (disponible:',
        'of': 'de',
        'for': 'per',
    },
    'esp': {
        # Navegación
        'products': 'Productos',
        'hello': 'Hola',
        'login': 'Iniciar Sesión',
        'logout': 'Cerrar Sesión',
        'admin': 'Admin',
        'my_products': 'Mis Productos',
        'cart': 'Carrito',
        'profile': 'Perfil',
        'create_account': 'Crear Cuenta',
        'forgot_password': 'He olvidado mi contraseña',
        'back_to_products': 'Volver a Productos',
        'continue_with_google': 'Continuar con Google',
        
        # Títulos de páginas
        'page_products': 'Productos Disponibles',
        'page_login': 'Iniciar Sesión',
        'page_register': 'Crear Cuenta',
        'page_checkout': 'Finalizar Compra',
        'page_profile': 'Mi Perfil',
        'page_admin': 'Panel de Administración',
        
        # Formularios - Labels
        'label_username': 'Nombre de usuario:',
        'label_password': 'Contraseña:',
        'label_email': 'Correo electrónico:',
        'label_address': 'Dirección de envío:',
        'label_account_type': 'Tipo de cuenta:',
        'label_dni': 'DNI/NIE:',
        'label_nif': 'NIF/CIF:',
        'label_name': 'Nombre:',
        'label_price': 'Precio:',
        'label_stock': 'Stock:',
        'label_quantity': 'Cantidad:',
        'label_product_name': 'Nombre del Producto:',
        
        # Formularios - Placeholders y ayuda
        'help_username': 'Entre 4 y 20 caracteres (solo letras, números y guiones bajos)',
        'help_password': 'Mínimo 8 caracteres, con al menos una letra y un número',
        'help_email': 'Introduce una dirección de correo electrónico válida',
        'help_address': 'Mínimo 10 caracteres',
        'help_dni': 'Formato: 8 números + letra (DNI) o X/Y/Z + 7 números + letra (NIE)',
        'help_nif': 'Formato: letra + 7 números + carácter de control',
        'help_username_placeholder': 'Elige un nombre de usuario',
        'help_address_placeholder': 'Calle, número, ciudad, código postal',
        
        # Botones
        'btn_login': 'Iniciar Sesión',
        'btn_register': 'Crear Cuenta',
        'btn_submit': 'Enviar',
        'btn_save': 'Guardar',
        'btn_cancel': 'Cancelar',
        'btn_delete': 'Eliminar',
        'btn_edit': 'Editar',
        'btn_add': 'Añadir',
        'btn_remove': 'Eliminar',
        'btn_confirm': 'Confirmar',
        'btn_back': 'Volver',
        'btn_download_invoice': 'Descargar Factura',
        'btn_delete_account': 'Eliminar Cuenta',
        'btn_create': 'Crear',
        'role_common': 'Common',
        'role_admin': 'Admin',
        'error_dni_invalid': 'DNI/NIE no válido. Formato: 8 números + letra (DNI) o X/Y/Z + 7 números + letra (NIE)',
        'error_nif_invalid': 'NIF/CIF no válido. Formato: letra + 7 números + carácter de control',
        'error_email_invalid': 'Formato de email no válido. Ejemplo: ejemplo@correo.com',
        'help_price': 'en euros (ej: 19.99)',
        'help_stock': 'disponible en inventario',
        
        # Mensajes generales
        'welcome': 'Bienvenido',
        'welcome_back': 'Bienvenido de nuevo',
        'error': 'Error',
        'success': 'Éxito',
        'warning': 'Advertencia',
        'info': 'Información',
        
        # Autenticación
        'login_required': 'Debes iniciar sesión',
        'invalid_credentials': 'Credenciales incorrectas',
        'logout_success': 'Sesión cerrada',
        'register_success': 'Cuenta creada correctamente',
        'password_reset_sent': 'Nueva contraseña enviada por correo',
        
        # Perfil
        'view_data': 'Ver mis datos',
        'edit_data': 'Editar mis datos',
        'purchase_history': 'Historial de compras',
        'no_purchases': 'No has hecho compras aún',
        'order_date': 'Fecha',
        'order_total': 'Total',
        'delete_account_confirm': '¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.',
        
        # Carrito
        'cart_empty': 'Tu carrito está vacío',
        'add_to_cart': 'Añadir al carrito',
        'remove_from_cart': 'Eliminar del carrito',
        'cart_total': 'Total del carrito',
        'cart_items': 'Artículos en el carrito',
        
        # Checkout
        'checkout': 'Finalizar compra',
        'checkout_as_guest': 'Comprar como invitado',
        'checkout_authenticated': 'Comprar como usuario registrado',
        'order_confirmation': 'Confirmación de pedido',
        'order_processed': 'Pedido procesado correctamente',
        'order_id': 'ID de pedido',
        
        # Productos
        'available_products': 'Productos Disponibles',
        'recommended_for_you': 'Productos para ti',
        'based_on_purchases': 'Basado en tus compras recientes',
        'trends': 'Tendencias',
        'popular_products': 'Productos Populares',
        'units_sold': 'unidades vendidas',
        'in_stock': 'En stock',
        'out_of_stock': 'Sin stock',
        'stock_available': 'Stock disponible:',
        'units': 'unidades',
        'product_out_of_stock': 'Producto agotado',
        'most_sold': 'Los productos más vendidos',
        'image_not_available': 'Imagen no disponible',
        
        # Políticas
        'accept_policies': 'Acepto las políticas de privacidad y condiciones de uso',
        'accept_newsletter': 'Quiero recibir ofertas y novedades por correo electrónico',
        'policies_title': 'Políticas de Privacidad y Condiciones de Uso',
        'policies_intro': 'Por favor, lee atentamente estas políticas antes de aceptarlas.',
        'accept_policies_button': 'Aceptar Políticas',
        
        # Admin
        'admin_dashboard': 'Panel de Administración',
        'admin_products': 'Productos',
        'admin_users': 'Usuarios',
        'admin_orders': 'Pedidos',
        'create_user': 'Crear Nuevo Usuario',
        'reset_password': 'Restablecer Contraseña',
        'edit_product': 'Editar Producto',
        'create_product': 'Crear Nuevo Producto',
        
        # Company
        'my_products_title': 'Mis Productos',
        'create_product_title': 'Crear Nuevo Producto',
        'edit_product_title': 'Editar Producto',
        
        # Footer
        'footer_text': '© 2024 TechShop - Práctica de Inteligencia Artificial',
        
        # Google OAuth
        'complete_profile': 'Completar Tu Perfil',
        'google_login_success': '¡Has iniciado sesión con Google!',
        'complete_profile_info': 'Para completar el registro, por favor, proporciona los siguientes datos:',
        
        # Validaciones
        'validation_required': 'Este campo es obligatorio',
        'validation_min_length': 'Debe tener al menos {min} caracteres',
        'validation_max_length': 'Debe tener como máximo {max} caracteres',
        'stock_label': 'Stock disponible:',
        'company_cannot_buy_message': 'Las empresas no pueden comprar productos. Gestiona tus productos desde',
        'image_main': 'Imagen principal de',
        'image_thumbnail': 'Miniatura de',
        'show_image': 'Mostrar imagen',
        'max_units_per_product': 'Máximo 5 unidades por producto (disponible:',
        'of': 'de',
        'for': 'para',
    },
    'eng': {
        # Navegación
        'products': 'Products',
        'hello': 'Hello',
        'login': 'Log In',
        'logout': 'Log Out',
        'admin': 'Admin',
        'my_products': 'My Products',
        'cart': 'Cart',
        'profile': 'Profile',
        'create_account': 'Create Account',
        'forgot_password': 'I forgot my password',
        'back_to_products': 'Back to Products',
        'continue_with_google': 'Continue with Google',
        
        # Títulos de páginas
        'page_products': 'Available Products',
        'page_login': 'Log In',
        'page_register': 'Create Account',
        'page_checkout': 'Checkout',
        'page_profile': 'My Profile',
        'page_admin': 'Admin Dashboard',
        
        # Formularios - Labels
        'label_username': 'Username:',
        'label_password': 'Password:',
        'label_email': 'Email:',
        'label_address': 'Shipping Address:',
        'label_account_type': 'Account Type:',
        'label_dni': 'DNI/NIE:',
        'label_nif': 'NIF/CIF:',
        'label_name': 'Name:',
        'label_price': 'Price:',
        'label_stock': 'Stock:',
        'label_quantity': 'Quantity:',
        'label_product_name': 'Product Name:',
        
        # Formularios - Placeholders y ayuda
        'help_username': 'Between 4 and 20 characters (only letters, numbers and underscores)',
        'help_password': 'Minimum 8 characters, with at least one letter and one number',
        'help_email': 'Enter a valid email address',
        'help_address': 'Minimum 10 characters',
        'help_dni': 'Format: 8 numbers + letter (DNI) or X/Y/Z + 7 numbers + letter (NIE)',
        'help_nif': 'Format: letter + 7 numbers + control character',
        'help_username_placeholder': 'Choose a username',
        'help_address_placeholder': 'Street, number, city, postal code',
        
        # Botones
        'btn_login': 'Log In',
        'btn_register': 'Create Account',
        'btn_submit': 'Submit',
        'btn_save': 'Save',
        'btn_cancel': 'Cancel',
        'btn_delete': 'Delete',
        'btn_edit': 'Edit',
        'btn_add': 'Add',
        'btn_remove': 'Remove',
        'btn_confirm': 'Confirm',
        'btn_back': 'Back',
        'btn_download_invoice': 'Download Invoice',
        'btn_delete_account': 'Delete Account',
        'btn_create': 'Create',
        'role_common': 'Common',
        'role_admin': 'Admin',
        'error_dni_invalid': 'Invalid DNI/NIE. Format: 8 numbers + letter (DNI) or X/Y/Z + 7 numbers + letter (NIE)',
        'error_nif_invalid': 'Invalid NIF/CIF. Format: letter + 7 numbers + control character',
        'error_email_invalid': 'Invalid email format. Example: example@email.com',
        'help_price': 'in euros (ex: 19.99)',
        'help_stock': 'available in inventory',
        
        # Mensajes generales
        'welcome': 'Welcome',
        'welcome_back': 'Welcome back',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Information',
        
        # Autenticación
        'login_required': 'You must log in',
        'invalid_credentials': 'Invalid credentials',
        'logout_success': 'Logged out',
        'register_success': 'Account created successfully',
        'password_reset_sent': 'New password sent by email',
        
        # Perfil
        'view_data': 'View my data',
        'edit_data': 'Edit my data',
        'purchase_history': 'Purchase history',
        'no_purchases': 'You haven\'t made any purchases yet',
        'order_date': 'Date',
        'order_total': 'Total',
        'delete_account_confirm': 'Are you sure you want to delete your account? This action cannot be undone.',
        
        # Carrito
        'cart_empty': 'Your cart is empty',
        'add_to_cart': 'Add to cart',
        'remove_from_cart': 'Remove from cart',
        'cart_total': 'Cart total',
        'cart_items': 'Items in cart',
        
        # Checkout
        'checkout': 'Checkout',
        'checkout_as_guest': 'Checkout as guest',
        'checkout_authenticated': 'Checkout as registered user',
        'order_confirmation': 'Order confirmation',
        'order_processed': 'Order processed successfully',
        'order_id': 'Order ID',
        
        # Productos
        'available_products': 'Available Products',
        'recommended_for_you': 'Products for you',
        'based_on_purchases': 'Based on your recent purchases',
        'trends': 'Trends',
        'popular_products': 'Popular Products',
        'units_sold': 'units sold',
        'in_stock': 'In stock',
        'out_of_stock': 'Out of stock',
        'stock_available': 'Stock available:',
        'units': 'units',
        'product_out_of_stock': 'Product out of stock',
        'most_sold': 'Most sold products',
        'image_not_available': 'Image not available',
        
        # Políticas
        'accept_policies': 'I accept the privacy policy and terms of use',
        'accept_newsletter': 'I want to receive offers and news by email',
        'policies_title': 'Privacy Policy and Terms of Use',
        'policies_intro': 'Please read these policies carefully before accepting them.',
        'accept_policies_button': 'Accept Policies',
        
        # Admin
        'admin_dashboard': 'Admin Dashboard',
        'admin_products': 'Products',
        'admin_users': 'Users',
        'admin_orders': 'Orders',
        'create_user': 'Create New User',
        'reset_password': 'Reset Password',
        'edit_product': 'Edit Product',
        'create_product': 'Create New Product',
        
        # Company
        'my_products_title': 'My Products',
        'create_product_title': 'Create New Product',
        'edit_product_title': 'Edit Product',
        
        # Footer
        'footer_text': '© 2024 TechShop - Artificial Intelligence Practice',
        
        # Google OAuth
        'complete_profile': 'Complete Your Profile',
        'google_login_success': 'You have logged in with Google!',
        'complete_profile_info': 'To complete registration, please provide the following information:',
        
        # Validaciones
        'validation_required': 'This field is required',
        'validation_min_length': 'Must have at least {min} characters',
        'validation_max_length': 'Must have at most {max} characters',
        'stock_label': 'Stock available:',
        'company_cannot_buy_message': 'Companies cannot buy products. Manage your products from',
        'image_main': 'Main image of',
        'image_thumbnail': 'Thumbnail of',
        'show_image': 'Show image',
        'max_units_per_product': 'Maximum 5 units per product (available:',
        'of': 'of',
        'for': 'for',
    }
}

def get_translation(key: str, lang: str = 'cat') -> str:
    """
    Obtener traducción de una clave.
    
    Args:
        key (str): Clave de traducción
        lang (str): Idioma ('cat', 'esp', 'eng')
        
    Returns:
        str: Texto traducido o la clave si no se encuentra
    """
    if lang not in TRANSLATIONS:
        lang = 'cat'
    
    return TRANSLATIONS.get(lang, {}).get(key, key)

def get_available_languages() -> list:
    """Obtener lista de idiomas disponibles."""
    return ['cat', 'esp', 'eng']

def get_language_name(lang: str) -> str:
    """Obtener nombre del idioma."""
    names = {
        'cat': 'Català',
        'esp': 'Español',
        'eng': 'English'
    }
    return names.get(lang, lang)
