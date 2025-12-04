# Templates - Capa de Presentación - TechShop

## 📁 Descripción

Esta carpeta contiene las plantillas HTML que forman la **capa de presentación** de la aplicación, siguiendo el patrón **Vista** de la arquitectura MVC. Las plantillas utilizan Jinja2 como motor de plantillas y **no contienen lógica de negocio ni acceso a datos**.

## 🎯 Responsabilidad

Las plantillas son responsables únicamente de:
- Mostrar datos al usuario
- Recibir datos del usuario (formularios)
- **NO contienen lógica de negocio**
- **NO contienen consultas SQL**
- **NO contienen cálculos complejos**

## 📂 Estructura

```
templates/
├── base.html                    # Plantilla base (layout principal)
├── products.html                # Catálogo de productos
├── product_detail.html          # Detalle de producto
├── checkout.html                # Página de checkout
├── order_confirmation.html      # Confirmación de pedido
├── login.html                   # Página de login
├── register.html                # Página de registro
├── forgot_password.html         # Recuperación de contraseña
├── complete_google_profile.html # Completar perfil Google
├── policies.html                # Políticas de privacidad
├── profile.html                 # Perfil de usuario
│
├── admin/                       # Templates de administración
│   ├── dashboard.html
│   ├── products.html
│   ├── product_form.html
│   ├── users.html
│   ├── user_form.html
│   ├── user_create_form.html
│   └── orders.html
│
└── company/                     # Templates para empresas
    ├── products.html
    └── product_form.html
```

## 🎨 Plantillas Principales

### **base.html**
Plantilla base que define el layout común de todas las páginas.

**Características:**
- Header con navegación
- Sistema de traducciones (banderas de idioma)
- Mensajes flash
- Footer común
- Bloque `{% block content %}` para contenido específico

**Uso:**
```jinja2
{% extends "base.html" %}
{% block content %}
  <!-- Contenido específico -->
{% endblock %}
```

### **products.html**
Muestra el catálogo completo de productos.

**Características:**
- Lista de productos con imágenes
- Formulario para añadir al carrito
- Recomendaciones personalizadas
- Sección de tendencias (más vendidos)

### **product_detail.html**
Vista detallada de un producto individual.

**Características:**
- Galería de imágenes (hasta 4)
- Hover para cambiar imagen principal
- Información completa del producto
- Formulario para añadir al carrito

### **checkout.html**
Página de proceso de compra.

**Características:**
- Resumen del carrito
- Formulario adaptativo:
  - Usuario autenticado: solo dirección
  - Invitado: todos los campos o opción de login
- Validaciones HTML5

### **profile.html**
Perfil de usuario con secciones.

**Secciones:**
- Ver datos personales
- Editar datos
- Historial de compras (con descarga de facturas)

## 🌐 Sistema de Traducciones

Todas las plantillas usan el sistema de traducciones:

```jinja2
{{ _('welcome') }}              <!-- Texto traducido -->
{{ _('products') }}              <!-- "Productes", "Productos", "Products" -->
{{ current_language }}           <!-- Idioma actual: 'cat', 'esp', 'eng' -->
```

**Idiomas soportados:**
- Catalán (por defecto)
- Español
- Inglés

## 📝 Uso de Blueprints

Todas las referencias a rutas usan nombres de blueprints:

```jinja2
{{ url_for('main.show_products') }}        <!-- En lugar de 'show_products' -->
{{ url_for('auth.login') }}                <!-- En lugar de 'login' -->
{{ url_for('profile.profile') }}           <!-- En lugar de 'profile' -->
{{ url_for('admin.admin_dashboard') }}      <!-- En lugar de 'admin_dashboard' -->
```

## ⚠️ Reglas Importantes (según reglas_techshop.md)

1. **No lógica de negocio**: Las plantillas solo muestran datos
2. **No consultas SQL**: No se accede directamente a la base de datos
3. **Validaciones HTML5**: Se usan atributos `required`, `minlength`, `maxlength`, `pattern`
4. **Separación de responsabilidades**: La presentación está separada de la lógica
5. **Reutilización**: Se usa `base.html` para evitar duplicación

## 🔒 Validaciones en Templates

### Atributos HTML5 usados:
- `required`: Campos obligatorios
- `minlength` / `maxlength`: Longitud de texto
- `type="email"`: Validación de email
- `type="number"`: Campos numéricos
- `min` / `max`: Rangos numéricos
- `pattern`: Patrones de validación (DNI, etc.)

### Ejemplo:
```html
<input type="text" 
       name="username" 
       required 
       minlength="4" 
       maxlength="20"
       pattern="[a-zA-Z0-9_]+">
```

## 📚 Referencias

- Ver `docs/reglas_techshop.md` sección 4 para validaciones del frontend
- Ver `routes/` para ver cómo se renderizan las plantillas
- Ver `utils/translations.py` para el sistema de traducciones

