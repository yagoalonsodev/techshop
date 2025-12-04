# Reglas de la Práctica TechShop

## 1. Contexto y Objetivos Generales

**Pràctica: TechShop**

Aquesta pràctica té com a objectiu que desenvolupis una petita aplicació web per gestionar un carretó de compres per a TechShop, una empresa fictícia que ven productes electrònics en línia. Aprendràs a aplicar el patró Model-Vista-Controlador (MVC) i l'arquitectura en tres capes (presentació, lògica de negoci i dades) utilitzant Python amb el micro-framework Flask i una base de dades SQLite com a sistema gestor lliure.

### Objectivos de Aprendizaje:

- **Comprendre la importància de separar responsabilitats** entre la vista (front-end), la lògica de negoci i l'accés a dades.
- **Dissenyar i implementar una base de dades senzilla** per gestionar productes, comandes i detalls de comanda.
- **Crear rutes i serveis a Flask** que encapsulin la lògica de negoci sense barrejar codi de presentació.
- **Aplicar validacions tant al servidor com al client** per garantir la coherència i integritat de les dades.
- **Integrar una eina d'intel·ligència artificial** com a assistent en la codificació i documentar l'ús que se n'ha fet.

## Reglas Generales

*[Contenido pendiente de recibir]*

## 2. Diseño de la Base de Datos y Diagrama Entidad-Relación

Per dur a terme aquesta pràctica, necessites definir un esquema de base de dades que permeti emmagatzemar els productes que ven TechShop, les comandes que fan els usuaris i els detalls de cada comanda. Utilitzarem SQLite perquè és senzill de configurar i no requereix instal·lació de servidor.

### Taulas Principales:

#### **Product** - Gestiona la llista de productes disponibles
- `id`: INTEGER, clau primària, autoincremental
- `name`: VARCHAR(100), nom del producte
- `price`: DECIMAL(10,2), preu del producte
- `stock`: INTEGER, unitats disponibles en inventari

