# Utilidades - TechShop

## 📁 Descripción

Esta carpeta contiene funciones y clases de utilidad que son compartidas por múltiples partes de la aplicación. Estas utilidades proporcionan funcionalidades transversales que no pertenecen a una capa específica.

## 🎯 Responsabilidad

Las utilidades proporcionan:
- Funciones de validación reutilizables
- Servicios auxiliares (email, facturas, traducciones)
- Funciones helper compartidas

## 📂 Estructura

```
utils/
├── __init__.py              # Inicialización del módulo
├── validators.py            # Validadores de datos (DNI, NIE, CIF, etc.)
├── email_service.py         # Servicio de envío de emails
├── invoice_generator.py     # Generador de facturas PDF
└── translations.py          # Sistema de traducciones (i18n)
```

## 🔧 Utilidades Disponibles

### **validators.py**
Validadores de datos del cliente (DNI, NIE, CIF).

**Funciones:**
- `validar_dni(dni)`: Valida formato y letra de DNI español
- `validar_nie(nie)`: Valida formato y letra de NIE
- `validar_cif(cif)`: Valida formato y dígito de control de CIF
- `validar_dni_nie(dni_nie)`: Valida DNI o NIE
- `validar_cif_nif(cif_nif)`: Valida CIF o NIF

**Uso:**
```python
from utils.validators import validar_dni, validar_cif_nif

if validar_dni("12345678Z"):
    print("DNI válido")
```

**Ubicación:** `utils/validators.py`

### **email_service.py**
Servicio para enviar emails (SMTP).

**Funciones:**
- `send_order_confirmation_email(...)`: Envía email de confirmación de pedido con factura adjunta
- `send_welcome_email(email, username)`: Envía email de bienvenida al registrarse
- `send_password_reset_email(email, username, new_password)`: Envía nueva contraseña por email

**Configuración:**
- Usa variables de entorno: `EMAIL`, `GOOGLE_PASSWORD_APP`
- Soporta HTML y adjuntos PDF

**Ubicación:** `utils/email_service.py`

### **invoice_generator.py**
Generador de facturas en formato PDF.

**Funciones:**
- `generate_invoice_pdf(order_id, user_id)`: Genera factura PDF para una comanda

**Características:**
- Usa ReportLab para generar PDFs
- Incluye datos de empresa y cliente
- Tabla de productos con detalles
- Estilo consistente y profesional

**Ubicación:** `utils/invoice_generator.py`

### **translations.py**
Sistema de internacionalización (i18n) y localización (l10n).

**Funciones:**
- `get_translation(key, lang)`: Obtiene traducción de una clave
- `get_available_languages()`: Lista idiomas disponibles
- `get_language_name(lang)`: Nombre del idioma

**Idiomas soportados:**
- `cat`: Catalán (por defecto)
- `esp`: Español
- `eng`: Inglés

**Uso en templates:**
```jinja2
{{ _('welcome') }}  <!-- Muestra "Benvingut", "Bienvenido" o "Welcome" según el idioma -->
```

**Ubicación:** `utils/translations.py`

## 💡 Uso General

```python
from utils.validators import validar_dni_nie
from utils.email_service import send_welcome_email
from utils.translations import get_translation

# Validar DNI
if validar_dni_nie("12345678Z"):
    # Enviar email
    send_welcome_email("user@example.com", "username")
    
# Obtener traducción
message = get_translation('welcome', 'cat')
```

## ⚠️ Reglas Importantes

1. **Reutilizables**: Las funciones deben ser genéricas y reutilizables
2. **Sin dependencias de capas**: No deben depender de rutas o templates
3. **Documentación**: Todas las funciones deben tener docstrings
4. **Validaciones**: Los validadores deben funcionar tanto en cliente como en servidor

## 📚 Referencias

- Ver `docs/reglas_techshop.md` para más detalles sobre validaciones
- Ver `routes/` para ver cómo se usan las utilidades

