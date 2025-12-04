# Servicios - Lógica de Negocio - TechShop

## 📁 Descripción

Esta carpeta contiene la **lógica de negocio** de la aplicación, siguiendo la arquitectura de **tres capas** y el principio de separación de responsabilidades. Los servicios encapsulan toda la lógica de negocio **sin mezclar código de presentación ni acceso directo a datos**.

## 🎯 Responsabilidad

Los servicios implementan las reglas de negocio de la aplicación:
- Validaciones de negocio
- Cálculos y transformaciones de datos
- Coordinación entre modelos
- **NO contienen código HTML ni consultas SQL directas**

## 📂 Estructura

```
services/
├── cart_service.py              # Gestión del carrito de compras
├── order_service.py              # Gestión de comandas
├── user_service.py               # Gestión de usuarios
├── product_service.py            # Gestión de productos
├── admin_service.py              # Funcionalidades de administración
├── company_service.py            # Gestión de productos para empresas
└── recommendation_service.py    # Sistema de recomendaciones
```

## 🔧 Servicios Disponibles

### **CartService**
Gestiona el carrito de compras del usuario.

**Funciones principales:**
- `add_to_cart(product_id, quantity, session)`: Añadir producto al carrito
- `remove_from_cart(product_id, session)`: Eliminar producto del carrito
- `validate_stock(product_id, quantity)`: Validar stock disponible
- `get_cart_contents(session)`: Obtener contenido del carrito
- `get_cart_total(session)`: Calcular total del carrito
- `clear_cart(session)`: Limpiar el carrito

**Reglas de negocio:**
- Máximo 5 unidades por producto
- Validación de stock disponible
- Validación de cantidad positiva

**Ubicación:** `services/cart_service.py`

### **OrderService**
Gestiona las comandas y órdenes.

**Funciones principales:**
- `create_order(cart, user_id)`: Crear una nueva comanda
- `create_order_in_transaction(conn, cart, user_id)`: Crear comanda en transacción
- `get_order_by_id(order_id)`: Obtener comanda por ID
- `get_orders_by_user_id(user_id)`: Obtener comandas de un usuario
- `get_order_items_for_email(order_id)`: Obtener items para email

**Reglas de negocio:**
- Calcula el total sumando `price * quantity` de cada producto
- Actualiza el inventario restando las unidades compradas
- Valida que el carrito no esté vacío

**Ubicación:** `services/order_service.py`

### **UserService**
Gestiona usuarios y autenticación.

**Funciones principales:**
- `create_user(...)`: Crear nuevo usuario
- `authenticate_user(username, password)`: Autenticar usuario
- `update_user_profile(...)`: Actualizar perfil de usuario
- `delete_user_account(user_id)`: Eliminar cuenta de usuario
- `reset_password_by_dni_and_email(...)`: Recuperar contraseña
- `check_missing_required_data(user_id)`: Verificar datos faltantes

**Reglas de negocio:**
- Validación de DNI/NIE/NIF según tipo de cuenta
- Validación de unicidad de username, email, DNI
- Hash seguro de contraseñas (bcrypt)

**Ubicación:** `services/user_service.py`

### **ProductService**
Gestiona productos y catálogo.

**Funciones principales:**
- `get_all_products()`: Obtener todos los productos
- `get_product_by_id(product_id)`: Obtener producto por ID
- `get_products_by_ids(product_ids)`: Obtener múltiples productos

**Ubicación:** `services/product_service.py`

### **AdminService**
Funcionalidades exclusivas para administradores.

**Funciones principales:**
- `get_dashboard_stats()`: Estadísticas del dashboard
- `get_all_products()`: Listar todos los productos
- `create_product(...)`: Crear producto
- `update_product(...)`: Actualizar producto
- `delete_product(product_id)`: Eliminar producto
- `get_all_users()`: Listar todos los usuarios
- `create_user(...)`: Crear usuario (con contraseña generada)
- `update_user(...)`: Actualizar usuario
- `reset_user_password(user_id)`: Resetear contraseña
- `delete_user(user_id)`: Eliminar usuario

**Ubicación:** `services/admin_service.py`

### **CompanyService**
Gestión de productos para usuarios tipo empresa.

**Funciones principales:**
- `get_company_products(company_id)`: Obtener productos de la empresa
- `create_product(company_id, ...)`: Crear producto
- `update_product(product_id, company_id, ...)`: Actualizar producto
- `delete_product(product_id, company_id)`: Eliminar producto (solo si no tiene ventas)
- `save_product_images(product_id, files)`: Guardar imágenes con compresión

**Reglas de negocio:**
- Máximo 4 imágenes por producto
- Compresión de imágenes al 80%
- No se pueden eliminar productos con ventas

**Ubicación:** `services/company_service.py`

### **RecommendationService**
Sistema de recomendaciones basado en ventas históricas.

**Funciones principales:**
- `get_top_selling_products(limit)`: Productos más vendidos
- `get_top_products_for_user(user_id, limit)`: Recomendaciones personalizadas

**Reglas de negocio:**
- Ordena por cantidad vendida (DESC)
- En caso de empate, ordena por nombre (ASC)
- Retorna lista vacía si no hay datos

**Ubicación:** `services/recommendation_service.py`

## 💡 Uso

```python
from services.cart_service import CartService
from services.order_service import OrderService

# Inicializar servicios
cart_service = CartService()
order_service = OrderService()

# Usar servicios
success, message = cart_service.add_to_cart(product_id=1, quantity=2, session=session)
```

## ⚠️ Reglas Importantes (según reglas_techshop.md)

1. **No mezclar con presentación**: Los servicios no conocen HTML ni templates
2. **No acceso directo a datos**: Los servicios usan modelos, no consultas SQL directas
3. **Validaciones de negocio**: Todas las validaciones de reglas de negocio están aquí
4. **Docstrings obligatorios**: Cada función debe tener documentación completa
5. **Manejo de errores**: Los servicios retornan tuplas `(success, message)` o `(success, data, message)`

## 📚 Referencias

- Ver `docs/reglas_techshop.md` sección 3 para más detalles sobre lógica de negocio
- Ver `routes/` para ver cómo se usan los servicios desde las rutas

