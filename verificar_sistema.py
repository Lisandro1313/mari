"""
Script de verificación del sistema MARI/MATECA
Verifica la integridad de la base de datos y la configuración
"""
import sqlite3
import os

def verificar_base_datos():
    """Verifica que la base de datos esté correctamente configurada"""
    print("=" * 60)
    print("VERIFICACIÓN DEL SISTEMA MARI/MATECA")
    print("=" * 60)
    
    db_path = 'mari.db'
    
    if not os.path.exists(db_path):
        print("❌ ERROR: Base de datos no encontrada")
        print("   Ejecuta el servidor una vez para crear la base de datos")
        return False
    
    print("✅ Base de datos encontrada")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [t[0] for t in cursor.fetchall()]
        
        tablas_requeridas = ['tutores', 'atenciones', 'turnos']
        print(f"\n📋 Tablas encontradas: {', '.join(tablas)}")
        
        for tabla in tablas_requeridas:
            if tabla in tablas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {tabla}: {count} registros")
            else:
                print(f"   ❌ Falta tabla: {tabla}")
        
        # Verificar índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indices = [i[0] for i in cursor.fetchall()]
        print(f"\n🔍 Índices creados: {len(indices)}")
        
        # Verificar integridad
        cursor.execute("PRAGMA integrity_check")
        integridad = cursor.fetchone()[0]
        if integridad == "ok":
            print("✅ Integridad de la base de datos: OK")
        else:
            print(f"❌ Problema de integridad: {integridad}")
        
        # Estadísticas generales
        cursor.execute("SELECT COUNT(*) FROM atenciones WHERE tipo_atencion='castracion'")
        castraciones = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM atenciones WHERE tipo_atencion='atencion_primaria'")
        atenciones_primarias = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tutores")
        tutores_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM turnos WHERE estado='pendiente'")
        turnos_pendientes = cursor.fetchone()[0]
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   • Castraciones: {castraciones}")
        print(f"   • Atenciones primarias: {atenciones_primarias}")
        print(f"   • Tutores registrados: {tutores_count}")
        print(f"   • Turnos pendientes: {turnos_pendientes}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    print("\n📁 VERIFICACIÓN DE ARCHIVOS:")
    
    archivos_requeridos = {
        'app.py': 'Aplicación principal',
        'database.py': 'Manejo de base de datos',
        'requirements.txt': 'Dependencias',
        'runtime.txt': 'Versión de Python',
        'Procfile': 'Configuración Render',
        'render.yaml': 'Configuración Render',
        'templates/index.html': 'Página principal',
        'templates/login.html': 'Página de login',
        'static/style.css': 'Estilos CSS',
        'static/script.js': 'JavaScript'
    }
    
    for archivo, descripcion in archivos_requeridos.items():
        if os.path.exists(archivo):
            print(f"   ✅ {archivo} - {descripcion}")
        else:
            print(f"   ❌ {archivo} - {descripcion} (FALTA)")

def mostrar_recomendaciones():
    """Muestra recomendaciones de uso"""
    print("\n" + "=" * 60)
    print("💡 RECOMENDACIONES DE USO:")
    print("=" * 60)
    print("""
1. SEGURIDAD:
   • Cambia el SECRET_KEY en app.py antes de producción
   • Cambia las credenciales de login (usuario/contraseña)
   • Haz backups regulares de mari.db

2. BACKUPS:
   • Ejecuta: copy mari.db mari_backup_FECHA.db
   • Guarda los backups en otro disco/nube

3. RENDIMIENTO:
   • La base de datos es SQLite (simple, ideal para <100k registros)
   • Si crece mucho, considera migrar a PostgreSQL

4. MANTENIMIENTO:
   • Verifica periódicamente la integridad con este script
   • Limpia archivos Excel antiguos de exportación

5. ACCESO:
   • Usuario: mariateresa
   • Contraseña: mateca
   • Cambia estas credenciales en app.py línea 18-19

6. DEPLOYMENT:
   • La página está en Render
   • Los cambios se suben automáticamente desde GitHub
   • URL: https://mateca.onrender.com (o tu dominio)
""")

if __name__ == '__main__':
    verificar_archivos()
    print()
    verificar_base_datos()
    mostrar_recomendaciones()
