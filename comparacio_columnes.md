# Comparació de Columnes: Dataset vs Schema de Base de Dades

## Columnes del Schema Original (database_schema.sql)

### Tabla Product:
- `id` → En dataset: **`product_id`**
- `name` → En dataset: **`product_name`**
- `price` → En dataset: **`product_price`**
- `stock` → En dataset: **`product_stock`**

### Tabla User:
- `id` → En dataset: **`user_id`**
- `username` → En dataset: **`username`** ✅
- `password_hash` → ❌ No inclosa (no és rellevant per experiències de compra)
- `email` → En dataset: **`user_email`**
- `address` → ❌ No inclosa (podria afegir-se)
- `created_at` → En dataset: **`user_registration_date`**

### Tabla Order:
- `id` → En dataset: **`order_id`**
- `total` → En dataset: **`order_total`**
- `created_at` → En dataset: **`order_date`**
- `user_id` → En dataset: **`user_id`**

### Tabla OrderItem:
- `id` → ❌ No inclosa (no és necessària per l'anàlisi)
- `order_id` → En dataset: **`order_id`**
- `product_id` → En dataset: **`product_id`**
- `quantity` → En dataset: **`quantity`** ✅

## Resum de Correspondència

### ✅ Columnes del Schema que ESTAN al Dataset (11 columnes):

1. **`order_id`** ← Order.id
2. **`order_date`** ← Order.created_at
3. **`order_total`** ← Order.total
4. **`user_id`** ← Order.user_id / User.id
5. **`username`** ← User.username
6. **`user_email`** ← User.email
7. **`user_registration_date`** ← User.created_at
8. **`product_id`** ← OrderItem.product_id / Product.id
9. **`product_name`** ← Product.name
10. **`product_price`** ← Product.price
11. **`product_stock`** ← Product.stock
12. **`quantity`** ← OrderItem.quantity

### ❌ Columnes del Schema que NO estan al Dataset:

- `password_hash` (User) - No és necessària per experiències de compra
- `address` (User) - No s'ha inclòs (però es podria afegir)
- `id` (OrderItem) - No és necessària per l'anàlisi

### ➕ Columnes AÑADIDES al Dataset (13 columnes):

1. **`user_age`** - Afegida per anàlisi demogràfica
2. **`days_since_registration`** - Calculada (mesura fidelitat)
3. **`product_category`** - Afegida per segmentació
4. **`item_subtotal`** - Calculada (preu × quantitat)
5. **`rating`** - Afegida per anàlisi de satisfacció
6. **`payment_method`** - Afegida per anàlisi de preferències
7. **`shipping_method`** - Afegida per anàlisi logística
8. **`discount_applied`** - Afegida per anàlisi promocional
9. **`is_weekend`** - Derivada temporal
10. **`day_of_week`** - Derivada temporal
11. **`month`** - Derivada temporal
12. **`hour`** - Derivada temporal

## Conclusió

**El dataset NO té exactament les mateixes columnes que el schema**, però:

- ✅ **Sí inclou totes les columnes rellevants** del schema per analitzar experiències de compra
- ✅ **Afegeix columnes addicionals** per enriquir l'anàlisi (com es va demanar en els requeriments: "entre 15 i 20 columnes")
- ✅ **Omet columnes no rellevants** per aquest propòsit (com `password_hash`)

Això és correcte perquè el dataset d'**experiències de compres** és un dataset denormalitzat que combina informació de múltiples taules del schema original per facilitar l'anàlisi.

