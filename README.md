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
│   ├── js/main.js           # JavaScript
│   └── img/
│       └── products/        # Carpeta per a les imatges dels productes (per ID)
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

## 📷 Imatges de producte

La botiga suporta fins a **4 fotografies per producte**. Per afegir o actualitzar les imatges:

1. Crea una carpeta per ID dins de `static/img/products/`.  
   Exemple: `static/img/products/1/` per al producte amb ID 1.
2. Afegeix fins a quatre arxius d'imatge (`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`).  
   L'ordre alfabètic dels noms determina quina imatge es mostra com a principal.
3. Refresca la pàgina de productes: la primera imatge es mostra gran i la resta apareixen com a miniatures sota la principal.

Aquesta organització evita barrejar lògica de negoci i presentació, i manté les imatges accessibles des de la capa estàtica (`/static`).

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

## 🧪 Test Cases

El projecte inclou un script exhaustiu de proves (`test_everything.py`) que valida totes les funcionalitats de l'aplicació. El script conté **80 test cases** organitzats en diferents categories.

### Executar els Tests

Per executar tots els test cases:

```bash
python3 test_everything.py
```

El script mostrarà un resum amb el nombre total de proves, les que han passat i les que han fallat, juntament amb un percentatge d'èxit.

### Categories de Test Cases

#### 1. Base de Dades i Models (7 tests)

- **BD - Inicialització**: Verifica la creació correcta de les taules de la base de dades
- **Modelo - Product**: Valida la creació i propietats del model Product
- **Modelo - User**: Valida la creació i propietats del model User
- **Modelo - User (created_at per defecte)**: Verifica que `created_at` s'assigna automàticament
- **Modelo - Order**: Valida la creació i propietats del model Order
- **Modelo - Order (created_at per defecte)**: Verifica que `created_at` s'assigna automàticament
- **Modelo - OrderItem**: Valida la creació i propietats del model OrderItem

#### 2. Gestió del Carretó (Cart Service) (17 tests)

- **Cart - Afegir producte**: Verifica l'addició bàsica de productes al carretó
- **Cart - Afegir producte diverses vegades respecta límit i stock**: Valida que múltiples crides respecten el límit de 5 unitats i el stock disponible
- **Cart - Stock insuficient**: Rebutja quantitats que excedeixen el stock disponible
- **Cart - Stock igual al disponible**: Permet afegir exactament el stock disponible
- **Cart - Límit 5 unitats**: Rebutja quantitats que excedeixen el límit de 5 unitats
- **Cart - Límit 5 unitats (borde exacte)**: Valida el límit exacte de 5 unitats
- **Cart - Quantitat negativa**: Rebutja quantitats negatives
- **Cart - Quantitat zero**: Rebutja quantitats zero
- **Cart - Quantitat no entera**: Rebutja valors no enters
- **Cart - Eliminar producte**: Verifica l'eliminació de productes del carretó
- **Cart - Eliminar inexistent**: Gestiona correctament l'eliminació de productes que no existeixen
- **Cart - Afegir producte inexistent**: Rebutja productes que no existeixen a la base de dades
- **Cart - Error de BD en validate_stock**: Gestiona errors de base de dades
- **Cart - Obtenir contingut**: Retorna correctament el contingut del carretó
- **Cart - Obtenir contingut amb múltiples productes**: Gestiona múltiples productes amb quantitats correctes
- **Cart - Calcular total**: Calcula correctament el total del carretó
- **Cart - Calcular total amb producte inexistent**: Ignora productes que ja no existeixen
- **Cart - Netejar carretó**: Buida correctament el carretó (idempotent)

#### 3. Gestió de Comandes (Order Service) (15 tests)

- **Order - Crear comanda**: Crea correctament una nova comanda
- **Order - Crear comanda deixa stock en zero**: Verifica que el stock arriba a zero quan s'utilitza tot
- **Order - Carretó buit**: Rebutja la creació de comandes amb carretó buit
- **Order - Carretó amb quantitats zero**: Tracta correctament quantitats zero al calcular el total
- **Order - Usuari no trobat**: Rebutja comandes per usuaris inexistents
- **Order - Calcular total**: Calcula correctament el total de la comanda
- **Order - Calcular total amb preus decimals**: Gestiona correctament preus amb decimals
- **Order - Calcular total ignora productes inexistents**: Ignora productes que no existeixen
- **Order - Obtenir per ID**: Retorna correctament una comanda per ID
- **Order - Comanda inexistent**: Gestiona correctament comandes que no existeixen
- **Order - ID negatiu no retorna comanda**: Rebutja IDs negatius
- **Order - Actualitzar inventari**: Redueix correctament el stock després de la comanda
- **Order (TX) - Carretó buit**: Valida transaccions amb carretó buit
- **Order (TX) - Usuari no trobat**: Valida transaccions amb usuari inexistent
- **Order - Error de BD al crear comanda**: Gestiona errors de base de dades

