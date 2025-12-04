#!/bin/bash
# Script para ejecutar todos los tests de TechShop
# Uso: ./tests/run_tests.sh o desde la raíz: bash tests/run_tests.sh

cd "$(dirname "$0")" || exit 1
python3 run_tests.py

