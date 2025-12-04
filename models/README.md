# Models de Dades - TechShop

## 📁 Descripció

Aquesta carpeta conté les classes de dades que representen les entitats de la base de dades, seguint el patró **Model** de l'arquitectura MVC i la **capa de dades** de l'arquitectura de tres capes.

## 🎯 Responsabilitat

Els models representen l'estructura de dades i proporcionen una interfície orientada a objectes per treballar amb les entitats de la base de dades, **sense contenir lògica de negoci**.

## 📂 Estructura

```
models/
├── __init__.py          # Exporta tots els models
├── models.py            # Arxiu de compatibilitat (importa des d'aquí)
├── product.py           # Model Product
├── user.py              # Model User
├── order.py             # Model Order
└── order_item.py       # Model OrderItem
```

## 📋 Models Disponibles

### **Product**
Representa un producte disponible a la botiga.

**Atributs:**
- `id` (int): Identificador únic
- `name` (str): Nom del producte
- `price` (Decimal): Preu del producte
- `stock` (int): Unitats disponibles en inventari

**Ubicació:** `models/product.py`

### **User**
Representa un usuari del sistema.

**Atributs:**
- `id` (int): Identificador únic
- `username` (str): Nom d'usuari (4-20 caràcters)
- `password_hash` (str): Hash de la contrasenya (no text pla)
- `email` (str): Adreça de correu electrònic
- `address` (str): Adreça d'enviament
- `account_type` (str): Tipus de compte ('user' o 'company')
- `role` (str): Rol de l'usuari ('common' o 'admin')
- `dni` (str): DNI per usuaris individuals
- `nif` (str): NIF per empreses
- `created_at` (datetime): Data de creació

**Ubicació:** `models/user.py`

### **Order**
Representa una comanda realitzada per un usuari.

**Atributs:**
- `id` (int): Identificador únic
- `total` (Decimal): Total de la comanda
- `created_at` (datetime): Data i hora de la comanda
- `user_id` (int): ID de l'usuari que va realitzar la comanda

**Ubicació:** `models/order.py`

### **OrderItem**
Representa un producte específic dins d'una comanda.

**Atributs:**
- `id` (int): Identificador únic
- `order_id` (int): ID de la comanda
- `product_id` (int): ID del producte
- `quantity` (int): Quantitat del producte en la comanda

**Ubicació:** `models/order_item.py`

## 🔗 Relacions

- Un **User** pot tenir moltes **Order**
- Cada **Order** pot contenir molts **OrderItem**
- Cada **OrderItem** referencia un sol **Product**

## 💡 Ús

```python
from models import Product, User, Order, OrderItem

# Crear instància de model
product = Product(id=1, name="iPhone", price=999.99, stock=10)
user = User(id=1, username="usuari", email="user@example.com", ...)
```

## ⚠️ Regles Importants

1. **No conté lògica de negoci**: Els models només representen dades
2. **No accedeix directament a la base de dades**: L'accés es fa a través de serveis
3. **Separació de responsabilitats**: Els models no coneixen com es mostren les dades ni com es processen

## 📚 Referències

- Veure `docs/reglas_techshop.md` per a més detalls sobre l'arquitectura
- Veure `docs/database_schema.sql` per a l'esquema complet de la base de dades
