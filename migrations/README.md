# Migracions de Base de Dades - TechShop

## 📁 Descripció

Aquesta carpeta conté scripts de migració per actualitzar l'esquema de la base de dades quan s'afegeixen noves funcionalitats o camps. Les migracions permeten evolucionar l'estructura de la base de dades sense perdre dades existents.

## 🎯 Responsabilitat

Els scripts de migració:
- Modifiquen l'esquema de la base de dades
- Afegeixen noves columnes o taules
- Migren dades existents quan és necessari
- Mantenen la integritat de les dades

## 📂 Estructura

```
migrations/
├── __init__.py                    # Inicialització del mòdul
├── migrate_database.py            # Migració general
├── migrate_add_company_id.py      # Afegir camp company_id a Product
└── migrate_add_dni_nif.py         # Afegir camps DNI i NIF a User
```

## 🔧 Migracions Disponibles

### **migrate_database.py**
Migració general que aplica totes les migracions pendents.

**Ús:**
```bash
python3 migrations/migrate_database.py
```

**Funcionalitats:**
- Verifica l'estat actual de la base de dades
- Aplica migracions pendents en ordre
- Registra les migracions aplicades

**Ubicació:** `migrations/migrate_database.py`

### **migrate_add_company_id.py**
Afegeix el camp `company_id` a la taula `Product` per associar productes amb empreses.

**Canvis:**
- Afegeix columna `company_id INTEGER` a `Product`
- Estableix relació amb `User(id)` on `account_type = 'company'`
- Permet que empreses gestionin els seus propis productes

**Ubicació:** `migrations/migrate_add_company_id.py`

### **migrate_add_dni_nif.py**
Afegeix camps `dni` i `nif` a la taula `User` per validació fiscal.

**Canvis:**
- Afegeix columna `dni VARCHAR(20)` per usuaris individuals
- Afegeix columna `nif VARCHAR(20)` per empreses
- Permet validació de documents fiscals

**Ubicació:** `migrations/migrate_add_dni_nif.py`

## 💡 Ús

### Executar una migració específica:
```bash
python3 migrations/migrate_add_dni_nif.py
```

### Executar totes les migracions:
```bash
python3 migrations/migrate_database.py
```

## ⚠️ Notes Importants

1. **Backup**: Sempre fes backup de la base de dades abans d'executar migracions
2. **Ordre**: Les migracions s'han d'executar en ordre cronològic
3. **Reversibilitat**: Algunes migracions no són reversibles
4. **Dades existents**: Les migracions intenten preservar dades existents

## 📚 Referències

- Veure `docs/database_schema.sql` per a l'esquema complet
- Veure `docs/reglas_techshop.md` per a més detalls sobre la base de dades
- Veure `scripts/init_database.py` per a inicialització inicial
