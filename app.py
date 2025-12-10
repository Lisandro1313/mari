from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from functools import wraps
from database import Database
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'mateca_gualeguaychu_2025_secret_key_mari'

# Configuración de sesión para desarrollo
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

# Inicializar base de datos (PostgreSQL en producción, SQLite local en desarrollo)
database_url = os.environ.get('DATABASE_URL')
db = Database(db_url=database_url) if database_url else Database(db_url='sqlite:///mari.db')

# EJECUTAR MIGRACIÓN: Eliminar constraint UNIQUE de DNI (solo una vez al inicio)
if database_url and 'postgresql' in database_url:
    try:
        print("🔧 Eliminando constraint UNIQUE de DNI en PostgreSQL...")
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Intentar eliminar el constraint
        try:
            cursor.execute("ALTER TABLE tutores DROP CONSTRAINT IF EXISTS tutores_dni_key;")
            print("  ✓ Constraint tutores_dni_key eliminado")
        except Exception as e:
            print(f"  - Error al eliminar constraint: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Migración completada")
    except Exception as e:
        print(f"❌ Error en migración: {e}")

# Credenciales de login
USUARIO = 'mariateresa'
PASSWORD = 'mateca'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"Checking login for {f.__name__}: session={dict(session)}")
        if 'logged_in' not in session:
            print("Not logged in, redirecting to login")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        print(f"Login attempt: usuario={data.get('usuario')}, password={data.get('password')}")
        if data.get('usuario') == USUARIO and data.get('password') == PASSWORD:
            session.permanent = True
            session['logged_in'] = True
            session['usuario'] = USUARIO
            print(f"Session set: {session}")
            return jsonify({'success': True})
        print("Login failed: incorrect credentials")
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'}), 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Página principal"""
    return render_template('index.html', usuario=session.get('usuario'))

