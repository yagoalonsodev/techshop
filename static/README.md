# Recursos Estáticos - TechShop

## 📁 Descripción

Esta carpeta contiene todos los recursos estáticos de la aplicación: archivos CSS, JavaScript e imágenes. Estos recursos son servidos directamente por Flask sin procesamiento del servidor.

## 🎯 Responsabilidad

Los recursos estáticos proporcionan:
- Estilos visuales (CSS)
- Interactividad del cliente (JavaScript)
- Imágenes y assets visuales

## 📂 Estructura

```
static/
├── css/
│   └── style.css           # Estilos principales de la aplicación
│
├── js/
│   └── main.js             # JavaScript principal
│
└── img/
    ├── carrito/
    │   └── 1.png           # Icono del carrito
    ├── logout/
    │   └── 1.png           # Icono de logout
    ├── flags/               # Banderas de idiomas
    │   ├── cat/1.svg       # Bandera catalana
    │   ├── esp/1.png       # Bandera española
    │   └── eng/1.png       # Bandera inglesa
    └── products/            # Imágenes de productos
        └── {product_id}/   # Carpeta por ID de producto
            ├── 1.jpg       # Primera imagen (principal)
            ├── 2.png       # Segunda imagen
            ├── 3.png       # Tercera imagen
            └── 4.png       # Cuarta imagen (máximo 4)
```

## 🎨 CSS (style.css)

### Características:
- Variables CSS para colores, espaciado y tipografía
- Diseño responsive
- Estilos para formularios, botones, tarjetas
- Efectos hover y transiciones
- Sistema de colores consistente

### Variables principales:
```css
--color-primary
--color-secondary
--color-success
--color-danger
--spacing-unit
--border-radius
```

## 📜 JavaScript (main.js)

### Funcionalidades:
- Validación de formularios en cliente
- Validación de DNI/NIE/CIF en tiempo real
- Manejo de eventos del carrito
- Actualización dinámica de imágenes en detalle de producto
- Comunicación entre ventanas (políticas de privacidad)
- Cambio de idioma

### Validaciones implementadas:
- `validarDNI(dni)`: Validación de DNI español
- `validarNIE(nie)`: Validación de NIE
- `validarCIF(cif)`: Validación de CIF

## 🖼️ Imágenes

### Estructura de imágenes de productos:
- **Ubicación**: `static/img/products/{product_id}/`
- **Formato**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- **Nomenclatura**: `1.ext`, `2.ext`, `3.ext`, `4.ext`
- **Máximo**: 4 imágenes por producto
- **Principal**: La primera imagen (orden alfabético) se muestra como principal

### Ejemplo:
```
static/img/products/1/
├── 1.jpg    # Imagen principal
├── 2.png    # Miniatura
├── 3.png    # Miniatura
└── 4.png    # Miniatura
```

### Procesamiento:
- Las imágenes se comprimen al 80% al subirlas (empresas)
- Se renombran automáticamente como `idfoto.ext`

## 💡 Uso en Templates

```jinja2
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- JavaScript -->
<script src="{{ url_for('static', filename='js/main.js') }}"></script>

<!-- Imágenes -->
<img src="{{ url_for('static', filename='img/products/1/1.jpg') }}" alt="Producto">

<!-- Banderas de idioma -->
<img src="{{ url_for('static', filename='img/flags/cat/1.svg') }}" alt="Català">
```

## ⚠️ Reglas Importantes

1. **No lógica de negocio**: JavaScript solo para validaciones y UX
2. **Validaciones dobles**: Las validaciones del cliente deben repetirse en el servidor
3. **Optimización**: Imágenes comprimidas para mejor rendimiento
4. **Organización**: Estructura clara por tipo de recurso

## 📚 Referencias

- Ver `docs/reglas_techshop.md` sección 4 para validaciones del frontend
- Ver `templates/` para ver cómo se usan los recursos estáticos

