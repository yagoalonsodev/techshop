# 🛒 TechShop - Gestió de Carretó de Compres

Aplicació web per gestionar un carretó de compres per a TechShop, una empresa fictícia que ven productes electrònics en línia.

## 📋 Descripció del Projecte

Aquesta aplicació implementa una botiga en línia completa amb les següents funcionalitats:
- Visualització de catàleg de productes
- Gestió del carretó de compres
- Validacions de stock i quantitat
- Procés de checkout complet
- Confirmació de comandes
- Arquitectura MVC amb tres capes (presentació, lògica de negoci, dades)

## 🏗️ Arquitectura

El projecte segueix el patró **Model-Vista-Controlador (MVC)** amb una arquitectura de **tres capes**:

- **Capa de Presentació**: Templates HTML amb Jinja2 (`templates/`)
- **Capa de Lògica de Negoci**: Serveis (`services/`)
- **Capa de Dades**: Models i base de datos SQLite (`models.py`, `techshop.db`)

## 📁 Estructura del Projecte

```
TechShop/
├── app.py                    # Aplicació principal Flask
├── models.py                 # Classes de dades (Product, User, Order, OrderItem)
├── services/                 # Lògica de negoci
│   ├── cart_service.py      # Gestió del carretó
│   └── order_service.py     # Gestió de comandes
├── templates/                # Plantilles HTML
│   ├── base.html            # Plantilla base
│   ├── products.html        # Catàleg de productes
│   ├── checkout.html        # Pàgina de checkout
│   └── order_confirmation.html # Confirmació de comanda
├── static/                   # Arxius estàtics
│   ├── css/style.css        # Estils CSS
│   └── js/main.js           # JavaScript
├── database_schema.sql       # Esquema de la base de dades
├── init_database.py          # Script per inicialitzar la BD
├── techshop.db              # Base de dades SQLite (es genera)
├── requirements.txt          # Dependències Python
├── .gitignore               # Arxius a ignorar per Git
└── README.md                # Aquest arxiu
```

## 🗃️ Base de Dades

La base de dades SQLite conté quatre taules principals:

### **Product**
- `id`: INTEGER (PK)
- `name`: VARCHAR(100)
- `price`: DECIMAL(10,2)
- `stock`: INTEGER

### **User**
- `id`: INTEGER (PK)
- `username`: VARCHAR(20)
- `password_hash`: VARCHAR(60)
- `email`: VARCHAR(100)
- `created_at`: DATETIME

### **Order**
- `id`: INTEGER (PK)
- `total`: DECIMAL(10,2)
- `created_at`: DATETIME
- `user_id`: INTEGER (FK → User)

### **OrderItem**
- `id`: INTEGER (PK)
- `order_id`: INTEGER (FK → Order)
- `product_id`: INTEGER (FK → Product)
- `quantity`: INTEGER

## 🚀 Instal·lació i Execució

### Prerequisits

- Python 3.8 o superior
- pip (gestor de paquets de Python)

### Passos d'Instal·lació

1. **Clonar o descarregar el repositori**

```bash
cd "1. Practica TechShop"
```

2. **Crear i activar l'entorn virtual**

```bash
# Crear entorn virtual
python3 -m venv venv

# Activar entorn virtual
# En macOS/Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

3. **Instal·lar dependències**

```bash
pip install -r requirements.txt
```

4. **Inicialitzar la base de dades**

```bash
python3 init_database.py
```

Aquest script crearà la base de dades `techshop.db` amb dades de prova (8 productes electrònics).

5. **Executar l'aplicació**

```bash
python3 app.py
```

6. **Accedir a l'aplicació**

Obre el navegador i accedeix a: **http://127.0.0.1:3000**

## 📦 Dependències

Les dependències principals del projecte són:

- **Flask 3.1.2**: Framework web
- **Werkzeug 3.1.3**: Utilitats WSGI i seguretat
- **Jinja2**: Motor de plantilles
- **SQLite3**: Base de dades (inclosa amb Python)

Per veure totes les dependències, consulta `requirements.txt`.

## 🎯 Funcionalitats Principals

### 1. Catàleg de Productes
- Visualització de tots els productes disponibles
- Informació de preu i stock
- Formulari per afegir al carretó

### 2. Gestió del Carretó
- Afegir productes (màxim 5 unitats per producte)
- Eliminar productes del carretó
- Validació de stock disponible
- Càlcul automàtic del total

### 3. Checkout
- Formulari amb validacions:
  - Nom d'usuari: 4-20 caràcters
  - Contrasenya: mínim 8 caràcters (amb hash segur)
  - Email: format vàlid
  - Adreça d'enviament: obligatòria
- Validacions HTML5 i servidor

### 4. Confirmació de Comanda
- Pàgina de confirmació amb detalls de la comanda
- ID de comanda únic
- Detall dels productes comprats

## 🔒 Validacions Implementades

### Frontend (HTML5)
- Camps obligatoris (`required`)
- Longitud mínima/màxima (`minlength`, `maxlength`)
- Tipus de dades (`type="email"`, `type="number"`)
- Rangs numèrics (`min`, `max`)
- Patrons de validació (`pattern`)

### Backend (Python)
- Validació de quantitats (1-5 unitats)
- Verificació de stock disponible
- Validació de dades d'usuari
- Control d'errors amb missatges clars
- Prevenció d'injeccions SQL (prepared statements)

## ⚠️ Regles de Negoci

1. **Límit de quantitat**: Màxim 5 unitats del mateix producte al carretó
2. **Validació de stock**: No es pot afegir més quantitat de la disponible
3. **Actualització d'inventari**: L'stock es redueix automàticament després de cada compra
4. **Seguretat de contrasenyes**: Les contrasenyes s'emmagatzemen amb hash bcrypt

## 🧪 Dades de Prova

Després d'executar `init_database.py`, la base de dades conté 8 productes:

- MacBook Pro 14" (1.999,00 €)
- iPhone 15 Pro (1.199,00 €)
- iPad Air (649,00 €)
- Apple Watch Series 9 (429,00 €)
- AirPods Pro (279,00 €)
- Magic Keyboard (349,00 €)
- Sony WH-1000XM5 (399,00 €)
- Samsung Galaxy S24 (899,00 €)

## 🛠️ Desenvolupament

### Estructura de Codi

- **Separació de responsabilitats**: Cada capa té una responsabilitat clara
- **Serveis reutilitzables**: La lògica de negoci està en serveis independents
- **Models de dades**: Classes Python que representen les entitats de la BD
- **Plantilles**: HTML amb Jinja2, sense lògica de negoci

### Millores Futures

- [ ] Sistema d'autenticació d'usuaris persistent
- [ ] Historial de comandes per usuari
- [ ] Cerca i filtratge de productes
- [ ] Sistema de valoracions i comentaris
- [ ] Passarel·la de pagament
- [ ] Panel d'administració

## 📝 Documentació Addicional

- `reglas_techshop.md`: Regles i requisits de la pràctica
- `memoria_ia.md`: Documentació de l'ús d'IA en el desenvolupament
- `ESTRUCTURA_FINAL.md`: Detalls de l'estructura final del projecte

## 👤 Autor

Aquest projecte ha estat desenvolupat com a pràctica per a l'assignatura **5073. Programació d'Intel·ligència Artificial**.

## 📄 Llicència

Aquest projecte és amb finalitats educatives.

---

**Data de creació**: Octubre 2024  
**Versió**: 1.0

