"""
Script per generar un dataset d'experiències de compres per TechShop
Genera un CSV amb entre 15-20 columnes i mínim 100k registres
AMB DADES UNA MICA SUCIES per simular problemes reals de qualitat de dades
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuració
NUM_REGISTRES = 130000  # Generem 130k per tenir ~100k després de la neteja
OUTPUT_FILE = 'techshop_purchase_experiences.csv'

# Semilla per reproduïbilitat
random.seed(42)
np.random.seed(42)

print(f"🚀 Generant dataset amb {NUM_REGISTRES:,} registres...")

# Productes EXACTES de la base de dades TechShop (de init_database.py)
PRODUCTES = [
    ("MacBook Pro 14\"", 1999.00, "Portàtils"),
    ("iPhone 15 Pro", 1199.00, "Telèfons"),
    ("iPad Air", 649.00, "Tabletes"),
    ("Apple Watch Series 9", 429.00, "Rellotges"),
    ("AirPods Pro", 279.00, "Auriculars"),
    ("Magic Keyboard", 349.00, "Accessoris"),
    ("Sony WH-1000XM5", 399.00, "Auriculars"),
    ("Samsung Galaxy S24", 899.00, "Telèfons"),
    ("Dell XPS 13", 1299.00, "Portàtils"),
    ("Logitech MX Master 3", 99.00, "Accessoris"),
]

# Mètodes de pagament
PAYMENT_METHODS = ["Targeta de Crèdit", "PayPal", "Transferència", "Bizum", "Targeta de Dèbit"]

# Mètodes d'enviament
SHIPPING_METHODS = ["Estàndard (3-5 dies)", "Express (1-2 dies)", "Premium (24h)", "Recollida a botiga"]

# Generar dades
print("📊 Generant dades...")

# Dates: últims 3 anys
start_date = datetime.now() - timedelta(days=1095)
date_range = (datetime.now() - start_date).days

data = []

for i in range(NUM_REGISTRES):
    # Seleccionar producte aleatori
    product = random.choice(PRODUCTES)
    product_name, base_price, category = product
    
    # ID de producte (1-10, ja que només tenim 10 productes de la BD)
    product_id = PRODUCTES.index(product) + 1
    
    # Informació de l'usuari
    user_id = random.randint(1, 5000)  # 5000 usuaris diferents
    username = f"user_{user_id:04d}"
    email = f"user{user_id}@email.com"
    
    # Data de registre de l'usuari (abans de la comanda)
    days_before_order = random.randint(0, 1095)
    user_registration_date = start_date + timedelta(days=random.randint(0, days_before_order))
    days_since_registration = (start_date + timedelta(days=days_before_order) - user_registration_date).days
    
    # Informació de la comanda
    order_id = random.randint(1, 80000)  # Aproximadament 80000 comandes
    order_date = start_date + timedelta(days=random.randint(0, date_range))
    
    # Quantitat (1-5, amb major probabilitat per quantitats baixes)
    quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.4, 0.3, 0.15, 0.1, 0.05])
    
    # Preu amb variació lleugera (descomptes ocasionales)
    discount_probability = random.random()
    if discount_probability < 0.15:  # 15% de productes amb descompte
        discount = random.uniform(0.05, 0.25)  # Descompte entre 5% i 25%
        product_price = base_price * (1 - discount)
        discount_applied = True
    else:
        product_price = base_price
        discount_applied = False
    
    # Stock aleatori (0-100)
    product_stock = random.randint(0, 100)
    
    # Subtotal del item
    item_subtotal = product_price * quantity
    
    # Total de la comanda (simplificat: item_subtotal * factor aleatori per simular múltiples items)
    items_in_order = random.randint(1, 5)
    order_total = item_subtotal * random.uniform(1.0, items_in_order * 0.8)
    
    # Rating (1-5, distribució normal amb mitjana 4.2)
    # PERÒ: introduir errors (5% de ratings fora de rang: 0, 6-10)
    rating_prob = random.random()
    if rating_prob < 0.05:  # 5% de ratings invàlids
        rating = random.choice([0, 6, 7, 8, 9, 10])  # Valors fora de rang
    elif rating_prob < 0.08:  # 3% de valors nuls
        rating = None
    else:
        rating = max(1, min(5, int(np.random.normal(4.2, 0.8))))
    
    # Mètodes de pagament i enviament
    # PERÒ: introduir valors nuls (7% i 5% respectivament)
    if random.random() < 0.07:
        payment_method = None
    else:
        payment_method = random.choice(PAYMENT_METHODS)
    
    if random.random() < 0.05:
        shipping_method = None
    else:
        shipping_method = random.choice(SHIPPING_METHODS)
    
    # Característiques temporals (només is_weekend per reduir columnes)
    day_of_week = order_date.weekday()  # 0=Lunes, 6=Domingo
    is_weekend = 1 if day_of_week >= 5 else 0
    
    # Edat de l'usuari (derivada, 18-75 anys)
    # PERÒ: introduir errors (3% fora de rang, 4% nuls)
    age_prob = random.random()
    if age_prob < 0.03:  # 3% fora de rang
        user_age = random.choice([15, 16, 17, 76, 77, 78, 100, 120])  # Edats invàlides
    elif age_prob < 0.07:  # 4% nuls
        user_age = None
    else:
        user_age = random.randint(18, 75)
    
    # INTRODUIR ERRORS EN QUANTITAT (2% de quantitats <= 0)
    if random.random() < 0.02:
        quantity = random.choice([0, -1, -2])
    
    # INTRODUIR ERRORS EN PREUS (1% de preus negatius)
    if random.random() < 0.01:
        product_price = -abs(product_price * random.uniform(0.1, 0.5))
    
    # INTRODUIR ERRORS EN STOCK (2% de stock negatiu)
    if random.random() < 0.02:
        product_stock = random.randint(-10, -1)
    
    # INTRODUIR INCONSISTÈNCIES EN SUBTOTAL (3% de casos on subtotal != preu × quantitat)
    if random.random() < 0.03:
        # Subtotal incorrecte (diferència del 5-20%)
        error_factor = random.uniform(0.8, 1.2)
        item_subtotal = product_price * quantity * error_factor
    else:
        item_subtotal = product_price * quantity
    
    # INTRODUIR ERRORS EN ORDER_TOTAL (2% de totals negatius)
    if random.random() < 0.02:
        order_total = -abs(order_total * random.uniform(0.1, 0.3))
    
    # INTRODUIR ERRORS EN DAYS_SINCE_REGISTRATION (1% de valors negatius)
    if random.random() < 0.01:
        days_since_registration = random.randint(-30, -1)
    
    # Truncar valors de text a 3 caràcters
    product_name_trunc = product_name[:3] if product_name else ""
    category_trunc = category[:3] if category else ""
    payment_method_trunc = payment_method[:3] if payment_method else None
    shipping_method_trunc = shipping_method[:3] if shipping_method else None
    
    # Afegir registre (REDUÏM COLUMNES: eliminem username, user_email, day_of_week, month, hour)
    data.append({
        'order_id': order_id,
        'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
        'order_total': round(order_total, 2),
        'user_id': user_id,
        'user_age': user_age,
        'user_registration_date': user_registration_date.strftime('%Y-%m-%d'),
        'days_since_registration': days_since_registration,
        'product_id': product_id,
        'product_name': product_name_trunc,
        'product_category': category_trunc,
        'product_price': round(product_price, 2),
        'product_stock': product_stock,
        'quantity': quantity,
        'item_subtotal': round(item_subtotal, 2),
        'rating': rating,
        'payment_method': payment_method_trunc,
        'shipping_method': shipping_method_trunc,
        'discount_applied': discount_applied,
        'is_weekend': is_weekend
    })
    
    if (i + 1) % 10000 == 0:
        print(f"  ✓ Generats {i + 1:,} registres...")

# Crear DataFrame
print("\n📦 Creant DataFrame...")
df = pd.DataFrame(data)

# Reordenar columnes per tenir un ordre lògic (15-20 columnes)
columns_order = [
    'order_id', 'order_date', 'order_total',
    'user_id', 'user_age', 
    'user_registration_date', 'days_since_registration',
    'product_id', 'product_name', 'product_category',
    'product_price', 'product_stock', 'quantity', 'item_subtotal',
    'rating', 'payment_method', 'shipping_method', 'discount_applied',
    'is_weekend'
]

df = df[columns_order]

# INTRODUIR DUPLICATS (1.5% de registres duplicats)
print("\n⚠️  Introduint dades sucies...")
num_duplicats = int(len(df) * 0.015)
indices_duplicar = random.sample(range(len(df)), num_duplicats)
duplicats = df.iloc[indices_duplicar].copy()
df = pd.concat([df, duplicats], ignore_index=True)
print(f"  ✓ Afegits {num_duplicats:,} registres duplicats")

# INTRODUIR VALORS NULS ADICIONALS EN ALTRES COLUMNES (5% en product_category)
null_indices = df.sample(frac=0.05, random_state=42).index
df.loc[null_indices, 'product_category'] = None
print(f"  ✓ Afegits valors nuls a product_category ({len(null_indices):,} registres)")

# INTRODUIR ERRORS DE FORMAT EN DATES (1% de dates mal formatejades o invàlides)
date_error_indices = df.sample(frac=0.01, random_state=43).index
df.loc[date_error_indices, 'order_date'] = df.loc[date_error_indices, 'order_date'].apply(
    lambda x: random.choice(['2024-13-45', 'invalid-date', '2024/02/30', '']) if random.random() < 0.5 else x
)
print(f"  ✓ Afegits errors de format en dates ({len(date_error_indices):,} registres)")

# TRUNCAR TOTS ELS VALORS DE TEXT A 3 CARÀCTERS (després de totes les modificacions)
print(f"\n✂️  Truncant tots els valors de text a 3 caràcters...")
df['product_name'] = df['product_name'].apply(lambda x: str(x)[:3] if pd.notna(x) and str(x) != 'None' else x)
df['product_category'] = df['product_category'].apply(lambda x: str(x)[:3] if pd.notna(x) and str(x) != 'None' else x)
df['payment_method'] = df['payment_method'].apply(lambda x: str(x)[:3] if pd.notna(x) and str(x) != 'None' else x)
df['shipping_method'] = df['shipping_method'].apply(lambda x: str(x)[:3] if pd.notna(x) and str(x) != 'None' else x)
print(f"  ✓ Tots els valors de text truncats a 3 caràcters")

# Guardar a CSV
print(f"\n💾 Guardant dataset a {OUTPUT_FILE}...")
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

print(f"\n✅ Dataset generat correctament!")
print(f"📊 Total de registres: {len(df):,}")
print(f"📋 Total de columnes: {len(df.columns)}")
print(f"📁 Arxius generat: {OUTPUT_FILE}")

# Estadístiques de qualitat de dades (dades sucies)
print(f"\n⚠️  ESTADÍSTIQUES DE QUALITAT DE DADES (dades sucies):")
print(f"  - Valors nuls totals: {df.isnull().sum().sum():,}")
print(f"  - Registres duplicats: {df.duplicated().sum():,}")
print(f"  - Ratings fora de rang [1-5]: {((df['rating'] < 1) | (df['rating'] > 5)).sum():,}")
print(f"  - Edats fora de rang [18-75]: {((df['user_age'] < 18) | (df['user_age'] > 75)).sum():,}")
print(f"  - Quantitats <= 0: {(df['quantity'] <= 0).sum():,}")
print(f"  - Preus negatius: {(df['product_price'] < 0).sum():,}")
print(f"  - Stock negatiu: {(df['product_stock'] < 0).sum():,}")
print(f"  - Totals negatius: {(df['order_total'] < 0).sum():,}")

print(f"\n📈 Estadístiques bàsiques:")
print(f"  - Rang de dates: {df['order_date'].min()} a {df['order_date'].max()}")
print(f"  - Usuaris únics: {df['user_id'].nunique():,}")
print(f"  - Productes únics: {df['product_id'].nunique()}")
print(f"  - Comandes úniques: {df['order_id'].nunique():,}")
valid_order_totals = df[df['order_total'] > 0]['order_total']
if len(valid_order_totals) > 0:
    print(f"  - Preu mitjà de comanda: {valid_order_totals.mean():.2f}€")
valid_ratings = df[(df['rating'] >= 1) & (df['rating'] <= 5)]['rating']
if len(valid_ratings) > 0:
    print(f"  - Rating mitjà: {valid_ratings.mean():.2f}")