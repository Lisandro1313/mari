"""
Script para separar tutores compartidos
Cada atención tendrá su propio tutor independiente
"""
import os
from database import Database

def separar_tutores():
    database_url = os.environ.get('DATABASE_URL')
    db = Database(db_url=database_url) if database_url else Database(db_url='sqlite:///mari.db')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        print("🔧 Separando tutores compartidos...")
        
        # Obtener todas las atenciones
        cursor.execute("""
            SELECT a.id, a.numero, a.tutor_id, 
                   t.nombre_apellido, t.dni, t.direccion, t.barrio, t.telefono
            FROM atenciones a
            JOIN tutores t ON a.tutor_id = t.id
            ORDER BY a.numero
        """)
        atenciones = cursor.fetchall()
        
        tutores_procesados = set()
        tutores_creados = 0
        
        for atencion in atenciones:
            atencion_id = atencion[0]
            numero = atencion[1]
            tutor_id_actual = atencion[2]
            nombre_apellido = atencion[3]
            dni = atencion[4]
            direccion = atencion[5]
            barrio = atencion[6]
            telefono = atencion[7]
            
            # Si este tutor_id ya fue procesado, crear uno nuevo
            if tutor_id_actual in tutores_procesados:
                if db.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO tutores (nombre_apellido, dni, direccion, barrio, telefono)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (nombre_apellido, dni, direccion, barrio, telefono))
                    nuevo_tutor_id = cursor.fetchone()[0]
                else:
                    cursor.execute("""
                        INSERT INTO tutores (nombre_apellido, dni, direccion, barrio, telefono)
                        VALUES (?, ?, ?, ?, ?)
                    """, (nombre_apellido, dni, direccion, barrio, telefono))
                    nuevo_tutor_id = cursor.lastrowid
                
                # Actualizar la atención con el nuevo tutor
                if db.db_type == 'postgresql':
                    cursor.execute("UPDATE atenciones SET tutor_id = %s WHERE id = %s", 
                                 (nuevo_tutor_id, atencion_id))
                else:
                    cursor.execute("UPDATE atenciones SET tutor_id = ? WHERE id = ?", 
                                 (nuevo_tutor_id, atencion_id))
                
                tutores_creados += 1
                print(f"  ✓ Atención #{numero} ahora tiene su propio tutor (nuevo ID: {nuevo_tutor_id})")
            else:
                tutores_procesados.add(tutor_id_actual)
        
        conn.commit()
        print(f"\n✅ Proceso completado: {tutores_creados} tutores nuevos creados")
        print(f"✅ Cada atención ahora tiene su tutor independiente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    separar_tutores()
