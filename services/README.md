# Serveis - Lògica de Negoci - TechShop

## 📁 Descripció

Aquesta carpeta conté la **lògica de negoci** de l'aplicació, seguint l'arquitectura de **tres capes** i el principi de separació de responsabilitats. Els serveis encapsulen tota la lògica de negoci **sense barrejar codi de presentació ni accés directe a dades**.

## 🎯 Responsabilitat

Els serveis implementen les regles de negoci de l'aplicació:
- Validacions de negoci
- Càlculs i transformacions de dades
- Coordinació entre models
- **NO contenen codi HTML ni consultes SQL directes**

## 📂 Estructura

```
services/
├── cart_service.py              # Gestió del carretó de compres
├── order_service.py              # Gestió de comandes
├── user_service.py               # Gestió d'usuaris
├── product_service.py            # Gestió de productes
├── admin_service.py              # Funcionalitats d'administració
├── company_service.py            # Gestió de productes per empreses
└── recommendation_service.py    # Sistema de recomanacions
```

## 🔧 Serveis Disponibles

### **CartService**
Gestiona el carretó de compres de l'usuari.

**Funcions principals:**
- `add_to_cart(product_id, quantity, session)`: Afegir producte al carretó
- `remove_from_cart(product_id, session)`: Eliminar producte del carretó
- `validate_stock(product_id, quantity)`: Validar stock disponible
- `get_cart_contents(session)`: Obtenir contingut del carretó
- `get_cart_total(session)`: Calcular total del carretó
- `clear_cart(session)`: Netejar el carretó

**Regles de negoci:**
- Màxim 5 unitats per producte
- Validació de stock disponible
- Validació de quantitat positiva

**Ubicació:** `services/cart_service.py`

### **OrderService**
Gestiona les comandes i ordres.

**Funcions principals:**
- `create_order(cart, user_id)`: Crear una nova comanda
- `create_order_in_transaction(conn, cart, user_id)`: Crear comanda en transacció
- `get_order_by_id(order_id)`: Obtenir comanda per ID
- `get_orders_by_user_id(user_id)`: Obtenir comandes d'un usuari
- `get_order_items_for_email(order_id)`: Obtenir items per email

**Regles de negoci:**
- Calcula el total sumant `price * quantity` de cada producte
- Actualitza l'inventari restant les unitats comprades
- Valida que el carretó no estigui buit

**Ubicació:** `services/order_service.py`

### **UserService**
Gestiona usuaris i autenticació.

**Funcions principals:**
- `create_user(...)`: Crear nou usuari
- `authenticate_user(username, password)`: Autenticar usuari
- `update_user_profile(...)`: Actualitzar perfil d'usuari
- `delete_user_account(user_id)`: Eliminar compte d'usuari
- `reset_password_by_dni_and_email(...)`: Recuperar contrasenya
- `check_missing_required_data(user_id)`: Verificar dades faltants

**Regles de negoci:**
- Validació de DNI/NIE/NIF segons tipus de compte
- Validació d'unicitat de username, email, DNI
- Hash segur de contrasenyes (bcrypt)

**Ubicació:** `services/user_service.py`

### **ProductService**
Gestiona productes i catàleg.

**Funcions principals:**
- `get_all_products()`: Obtenir tots els productes
- `get_product_by_id(product_id)`: Obtenir producte per ID
- `get_products_by_ids(product_ids)`: Obtenir múltiples productes

**Ubicació:** `services/product_service.py`

### **AdminService**
Funcionalitats exclusives per administradors.

**Funcions principals:**
- `get_dashboard_stats()`: Estadístiques del dashboard
- `get_all_products()`: Llistar tots els productes
- `create_product(...)`: Crear producte
- `update_product(...)`: Actualitzar producte
- `delete_product(product_id)`: Eliminar producte
- `get_all_users()`: Llistar tots els usuaris
- `create_user(...)`: Crear usuari (amb contrasenya generada)
- `update_user(...)`: Actualitzar usuari
- `reset_user_password(user_id)`: Restablir contrasenya
- `delete_user(user_id)`: Eliminar usuari

**Ubicació:** `services/admin_service.py`

### **CompanyService**
Gestió de productes per usuaris tipus empresa.

**Funcions principals:**
- `get_company_products(company_id)`: Obtenir productes de l'empresa
- `create_product(company_id, ...)`: Crear producte
- `update_product(product_id, company_id, ...)`: Actualitzar producte
- `delete_product(product_id, company_id)`: Eliminar producte (només si no té vendes)
- `save_product_images(product_id, files)`: Guardar imatges amb compressió

**Regles de negoci:**
- Màxim 4 imatges per producte
- Compressió d'imatges al 80%
- No es poden eliminar productes amb vendes

**Ubicació:** `services/company_service.py`

### **RecommendationService**
Sistema de recomanacions basat en vendes històriques.

**Funcions principals:**
- `get_top_selling_products(limit)`: Productes més venuts
- `get_top_products_for_user(user_id, limit)`: Recomanacions personalitzades

**Regles de negoci:**
- Ordena per quantitat venuda (DESC)
- En cas d'empat, ordena per nom (ASC)
- Retorna llista buida si no hi ha dades

**Ubicació:** `services/recommendation_service.py`

## 💡 Ús

```python
from services.cart_service import CartService
from services.order_service import OrderService

# Inicialitzar serveis
cart_service = CartService()
order_service = OrderService()

# Usar serveis
success, message = cart_service.add_to_cart(product_id=1, quantity=2, session=session)
```

## ⚠️ Regles Importants (segons reglas_techshop.md)

1. **No barrejar amb presentació**: Els serveis no coneixen HTML ni templates
2. **No accés directe a dades**: Els serveis usen models, no consultes SQL directes
3. **Validacions de negoci**: Totes les validacions de regles de negoci estan aquí
4. **Docstrings obligatoris**: Cada funció ha de tenir documentació completa
5. **Maneig d'errors**: Els serveis retornen tuples `(success, message)` o `(success, data, message)`

## 📚 Referències

- Veure `docs/reglas_techshop.md` secció 3 per a més detalls sobre lògica de negoci
- Veure `routes/` per a veure com s'usen els serveis des de les rutes
