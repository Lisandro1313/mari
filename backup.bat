@echo off
echo ============================================================
echo     BACKUP SISTEMA MARI/MATECA
echo ============================================================
echo.

REM Crear carpeta de backups si no existe
if not exist "backups" mkdir backups

REM Obtener fecha y hora
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set mytime=%%a%%b)

REM Crear backup de la base de datos
set backup_file=backups\mari_backup_%mydate%_%mytime%.db
copy mari.db "%backup_file%" > nul

if %ERRORLEVEL% == 0 (
    echo [OK] Backup creado: %backup_file%
    echo.
    echo Backups disponibles:
    dir /b backups\*.db
) else (
    echo [ERROR] No se pudo crear el backup
)

echo.
echo ============================================================
pause
