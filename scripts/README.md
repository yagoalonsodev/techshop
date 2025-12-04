# Scripts d'Utilitat - TechShop

## 📁 Descripció

Aquesta carpeta conté scripts executables d'utilitat per a la gestió i manteniment de l'aplicació. Aquests scripts s'executen des de la línia de comandes i faciliten tasques administratives i de configuració.

## 🎯 Responsabilitat

Els scripts proporcionen funcionalitats de:
- Inicialització de la base de dades
- Creació d'usuaris administradors
- Generació de dades de prova
- Tasques de manteniment

## 📂 Estructura

```
scripts/
├── __init__.py              # Inicialització del mòdul
├── init_database.py         # Inicialitzar base de dades amb dades de prova
├── create_admin_user.py     # Crear usuari administrador
└── generate_dataset.py      # Generar dataset de compres per anàlisi
```

## 🔧 Scripts Disponibles

### **init_database.py**
Inicialitza la base de dades amb l'esquema complet i dades de prova.

**Ús:**
```bash
python3 scripts/init_database.py
```

**Funcionalitats:**
- Crea totes les taules necessàries
- Insereix productes d'exemple (8 productes electrònics)
- Configura l'estructura inicial de la base de dades

**Ubicació:** `scripts/init_database.py`

### **create_admin_user.py**
Crea un usuari administrador al sistema.

**Ús:**
```bash
python3 scripts/create_admin_user.py
```

**Funcionalitats:**
- Crea usuari amb rol `admin`
- Genera contrasenya automàticament
- Mostra credencials en consola

**Ubicació:** `scripts/create_admin_user.py`

### **generate_dataset.py**
Genera un dataset de compres per anàlisi de dades.

**Ús:**
```bash
python3 scripts/generate_dataset.py
```

**Funcionalitats:**
- Genera dades de compres simulades
- Exporta a CSV per anàlisi
- Útil per proves del sistema de recomanacions

**Ubicació:** `scripts/generate_dataset.py`

## 💡 Execució

Tots els scripts s'han d'executar des de l'arrel del projecte:

```bash
# Des de l'arrel del projecte
python3 scripts/init_database.py
python3 scripts/create_admin_user.py
python3 scripts/generate_dataset.py
```

## ⚠️ Notes Importants

1. **Base de dades**: Alguns scripts modifiquen la base de dades, usa'ls amb precaució
2. **Entorn virtual**: Assegura't de tenir l'entorn virtual activat
3. **Permisos**: Alguns scripts requereixen permisos d'escriptura a la base de dades

## 📚 Referències

- Veure `docs/reglas_techshop.md` per a més detalls sobre la base de dades
- Veure `migrations/` per a scripts de migració d'esquema
