import sqlite3
from datetime import datetime, timedelta
import random

# Datos de ejemplo - Gualeguaychú, Entre Ríos
nombres_animales = [
    "Max", "Luna", "Rocky", "Bella", "Charlie", "Lola", "Toby", "Mimi",
    "Bobby", "Nala", "Duke", "Cleo", "Zeus", "Kitty", "Bruno", "Pelusa",
    "Rex", "Nina", "Lucky", "Princesa", "Cooper", "Manchas", "Simba", "Michi"
]

# Barrios reales de Gualeguaychú
barrios_gchu = [
    "Centro", "Pueblo Nuevo", "Barrio Parque", "Pueblo Belgrano",
    "Villa Elisa", "Larralde", "San José", "Villa Zorraquín",
    "Rocamora", "Arroyo de la China", "Parque San Martín", "Los Médanos",
    "Pueblo Liebig", "Villa Mariano Moreno", "Barrio Ayuí"
]

# Calles reales de Gualeguaychú
calles_gchu = [
    "San Martín", "Bolívar", "25 de Mayo", "Urquiza", "Rivadavia",
    "Costanera", "San Lorenzo", "Gervasio Méndez", "Luis N. Palma",
    "Rocamora", "Picada Berón de Astrada", "Andrés Paez", "3 de Febrero",
    "España", "Italia", "Constitución", "Belgrano", "Mitre"
]

nombres_tutores = [
    ("María González", "25678901"),
    ("Juan Pérez", "30456789"),
    ("Ana López", "28234567"),
    ("Carlos Rodríguez", "32567890"),
    ("Laura Martínez", "27890123"),
    ("Diego Fernández", "31234567"),
    ("Sofía Sánchez", "29456789"),
    ("Pablo García", "33678901"),
    ("Carla Díaz", "26789012"),
    ("Martín Torres", "34567890"),
    ("Lucía Romero", "28901234"),
    ("Fernando Castro", "32123456"),
    ("Gabriela Flores", "29678901"),
    ("Ricardo Morales", "31890123"),
    ("Valentina Ruiz", "27345678")
]

telefonos = [
    "3446-123456", "3446-234567", "3446-345678", "3446-456789",
    "3446-567890", "3446-678901", "3446-789012", "3446-890123"
]

def generar_datos_ejemplo():
    """Genera 30 registros de ejemplo en la base de datos"""
    conn = sqlite3.connect('mari.db')
    cursor = conn.cursor()
    
    # Limpiar datos existentes
    cursor.execute('DELETE FROM castraciones')
    cursor.execute('DELETE FROM tutores')
    cursor.execute('DELETE FROM turnos')
    
    print("Generando datos de ejemplo para Gualeguaychú...")
    
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
        atencion_primaria = 1 if random.random() > 0.3 else 0  # 70% atención primaria
        
        # Datos del tutor - Direcciones de Gualeguaychú
        tutor = random.choice(nombres_tutores)
        nombre_apellido = tutor[0]
        dni = tutor[1]
        calle = random.choice(calles_gchu)
        numero_casa = random.randint(100, 9999)
        direccion = f"{calle} {numero_casa}"
        barrio = random.choice(barrios_gchu)
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
                INSERT INTO castraciones (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id, atencion_primaria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id, atencion_primaria))
            print(f"✓ Registro {numero}: {nombre_animal} ({especie} - {sexo}) - {fecha}")
        except Exception as e:
            print(f"✗ Error en registro {numero}: {e}")
    
    # Generar turnos para esta semana
    print("\nGenerando turnos de esta semana...")
    tipos_turno = ["Castración", "Retiro de puntos", "Control post-operatorio", "Consulta"]
    horas = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
    
    for dia in range(7):
        fecha_turno = (datetime.now() + timedelta(days=dia)).strftime('%Y-%m-%d')
        num_turnos = random.randint(2, 5)
        
        for _ in range(num_turnos):
            hora = random.choice(horas)
            nombre_animal = random.choice(nombres_animales)
            tutor = random.choice(nombres_tutores)
            tipo = random.choice(tipos_turno)
            telefono_t = random.choice(telefonos)
            estado = 'pendiente' if dia > 0 else random.choice(['pendiente', 'completado', 'cancelado'])
            
            cursor.execute('''
                INSERT INTO turnos (fecha, hora, nombre_animal, tutor_nombre, telefono, tipo, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_turno, hora, nombre_animal, tutor[0], telefono_t, tipo, estado))
    
    conn.commit()
    conn.close()
    print(f"\n¡Listo! Se generaron 30 registros y turnos para Gualeguaychú")

if __name__ == '__main__':
    generar_datos_ejemplo()
