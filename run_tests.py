#!/usr/bin/env python3
"""
Script para ejecutar todos los tests de TechShop
Ejecuta: python run_tests.py
"""
import sys
import os

# Asegurar que el directorio actual está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ejecutar el test runner
if __name__ == '__main__':
    from tests.test_runner import main
    success = main()
    sys.exit(0 if success else 1)

