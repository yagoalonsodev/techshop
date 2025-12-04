# Migraciones de Base de Datos - TechShop

## 📁 Descripción

Esta carpeta contiene scripts de migración para actualizar el esquema de la base de datos cuando se añaden nuevas funcionalidades o campos. Las migraciones permiten evolucionar la estructura de la base de datos sin perder datos existentes.

## 🎯 Responsabilidad

Los scripts de migración:
- Modifican el esquema de la base de datos
- Añaden nuevas columnas o tablas
- Migran datos existentes cuando es necesario
- Mantienen la integridad de los datos

## 📂 Estructura

```
migrations/
├── __init__.py                    # Inicialización del módulo
├── migrate_database.py            # Migración general
├── migrate_add_company_id.py      # Añadir campo company_id a Product
└── migrate_add_dni_nif.py         # Añadir campos DNI y NIF a User
```

## 🔧 Migraciones Disponibles

### **migrate_database.py**
Migración general que aplica todas las migraciones pendientes.

**Uso:**
```bash
python3 migrations/migrate_database.py
```

**Funcionalidades:**
- Verifica el estado actual de la base de datos
- Aplica migraciones pendientes en orden
- Registra las migraciones aplicadas

**Ubicación:** `migrations/migrate_database.py`

### **migrate_add_company_id.py**
Añade el campo `company_id` a la tabla `Product` para asociar productos con empresas.

**Cambios:**
- Añade columna `company_id INTEGER` a `Product`
- Establece relación con `User(id)` donde `account_type = 'company'`
- Permite que empresas gestionen sus propios productos

**Ubicación:** `migrations/migrate_add_company_id.py`

### **migrate_add_dni_nif.py**
Añade campos `dni` y `nif` a la tabla `User` para validación fiscal.

**Cambios:**
- Añade columna `dni VARCHAR(20)` para usuarios individuales
- Añade columna `nif VARCHAR(20)` para empresas
- Permite validación de documentos fiscales

**Ubicación:** `migrations/migrate_add_dni_nif.py`

## 💡 Uso

### Ejecutar una migración específica:
```bash
python3 migrations/migrate_add_dni_nif.py
```

### Ejecutar todas las migraciones:
```bash
python3 migrations/migrate_database.py
```

## ⚠️ Notas Importantes

1. **Backup**: Siempre haz backup de la base de datos antes de ejecutar migraciones
2. **Orden**: Las migraciones deben ejecutarse en orden cronológico
3. **Reversibilidad**: Algunas migraciones no son reversibles
4. **Datos existentes**: Las migraciones intentan preservar datos existentes

## 📚 Referencias

- Ver `docs/database_schema.sql` para el esquema completo
- Ver `docs/reglas_techshop.md` para más detalles sobre la base de datos
- Ver `scripts/init_database.py` para inicialización inicial

