import sqlite3
from datetime import datetime, timedelta
import random

# Datos de ejemplo
nombres_animales = [
    "Max", "Luna", "Rocky", "Bella", "Charlie", "Lola", "Toby", "Mimi",
    "Bobby", "Nala", "Duke", "Cleo", "Zeus", "Kitty", "Bruno", "Pelusa",
    "Rex", "Nina", "Lucky", "Princesa", "Cooper", "Manchas", "Simba", "Michi"
]

nombres_tutores = [
    ("María González", "25678901", "Av. San Martín 450", "Centro"),
    ("Juan Pérez", "30456789", "Calle Mitre 123", "Belgrano"),
    ("Ana López", "28234567", "Bv. Sarmiento 890", "Alta Córdoba"),
    ("Carlos Rodríguez", "32567890", "Calle Rivadavia 234", "Nueva Córdoba"),
    ("Laura Martínez", "27890123", "Av. Colón 567", "General Paz"),
    ("Diego Fernández", "31234567", "Calle Independencia 789", "Alberdi"),
    ("Sofía Sánchez", "29456789", "Bv. Illia 345", "Cerro de las Rosas"),
    ("Pablo García", "33678901", "Av. Rafael Núñez 890", "Arguello"),
    ("Carla Díaz", "26789012", "Calle Duarte Quirós 123", "Centro"),
    ("Martín Torres", "34567890", "Av. Vélez Sarsfield 456", "San Vicente"),
    ("Lucía Romero", "28901234", "Calle Fructuoso Rivera 678", "Observatorio"),
    ("Fernando Castro", "32123456", "Bv. Los Alemanes 234", "Jardín"),
    ("Gabriela Flores", "29678901", "Av. Richieri 567", "Pueyrredón"),
    ("Ricardo Morales", "31890123", "Calle Caseros 890", "Güemes"),
    ("Valentina Ruiz", "27345678", "Av. Hipólito Yrigoyen 345", "Centro")
]

telefonos = [
    "351-2345678", "351-3456789", "351-4567890", "351-5678901",
    "351-6789012", "351-7890123", "351-8901234", "351-9012345"
]

def generar_datos_ejemplo():
    """Genera 30 registros de ejemplo en la base de datos"""
    conn = sqlite3.connect('mari.db')
    cursor = conn.cursor()
    
    # Limpiar datos existentes
    cursor.execute('DELETE FROM castraciones')
    cursor.execute('DELETE FROM tutores')
    
    print("Generando datos de ejemplo...")
    
    fecha_inicio = datetime.now() - timedelta(days=180)  # Últimos 6 meses
    
    for i in range(30):
        # Datos del animal
        numero = i + 1
        dias_atras = random.randint(0, 180)
        fecha = (fecha_inicio + timedelta(days=dias_atras)).strftime('%Y-%m-%d')
        nombre_animal = random.choice(nombres_animales)
        especie = random.choice(["Canino", "Canino", "Canino", "Felino", "Felino"])  # Más caninos
        sexo = random.choice(["Macho", "Hembra"])
        edad = random.choice(["6 meses", "1 año", "2 años", "3 años", "4 años", "5 años", "8 meses"])
        
        # Datos del tutor
        tutor = random.choice(nombres_tutores)
        nombre_apellido = tutor[0]
        dni = tutor[1]
        direccion = tutor[2]
        barrio = tutor[3]
        telefono = random.choice(telefonos)
        
        # Buscar o crear tutor
        cursor.execute('SELECT id FROM tutores WHERE dni = ?', (dni,))
        tutor_row = cursor.fetchone()
        
        if tutor_row:
            tutor_id = tutor_row[0]
        else:
            cursor.execute('''
                INSERT INTO tutores (nombre_apellido, dni, direccion, barrio, telefono)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre_apellido, dni, direccion, barrio, telefono))
            tutor_id = cursor.lastrowid
        
        # Agregar castración
        try:
            cursor.execute('''
                INSERT INTO castraciones (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id))
            print(f"✓ Registro {numero}: {nombre_animal} ({especie} - {sexo}) - {fecha}")
        except Exception as e:
            print(f"✗ Error en registro {numero}: {e}")
    
    conn.commit()
    conn.close()
    print(f"\n¡Listo! Se generaron 30 registros de ejemplo")

if __name__ == '__main__':
    generar_datos_ejemplo()
