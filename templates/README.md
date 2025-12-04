# Plantilles - Capa de Presentació - TechShop

## 📁 Descripció

Aquesta carpeta conté les plantilles HTML que formen la **capa de presentació** de l'aplicació, seguint el patró **Vista** de l'arquitectura MVC. Les plantilles utilitzen Jinja2 com a motor de plantilles i **no contenen lògica de negoci ni accés a dades**.

## 🎯 Responsabilitat

Les plantilles són responsables únicament de:
- Mostrar dades a l'usuari
- Rebre dades de l'usuari (formularis)
- **NO contenen lògica de negoci**
- **NO contenen consultes SQL**
- **NO contenen càlculs complexos**

## 📂 Estructura

```
templates/
├── base.html                    # Plantilla base (layout principal)
├── products.html                # Catàleg de productes
├── product_detail.html          # Detall de producte
├── checkout.html                # Pàgina de checkout
├── order_confirmation.html      # Confirmació de comanda
├── login.html                   # Pàgina de login
├── register.html                # Pàgina de registre
├── forgot_password.html         # Recuperació de contrasenya
├── complete_google_profile.html # Completar perfil Google
├── policies.html                # Polítiques de privacitat
├── profile.html                 # Perfil d'usuari
│
├── admin/                       # Plantilles d'administració
│   ├── dashboard.html
│   ├── products.html
│   ├── product_form.html
│   ├── users.html
│   ├── user_form.html
│   ├── user_create_form.html
│   └── orders.html
│
└── company/                     # Plantilles per empreses
    ├── products.html
    └── product_form.html
```

## 🎨 Plantilles Principals

### **base.html**
Plantilla base que defineix el layout comú de totes les pàgines.

**Característiques:**
- Header amb navegació
- Sistema de traduccions (banderes d'idioma)
- Missatges flash
- Footer comú
- Bloc `{% block content %}` per a contingut específic

**Ús:**
```jinja2
{% extends "base.html" %}
{% block content %}
  <!-- Contingut específic -->
{% endblock %}
```

### **products.html**
Mostra el catàleg complet de productes.

**Característiques:**
- Llista de productes amb imatges
- Formulari per afegir al carretó
- Recomanacions personalitzades
- Secció de tendències (més venuts)

### **product_detail.html**
Vista detallada d'un producte individual.

**Característiques:**
- Galeria d'imatges (fins a 4)
- Hover per canviar imatge principal
- Informació completa del producte
- Formulari per afegir al carretó

### **checkout.html**
Pàgina de procés de compra.

**Característiques:**
- Resum del carretó
- Formulari adaptatiu:
  - Usuari autenticat: només adreça
  - Convidat: tots els camps o opció de login
- Validacions HTML5

### **profile.html**
Perfil d'usuari amb seccions.

**Seccions:**
- Veure dades personals
- Editar dades
- Historial de compres (amb descàrrega de factures)

## 🌐 Sistema de Traduccions

Totes les plantilles usen el sistema de traduccions:

```jinja2
{{ _('welcome') }}              <!-- Text traduït -->
{{ _('products') }}              <!-- "Productes", "Productos", "Products" -->
{{ current_language }}           <!-- Idioma actual: 'cat', 'esp', 'eng' -->
```

**Idiomes suportats:**
- Català (per defecte)
- Espanyol
- Anglès

## 📝 Ús de Blueprints

Totes les referències a rutes usen noms de blueprints:

```jinja2
{{ url_for('main.show_products') }}        <!-- En lloc de 'show_products' -->
{{ url_for('auth.login') }}                <!-- En lloc de 'login' -->
{{ url_for('profile.profile') }}           <!-- En lloc de 'profile' -->
{{ url_for('admin.admin_dashboard') }}      <!-- En lloc de 'admin_dashboard' -->
```

## ⚠️ Regles Importants (segons reglas_techshop.md)

1. **No lògica de negoci**: Les plantilles només mostren dades
2. **No consultes SQL**: No s'accedeix directament a la base de dades
3. **Validacions HTML5**: S'usen atributs `required`, `minlength`, `maxlength`, `pattern`
4. **Separació de responsabilitats**: La presentació està separada de la lògica
5. **Reutilització**: S'usa `base.html` per evitar duplicació

## 🔒 Validacions en Plantilles

### Atributs HTML5 usats:
- `required`: Camps obligatoris
- `minlength` / `maxlength`: Longitud de text
- `type="email"`: Validació d'email
- `type="number"`: Camps numèrics
- `min` / `max`: Rangs numèrics
- `pattern`: Patrons de validació (DNI, etc.)

### Exemple:
```html
<input type="text" 
       name="username" 
       required 
       minlength="4" 
       maxlength="20"
       pattern="[a-zA-Z0-9_]+">
```

## 📚 Referències

- Veure `docs/reglas_techshop.md` secció 4 per a validacions del frontend
- Veure `routes/` per a veure com es renderitzen les plantilles
- Veure `utils/translations.py` per al sistema de traduccions
