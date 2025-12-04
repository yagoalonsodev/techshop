# Rutes de TechShop

## 📁 Estructura Organitzada

Les rutes estan organitzades en blueprints de Flask seguint bones pràctiques:

```
routes/
├── __init__.py          # Registra tots els blueprints
├── helpers.py           # Funcions auxiliars i decoradors
├── main.py              # Rutes principals (productes, carretó, checkout)
├── auth.py              # Autenticació (login, register, logout, OAuth)
├── profile.py           # Perfil d'usuari
├── admin.py             # Panell d'administració
├── company.py           # Gestió de productes per empreses
└── utils.py             # Utilitats (idioma, polítiques)
```

## 🔄 Estat de Migració

**✅ COMPLETAT**: Totes les rutes han estat migrades a blueprints organitzats

**Estructura actual**:
- `app.py`: Només configuració de Flask, OAuth, context processors i registre de blueprints (~100 línies)
- `routes/main.py`: Rutes principals (productes, carretó, checkout, ordres)
- `routes/auth.py`: Autenticació (login, register, logout, OAuth de Google, recuperació de contrasenya)
- `routes/profile.py`: Perfil d'usuari (veure dades, editar, historial, factures)
- `routes/admin.py`: Panell d'administració (CRUD de productes, usuaris, ordres)
- `routes/company.py`: Gestió de productes per empreses
- `routes/utils.py`: Utilitats (canvi d'idioma, polítiques)

**Total**: 37 rutes organitzades en 6 blueprints

### Avantatges d'usar Blueprints:

1. **Organització**: Rutes agrupades per funcionalitat
2. **Mantenibilitat**: Arxius més petits i fàcils de navegar
3. **Escalabilitat**: Fàcil afegir noves rutes
4. **Bones pràctiques**: Segueix estàndards de Flask
