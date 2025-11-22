@echo off
echo ========================================
echo MARI - Sistema de Registro Municipal
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
    echo.
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo.

REM Instalar dependencias
echo Instalando/Actualizando dependencias...
pip install -r requirements.txt
echo.

REM Ejecutar la aplicación
echo Iniciando servidor MARI...
echo.
python app.py

pause
