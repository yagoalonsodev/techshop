# Modelos de Datos - TechShop

## 📁 Descripción

Esta carpeta contiene las clases de datos que representan las entidades de la base de datos, siguiendo el patrón **Model** de la arquitectura MVC y la **capa de datos** de la arquitectura de tres capas.

## 🎯 Responsabilidad

Los modelos representan la estructura de datos y proporcionan una interfaz orientada a objetos para trabajar con las entidades de la base de datos, **sin contener lógica de negocio**.

## 📂 Estructura

```
models/
├── __init__.py          # Exporta todos los modelos
├── models.py            # Archivo de compatibilidad (importa desde aquí)
├── product.py           # Modelo Product
├── user.py              # Modelo User
├── order.py             # Modelo Order
└── order_item.py       # Modelo OrderItem
```

## 📋 Modelos Disponibles

### **Product**
Representa un producto disponible en la tienda.

**Atributos:**
- `id` (int): Identificador único
- `name` (str): Nombre del producto
- `price` (Decimal): Precio del producto
- `stock` (int): Unidades disponibles en inventario

**Ubicación:** `models/product.py`

### **User**
Representa un usuario del sistema.

**Atributos:**
- `id` (int): Identificador único
- `username` (str): Nombre de usuario (4-20 caracteres)
- `password_hash` (str): Hash de la contraseña (no texto plano)
- `email` (str): Dirección de correo electrónico
- `address` (str): Dirección de envío
- `account_type` (str): Tipo de cuenta ('user' o 'company')
- `role` (str): Rol del usuario ('common' o 'admin')
- `dni` (str): DNI para usuarios individuales
- `nif` (str): NIF para empresas
- `created_at` (datetime): Fecha de creación

**Ubicación:** `models/user.py`

### **Order**
Representa una comanda realizada por un usuario.

**Atributos:**
- `id` (int): Identificador único
- `total` (Decimal): Total de la comanda
- `created_at` (datetime): Fecha y hora de la comanda
- `user_id` (int): ID del usuario que realizó la comanda

**Ubicación:** `models/order.py`

### **OrderItem**
Representa un producto específico dentro de una comanda.

**Atributos:**
- `id` (int): Identificador único
- `order_id` (int): ID de la comanda
- `product_id` (int): ID del producto
- `quantity` (int): Cantidad del producto en la comanda

**Ubicación:** `models/order_item.py`

## 🔗 Relaciones

- Un **User** puede tener muchas **Order**
- Cada **Order** puede contener muchos **OrderItem**
- Cada **OrderItem** referencia un solo **Product**

## 💡 Uso

```python
from models import Product, User, Order, OrderItem

# Crear instancia de modelo
product = Product(id=1, name="iPhone", price=999.99, stock=10)
user = User(id=1, username="usuario", email="user@example.com", ...)
```

## ⚠️ Reglas Importantes

1. **No contiene lógica de negocio**: Los modelos solo representan datos
2. **No accede directamente a la base de datos**: El acceso se hace a través de servicios
3. **Separación de responsabilidades**: Los modelos no conocen cómo se muestran los datos ni cómo se procesan

## 📚 Referencias

- Ver `docs/reglas_techshop.md` para más detalles sobre la arquitectura
- Ver `docs/database_schema.sql` para el esquema completo de la base de datos

