#!/bin/bash
# Script de inicio para Render

echo "🔧 Ejecutando migraciones de base de datos..."
python fix_database.py

echo "🔧 Separando tutores compartidos..."
python separar_tutores.py

echo "🚀 Iniciando aplicación..."
gunicorn app:app
