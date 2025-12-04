# Estructura del Proyecto TechShop

## 📁 Organización de Carpetas

```
TechShop/
├── models/              # Modelos de datos (Product, User, Order, OrderItem)
├── routes/              # Rutas HTTP (estructura preparada)
├── services/            # Lógica de negocio
├── templates/           # Plantillas HTML
├── static/              # Recursos estáticos (CSS, JS, imágenes)
├── utils/               # Utilidades (validadores, email, traducciones)
├── tests/               # Tests organizados por módulo
│   ├── run_tests.py     # Script para ejecutar todos los tests
│   ├── run_tests.sh     # Script bash para ejecutar tests
│   ├── test_runner.py   # Runner principal de tests
│   ├── test_common.py   # Utilidades comunes para tests
│   └── test_*.py        # Tests organizados por módulo
├── scripts/             # Scripts de utilidad
│   ├── init_database.py
│   ├── create_admin_user.py
│   └── generate_dataset.py
├── migrations/          # Scripts de migración de BD
│   ├── migrate_database.py
│   ├── migrate_add_company_id.py
│   └── migrate_add_dni_nif.py
├── docs/                # Documentación
│   ├── memoria.md
│   ├── reglas_techshop.md
│   ├── comparacio_columnes.md
│   ├── database_schema.sql
│   ├── diagrama_clases.xml
│   └── img/             # Imágenes de documentación
├── data/                # Archivos de datos
│   └── techshop_purchase_experiences.csv
├── notebooks/           # Notebooks de análisis
│   └── analisi_dataset.ipynb
├── app.py               # Aplicación principal Flask
├── models.py            # Compatibilidad (importa desde models/)
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno (no versionado)
└── techshop.db          # Base de datos SQLite (no versionado)
```

## 🎯 Principios de Organización

### Separación de Responsabilidades
- **models/**: Clases de datos (capa de datos)
- **services/**: Lógica de negocio (capa de negocio)
- **routes/**: Rutas HTTP (capa de control)
- **templates/**: Vistas HTML (capa de presentación)

### Organización por Tipo
- **scripts/**: Scripts ejecutables de utilidad
- **migrations/**: Scripts de migración de base de datos
- **docs/**: Documentación del proyecto
- **data/**: Archivos de datos
- **notebooks/**: Análisis y experimentación

### Buenas Prácticas
- Cada carpeta tiene su `__init__.py` cuando corresponde
- Archivos relacionados están agrupados
- La raíz del proyecto está limpia (solo archivos esenciales)
- Estructura escalable y mantenible

