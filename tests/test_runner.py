#!/usr/bin/env python3
"""
Test Runner para ejecutar todos los tests organizados por módulo
Sigue las buenas prácticas de organización de tests
"""
import os
import sys
from tests.test_common import (
    Colors, run_test, reset_test_counters, get_test_stats,
    init_test_db, cleanup_test_db
)

# Importar todos los módulos de test
from tests import test_models
from tests import test_cart_service
from tests import test_order_service
from tests import test_user_service
from tests import test_product_service
from tests import test_admin_service
from tests import test_company_service
from tests import test_recommendation_service
from tests import test_validators
from tests import test_web_routes
from tests import test_security
from tests import test_integration


def collect_all_tests():
    """Recopila todos los tests de todos los módulos de forma dinámica"""
    all_tests = []
    
    # Mapeo de módulos a prefijos de categoría
    test_modules = [
        (test_models, "Models"),
        (test_cart_service, "Cart"),
        (test_order_service, "Order"),
        (test_user_service, "UserService"),
        (test_product_service, "ProductService"),
        (test_admin_service, "AdminService"),
        (test_company_service, "CompanyService"),
        (test_recommendation_service, "Recommendation"),
        (test_validators, "Validator"),
        (test_web_routes, "Web"),
        (test_security, "Security"),
        (test_integration, "Integration"),
    ]
    
    for test_module, category_prefix in test_modules:
        # Encontrar todas las funciones que empiezan con 'test_'
        test_functions = [
            attr for attr in dir(test_module) 
            if attr.startswith('test_') and callable(getattr(test_module, attr))
        ]
        
        for test_name in test_functions:
            try:
                test_func = getattr(test_module, test_name)
                # Crear nombre legible para el display
                display_name = test_name.replace('test_', '')
                # Remover prefijos comunes
                for prefix in ['user_service_', 'product_service_', 'admin_service_', 
                              'company_service_', 'company_', 'recommendations_', 
                              'validator_', 'web_', 'security_']:
                    if display_name.startswith(prefix):
                        display_name = display_name[len(prefix):]
                        break
                display_name = display_name.replace('_', ' ').title()
                all_tests.append((f"{category_prefix} - {display_name}", test_func))
            except AttributeError:
                # Si no se puede obtener la función, saltarla
                continue
    
    return all_tests


def main():
    """Función principal para ejecutar todos los tests"""
    print(f"\n{Colors.BOLD}{'='*80}\n🧪 TEST RUNNER - TECHSHOP\n{'='*80}{Colors.END}\n")
    
    # Inicializar contadores
    reset_test_counters()
    
    # Inicializar base de datos de prueba
    init_test_db()
    
    try:
        # Recopilar todos los tests
        all_tests = collect_all_tests()
        
        print(f"{Colors.BLUE}📋 Ejecutando {len(all_tests)} tests organizados por módulo...{Colors.END}\n")
        
        # Ejecutar todos los tests
        for name, test_func in all_tests:
            run_test(name, test_func)
        
        # Mostrar resumen
        stats = get_test_stats()
        print(f"\n{Colors.BOLD}{'='*80}\n📊 RESUMEN DE PRUEBAS\n{'='*80}{Colors.END}")
        print(f"Total de pruebas: {stats['total']}")
        print(f"{Colors.GREEN}✅ Pruebas exitosas: {stats['passed']}{Colors.END}")
        print(f"{Colors.RED}❌ Pruebas fallidas: {stats['failed']}{Colors.END}")
        if stats['total'] > 0:
            print(f"{Colors.YELLOW}📈 Porcentaje de éxito: {stats['success_rate']:.1f}%{Colors.END}")
        
        print(f"\n{Colors.BOLD}{'='*80}")
        if stats['failed'] == 0:
            print(f"{Colors.GREEN}🎉 ¡TODAS LAS PRUEBAS PASARON!{Colors.END}")
        else:
            print(f"{Colors.RED}⚠️  HAY {stats['failed']} PRUEBAS FALLIDAS{Colors.END}")
        print(f"{'='*80}{Colors.END}\n")
        
        return stats['failed'] == 0
        
    finally:
        # Limpiar base de datos de prueba
        cleanup_test_db()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

