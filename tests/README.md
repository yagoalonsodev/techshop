# Tests de TechShop

## 📁 Estructura Organitzada

Els tests han estat organitzats seguint les **bones pràctiques de Python** i l'estructura del projecte:

```
tests/
├── __init__.py                    # Inicialització del paquet
├── test_common.py                 # Utilitats compartides (MockSession, Colors, asserts)
├── test_models.py                 # Tests de models (Product, User, Order, OrderItem)
├── test_cart_service.py           # Tests de CartService
├── test_order_service.py          # Tests de OrderService
├── test_user_service.py           # Tests de UserService
├── test_product_service.py        # Tests de ProductService
├── test_admin_service.py          # Tests de AdminService
├── test_company_service.py        # Tests de CompanyService
├── test_recommendation_service.py # Tests de RecommendationService
├── test_validators.py             # Tests de validadors (DNI, NIE, CIF)
├── test_web_routes.py             # Tests de rutes Flask (integració web)
├── test_security.py               # Tests de seguretat (XSS, SQL injection, etc.)
├── test_integration.py            # Tests end-to-end i integració
└── test_runner.py                 # Executor principal de tots els tests
```

## 🚀 Executar Tests

### Executar tots els tests (recomanat):
```bash
# Des de l'arrel del projecte:
python3 tests/run_tests.py

# O usant el script bash:
bash tests/run_tests.sh

# O des de dins de la carpeta tests:
cd tests && python3 run_tests.py
```

### Executar directament el test runner:
```bash
python3 -m tests.test_runner
```

### Executar un mòdul específic:
```bash
# Exemple: només tests de CartService
python -c "from tests import test_cart_service; import tests.test_common as tc; tc.init_test_db(); [tc.run_test(name.replace('test_', ''), getattr(test_cart_service, name)) for name in dir(test_cart_service) if name.startswith('test_')]"
```

### Executar un test específic:
```python
from tests.test_common import *
from tests import test_cart_service

init_test_db()
run_test("Cart - Afegir producte", test_cart_service.test_cart_add)
```

## 📊 Avantatges d'aquesta Organització

1. **Mantenibilitat**: Arxius més petits i fàcils de navegar
2. **Organització**: Reflecteix l'estructura del codi font
3. **Execució selectiva**: Pots executar només els tests d'un mòdul
4. **Escalabilitat**: Fàcil afegir nous tests
5. **Bones pràctiques**: Segueix estàndards de Python i testing

## 📝 Notes

- Tots els tests usen `test.db` com a base de dades de prova (es crea i s'elimina automàticament)
- Les utilitats comunes estan a `test_common.py`
- El test runner (`test_runner.py`) executa tots els tests i mostra un resum

## 📝 Scripts d'Execució

- `tests/run_tests.py`: Script principal per executar tots els tests (recomanat)
- `tests/run_tests.sh`: Script bash alternatiu
- `tests/test_runner.py`: Executor intern de tests (usat pels scripts anteriors)
