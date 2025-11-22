from flask import Flask, render_template, request, jsonify
from database import Database
from datetime import datetime

app = Flask(__name__)
db = Database()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

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
def obtener_estadisticas():
    """Endpoint para obtener estadísticas con filtros opcionales"""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    stats = db.obtener_estadisticas(fecha_desde, fecha_hasta)
    
    # Formatear estadísticas para JSON
    return jsonify({
        'total': stats['total'],
        'por_especie': [{'especie': row[0], 'cantidad': row[1]} for row in stats['por_especie']],
        'por_sexo': [{'sexo': row[0], 'cantidad': row[1]} for row in stats['por_sexo']],
        'por_dia': [{'dia': row[0], 'cantidad': row[1]} for row in stats['por_dia']],
        'por_semana': [{'semana': row[0], 'cantidad': row[1]} for row in stats['por_semana']],
        'por_mes': [{'mes': row[0], 'cantidad': row[1]} for row in stats['por_mes']],
        'por_barrio': [{'barrio': row[0], 'cantidad': row[1]} for row in stats['por_barrio']],
        'por_anio': [{'anio': row[0], 'cantidad': row[1]} for row in stats['por_anio']],
        'especie_sexo': [{'especie': row[0], 'sexo': row[1], 'cantidad': row[2]} for row in stats['especie_sexo']]
    })

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
def obtener_dashboard():
    """Endpoint para obtener datos del dashboard"""
    stats = db.obtener_dashboard_stats()
    
    return jsonify({
        'hoy': stats['hoy'],
        'semana': stats['semana'],
        'mes': stats['mes'],
        'primaria_hoy': stats['primaria_hoy'],
        'recurrente_hoy': stats['recurrente_hoy'],
        'ultimas': [
            {
                'numero': row[0],
                'fecha': row[1],
                'nombre_animal': row[2],
                'especie': row[3],
                'tutor': row[4],
                'primaria': row[5]
            } for row in stats['ultimas']
        ],
        'turnos_hoy': [
            {
                'id': row[0],
                'hora': row[1],
                'nombre_animal': row[2],
                'tutor_nombre': row[3],
                'tipo': row[4],
                'estado': row[5]
            } for row in stats['turnos_hoy']
        ],
        'turnos_semana': [
            {
                'fecha': row[0],
                'hora': row[1],
                'nombre_animal': row[2],
                'tutor_nombre': row[3],
                'tipo': row[4],
                'estado': row[5]
            } for row in stats['turnos_semana']
        ]
    })

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

if __name__ == '__main__':
    print("=" * 60)
    print("MARI - Sistema de Registro de Castraciones Municipales")
    print("Gualeguaychú, Entre Ríos")
    print("=" * 60)
    print("\nServidor iniciado en: http://localhost:5000")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
