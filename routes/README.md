# Rutas de TechShop

## 📁 Estructura Organizada

Las rutas están organizadas en blueprints de Flask siguiendo buenas prácticas:

```
routes/
├── __init__.py          # Registra todos los blueprints
├── helpers.py           # Funciones auxiliares y decoradores
├── main.py              # Rutas principales (productos, carrito, checkout)
├── auth.py              # Autenticación (login, register, logout, OAuth)
├── profile.py           # Perfil de usuario
├── admin.py             # Panel de administración
├── company.py           # Gestión de productos para empresas
└── utils.py             # Utilidades (idioma, políticas)
```

## 🔄 Estado de Migración

**✅ COMPLETADO**: Todas las rutas han sido migradas a blueprints organizados

**Estructura actual**:
- `app.py`: Solo configuración de Flask, OAuth, context processors y registro de blueprints (~100 líneas)
- `routes/main.py`: Rutas principales (productos, carrito, checkout, órdenes)
- `routes/auth.py`: Autenticación (login, register, logout, OAuth de Google, recuperación de contraseña)
- `routes/profile.py`: Perfil de usuario (ver datos, editar, historial, facturas)
- `routes/admin.py`: Panel de administración (CRUD de productos, usuarios, órdenes)
- `routes/company.py`: Gestión de productos para empresas
- `routes/utils.py`: Utilidades (cambio de idioma, políticas)

**Total**: 37 rutas organizadas en 6 blueprints

### Ventajas de usar Blueprints:

1. **Organización**: Rutas agrupadas por funcionalidad
2. **Mantenibilidad**: Archivos más pequeños y fáciles de navegar
3. **Escalabilidad**: Fácil agregar nuevas rutas
4. **Buenas prácticas**: Sigue estándares de Flask

