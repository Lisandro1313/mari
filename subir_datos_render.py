"""
Script para subir todos los datos de la base de datos local a Render
"""
import sqlite3
import requests
import json

# Configuración
RENDER_URL = "https://mateca.onrender.com"  # Tu URL de Render
USUARIO = "mariateresa"
PASSWORD = "mateca"

def obtener_datos_locales():
    """Lee todos los datos de la base de datos local"""
    conn = sqlite3.connect('mari.db')
    cursor = conn.cursor()
    
    # Obtener todas las atenciones con datos de tutores
    cursor.execute('''
        SELECT 
            a.numero, a.fecha, a.tipo_atencion, a.nombre_animal, 
            a.especie, a.sexo, a.edad,
            t.nombre_apellido, t.dni, t.direccion, t.barrio, t.telefono,
            a.motivo, a.diagnostico, a.tratamiento, a.derivacion, a.observaciones
        FROM atenciones a
        JOIN tutores t ON a.tutor_id = t.id
        ORDER BY a.numero
    ''')
    
    atenciones = cursor.fetchall()
    conn.close()
    
    return atenciones

def login_render():
    """Hace login en Render y obtiene la sesión"""
    session = requests.Session()
    
    response = session.post(
        f"{RENDER_URL}/login",
        json={"usuario": USUARIO, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        print("✅ Login exitoso en Render")
        return session
    else:
        print(f"❌ Error en login: {response.status_code}")
        return None

def subir_atencion(session, datos):
    """Sube una atención a Render"""
    numero, fecha, tipo_atencion, nombre_animal, especie, sexo, edad, \
    nombre_apellido, dni, direccion, barrio, telefono, \
    motivo, diagnostico, tratamiento, derivacion, observaciones = datos
    
    atencion = {
        "numero": numero,
        "fecha": fecha,
        "tipo_atencion": tipo_atencion,
        "nombre_animal": nombre_animal,
        "especie": especie,
        "sexo": sexo,
        "edad": edad or "",
        "nombre_apellido": nombre_apellido,
        "dni": dni,
        "direccion": direccion or "",
        "barrio": barrio or "",
        "telefono": telefono or "",
        "motivo": motivo or "",
        "diagnostico": diagnostico or "",
        "tratamiento": tratamiento or "",
        "derivacion": derivacion or "",
        "observaciones": observaciones or ""
    }
    
    response = session.post(
        f"{RENDER_URL}/api/atenciones",
        json=atencion
    )
    
    return response.status_code == 200

def main():
    print("=" * 60)
    print("SUBIDA DE DATOS A RENDER")
    print("=" * 60)
    
    # Leer datos locales
    print("\n📂 Leyendo datos de mari.db local...")
    atenciones = obtener_datos_locales()
    print(f"✅ {len(atenciones)} registros encontrados")
    
    # Login en Render
    print("\n🔐 Conectando con Render...")
    session = login_render()
    
    if not session:
        print("❌ No se pudo conectar con Render")
        return
    
    # Subir cada atención
    print(f"\n📤 Subiendo {len(atenciones)} registros...")
    exitosos = 0
    errores = 0
    
    for i, atencion in enumerate(atenciones, 1):
        numero = atencion[0]
        if subir_atencion(session, atencion):
            exitosos += 1
            print(f"  ✅ [{i}/{len(atenciones)}] Registro #{numero} subido")
        else:
            errores += 1
            print(f"  ❌ [{i}/{len(atenciones)}] Error en registro #{numero}")
    
    print("\n" + "=" * 60)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Errores: {errores}")
    print(f"📊 Total: {len(atenciones)}")
    print("=" * 60)
    print("\n✨ ¡Proceso completado!")
    print(f"🌐 Verificá en: {RENDER_URL}")

if __name__ == "__main__":
    main()