#### 4. Validacions de Formulari (9 tests)

- **Validació - Username longitud**: Valida que el nom d'usuari tingui entre 4 i 20 caràcters
- **Validació - Username casos límit**: Prova casos límit de longitud (massa curt, massa llarg)
- **Validació - Password longitud**: Valida longitud mínima de 8 caràcters
- **Validació - Password complexitat**: Requereix lletres i números
- **Validació - Email**: Valida format bàsic d'email (conté @ i domini amb punt)
- **Validació - Email casos límit**: Prova correus amb subdominis, sense TLD, amb múltiples @
- **Validació - Direcció**: Requereix mínim 10 caràcters
- **Validació - Direcció molt llarga**: Accepta adreces llargues que superin el mínim
- **Validació - Camps obligatoris**: Verifica que tots els camps obligatoris estiguin omplerts

#### 5. Seguretat de Contrasenyes (9 tests)

- **Password - Generar hash**: Genera hash segur de contrasenyes
- **Password - Verificar hash**: Verifica correctament contrasenyes vàlides
- **Password - Verificar password incorrecte**: Rebutja contrasenyes incorrectes
- **Password - Hashes diferents mateix password**: Cada hash és únic (salts diferents)
- **Password - Amb símbols segueix sent vàlida**: Accepta contrasenyes amb símbols que compleixen les regles
- **Password - Regles rebutgen buida i simples**: Rebutja contrasenyes buides, només lletres o només números
- **Password - Hash manipulat no verifica**: Rebutja hashes que han estat manipulats
- **Password - Text pla en password_hash és rebutjat**: No accepta contrasenyes en text pla com a hash vàlid

#### 6. Sistema de Recomanacions (12 tests)

- **Recomanacions - Ordenar per vendes**: Ordena productes per unitats venudes
- **Recomanacions - Desempat per nom**: En cas d'empat, ordena alfabèticament per nom
- **Recomanacions - Límit zero**: Retorna llista buida amb límit 0
- **Recomanacions - Límit negatiu**: Retorna llista buida amb límit negatiu
- **Recomanacions - Sense vendes**: Retorna llista buida quan no hi ha vendes
- **Recomanacions - Límit major que nombre de productes**: Retorna només els productes disponibles
- **Recomanacions - Per usuari**: Retorna recomanacions personalitzades per usuari
- **Recomanacions - Per usuari amb límit zero**: Retorna llista buida amb límit 0 per usuari
- **Recomanacions - Per usuari amb límit negatiu**: Retorna llista buida amb límit negatiu per usuari
- **Recomanacions - Usuari sense compres**: Retorna llista buida per usuaris sense comandes
- **Recomanacions - user_id None**: Gestiona correctament user_id None
- **Recomanacions - Error de BD retorna buida**: Retorna llista buida en cas d'error de base de dades

#### 7. Tests d'Integració Web (Flask) (5 tests)

- **Web - GET / (productes)**: La pàgina principal de productes carrega correctament
- **Web - GET /checkout amb carretó buit**: Mostra missatge adequat quan el carretó està buit
- **Web - POST /add_to_cart sense CSRF ha de fallar**: Protecció CSRF activa
- **Web - POST /process_order sense camps obligatoris no crea comanda**: Validació de camps obligatoris
- **Web - Flux complet de checkout crea comanda i buida carretó**: Flux complet de compra funcional

### Resum de Test Cases

- **Total de test cases**: 80
- **Cobertura**: Models, Serveis, Validacions, Seguretat, Recomanacions i Integració Web
- **Tipus de proves**: Unitàries, d'integració i end-to-end
- **Gestió d'errors**: Tests específics per errors de BD, valors invàlids i casos límit

Tots els tests utilitzen una base de dades de prova (`test.db`) que es crea i s'elimina automàticament durant l'execució, assegurant que no s'afecti la base de dades principal de l'aplicació.

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