@app.route('/api/exportar', methods=['GET'])
@login_required
def exportar_excel():
    """Endpoint para exportar datos a Excel"""
    try:
        filename = f'atenciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        exito, mensaje = db.exportar_a_excel(filename)
        
        if exito:
            return send_file(filename, 
                           as_attachment=True,
                           download_name=filename,
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            return jsonify({'success': False, 'message': mensaje}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/atenciones', methods=['POST'])
@login_required
def agregar_atencion():
    """Endpoint para agregar una nueva atención (castración o atención primaria)"""
    data = request.json
    
    # Validar campos requeridos
    campos_requeridos = ['numero', 'fecha', 'nombre_animal', 'especie', 'sexo', 'nombre_apellido', 'dni']
    for campo in campos_requeridos:
        if not data.get(campo):
            return jsonify({'success': False, 'message': f'El campo {campo} es requerido'}), 400
    
    try:
        exito, mensaje = db.agregar_atencion(
            numero=data['numero'],
            fecha=data['fecha'],
            tipo_atencion=data.get('tipo_atencion', 'castracion'),
            nombre_animal=data['nombre_animal'],
            especie=data['especie'],
            sexo=data['sexo'],
            edad=data.get('edad', ''),
            nombre_apellido=data['nombre_apellido'],
            dni=data['dni'],
            direccion=data.get('direccion', ''),
            barrio=data.get('barrio', ''),
            telefono=data.get('telefono', ''),
            motivo=data.get('motivo', ''),
            diagnostico=data.get('diagnostico', ''),
            tratamiento=data.get('tratamiento', ''),
            derivacion=data.get('derivacion', ''),
            observaciones=data.get('observaciones', '')
        )
        
        if exito:
            return jsonify({'success': True, 'message': mensaje})
        else:
            return jsonify({'success': False, 'message': mensaje}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/atenciones', methods=['GET'])
@login_required
def buscar_atenciones():
    """Endpoint para buscar atenciones"""
    filtros = {
        'numero': request.args.get('numero'),
        'tipo_atencion': request.args.get('tipo_atencion'),
        'especie': request.args.get('especie'),
        'dni': request.args.get('dni'),
        'barrio': request.args.get('barrio'),
        'nombre_animal': request.args.get('nombre_animal'),
        'fecha_desde': request.args.get('fecha_desde'),
        'fecha_hasta': request.args.get('fecha_hasta')
    }
    
    # Remover filtros vacíos
    filtros = {k: v for k, v in filtros.items() if v}
    
    resultados = db.buscar_atenciones(filtros)
    
    # Convertir resultados a lista de diccionarios
    atenciones = []
    for row in resultados:
        atenciones.append({
            'id': row[0],
            'numero': row[1],
            'fecha': row[2],
            'tipo_atencion': row[3],
            'nombre_animal': row[4],
            'especie': row[5],
            'sexo': row[6],
            'edad': row[7],
            'tutor': {
                'nombre_apellido': row[8],
                'dni': row[9],
                'direccion': row[10],
                'barrio': row[11],
                'telefono': row[12]
            },
            'motivo': row[13],
            'diagnostico': row[14],
            'tratamiento': row[15],
            'derivacion': row[16],
            'observaciones': row[17]
        })
    
    return jsonify(atenciones)

@app.route('/api/castraciones', methods=['POST'])
def agregar_castracion():
    """Endpoint para agregar una nueva castración"""
    data = request.json
    
    try:
        exito, mensaje = db.agregar_castracion(
            numero=data['numero'],
            fecha=data['fecha'],
            nombre_animal=data['nombre_animal'],
            especie=data['especie'],
            sexo=data['sexo'],
            edad=data.get('edad', ''),
            nombre_apellido=data['nombre_apellido'],
            dni=data['dni'],
            direccion=data.get('direccion', ''),
            barrio=data.get('barrio', ''),
            telefono=data.get('telefono', '')
        )
        
        if exito:
            return jsonify({'success': True, 'message': mensaje})
        else:
            return jsonify({'success': False, 'message': mensaje}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/castraciones', methods=['GET'])
def buscar_castraciones():
    """Endpoint para buscar castraciones"""
    filtros = {
        'numero': request.args.get('numero'),
        'especie': request.args.get('especie'),
        'dni': request.args.get('dni'),
        'barrio': request.args.get('barrio'),
        'fecha_desde': request.args.get('fecha_desde'),
        'fecha_hasta': request.args.get('fecha_hasta')
    }
    
    # Remover filtros vacíos
    filtros = {k: v for k, v in filtros.items() if v}
    
    resultados = db.buscar_castraciones(filtros)
    
    # Convertir resultados a lista de diccionarios
    castraciones = []
    for row in resultados:
        castraciones.append({
            'numero': row[0],
            'fecha': row[1],
            'nombre_animal': row[2],
            'especie': row[3],
            'sexo': row[4],
            'edad': row[5],
            'tutor': {
                'nombre_apellido': row[6],
                'dni': row[7],
                'direccion': row[8],
                'barrio': row[9],
                'telefono': row[10]
            }
        })
    
    return jsonify(castraciones)

@app.route('/api/estadisticas', methods=['GET'])
@login_required
def obtener_estadisticas():
    """Endpoint para obtener estadísticas con filtros opcionales"""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    stats = db.obtener_estadisticas(fecha_desde, fecha_hasta)
    
    # Formatear estadísticas para JSON (arrays para Chart.js)
    return jsonify({
        'total': stats['total'],
        'por_tipo': stats.get('por_tipo', []),
        'por_especie': stats['por_especie'],
        'por_sexo': stats['por_sexo'],
        'por_dia': stats['por_dia'],
        'por_semana': stats['por_semana'],
        'por_mes': stats['por_mes'],
        'por_barrio': stats['por_barrio'],
        'por_anio': stats['por_anio'],
        'especie_sexo': stats['especie_sexo']
    })

@app.route('/api/estadisticas/barrios', methods=['GET'])
@login_required
def obtener_estadisticas_barrios():
    """Endpoint para obtener estadísticas de castraciones por barrio para el mapa"""
    try:
        import unicodedata
        import re
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = db.convert_query('''
            SELECT t.barrio, COUNT(a.id) as total
            FROM atenciones a
            JOIN tutores t ON a.tutor_id = t.id
            WHERE a.tipo_atencion = %s AND t.barrio IS NOT NULL AND t.barrio != ''
            GROUP BY t.barrio
            ORDER BY total DESC
        ''')
        
        cursor.execute(query, ('castracion',))
        resultados = cursor.fetchall()
        conn.close()
        
        # Función para normalizar nombres de barrios
        def normalizar_barrio(nombre):
            if not nombre:
                return ""
            # Remover tildes
            nombre = ''.join(c for c in unicodedata.normalize('NFD', nombre) 
                           if unicodedata.category(c) != 'Mn')
            # Convertir a minúsculas y remover espacios extras
            nombre = re.sub(r'\s+', ' ', nombre.lower().strip())
            # Remover palabras comunes
            nombre = re.sub(r'\b(barrio|sum|b°|bº)\b', '', nombre).strip()
            return nombre
        
        # Agrupar barrios por nombre normalizado
        barrios_agrupados = {}
        for barrio, total in resultados:
            barrio_normalizado = normalizar_barrio(barrio)
            if barrio_normalizado:
                if barrio_normalizado not in barrios_agrupados:
                    barrios_agrupados[barrio_normalizado] = {
                        'nombre_original': barrio,
                        'total': 0,
                        'variantes': []
                    }
                barrios_agrupados[barrio_normalizado]['total'] += total
                barrios_agrupados[barrio_normalizado]['variantes'].append(barrio)
        
        # Convertir a diccionario con el nombre original más común
        barrios_stats = {}
        for datos in barrios_agrupados.values():
            # Usar el nombre original más frecuente o el primero
            nombre = datos['nombre_original']
            barrios_stats[nombre] = datos['total']
        
        return jsonify(barrios_stats)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/barrios/lista', methods=['GET'])
@login_required
def obtener_lista_barrios():
    """Endpoint para obtener lista de todos los barrios registrados con conteo"""
    try:
        import unicodedata
        import re
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = db.convert_query('''
            SELECT barrio, COUNT(*) as registros
            FROM tutores
            WHERE barrio IS NOT NULL AND barrio != ''
            GROUP BY barrio
            ORDER BY registros DESC
        ''')
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()
        
        # Función para normalizar nombres
        def normalizar_barrio(nombre):
            if not nombre:
                return ""
            nombre = ''.join(c for c in unicodedata.normalize('NFD', nombre) 
                           if unicodedata.category(c) != 'Mn')
            nombre = re.sub(r'\s+', ' ', nombre.lower().strip())
            nombre = re.sub(r'\b(barrio|sum|b°|bº)\b', '', nombre).strip()
            return nombre
        
        # Agrupar barrios similares
        barrios_agrupados = {}
        for barrio, registros in resultados:
            barrio_normalizado = normalizar_barrio(barrio)
            if barrio_normalizado:
                if barrio_normalizado not in barrios_agrupados:
                    barrios_agrupados[barrio_normalizado] = {
                        'nombre': barrio,
                        'registros': 0,
                        'variantes': []
                    }
                barrios_agrupados[barrio_normalizado]['registros'] += registros
                if barrio not in barrios_agrupados[barrio_normalizado]['variantes']:
                    barrios_agrupados[barrio_normalizado]['variantes'].append(barrio)
        
        # Convertir a lista ordenada
        barrios_lista = []
        for datos in barrios_agrupados.values():
            barrios_lista.append({
                'nombre': datos['nombre'],
                'registros': datos['registros'],
                'variantes': datos['variantes']
            })
        
        barrios_lista.sort(key=lambda x: x['registros'], reverse=True)
        
        return jsonify(barrios_lista)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/atenciones/<int:numero>', methods=['GET'])
@login_required
def obtener_atencion(numero):
    """Endpoint para obtener una atención específica por número"""
    try:
        filtros = {'numero': numero}
        resultados = db.buscar_atenciones(filtros)
        
        if not resultados:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        
        row = resultados[0]
        
        # Formatear fecha para input type="date" (YYYY-MM-DD)
        fecha = row[2]
        if fecha:
            # Si es un objeto datetime o date
            if hasattr(fecha, 'strftime'):
                fecha = fecha.strftime('%Y-%m-%d')
            # Si es string
            elif isinstance(fecha, str):
                # Si viene en formato DD/MM/YYYY
                if '/' in fecha:
                    partes = fecha.split('/')
                    if len(partes) == 3:
                        fecha = f"{partes[2].split(' ')[0]}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
                # Si viene con hora, extraer solo la fecha
                elif ' ' in fecha:
                    fecha = fecha.split(' ')[0]
                elif 'T' in fecha:
                    fecha = fecha.split('T')[0]
        
        atencion = {
            'id': row[0],
            'numero': row[1],
            'fecha': fecha,
            'tipo_atencion': row[3],
            'nombre_animal': row[4],
            'especie': row[5],
            'sexo': row[6],
            'edad': row[7],
            'tutor': {
                'nombre_apellido': row[8],
                'dni': row[9],
                'direccion': row[10],
                'barrio': row[11],
                'telefono': row[12]
            },
            'motivo': row[13] or '',
            'diagnostico': row[14] or '',
            'tratamiento': row[15] or '',
            'derivacion': row[16] or '',
            'observaciones': row[17] or ''
        }
        return jsonify(atencion)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/atenciones/<int:numero>', methods=['PUT'])
@login_required
def editar_atencion(numero):
    """Endpoint para editar una atención existente"""
    data = request.json
    try:
        exito, mensaje = db.editar_atencion(numero, data)
        if exito:
            return jsonify({'success': True, 'message': mensaje})
        else:
            return jsonify({'success': False, 'message': mensaje}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/atenciones/<int:numero>', methods=['DELETE'])
@login_required
def eliminar_atencion(numero):
    """Endpoint para eliminar una atención"""
    try:
        exito, mensaje = db.eliminar_atencion(numero)
        if exito:
            return jsonify({'success': True, 'message': mensaje})
        else:
            return jsonify({'success': False, 'message': mensaje}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/siguiente-numero', methods=['GET'])
def siguiente_numero():
    """Endpoint para obtener el siguiente número de registro"""
    numero = db.obtener_siguiente_numero()
    return jsonify({'numero': numero})

@app.route('/api/castraciones/<int:numero>', methods=['GET'])
def obtener_castracion(numero):
    """Endpoint para obtener una castración específica"""
    castracion = db.obtener_castracion_por_id(numero)
    if castracion:
        return jsonify(castracion)
    return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404

@app.route('/api/castraciones/<int:numero>', methods=['PUT'])
def actualizar_castracion(numero):
    """Endpoint para actualizar una castración"""
    data = request.json
    
    try:
        exito, mensaje = db.actualizar_castracion(
            numero_original=numero,
            numero=data['numero'],
            fecha=data['fecha'],
            nombre_animal=data['nombre_animal'],
            especie=data['especie'],
            sexo=data['sexo'],
            edad=data.get('edad', ''),
            nombre_apellido=data['nombre_apellido'],
            dni=data['dni'],
            direccion=data.get('direccion', ''),
            barrio=data.get('barrio', ''),
            telefono=data.get('telefono', '')
        )
        
        if exito:
            return jsonify({'success': True, 'message': mensaje})
        else:
            return jsonify({'success': False, 'message': mensaje}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/castraciones/<int:numero>', methods=['DELETE'])
def eliminar_castracion(numero):
    """Endpoint para eliminar una castración"""
    exito, mensaje = db.eliminar_castracion(numero)
    
    if exito:
        return jsonify({'success': True, 'message': mensaje})
    else:
        return jsonify({'success': False, 'message': mensaje}), 404

@app.route('/api/dashboard', methods=['GET'])
@login_required
def obtener_dashboard():
    """Endpoint para obtener datos del dashboard"""
    try:
        stats = db.obtener_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"Error en dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/turnos', methods=['POST'])
def agregar_turno():
    """Endpoint para agregar un turno"""
    data = request.json
    
    exito, mensaje = db.agregar_turno(
        fecha=data['fecha'],
        hora=data['hora'],
        nombre_animal=data['nombre_animal'],
        tutor_nombre=data['tutor_nombre'],
        telefono=data.get('telefono', ''),
        tipo=data['tipo'],
        observaciones=data.get('observaciones', '')
    )
    
    if exito:
        return jsonify({'success': True, 'message': mensaje})
    else:
        return jsonify({'success': False, 'message': mensaje}), 400

@app.route('/api/turnos/<int:turno_id>', methods=['PUT'])
def actualizar_turno(turno_id):
    """Endpoint para actualizar estado de turno"""
    data = request.json
    exito, mensaje = db.actualizar_estado_turno(turno_id, data['estado'])
    
    if exito:
        return jsonify({'success': True, 'message': mensaje})
    else:
        return jsonify({'success': False, 'message': mensaje}), 400

@app.route('/api/turnos/<int:turno_id>', methods=['DELETE'])
def eliminar_turno(turno_id):
    """Endpoint para eliminar turno"""
    exito, mensaje = db.eliminar_turno(turno_id)
    
    if exito:
        return jsonify({'success': True, 'message': mensaje})
    else:
        return jsonify({'success': False, 'message': mensaje}), 404

@app.route('/api/auditoria', methods=['GET'])
@login_required
def obtener_auditoria():
    """Endpoint para obtener logs de auditoría"""
    try:
        logs = db.obtener_auditoria(100)  # Últimos 100 registros
        
        # Convertir a formato JSON
        resultado = []
        for log in logs:
            # Convertir fecha_hora a string ISO si es necesario
            fecha_hora = log[1]
            if isinstance(fecha_hora, datetime):
                fecha_hora = fecha_hora.isoformat()
            elif isinstance(fecha_hora, str):
                # Si ya es string, asegurarse que esté en formato ISO
                try:
                    dt = datetime.fromisoformat(fecha_hora.replace(' ', 'T'))
                    fecha_hora = dt.isoformat()
                except:
                    pass  # Si falla, usar el valor original
            
            resultado.append({
                'id': log[0],
                'fecha_hora': fecha_hora,
                'tipo_operacion': log[2],
                'tabla': log[3],
                'registro_id': log[4],
                'usuario': log[5],
                'datos_anteriores': log[6],
                'datos_nuevos': log[7],
                'descripcion': log[8]
            })
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("MARI - Sistema de Registro de Castraciones Municipales")
    print("Gualeguaychú, Entre Ríos")
    print("=" * 60)
    print("\nServidor iniciado en: http://localhost:5000")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 60)
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
