# Recursos Estàtics - TechShop

## 📁 Descripció

Aquesta carpeta conté tots els recursos estàtics de l'aplicació: arxius CSS, JavaScript i imatges. Aquests recursos són servits directament per Flask sense processament del servidor.

## 🎯 Responsabilitat

Els recursos estàtics proporcionen:
- Estils visuals (CSS)
- Interactivitat del client (JavaScript)
- Imatges i assets visuals

## 📂 Estructura

```
static/
├── css/
│   └── style.css           # Estils principals de l'aplicació
│
├── js/
│   └── main.js             # JavaScript principal
│
└── img/
    ├── carrito/
    │   └── 1.png           # Icona del carretó
    ├── logout/
    │   └── 1.png           # Icona de logout
    ├── flags/               # Banderes d'idiomes
    │   ├── cat/1.svg       # Bandera catalana
    │   ├── esp/1.png       # Bandera espanyola
    │   └── eng/1.png       # Bandera anglesa
    └── products/            # Imatges de productes
        └── {product_id}/   # Carpeta per ID de producte
            ├── 1.jpg       # Primera imatge (principal)
            ├── 2.png       # Segona imatge
            ├── 3.png       # Tercera imatge
            └── 4.png       # Quarta imatge (màxim 4)
```

## 🎨 CSS (style.css)

### Característiques:
- Variables CSS per colors, espaiat i tipografia
- Disseny responsive
- Estils per formularis, botons, targetes
- Efectes hover i transicions
- Sistema de colors consistent

### Variables principals:
```css
--color-primary
--color-secondary
--color-success
--color-danger
--spacing-unit
--border-radius
```

## 📜 JavaScript (main.js)

### Funcionalitats:
- Validació de formularis en client
- Validació de DNI/NIE/CIF en temps real
- Maneig d'esdeveniments del carretó
- Actualització dinàmica d'imatges en detall de producte
- Comunicació entre finestres (polítiques de privacitat)
- Canvi d'idioma

### Validacions implementades:
- `validarDNI(dni)`: Validació de DNI espanyol
- `validarNIE(nie)`: Validació de NIE
- `validarCIF(cif)`: Validació de CIF

## 🖼️ Imatges

### Estructura d'imatges de productes:
- **Ubicació**: `static/img/products/{product_id}/`
- **Format**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- **Nomenclatura**: `1.ext`, `2.ext`, `3.ext`, `4.ext`
- **Màxim**: 4 imatges per producte
- **Principal**: La primera imatge (ordre alfabètic) es mostra com a principal

### Exemple:
```
static/img/products/1/
├── 1.jpg    # Imatge principal
├── 2.png    # Miniatura
├── 3.png    # Miniatura
└── 4.png    # Miniatura
```

### Processament:
- Les imatges es comprimeixen al 80% en pujar-les (empreses)
- Es renombren automàticament com `idfoto.ext`

## 💡 Ús en Plantilles

```jinja2
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- JavaScript -->
<script src="{{ url_for('static', filename='js/main.js') }}"></script>

<!-- Imatges -->
<img src="{{ url_for('static', filename='img/products/1/1.jpg') }}" alt="Producte">

<!-- Banderes d'idioma -->
<img src="{{ url_for('static', filename='img/flags/cat/1.svg') }}" alt="Català">
```

## ⚠️ Regles Importants

1. **No lògica de negoci**: JavaScript només per validacions i UX
2. **Validacions dobles**: Les validacions del client han de repetir-se en el servidor
3. **Optimització**: Imatges comprimides per millor rendiment
4. **Organització**: Estructura clara per tipus de recurs

## 📚 Referències

- Veure `docs/reglas_techshop.md` secció 4 per a validacions del frontend
- Veure `templates/` per a veure com s'usen els recursos estàtics
