# Utilitats - TechShop

## 📁 Descripció

Aquesta carpeta conté funcions i classes d'utilitat que són compartides per múltiples parts de l'aplicació. Aquestes utilitats proporcionen funcionalitats transversals que no pertanyen a una capa específica.

## 🎯 Responsabilitat

Les utilitats proporcionen:
- Funcions de validació reutilitzables
- Serveis auxiliars (email, factures, traduccions)
- Funcions helper compartides

## 📂 Estructura

```
utils/
├── __init__.py              # Inicialització del mòdul
├── validators.py            # Validadors de dades (DNI, NIE, CIF, etc.)
├── email_service.py         # Servei d'enviament d'emails
├── invoice_generator.py     # Generador de factures PDF
└── translations.py          # Sistema de traduccions (i18n)
```

## 🔧 Utilitats Disponibles

### **validators.py**
Validadors de dades del client (DNI, NIE, CIF).

**Funcions:**
- `validar_dni(dni)`: Valida format i lletra de DNI espanyol
- `validar_nie(nie)`: Valida format i lletra de NIE
- `validar_cif(cif)`: Valida format i dígit de control de CIF
- `validar_dni_nie(dni_nie)`: Valida DNI o NIE
- `validar_cif_nif(cif_nif)`: Valida CIF o NIF

**Ús:**
```python
from utils.validators import validar_dni, validar_cif_nif

if validar_dni("12345678Z"):
    print("DNI vàlid")
```

**Ubicació:** `utils/validators.py`

### **email_service.py**
Servei per enviar emails (SMTP).

**Funcions:**
- `send_order_confirmation_email(...)`: Envia email de confirmació de comanda amb factura adjunta
- `send_welcome_email(email, username)`: Envia email de benvinguda en registrar-se
- `send_password_reset_email(email, username, new_password)`: Envia nova contrasenya per email

**Configuració:**
- Usa variables d'entorn: `EMAIL`, `GOOGLE_PASSWORD_APP`
- Suporta HTML i adjunts PDF

**Ubicació:** `utils/email_service.py`

### **invoice_generator.py**
Generador de factures en format PDF.

**Funcions:**
- `generate_invoice_pdf(order_id, user_id)`: Genera factura PDF per a una comanda

**Característiques:**
- Usa ReportLab per generar PDFs
- Inclou dades d'empresa i client
- Taula de productes amb detalls
- Estil consistent i professional

**Ubicació:** `utils/invoice_generator.py`

### **translations.py**
Sistema d'internacionalització (i18n) i localització (l10n).

**Funcions:**
- `get_translation(key, lang)`: Obté traducció d'una clau
- `get_available_languages()`: Llista idiomes disponibles
- `get_language_name(lang)`: Nom de l'idioma

**Idiomes suportats:**
- `cat`: Català (per defecte)
- `esp`: Espanyol
- `eng`: Anglès

**Ús en templates:**
```jinja2
{{ _('welcome') }}  <!-- Mostra "Benvingut", "Bienvenido" o "Welcome" segons l'idioma -->
```

**Ubicació:** `utils/translations.py`

## 💡 Ús General

```python
from utils.validators import validar_dni_nie
from utils.email_service import send_welcome_email
from utils.translations import get_translation

# Validar DNI
if validar_dni_nie("12345678Z"):
    # Enviar email
    send_welcome_email("user@example.com", "username")
    
# Obtenir traducció
message = get_translation('welcome', 'cat')
```

## ⚠️ Regles Importants

1. **Reutilitzables**: Les funcions han de ser genèriques i reutilitzables
2. **Sense dependències de capes**: No han de dependre de rutes o templates
3. **Documentació**: Totes les funcions han de tenir docstrings
4. **Validacions**: Els validadors han de funcionar tant en client com en servidor

## 📚 Referències

- Veure `docs/reglas_techshop.md` per a més detalls sobre validacions
- Veure `routes/` per a veure com s'usen les utilitats
