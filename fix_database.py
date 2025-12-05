"""
Script para arreglar la base de datos:
1. Eliminar constraint UNIQUE de DNI en tutores
2. Permitir múltiples tutores con el mismo DNI
"""
import os
from database import Database

def fix_database():
    database_url = os.environ.get('DATABASE_URL')
    db = Database(db_url=database_url) if database_url else Database(db_url='sqlite:///mari.db')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        if db.db_type == 'postgresql':
            print("🔧 Eliminando constraint UNIQUE de DNI en PostgreSQL...")
            # Eliminar constraint único en PostgreSQL
            cursor.execute("""
                ALTER TABLE tutores DROP CONSTRAINT IF EXISTS tutores_dni_key;
            """)
            conn.commit()
            print("✅ Constraint eliminado en PostgreSQL")
            
        else:
            print("🔧 Recreando tabla tutores en SQLite sin UNIQUE constraint...")
            # En SQLite, necesitamos recrear la tabla
            cursor.execute("PRAGMA foreign_keys=off;")
            
            # Crear tabla temporal sin el constraint
            cursor.execute("""
                CREATE TABLE tutores_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_apellido TEXT NOT NULL,
                    dni TEXT NOT NULL,
                    direccion TEXT,
                    barrio TEXT,
                    telefono TEXT
                );
            """)
            
            # Copiar datos
            cursor.execute("""
                INSERT INTO tutores_new (id, nombre_apellido, dni, direccion, barrio, telefono)
                SELECT id, nombre_apellido, dni, direccion, barrio, telefono FROM tutores;
            """)
            
            # Eliminar tabla vieja y renombrar
            cursor.execute("DROP TABLE tutores;")
            cursor.execute("ALTER TABLE tutores_new RENAME TO tutores;")
            
            cursor.execute("PRAGMA foreign_keys=on;")
            conn.commit()
            print("✅ Tabla recreada en SQLite sin constraint UNIQUE")
            
        print("✅ Base de datos corregida exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()
