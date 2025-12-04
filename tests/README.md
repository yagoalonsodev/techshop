# Tests de TechShop

## 📁 Estructura Organizada

Los tests han sido organizados siguiendo las **buenas prácticas de Python** y la estructura del proyecto:

```
tests/
├── __init__.py                    # Inicialización del paquete
├── test_common.py                 # Utilidades compartidas (MockSession, Colors, asserts)
├── test_models.py                 # Tests de modelos (Product, User, Order, OrderItem)
├── test_cart_service.py           # Tests de CartService
├── test_order_service.py          # Tests de OrderService
├── test_user_service.py           # Tests de UserService
├── test_product_service.py        # Tests de ProductService
├── test_admin_service.py          # Tests de AdminService
├── test_company_service.py        # Tests de CompanyService
├── test_recommendation_service.py # Tests de RecommendationService
├── test_validators.py             # Tests de validadores (DNI, NIE, CIF)
├── test_web_routes.py             # Tests de rutas Flask (integración web)
├── test_security.py               # Tests de seguridad (XSS, SQL injection, etc.)
├── test_integration.py            # Tests end-to-end e integración
└── test_runner.py                 # Ejecutor principal de todos los tests
```

## 🚀 Ejecutar Tests

### Ejecutar todos los tests (recomendado):
```bash
# Desde la raíz del proyecto:
python3 tests/run_tests.py

# O usando el script bash:
bash tests/run_tests.sh

# O desde dentro de la carpeta tests:
cd tests && python3 run_tests.py
```

### Ejecutar directamente el test runner:
```bash
python3 -m tests.test_runner
```

### Ejecutar un módulo específico:
```bash
# Ejemplo: solo tests de CartService
python -c "from tests import test_cart_service; import tests.test_common as tc; tc.init_test_db(); [tc.run_test(name.replace('test_', ''), getattr(test_cart_service, name)) for name in dir(test_cart_service) if name.startswith('test_')]"
```

### Ejecutar un test específico:
```python
from tests.test_common import *
from tests import test_cart_service

init_test_db()
run_test("Cart - Agregar producto", test_cart_service.test_cart_add)
```

## 📊 Ventajas de esta Organización

1. **Mantenibilidad**: Archivos más pequeños y fáciles de navegar
2. **Organización**: Refleja la estructura del código fuente
3. **Ejecución selectiva**: Puedes ejecutar solo los tests de un módulo
4. **Escalabilidad**: Fácil agregar nuevos tests
5. **Buenas prácticas**: Sigue estándares de Python y testing

## 📝 Notas

- Todos los tests usan `test.db` como base de datos de prueba (se crea y elimina automáticamente)
- Las utilidades comunes están en `test_common.py`
- El test runner (`test_runner.py`) ejecuta todos los tests y muestra un resumen

## 📝 Scripts de Ejecución

- `tests/run_tests.py`: Script principal para ejecutar todos los tests (recomendado)
- `tests/run_tests.sh`: Script bash alternativo
- `tests/test_runner.py`: Ejecutor interno de tests (usado por los scripts anteriores)

