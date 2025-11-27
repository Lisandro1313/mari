import os
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import sqlite3

# Intentar importar psycopg2 (solo disponible en producción)
psycopg2 = None
try:
    import psycopg2
    import psycopg2.extras
    print("✅ psycopg2 importado correctamente")
except ImportError as e:
    print(f"⚠️ psycopg2 no disponible: {e}")
except Exception as e:
    print(f"❌ Error al importar psycopg2: {e}")

class Database:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        
        print(f"🔍 DATABASE_URL: {self.db_url[:50] if self.db_url else 'None'}...")
        print(f"🔍 psycopg2 disponible: {psycopg2 is not None}")
        
        # Determinar tipo de base de datos
        if self.db_url and self.db_url.startswith('postgresql'):
            if psycopg2 is None:
                # Intentar importar de nuevo por si acaso
                try:
                    import psycopg2 as pg2
                    globals()['psycopg2'] = pg2
                    print("✅ psycopg2 importado en segundo intento")
                except ImportError:
                    raise ValueError("psycopg2 no está instalado. Instalar con: pip install psycopg2-binary")
            self.db_type = 'postgresql'
            print("✅ Usando PostgreSQL")
        elif self.db_url and self.db_url.startswith('sqlite'):
            self.db_type = 'sqlite'
            self.db_name = self.db_url.replace('sqlite:///', '')
            print(f"✅ Usando SQLite: {self.db_name}")
        else:
            # Fallback a SQLite local
            self.db_type = 'sqlite'
            self.db_name = 'mari.db'
            print(f"✅ Usando SQLite por defecto: {self.db_name}")
            
        self.init_db()
    
    def get_connection(self):
        if self.db_type == 'postgresql':
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_name)
    
    def get_placeholder(self):
        """Retorna el placeholder correcto según el tipo de BD"""
        return '%s' if self.db_type == 'postgresql' else '?'
    
    def get_autoincrement(self):
        """Retorna el tipo de autoincremento correcto"""
        return 'SERIAL' if self.db_type == 'postgresql' else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    
    def convert_query(self, query):
        """Convierte placeholders según el tipo de BD"""
        if self.db_type == 'sqlite':
            return query.replace('%s', '?')
        return query
    
    def get_integrity_error(self):
        """Retorna la excepción de integridad correcta"""
        if self.db_type == 'postgresql':
            return psycopg2.IntegrityError
        return sqlite3.IntegrityError
    
    def init_db(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        pk = self.get_autoincrement()
        
        # Tabla de tutores
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS tutores (
                id {pk},
                nombre_apellido TEXT NOT NULL,
                dni TEXT NOT NULL,
                direccion TEXT,
                barrio TEXT,
                telefono TEXT,
                UNIQUE(dni)
            )
        ''')
        
        # Tabla de atenciones (unifica castraciones y atención primaria)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS atenciones (
                id {pk},
                numero INTEGER UNIQUE NOT NULL,
                fecha DATE NOT NULL,
                tipo_atencion TEXT NOT NULL,
                nombre_animal TEXT NOT NULL,
                especie TEXT NOT NULL,
                sexo TEXT NOT NULL,
                edad TEXT,
                tutor_id INTEGER NOT NULL,
                motivo TEXT,
                diagnostico TEXT,
                tratamiento TEXT,
                derivacion TEXT,
                estado TEXT DEFAULT 'completado',
                observaciones TEXT,
                FOREIGN KEY (tutor_id) REFERENCES tutores(id)
            )
        ''')
        
        # Tabla de turnos/cronograma
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS turnos (
                id {pk},
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
        
        # Tabla de auditoría/log
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS auditoria (
                id {pk},
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tipo_operacion TEXT NOT NULL,
                tabla TEXT NOT NULL,
                registro_id INTEGER,
                usuario TEXT,
                datos_anteriores TEXT,
                datos_nuevos TEXT,
                descripcion TEXT
            )
        ''')
        
        # Crear índices para mejorar rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_atenciones_fecha ON atenciones(fecha)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_atenciones_tipo ON atenciones(tipo_atencion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_atenciones_numero ON atenciones(numero)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tutores_dni ON tutores(dni)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_fecha ON turnos(fecha)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha_hora)')
        
        conn.commit()
        conn.close()
    
    def agregar_atencion(self, numero, fecha, tipo_atencion, nombre_animal, especie, sexo, edad,
                        nombre_apellido, dni, direccion, barrio, telefono, 
                        motivo='', diagnostico='', tratamiento='', derivacion='', observaciones=''):
        """Agrega una nueva atención (castración o atención primaria) a la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar o crear tutor
            cursor.execute(self.convert_query('SELECT id FROM tutores WHERE dni = %s'), (dni,))
            tutor = cursor.fetchone()
            
            if tutor:
                tutor_id = tutor[0]
                # Actualizar datos del tutor
                cursor.execute(self.convert_query('''
                    UPDATE tutores 
                    SET nombre_apellido = %s, direccion = %s, barrio = %s, telefono = %s
                    WHERE id = %s
                '''), (nombre_apellido, direccion, barrio, telefono, tutor_id))
            else:
                # Crear nuevo tutor
                cursor.execute(self.convert_query('''
                    INSERT INTO tutores (nombre_apellido, dni, direccion, barrio, telefono)
                    VALUES (%s, %s, %s, %s, %s)
                '''), (nombre_apellido, dni, direccion, barrio, telefono))
                tutor_id = cursor.lastrowid
            
            # Agregar atención
            cursor.execute(self.convert_query('''
                INSERT INTO atenciones (numero, fecha, tipo_atencion, nombre_animal, especie, sexo, edad, 
                                       tutor_id, motivo, diagnostico, tratamiento, derivacion, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''), (numero, fecha, tipo_atencion, nombre_animal, especie, sexo, edad, tutor_id,
                  motivo, diagnostico, tratamiento, derivacion, observaciones))
            
            conn.commit()
            tipo_texto = "Castración" if tipo_atencion == "castracion" else "Atención primaria"
            return True, f"{tipo_texto} registrada exitosamente (#{numero})"
        except self.get_integrity_error() as e:
            conn.rollback()
            if "numero" in str(e).lower():
                return False, f"El número {numero} ya existe en el sistema"
            elif "dni" in str(e).lower():
                return False, "Error al procesar los datos del tutor"
            return False, f"Error de integridad: {str(e)}"
        except Exception as e:
            conn.rollback()
            return False, f"Error al registrar: {str(e)}"
        finally:
            conn.close()

    def editar_atencion(self, numero, datos, usuario='mariateresa'):
        """Edita una atención existente y registra cambios en auditoría"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener datos anteriores para auditoría
            cursor.execute('''
                SELECT a.*, t.nombre_apellido, t.dni 
                FROM atenciones a 
                JOIN tutores t ON a.tutor_id = t.id 
                WHERE a.numero = %s
            ''', (numero,))
            row_anterior = cursor.fetchone()
            
            if not row_anterior:
                return False, "Registro no encontrado"
            
            datos_anteriores = f"#{row_anterior[1]} - {row_anterior[4]} ({row_anterior[5]}) - Tutor: {row_anterior[-2]}"
            
            # Actualizar datos
            cursor.execute('''
                UPDATE atenciones 
                SET fecha = %s, nombre_animal = %s, especie = %s, sexo = %s, edad = %s,
                    motivo = %s, diagnostico = %s, tratamiento = %s, derivacion = %s, observaciones = %s
                WHERE numero = %s
            ''', (datos.get('fecha'), datos.get('nombre_animal'), datos.get('especie'), 
                  datos.get('sexo'), datos.get('edad'), datos.get('motivo', ''), 
                  datos.get('diagnostico', ''), datos.get('tratamiento', ''), 
                  datos.get('derivacion', ''), datos.get('observaciones', ''), numero))
            
            # Registrar en auditoría
            datos_nuevos = f"#{numero} - {datos.get('nombre_animal')} ({datos.get('especie')})"
            self.registrar_auditoria(
                'UPDATE', 'atenciones', row_anterior[0], usuario,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                descripcion=f"Edición de atención #{numero}"
            )
            
            conn.commit()
            return True, "Registro actualizado y cambios guardados en historial"
        except Exception as e:
            conn.rollback()
            return False, f"Error al editar: {str(e)}"
        finally:
            conn.close()
    
    def registrar_auditoria(self, tipo_operacion, tabla, registro_id, usuario, datos_anteriores='', datos_nuevos='', descripcion=''):
        """Registra una operación en la tabla de auditoría"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO auditoria (tipo_operacion, tabla, registro_id, usuario, datos_anteriores, datos_nuevos, descripcion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (tipo_operacion, tabla, registro_id, usuario, datos_anteriores, datos_nuevos, descripcion))
            conn.commit()
        except Exception as e:
            print(f"Error al registrar auditoría: {e}")
        finally:
            conn.close()
    
    def eliminar_atencion(self, numero, usuario='mariateresa'):
        """Elimina una atención (soft delete - guarda en auditoría)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener datos antes de eliminar
            cursor.execute('''
                SELECT a.*, t.nombre_apellido, t.dni 
                FROM atenciones a 
                JOIN tutores t ON a.tutor_id = t.id 
                WHERE a.numero = %s
            ''', (numero,))
            row = cursor.fetchone()
            
            if not row:
                return False, "Registro no encontrado"
            
            # Guardar en auditoría
            datos_anteriores = f"#{row[1]} - {row[4]} ({row[5]}) - Tutor: {row[-2]} (DNI: {row[-1]})"
            self.registrar_auditoria(
                'DELETE', 'atenciones', row[0], usuario, 
                datos_anteriores=datos_anteriores,
                descripcion=f"Eliminación de atención #{numero}"
            )
            
            # Eliminar
            cursor.execute('DELETE FROM atenciones WHERE numero = %s', (numero,))
            conn.commit()
            return True, "Registro eliminado y guardado en historial"
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"
        finally:
            conn.close()
    
    def obtener_auditoria(self, limite=100):
        """Obtiene el historial de auditoría"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, fecha_hora, tipo_operacion, tabla, registro_id, usuario, 
                   datos_anteriores, datos_nuevos, descripcion
            FROM auditoria
            ORDER BY fecha_hora DESC
            LIMIT %s
        ''', (limite,))
        
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    # Mantener compatibilidad con código antiguo
    def agregar_castracion(self, numero, fecha, nombre_animal, especie, sexo, edad,
                          nombre_apellido, dni, direccion, barrio, telefono):
        """Método legacy - redirige a agregar_atencion con tipo castración"""
        return self.agregar_atencion(numero, fecha, 'castracion', nombre_animal, especie, sexo, edad,
                                     nombre_apellido, dni, direccion, barrio, telefono)
    
    def buscar_atenciones(self, filtros=None):
        """Busca atenciones con filtros opcionales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT a.id, a.numero, a.fecha, a.tipo_atencion, a.nombre_animal, a.especie, a.sexo, a.edad,
                   t.nombre_apellido, t.dni, t.direccion, t.barrio, t.telefono,
                   a.motivo, a.diagnostico, a.tratamiento, a.derivacion, a.observaciones
            FROM atenciones a
            JOIN tutores t ON a.tutor_id = t.id
            WHERE 1=1
        '''
        params = []
        
        if filtros:
            if filtros.get('numero'):
                query += ' AND a.numero = %s'
                params.append(filtros['numero'])
            if filtros.get('tipo_atencion'):
                query += ' AND a.tipo_atencion = %s'
                params.append(filtros['tipo_atencion'])
            if filtros.get('especie'):
                query += ' AND a.especie LIKE %s'
                params.append(f"%{filtros['especie']}%")
            if filtros.get('dni'):
                query += ' AND t.dni LIKE %s'
                params.append(f"%{filtros['dni']}%")
            if filtros.get('barrio'):
                query += ' AND t.barrio LIKE %s'
                params.append(f"%{filtros['barrio']}%")
            if filtros.get('nombre_animal'):
                query += ' AND a.nombre_animal LIKE %s'
                params.append(f"%{filtros['nombre_animal']}%")
            if filtros.get('fecha_desde'):
                query += ' AND a.fecha >= %s'
                params.append(filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                query += ' AND a.fecha <= %s'
                params.append(filtros['fecha_hasta'])
        
        query += ' ORDER BY a.numero DESC'
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        
        return resultados

    # Mantener compatibilidad con código antiguo
    def buscar_castraciones(self, filtros=None):
        """Método legacy - busca solo castraciones"""
        if filtros is None:
            filtros = {}
        filtros['tipo_atencion'] = 'castracion'
        return self.buscar_atenciones(filtros)
    
    def obtener_estadisticas(self, fecha_desde=None, fecha_hasta=None):
        """Obtiene estadísticas con filtros de fecha opcionales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Construir condición de fecha
        fecha_condicion = "1=1"
        fecha_params = []
        if fecha_desde:
            fecha_condicion += " AND fecha >= %s"
            fecha_params.append(fecha_desde)
        if fecha_hasta:
            fecha_condicion += " AND fecha <= %s"
            fecha_params.append(fecha_hasta)
        
        # Total de atenciones
        cursor.execute(f'SELECT COUNT(*) FROM atenciones WHERE {fecha_condicion}', fecha_params)
        stats['total'] = cursor.fetchone()[0]
        
        # Por tipo de atención
        cursor.execute(f'''
            SELECT tipo_atencion, COUNT(*) as cantidad
            FROM atenciones
            WHERE {fecha_condicion}
            GROUP BY tipo_atencion
            ORDER BY cantidad DESC
        ''', fecha_params)
        stats['por_tipo'] = cursor.fetchall()
        
        # Por especie
        cursor.execute(f'''
            SELECT especie, COUNT(*) as cantidad
            FROM atenciones
            WHERE {fecha_condicion}
            GROUP BY especie
            ORDER BY cantidad DESC
        ''', fecha_params)
        stats['por_especie'] = cursor.fetchall()
        
        # Por sexo
        cursor.execute(f'''
            SELECT sexo, COUNT(*) as cantidad
            FROM atenciones
            WHERE {fecha_condicion}
            GROUP BY sexo
        ''', fecha_params)
        stats['por_sexo'] = cursor.fetchall()
        
        # Por día
        cursor.execute(f'''
            SELECT DATE(fecha) as dia, COUNT(*) as cantidad
            FROM atenciones
            WHERE {fecha_condicion}
            GROUP BY dia
            ORDER BY dia ASC
        ''', fecha_params)
        stats['por_dia'] = cursor.fetchall()
        
        # Por semana
        cursor.execute(f'''
            SELECT strftime('%Y-W%W', fecha) as semana, COUNT(*) as cantidad
            FROM atenciones
            WHERE {fecha_condicion}
            GROUP BY semana
            ORDER BY semana ASC
        ''', fecha_params)
        stats['por_semana'] = cursor.fetchall()
        
        # Por mes
        cursor.execute(f'''
            SELECT strftime('%Y-%m', fecha) as mes, COUNT(*) as cantidad
            FROM atenciones
            WHERE {fecha_condicion}
            GROUP BY mes
            ORDER BY mes ASC
        ''', fecha_params)
        stats['por_mes'] = cursor.fetchall()
        
        # Por barrio
        cursor.execute(f'''
            SELECT t.barrio, COUNT(*) as cantidad
            FROM atenciones a
            JOIN tutores t ON a.tutor_id = t.id
            WHERE t.barrio IS NOT NULL AND t.barrio != '' AND {fecha_condicion}
            GROUP BY t.barrio
            ORDER BY cantidad DESC
            LIMIT 15
        ''', fecha_params)
        stats['por_barrio'] = cursor.fetchall()
        
        # Por año
        cursor.execute(f'''
            SELECT strftime('%Y', fecha) as anio, COUNT(*) as cantidad
            FROM atenciones
            WHERE {fecha_condicion}
            GROUP BY anio
            ORDER BY anio DESC
        ''', fecha_params)
        stats['por_anio'] = cursor.fetchall()
        
        # Totales por especie y sexo combinados
        cursor.execute(f'''
            SELECT especie, sexo, COUNT(*) as cantidad
            FROM atenciones
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
        cursor.execute('SELECT MAX(numero) FROM atenciones')
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
            WHERE c.numero = %s
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
            cursor.execute('SELECT id FROM tutores WHERE dni = %s', (dni,))
            tutor = cursor.fetchone()
            
            if tutor:
                tutor_id = tutor[0]
                # Actualizar datos del tutor
                cursor.execute('''
                    UPDATE tutores 
                    SET nombre_apellido = %s, direccion = %s, barrio = %s, telefono = %s
                    WHERE id = %s
                ''', (nombre_apellido, direccion, barrio, telefono, tutor_id))
            else:
                # Crear nuevo tutor
                cursor.execute('''
                    INSERT INTO tutores (nombre_apellido, dni, direccion, barrio, telefono)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (nombre_apellido, dni, direccion, barrio, telefono))
                tutor_id = cursor.lastrowid
            
            # Actualizar castración
            cursor.execute('''
                UPDATE castraciones
                SET numero = %s, fecha = %s, nombre_animal = %s, especie = %s, sexo = %s, edad = %s, tutor_id = %s
                WHERE numero = %s
            ''', (numero, fecha, nombre_animal, especie, sexo, edad, tutor_id, numero_original))
            
            conn.commit()
            return True, "Registro actualizado exitosamente"
        except self.get_integrity_error():
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
            cursor.execute('DELETE FROM castraciones WHERE numero = %s', (numero,))
            
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
        
        # Atenciones de hoy (total)
        cursor.execute('''
            SELECT COUNT(*) FROM atenciones 
            WHERE DATE(fecha) = DATE('now')
        ''')
        stats['hoy'] = cursor.fetchone()[0]
        
        # Atenciones de esta semana
        cursor.execute('''
            SELECT COUNT(*) FROM atenciones 
            WHERE DATE(fecha) >= DATE('now', 'weekday 0', '-7 days')
        ''')
        stats['semana'] = cursor.fetchone()[0]
        
        # Atenciones del mes
        cursor.execute('''
            SELECT COUNT(*) FROM atenciones 
            WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
        ''')
        stats['mes'] = cursor.fetchone()[0]
        
        # Atención primaria del día
        cursor.execute('''
            SELECT COUNT(*) FROM atenciones 
            WHERE DATE(fecha) = DATE('now')
            AND tipo_atencion = 'atencion_primaria'
        ''')
        stats['primaria_hoy'] = cursor.fetchone()[0]
        
        # Últimas 5 atenciones
        cursor.execute('''
            SELECT a.numero, a.fecha, a.tipo_atencion, a.nombre_animal, a.especie, 
                   t.nombre_apellido
            FROM atenciones a
            JOIN tutores t ON a.tutor_id = t.id
            ORDER BY a.fecha DESC, a.numero DESC
            LIMIT 5
        ''')
        resultados = cursor.fetchall()
        stats['ultimas'] = [
            {
                'numero': r[0],
                'fecha': r[1],
                'tipo_atencion': r[2],
                'nombre_animal': r[3],
                'especie': r[4],
                'tutor': r[5]
            }
            for r in resultados
        ]
        
        # Turnos de hoy
        cursor.execute('''
            SELECT id, hora, nombre_animal, tutor_nombre, tipo, estado
            FROM turnos
            WHERE DATE(fecha) = DATE('now')
            ORDER BY hora
        ''')
        resultados = cursor.fetchall()
        stats['turnos_hoy'] = [
            {
                'id': r[0],
                'hora': r[1],
                'nombre_animal': r[2],
                'tutor_nombre': r[3],
                'tipo': r[4],
                'estado': r[5]
            }
            for r in resultados
        ]
        
        # Turnos de esta semana
        cursor.execute('''
            SELECT fecha, hora, nombre_animal, tutor_nombre, tipo, estado, id
            FROM turnos
            WHERE DATE(fecha) >= DATE('now')
            AND DATE(fecha) <= DATE('now', '+7 days')
            ORDER BY fecha, hora
        ''')
        resultados = cursor.fetchall()
        stats['turnos_semana'] = [
            {
                'fecha': r[0],
                'hora': r[1],
                'nombre_animal': r[2],
                'tutor_nombre': r[3],
                'tipo': r[4],
                'estado': r[5],
                'id': r[6]
            }
            for r in resultados
        ]
        
        conn.close()
        return stats
    
    def agregar_turno(self, fecha, hora, nombre_animal, tutor_nombre, telefono, tipo, observaciones=''):
        """Agrega un nuevo turno al cronograma"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO turnos (fecha, hora, nombre_animal, tutor_nombre, telefono, tipo, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
            cursor.execute('UPDATE turnos SET estado = %s WHERE id = %s', (estado, turno_id))
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
            cursor.execute('DELETE FROM turnos WHERE id = %s', (turno_id,))
            conn.commit()
            return True, "Turno eliminado"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    def exportar_a_excel(self, filename='atenciones_export.xlsx', filtros=None):
        """Exporta todas las atenciones a un archivo Excel"""
        try:
            conn = self.get_connection()
            
            # Obtener datos de atenciones con información completa
            query = '''
                SELECT 
                    a.numero AS 'Número',
                    a.fecha AS 'Fecha',
                    a.tipo_atencion AS 'Tipo de Atención',
                    a.nombre_animal AS 'Nombre Animal',
                    a.especie AS 'Especie',
                    a.sexo AS 'Sexo',
                    COALESCE(a.edad, '') AS 'Edad',
                    t.nombre_apellido AS 'Tutor',
                    t.dni AS 'DNI',
                    COALESCE(t.telefono, '') AS 'Teléfono',
                    COALESCE(t.direccion, '') AS 'Dirección',
                    COALESCE(t.barrio, '') AS 'Barrio',
                    COALESCE(a.motivo, '') AS 'Motivo',
                    COALESCE(a.diagnostico, '') AS 'Diagnóstico',
                    COALESCE(a.tratamiento, '') AS 'Tratamiento',
                    COALESCE(a.derivacion, '') AS 'Derivación',
                    a.estado AS 'Estado',
                    COALESCE(a.observaciones, '') AS 'Observaciones'
                FROM atenciones a
                JOIN tutores t ON a.tutor_id = t.id
                ORDER BY a.numero DESC
            '''
            
            # Leer datos en DataFrame
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Crear archivo Excel con formato
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Atenciones', index=False)
                
                # Obtener el workbook y sheet para formatear
                workbook = writer.book
                worksheet = writer.sheets['Atenciones']
                
                # Formatear encabezados
                header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
                header_font = Font(color='FFFFFF', bold=True)
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                
                # Ajustar anchos de columna
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
            return True, f"Datos exportados exitosamente a {filename}"
            
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"

