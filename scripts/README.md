# Scripts de Utilidad - TechShop

## 📁 Descripción

Esta carpeta contiene scripts ejecutables de utilidad para la gestión y mantenimiento de la aplicación. Estos scripts se ejecutan desde la línea de comandos y facilitan tareas administrativas y de configuración.

## 🎯 Responsabilidad

Los scripts proporcionan funcionalidades de:
- Inicialización de la base de datos
- Creación de usuarios administradores
- Generación de datos de prueba
- Tareas de mantenimiento

## 📂 Estructura

```
scripts/
├── __init__.py              # Inicialización del módulo
├── init_database.py         # Inicializar base de datos con datos de prueba
├── create_admin_user.py     # Crear usuario administrador
└── generate_dataset.py      # Generar dataset de compras para análisis
```

## 🔧 Scripts Disponibles

### **init_database.py**
Inicializa la base de datos con el esquema completo y datos de prueba.

**Uso:**
```bash
python3 scripts/init_database.py
```

**Funcionalidades:**
- Crea todas las tablas necesarias
- Inserta productos de ejemplo (8 productos electrónicos)
- Configura la estructura inicial de la base de datos

**Ubicación:** `scripts/init_database.py`

### **create_admin_user.py**
Crea un usuario administrador en el sistema.

**Uso:**
```bash
python3 scripts/create_admin_user.py
```

**Funcionalidades:**
- Crea usuario con rol `admin`
- Genera contraseña automáticamente
- Muestra credenciales en consola

**Ubicación:** `scripts/create_admin_user.py`

### **generate_dataset.py**
Genera un dataset de compras para análisis de datos.

**Uso:**
```bash
python3 scripts/generate_dataset.py
```

**Funcionalidades:**
- Genera datos de compras simuladas
- Exporta a CSV para análisis
- Útil para pruebas del sistema de recomendaciones

**Ubicación:** `scripts/generate_dataset.py`

## 💡 Ejecución

Todos los scripts deben ejecutarse desde la raíz del proyecto:

```bash
# Desde la raíz del proyecto
python3 scripts/init_database.py
python3 scripts/create_admin_user.py
python3 scripts/generate_dataset.py
```

## ⚠️ Notas Importantes

1. **Base de datos**: Algunos scripts modifican la base de datos, úsalos con precaución
2. **Entorno virtual**: Asegúrate de tener el entorno virtual activado
3. **Permisos**: Algunos scripts requieren permisos de escritura en la base de datos

## 📚 Referencias

- Ver `docs/reglas_techshop.md` para más detalles sobre la base de datos
- Ver `migrations/` para scripts de migración de esquema

