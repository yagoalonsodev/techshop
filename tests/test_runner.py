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
    """Recopila todos los tests de todos los módulos"""
    all_tests = []
    
    # Tests de modelos
    all_tests.extend([
        ("BD - Inicialización", test_models.test_db_init),
        ("Modelo - Product", test_models.test_product),
        ("Modelo - User", test_models.test_user),
        ("Modelo - User (created_at por defecto)", test_models.test_user_created_at_default),
        ("Modelo - Order", test_models.test_order),
        ("Modelo - Order (created_at por defecto)", test_models.test_order_created_at_default),
        ("Modelo - OrderItem", test_models.test_orderitem),
    ])
    
    # Tests de CartService
    cart_tests = [attr for attr in dir(test_cart_service) if attr.startswith('test_')]
    for test_name in cart_tests:
        test_func = getattr(test_cart_service, test_name)
        display_name = test_name.replace('test_', '').replace('_', ' ').title()
        all_tests.append((f"Cart - {display_name}", test_func))
    
    # Tests de OrderService
    order_tests = [attr for attr in dir(test_order_service) if attr.startswith('test_')]
    for test_name in order_tests:
        test_func = getattr(test_order_service, test_name)
        display_name = test_name.replace('test_', '').replace('_', ' ').title()
        all_tests.append((f"Order - {display_name}", test_func))
    
    # Tests de UserService
    user_tests = [attr for attr in dir(test_user_service) if attr.startswith('test_')]
    for test_name in user_tests:
        test_func = getattr(test_user_service, test_name)
        display_name = test_name.replace('test_user_service_', '').replace('_', ' ').title()
        all_tests.append((f"UserService - {display_name}", test_func))
    
    # Tests de ProductService
    product_tests = [attr for attr in dir(test_product_service) if attr.startswith('test_')]
    for test_name in product_tests:
        test_func = getattr(test_product_service, test_name)
        display_name = test_name.replace('test_product_service_', '').replace('_', ' ').title()
        all_tests.append((f"ProductService - {display_name}", test_func))
    
    # Tests de AdminService
    admin_tests = [attr for attr in dir(test_admin_service) if attr.startswith('test_')]
    for test_name in admin_tests:
        test_func = getattr(test_admin_service, test_name)
        display_name = test_name.replace('test_admin_service_', '').replace('_', ' ').title()
        all_tests.append((f"AdminService - {display_name}", test_func))
    
    # Tests de CompanyService
    company_tests = [attr for attr in dir(test_company_service) if attr.startswith('test_')]
    for test_name in company_tests:
        test_func = getattr(test_company_service, test_name)
        display_name = test_name.replace('test_company_', '').replace('test_company_service_', '').replace('_', ' ').title()
        all_tests.append((f"CompanyService - {display_name}", test_func))
    
    # Tests de RecommendationService
    rec_tests = [attr for attr in dir(test_recommendation_service) if attr.startswith('test_')]
    for test_name in rec_tests:
        test_func = getattr(test_recommendation_service, test_name)
        display_name = test_name.replace('test_recommendations_', '').replace('_', ' ').title()
        all_tests.append((f"Recommendation - {display_name}", test_func))
    
    # Tests de Validators
    validator_tests = [attr for attr in dir(test_validators) if attr.startswith('test_')]
    for test_name in validator_tests:
        test_func = getattr(test_validators, test_name)
        display_name = test_name.replace('test_validator_', '').replace('test_', '').replace('_', ' ').title()
        all_tests.append((f"Validator - {display_name}", test_func))
    
    # Tests de Web Routes
    web_tests = [attr for attr in dir(test_web_routes) if attr.startswith('test_')]
    for test_name in web_tests:
        test_func = getattr(test_web_routes, test_name)
        display_name = test_name.replace('test_web_', '').replace('_', ' ').title()
        all_tests.append((f"Web - {display_name}", test_func))
    
    # Tests de Security
    security_tests = [attr for attr in dir(test_security) if attr.startswith('test_')]
    for test_name in security_tests:
        test_func = getattr(test_security, test_name)
        display_name = test_name.replace('test_security_', '').replace('_', ' ').title()
        all_tests.append((f"Security - {display_name}", test_func))
    
    # Tests de Integration
    integration_tests = [attr for attr in dir(test_integration) if attr.startswith('test_')]
    for test_name in integration_tests:
        test_func = getattr(test_integration, test_name)
        display_name = test_name.replace('test_', '').replace('_', ' ').title()
        all_tests.append((f"Integration - {display_name}", test_func))
    
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

