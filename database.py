import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='mari.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de tutores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tutores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_apellido TEXT NOT NULL,
                dni TEXT NOT NULL,
                direccion TEXT,
                barrio TEXT,
                telefono TEXT,
                UNIQUE(dni)
            )
        ''')
        
        # Tabla de castraciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS castraciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero INTEGER UNIQUE NOT NULL,
                fecha DATE NOT NULL,
                nombre_animal TEXT NOT NULL,
                especie TEXT NOT NULL,
                sexo TEXT NOT NULL,
                edad TEXT,
                tutor_id INTEGER NOT NULL,
                atencion_primaria INTEGER DEFAULT 0,
                observaciones TEXT,
                FOREIGN KEY (tutor_id) REFERENCES tutores(id)
            )
        ''')
        
        # Tabla de turnos/cronograma
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                hora TEXT NOT NULL,
                nombre_animal TEXT NOT NULL,
                tutor_nombre TEXT NOT NULL,
                telefono TEXT,
                tipo TEXT NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                observaciones TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def agregar_castracion(self, numero, fecha, nombre_animal, especie, sexo, edad,
                          nombre_apellido, dni, direccion, barrio, telefono):
        """Agrega una nueva castración a la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar o crear tutor
            cursor.execute('SELECT id FROM tutores WHERE dni = ?', (dni,))
            tutor = cursor.fetchone()
            
            if tutor:
                tutor_id = tutor[0]
                # Actualizar datos del tutor
                cursor.execute('''
                    UPDATE tutores 
                    SET nombre_apellido = ?, direccion = ?, barrio = ?, telefono = ?
                    WHERE id = ?
                ''', (nombre_apellido, direccion, barrio, telefono, tutor_id))
            else:
                # Crear nuevo tutor
                cursor.execute('''
                    INSERT INTO tutores (nombre_apellido, dni, direccion, barrio, telefono)
                    VALUES (?, ?, ?, ?, ?)
                ''', (nombre_apellido, dni, direccion, barrio, telefono))
                tutor_id = cursor.lastrowid
            
            # Agregar castración
            cursor.execute('''
                INSERT INTO castraciones (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id))
            
            conn.commit()
            return True, "Castración registrada exitosamente"
        except sqlite3.IntegrityError as e:
            return False, f"Error: El número de registro ya existe"
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"
        finally:
            conn.close()
    
    def buscar_castraciones(self, filtros=None):
        """Busca castraciones con filtros opcionales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT c.numero, c.fecha, c.nombre_animal, c.especie, c.sexo, c.edad,
                   t.nombre_apellido, t.dni, t.direccion, t.barrio, t.telefono
            FROM castraciones c
            JOIN tutores t ON c.tutor_id = t.id
            WHERE 1=1
        '''
        params = []
        
        if filtros:
            if filtros.get('numero'):
                query += ' AND c.numero = ?'
                params.append(filtros['numero'])
            if filtros.get('especie'):
                query += ' AND c.especie LIKE ?'
                params.append(f"%{filtros['especie']}%")
            if filtros.get('dni'):
                query += ' AND t.dni LIKE ?'
                params.append(f"%{filtros['dni']}%")
            if filtros.get('barrio'):
                query += ' AND t.barrio LIKE ?'
                params.append(f"%{filtros['barrio']}%")
            if filtros.get('fecha_desde'):
                query += ' AND c.fecha >= ?'
                params.append(filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                query += ' AND c.fecha <= ?'
                params.append(filtros['fecha_hasta'])
        
        query += ' ORDER BY c.numero DESC'
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        
        return resultados
    
    def obtener_estadisticas(self, fecha_desde=None, fecha_hasta=None):
        """Obtiene estadísticas con filtros de fecha opcionales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Construir condición de fecha
        fecha_condicion = "1=1"
        fecha_params = []
        if fecha_desde:
            fecha_condicion += " AND fecha >= ?"
            fecha_params.append(fecha_desde)
        if fecha_hasta:
            fecha_condicion += " AND fecha <= ?"
            fecha_params.append(fecha_hasta)
        
        # Total de castraciones
        cursor.execute(f'SELECT COUNT(*) FROM castraciones WHERE {fecha_condicion}', fecha_params)
        stats['total'] = cursor.fetchone()[0]
        
        # Por especie
        cursor.execute(f'''
            SELECT especie, COUNT(*) as cantidad
            FROM castraciones
            WHERE {fecha_condicion}
            GROUP BY especie
            ORDER BY cantidad DESC
        ''', fecha_params)
        stats['por_especie'] = cursor.fetchall()
        
        # Por sexo
        cursor.execute(f'''
            SELECT sexo, COUNT(*) as cantidad
            FROM castraciones
            WHERE {fecha_condicion}
            GROUP BY sexo
        ''', fecha_params)
        stats['por_sexo'] = cursor.fetchall()
        
        # Por día (últimos 30 días o rango seleccionado)
        cursor.execute(f'''
            SELECT DATE(fecha) as dia, COUNT(*) as cantidad
            FROM castraciones
            WHERE {fecha_condicion}
            GROUP BY dia
            ORDER BY dia ASC
        ''', fecha_params)
        stats['por_dia'] = cursor.fetchall()
        
        # Por semana
        cursor.execute(f'''
            SELECT strftime('%Y-W%W', fecha) as semana, COUNT(*) as cantidad
            FROM castraciones
            WHERE {fecha_condicion}
            GROUP BY semana
            ORDER BY semana ASC
        ''', fecha_params)
        stats['por_semana'] = cursor.fetchall()
        
        # Por mes
        cursor.execute(f'''
            SELECT strftime('%Y-%m', fecha) as mes, COUNT(*) as cantidad
            FROM castraciones
            WHERE {fecha_condicion}
            GROUP BY mes
            ORDER BY mes ASC
        ''', fecha_params)
        stats['por_mes'] = cursor.fetchall()
        
        # Por barrio
        cursor.execute(f'''
            SELECT t.barrio, COUNT(*) as cantidad
            FROM castraciones c
            JOIN tutores t ON c.tutor_id = t.id
            WHERE t.barrio IS NOT NULL AND t.barrio != '' AND {fecha_condicion}
            GROUP BY t.barrio
            ORDER BY cantidad DESC
            LIMIT 15
        ''', fecha_params)
        stats['por_barrio'] = cursor.fetchall()
        
        # Por año
        cursor.execute(f'''
            SELECT strftime('%Y', fecha) as anio, COUNT(*) as cantidad
            FROM castraciones
            WHERE {fecha_condicion}
            GROUP BY anio
            ORDER BY anio DESC
        ''', fecha_params)
        stats['por_anio'] = cursor.fetchall()
        
        # Totales por especie y sexo combinados
        cursor.execute(f'''
            SELECT especie, sexo, COUNT(*) as cantidad
            FROM castraciones
            WHERE {fecha_condicion}
            GROUP BY especie, sexo
            ORDER BY especie, sexo
        ''', fecha_params)
        stats['especie_sexo'] = cursor.fetchall()
        
        conn.close()
        return stats
    
    def obtener_siguiente_numero(self):
        """Obtiene el siguiente número de registro disponible"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(numero) FROM castraciones')
        max_num = cursor.fetchone()[0]
        conn.close()
        return (max_num or 0) + 1
    
    def obtener_castracion_por_id(self, numero):
        """Obtiene una castración específica por número de registro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.numero, c.fecha, c.nombre_animal, c.especie, c.sexo, c.edad,
                   t.nombre_apellido, t.dni, t.direccion, t.barrio, t.telefono
            FROM castraciones c
            JOIN tutores t ON c.tutor_id = t.id
            WHERE c.numero = ?
        ''', (numero,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            return {
                'numero': resultado[0],
                'fecha': resultado[1],
                'nombre_animal': resultado[2],
                'especie': resultado[3],
                'sexo': resultado[4],
                'edad': resultado[5],
                'tutor': {
                    'nombre_apellido': resultado[6],
                    'dni': resultado[7],
                    'direccion': resultado[8],
                    'barrio': resultado[9],
                    'telefono': resultado[10]
                }
            }
        return None
    
    def actualizar_castracion(self, numero_original, numero, fecha, nombre_animal, especie, sexo, edad,
                             nombre_apellido, dni, direccion, barrio, telefono):
        """Actualiza una castración existente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar o crear tutor
            cursor.execute('SELECT id FROM tutores WHERE dni = ?', (dni,))
            tutor = cursor.fetchone()
            
            if tutor:
                tutor_id = tutor[0]
                # Actualizar datos del tutor
                cursor.execute('''
                    UPDATE tutores 
                    SET nombre_apellido = ?, direccion = ?, barrio = ?, telefono = ?
                    WHERE id = ?
                ''', (nombre_apellido, direccion, barrio, telefono, tutor_id))
            else:
                # Crear nuevo tutor
                cursor.execute('''
                    INSERT INTO tutores (nombre_apellido, dni, direccion, barrio, telefono)
                    VALUES (?, ?, ?, ?, ?)
                ''', (nombre_apellido, dni, direccion, barrio, telefono))
                tutor_id = cursor.lastrowid
            
            # Actualizar castración
            cursor.execute('''
                UPDATE castraciones
                SET numero = ?, fecha = ?, nombre_animal = ?, especie = ?, sexo = ?, edad = ?, tutor_id = ?
                WHERE numero = ?
            ''', (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id, numero_original))
            
            conn.commit()
            return True, "Registro actualizado exitosamente"
        except sqlite3.IntegrityError:
            return False, f"Error: El número de registro {numero} ya existe"
        except Exception as e:
            return False, f"Error al actualizar: {str(e)}"
        finally:
            conn.close()
    
    def eliminar_castracion(self, numero):
        """Elimina una castración por número de registro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM castraciones WHERE numero = ?', (numero,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Registro eliminado exitosamente"
            else:
                conn.close()
                return False, "No se encontró el registro"
        except Exception as e:
            conn.close()
            return False, f"Error al eliminar: {str(e)}"
    
    def obtener_dashboard_stats(self):
        """Obtiene estadísticas para el dashboard principal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Castraciones de hoy
        cursor.execute('''
            SELECT COUNT(*) FROM castraciones 
            WHERE DATE(fecha) = DATE('now')
        ''')
        stats['hoy'] = cursor.fetchone()[0]
        
        # Castraciones de esta semana
        cursor.execute('''
            SELECT COUNT(*) FROM castraciones 
            WHERE DATE(fecha) >= DATE('now', 'weekday 0', '-7 days')
        ''')
        stats['semana'] = cursor.fetchone()[0]
        
        # Castraciones del mes
        cursor.execute('''
            SELECT COUNT(*) FROM castraciones 
            WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
        ''')
        stats['mes'] = cursor.fetchone()[0]
        
        # Atención primaria vs recurrente hoy
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN atencion_primaria = 1 THEN 1 ELSE 0 END) as primaria,
                SUM(CASE WHEN atencion_primaria = 0 THEN 1 ELSE 0 END) as recurrente
            FROM castraciones 
            WHERE DATE(fecha) = DATE('now')
        ''')
        row = cursor.fetchone()
        stats['primaria_hoy'] = row[0] or 0
        stats['recurrente_hoy'] = row[1] or 0
        
        # Últimas 5 castraciones
        cursor.execute('''
            SELECT c.numero, c.fecha, c.nombre_animal, c.especie, 
                   t.nombre_apellido, c.atencion_primaria
            FROM castraciones c
            JOIN tutores t ON c.tutor_id = t.id
            ORDER BY c.fecha DESC, c.numero DESC
            LIMIT 5
        ''')
        stats['ultimas'] = cursor.fetchall()
        
        # Turnos de hoy
        cursor.execute('''
            SELECT id, hora, nombre_animal, tutor_nombre, tipo, estado
            FROM turnos
            WHERE DATE(fecha) = DATE('now')
            ORDER BY hora
        ''')
        stats['turnos_hoy'] = cursor.fetchall()
        
        # Turnos de esta semana
        cursor.execute('''
            SELECT fecha, hora, nombre_animal, tutor_nombre, tipo, estado
            FROM turnos
            WHERE DATE(fecha) >= DATE('now')
            AND DATE(fecha) <= DATE('now', '+7 days')
            ORDER BY fecha, hora
        ''')
        stats['turnos_semana'] = cursor.fetchall()
        
        conn.close()
        return stats
    
    def agregar_turno(self, fecha, hora, nombre_animal, tutor_nombre, telefono, tipo, observaciones=''):
        """Agrega un nuevo turno al cronograma"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO turnos (fecha, hora, nombre_animal, tutor_nombre, telefono, tipo, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha, hora, nombre_animal, tutor_nombre, telefono, tipo, observaciones))
            
            conn.commit()
            return True, "Turno agendado exitosamente"
        except Exception as e:
            return False, f"Error al agendar turno: {str(e)}"
        finally:
            conn.close()
    
    def actualizar_estado_turno(self, turno_id, estado):
        """Actualiza el estado de un turno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE turnos SET estado = ? WHERE id = ?', (estado, turno_id))
            conn.commit()
            return True, "Estado actualizado"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
    
    def eliminar_turno(self, turno_id):
        """Elimina un turno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM turnos WHERE id = ?', (turno_id,))
            conn.commit()
            return True, "Turno eliminado"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