#### **User** - Conté la informació de l'usuari que fa la compra
- `id`: INTEGER, clau primària, autoincremental
- `username`: VARCHAR(20), nom d'usuari (entre 4 i 20 caràcters)
- `password_hash`: VARCHAR(60), contrasenya codificada de manera segura (no s'emmagatzema la contrasenya en text pla)
- `email`: VARCHAR(100), adreça de correu electrònic
- `created_at`: DATETIME, data i hora de creació del compte

#### **Order** - Representa cada comanda realitzada
- `id`: INTEGER, clau primària, autoincremental
- `total`: DECIMAL(10,2), total de la comanda
- `created_at`: DATETIME, data i hora de la comanda
- `user_id`: INTEGER, clau forana que apunta a User(id)

#### **OrderItem** - Especifica els productes que formen part d'una comanda
- `id`: INTEGER, clau primària, autoincremental
- `order_id`: INTEGER, clau forana cap a Order(id)
- `product_id`: INTEGER, clau forana cap a Product(id)
- `quantity`: INTEGER, quantitat d'aquest producte en la comanda

### Relaciones:
- Un **User** pot tenir moltes comandes (**Order**)
- Cada **Order** pot contenir molts elements (**OrderItem**)
- Cada **OrderItem** referencia un sol **Product**

## Reglas de Base de Datos

*[Contenido pendiente de recibir]*

## 3. Lógica de Negocio y Rutas

La tercera pàgina hauria de descriure detalladament la lògica de negoci i com s'implementen les rutes a Flask sense barrejar codi de presentació ni d'accés a dades.

### Funciones Clave de Lógica de Negocio:

#### **add_to_cart(product_id, quantity)**
- Afegir un producte al carretó
- Comprova que la quantitat sigui un enter positiu
- Verifica que no superi el límit de 5 unitats del mateix producte
- Si la suma de quantitats existents al carretó i la nova quantitat sobrepassa el límit, es llançarà una excepció o es retornarà un missatge d'error

#### **remove_from_cart(product_id)**
- Eliminar un producte del carretó
- Aquesta funció no ha de conèixer detalls sobre com es mostra el carretó

#### **validate_stock(product_id, quantity)**
- Abans d'afegir al carretó, comprova que hi hagi prou stock disponible a la taula Product
- Si no n'hi ha suficient, informa l'usuari

#### **create_order(cart, user_id)**
- Quan l'usuari finalitza la compra, aquesta funció calcula el total de la comanda sumant price * quantity de cada producte
- Actualitza l'inventari restant les unitats comprades
- Emmagatzema la nova comanda i les seves línies a les taules Order i OrderItem

### Rutas HTTP:

#### **show_products()**
- Ruta que obté tots els productes de la base de dades
- Els passa a la capa de presentació

#### **checkout()**
- Ruta que mostra el resum del carretó i un formulari per introduir dades de l'usuari
- Crida a create_order() si l'usuari confirma la compra

### Organización del Código:

Per mantenir el codi net, és recomanable organitzar-lo en mòduls:

- **models.py**: Per definir les classes de dades
- **services/**: Per la lògica de negoci (per exemple, order_service.py, cart_service.py)
- **routes.py** o **controllers.py**: Per definir les rutes HTTP

### Documentación:

- Cada funció ha de tenir **docstrings** explicant els seus paràmetres, validacions i possibles excepcions

## Reglas de Implementación

*[Contenido pendiente de recibir]*

## 4. Validaciones del Frontend y Entrega del Proyecto

En aquesta quarta pàgina descriu les validacions que has d'implementar a la capa de presentació i els requisits per al lliurament.

### Validaciones del Frontend:

#### **Formulario de Checkout**
El formulari de checkout ha de contenir com a mínim els camps:
- **username**: entre 4 i 20 caràcters
- **password**: mínim 8 caràcters
- **adreça de correu electrònic**
- **adreça d'enviament**

#### **Atributos HTML de Validación**
Utilitza atributs HTML per validar les dades a nivell de client:
- `required`: camps obligatoris
- `minlength`: longitud mínima
- `maxlength`: longitud màxima
- `pattern`: patró de validació

#### **Campos Numéricos**
- Els camps numèrics (com la quantitat) han d'utilitzar l'element `<input type='number'>`
- Amb el rang adequat (1–5) per evitar valors no vàlids

#### **Manejo de Errores**
- Envia els errors de validació de manera clara a l'usuari
- Sense revelar informació interna del servidor

### Estructura del Proyecto:

Estructura el projecte en carpetes:
- `/models`: Classes de dades
- `/services`: Lògica de negoci
- `/routes` o `/controllers`: Rutes HTTP
- `/templates`: Plantilles HTML
- `/static`: Fitxers CSS/JS

### Documentación del Proyecto:

Inclou un fitxer **README.md** amb:
- Instruccions per executar l'aplicació
- Dependències necessàries
- Captures de pantalla

### Entrega del Proyecto:

- Entrega el projecte en un **repositori**
- Que contingui tot el codi
- La memoria final de la práctica en un **únic document per separat**

## 5. Uso de la Inteligencia Artificial y Requisitos Adicionales

La darrera secció està dedicada a l'ús de la intel·ligència artificial (IA) com a recurs per a la realització de la pràctica.

### Aplicaciones de la IA en el Proyecto:

#### **Generación de Código**
- Generar esbossos de codi o fragments que compleixin els requisits de l'arquitectura MVC i de les tres capes
- Quan facis una petició a la IA, defineix clarament les regles:
  - "No barregis la lògica de negoci amb la presentació"
  - "Limita la quantitat del carretó a 5 unitats"
  - "Utilitza noms de funcions en anglès seguint snake_case"

#### **Revisión de Código**
- Pots demanar a la IA que avaluï si la teva funció add_to_cart respecta les restriccions
- Verificar si hi ha punts febles de seguretat
- Interpretar la resposta i aplicar les millores suggerides

#### **Optimización**
- Obtenir suggeriments d'optimització:
  - Com gestionar l'estat del carretó de manera eficient
  - Com implementar un patró repositori per accedir a la base de dades

### Documentación del Uso de IA:

En la memòria, inclou una secció amb:
- **Transcripcions** de les peticions i respostes que hagis considerat útils
- **Reflexió** sobre com la IA t'ha ajudat i quins límits té
- **Criteri crític** aplicat (no t'has limitat a copiar i enganxar)

### Reglas Establecidas para la IA:

Has d'especificar clarament quines regles has establert a la IA per assegurar que no es vulnerin els principis de l'arquitectura:

- **No barrejar el codi HTML** amb consultes SQL o lògica de negoci
- **Tots els accessos a la base de dades** s'han de fer a través de funcions o mètodes específics en la capa de dades
- **No superar les 5 unitats** per producte al carretó
- **Validar sempre les dades** rebudes des del client abans de processar-les

### Evaluación Integral:

Aquesta pràctica no només avalua la part tècnica sinó també:
- La teva capacitat de treballar de manera **responsable** amb eines d'IA
- D'explicar el **raonament** darrere de les teves decisions
- De respectar els **estàndards de desenvolupament professional**

## Reglas de Evaluación

*[Contenido pendiente de recibir]*

---

*Documento completado con todos los apartados de la práctica TechShop.*
