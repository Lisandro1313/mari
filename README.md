# 🏥 MATECA - Sistema Municipal de Registro de Castraciones

Sistema completo de gestión y registro de castraciones de animales para veterinarios municipales de Gualeguaychú, Entre Ríos.

## 🌐 Demo en vivo

**Accedé a la aplicación:** [https://mateca.onrender.com](https://mateca.onrender.com)

## 📋 Características

- 🏠 **Dashboard operativo** con métricas en tiempo real
- 📅 **Gestión de turnos** y cronograma semanal
- ✅ **Registro completo** de castraciones con datos del animal y tutor
- 🔍 **Búsqueda avanzada** por múltiples criterios
- 📊 **Estadísticas detalladas** con gráficos interactivos (Chart.js)
- 💾 **Base de datos SQLite** integrada
- 🎨 **Interfaz moderna y amigable**
- 📱 **Diseño responsive** para usar en cualquier dispositivo
- 🗺️ **Datos locales** con barrios y calles de Gualeguaychú

## 🗂️ Datos que registra

### Datos del Animal

- Número de registro (único)
- Fecha de castración
- Nombre del animal
- Especie (Canino, Felino, Otro)
- Sexo (Macho, Hembra)
- Edad

### Datos del Tutor

- Nombre y Apellido
- DNI
- Dirección
- Barrio
- Teléfono

## 📊 Estadísticas Disponibles

El sistema genera automáticamente:

- Total de castraciones realizadas
- Cantidad por especie (Caninos, Felinos, etc.)
- Distribución por sexo
- Registro por mes (últimos 12 meses)
- Registro por año
- Top 10 barrios con más castraciones

## 🚀 Instalación y Uso

### Requisitos

- Python 3.7 o superior
- Navegador web moderno

### Instalación Rápida (Windows)

1. **Doble clic en `iniciar.bat`**

   El script automáticamente:

   - Crea un entorno virtual de Python
   - Instala todas las dependencias necesarias
   - Inicia el servidor

2. **Abrir el navegador** y visitar:
   ```
   http://localhost:5000
   ```

### Instalación Manual

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

## 📖 Guía de Uso

### Registrar una Castración

1. Ir a la pestaña **"📝 Nuevo Registro"**
2. Completar los datos del animal
3. Completar los datos del tutor
4. Hacer clic en **"Guardar Registro"**

El número de registro se auto-incrementa automáticamente.

### Buscar Registros

1. Ir a la pestaña **"🔍 Búsqueda"**
2. Completar uno o más filtros:
   - Número de registro
   - Especie
   - DNI del tutor
   - Barrio
   - Rango de fechas
3. Hacer clic en **"Buscar"**

### Ver Estadísticas

1. Ir a la pestaña **"📊 Estadísticas"**
2. El sistema muestra automáticamente:
   - Total de castraciones
   - Gráficos por especie, sexo, mes, año y barrio

## 🗄️ Estructura del Proyecto

```
MARI/
├── app.py                 # Aplicación Flask (servidor web)
├── database.py            # Gestión de base de datos SQLite
├── requirements.txt       # Dependencias Python
├── iniciar.bat           # Script de inicio automático
├── README.md             # Esta documentación
├── mari.db               # Base de datos (se crea automáticamente)
├── templates/
│   └── index.html        # Interfaz web principal
└── static/
    ├── style.css         # Estilos y diseño
    └── script.js         # Funcionalidad JavaScript
```

## 🔧 Características Técnicas

- **Backend**: Python + Flask
- **Base de datos**: SQLite (sin configuración necesaria)
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **API REST**: Endpoints JSON para todas las operaciones
- **Sin dependencias externas** de librerías JavaScript

## 📝 Notas Importantes

- La base de datos `mari.db` se crea automáticamente en el primer uso
- Los números de registro deben ser únicos
- El DNI del tutor se usa para evitar duplicados y mantener datos actualizados
- Todos los registros quedan guardados permanentemente

## 🆘 Solución de Problemas

### El servidor no inicia

- Verificar que Python está instalado: `python --version`
- Verificar que el puerto 5000 no está en uso
- Revisar que las dependencias están instaladas: `pip list`

### No puedo acceder desde el navegador

- Verificar que el servidor está corriendo
- Probar con `http://127.0.0.1:5000` en lugar de localhost
- Desactivar temporalmente el firewall/antivirus

### Error al guardar registros

- Verificar que el número de registro no esté duplicado
- Verificar que todos los campos obligatorios estén completos (marcados con \*)

## 📞 Soporte

Para problemas o consultas sobre el sistema MARI, contactar al área de sistemas del municipio.

## 📄 Licencia

Sistema desarrollado para uso interno municipal.

---

**MARI** - Sistema Municipal de Registro de Castraciones  
Versión 1.0 - 2025
