// Variables globales
let charts = {};
let dashboardData = null;

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupNavigation();
    setupFormHandlers();
    cargarSiguienteNumero();
    establecerFechaActual();
    cargarDashboard();
    updateDateTime();
    setInterval(updateDateTime, 1000);
});

function initializeApp() {
    // Configurar tipo de atención selector
    document.querySelectorAll('.tipo-option').forEach(option => {
        option.addEventListener('click', function () {
            document.querySelectorAll('.tipo-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            this.querySelector('input').checked = true;

            const tipo = this.querySelector('input').value;
            const sectionAtencionPrimaria = document.getElementById('section-atencion-primaria');
            sectionAtencionPrimaria.style.display = tipo === 'atencion_primaria' ? 'block' : 'none';
        });
    });
}

function updateDateTime() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('current-datetime').textContent =
        now.toLocaleDateString('es-AR', options);
}

function establecerFechaActual() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('fecha').value = today;
}

async function cargarSiguienteNumero() {
    try {
        const response = await fetch('/api/siguiente-numero');
        const data = await response.json();
        document.getElementById('numero').value = data.numero;
    } catch (error) {
        console.error('Error al cargar siguiente número:', error);
    }
}

// ===== NAVEGACIÓN =====
function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            showSection(section);
        });
    });
}

function showSection(sectionName) {
    // Actualizar nav
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // Actualizar contenido
    document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
    document.getElementById(sectionName).classList.add('active');

    // Actualizar título
    const titles = {
        dashboard: { title: 'Dashboard', subtitle: 'Vista general del sistema' },
        registro: { title: 'Nueva Atención', subtitle: 'Registrar castración o atención primaria' },
        busqueda: { title: 'Búsqueda', subtitle: 'Consultar atenciones registradas' },
        estadisticas: { title: 'Estadísticas', subtitle: 'Análisis y reportes' },
        turnos: { title: 'Agenda', subtitle: 'Gestión de turnos' }
    };

    document.getElementById('section-title').textContent = titles[sectionName].title;
    document.getElementById('section-subtitle').textContent = titles[sectionName].subtitle;

    // Cargar datos específicos
    if (sectionName === 'dashboard') cargarDashboard();
    if (sectionName === 'estadisticas') cargarEstadisticas();
    if (sectionName === 'turnos') cargarTodosTurnos();
}

// ===== DASHBOARD =====
async function cargarDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        dashboardData = await response.json();

        // Actualizar métricas
        document.getElementById('metric-hoy').textContent = dashboardData.hoy || 0;
        document.getElementById('metric-semana').textContent = dashboardData.semana || 0;
        document.getElementById('metric-mes').textContent = dashboardData.mes || 0;
        document.getElementById('metric-primaria').textContent = dashboardData.primaria_hoy || 0;

        // Renderizar secciones
        renderizarTurnosHoy(dashboardData.turnos_hoy);
        renderizarUltimasAtenciones(dashboardData.ultimas);
        renderizarCronograma(dashboardData.turnos_semana);

    } catch (error) {
        console.error('Error al cargar dashboard:', error);
        mostrarNotificacion('Error al cargar datos del dashboard', 'error');
    }
}

function renderizarTurnosHoy(turnos) {
    const container = document.getElementById('turnos-hoy-container');

    if (!turnos || turnos.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">No hay turnos programados para hoy</p>';
        return;
    }

    container.innerHTML = turnos.map(turno => `
        <div class="turno-item">
            <div>
                <div class="turno-hora">${turno.hora}</div>
                <div class="turno-detalles">
                    <strong>${turno.nombre_animal}</strong> - ${turno.tutor_nombre}
                    <br><span style="font-size: 0.85em;">${turno.tipo}</span>
                </div>
            </div>
            <div class="turno-actions">
                ${turno.estado === 'pendiente' ? `
                    <button class="btn-icon btn-complete" onclick="actualizarEstadoTurno(${turno.id}, 'completado')" title="Completar">✓</button>
                    <button class="btn-icon btn-cancel" onclick="actualizarEstadoTurno(${turno.id}, 'cancelado')" title="Cancelar">✕</button>
                ` : `
                    <span class="estado-badge estado-${turno.estado}">${turno.estado}</span>
                `}
            </div>
        </div>
    `).join('');
}

function renderizarUltimasAtenciones(atenciones) {
    const container = document.getElementById('ultimas-atenciones-container');

    if (!atenciones || atenciones.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">No hay atenciones recientes</p>';
        return;
    }

    container.innerHTML = atenciones.map(a => `
        <div class="atencion-item">
            <div>
                <div class="atencion-numero">#${a.numero} - ${a.nombre_animal}</div>
                <div class="atencion-detalles">
                    ${formatearFecha(a.fecha)} - ${a.especie}
                    <br><span class="result-tipo ${a.tipo_atencion === 'castracion' ? 'tipo-castracion' : 'tipo-atencion-primaria'}">
                        ${a.tipo_atencion === 'castracion' ? 'Castración' : 'Atención Primaria'}
                    </span>
                </div>
            </div>
            <div style="text-align: right; color: #64748b; font-size: 0.9em;">
                ${a.tutor}
            </div>
        </div>
    `).join('');
}

function renderizarCronograma(turnos) {
    const container = document.getElementById('cronograma-container');

    if (!turnos || turnos.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">No hay turnos programados para esta semana</p>';
        return;
    }

    // Agrupar turnos por fecha
    const turnosPorFecha = {};
    turnos.forEach(turno => {
        if (!turnosPorFecha[turno.fecha]) {
            turnosPorFecha[turno.fecha] = [];
        }
        turnosPorFecha[turno.fecha].push(turno);
    });

    // Ordenar fechas
    const fechasOrdenadas = Object.keys(turnosPorFecha).sort();

    container.innerHTML = fechasOrdenadas.map(fecha => {
        const turnosDia = turnosPorFecha[fecha];
        return `
            <div class="cronograma-dia">
                <div class="cronograma-fecha">${formatearFechaCronograma(fecha)}</div>
                <div class="cronograma-turnos">
                    ${turnosDia.map(turno => `
                        <div class="cronograma-turno">
                            <span class="cronograma-turno-hora">${turno.hora}</span>
                            <span class="cronograma-turno-info">${turno.nombre_animal} - ${turno.tipo}</span>
                            <span class="estado-badge estado-${turno.estado}">${turno.estado}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function formatearFechaCronograma(fecha) {
    const [year, month, day] = fecha.split('-');
    const fechaObj = new Date(year, month - 1, day);
    const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

    return `${dias[fechaObj.getDay()]} ${day}/${month} - ${meses[parseInt(month) - 1]} ${year}`;
}

// ===== FORMULARIO ATENCIÓN =====
function setupFormHandlers() {
    document.getElementById('form-atencion').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = {
            numero: parseInt(formData.get('numero')),
            fecha: formData.get('fecha'),
            tipo_atencion: formData.get('tipo_atencion'),
            nombre_animal: formData.get('nombre_animal'),
            especie: formData.get('especie'),
            sexo: formData.get('sexo'),
            edad: formData.get('edad') || '',
            nombre_apellido: formData.get('nombre_apellido'),
            dni: formData.get('dni'),
            telefono: formData.get('telefono') || '',
            direccion: formData.get('direccion') || '',
            barrio: formData.get('barrio') || '',
            motivo: formData.get('motivo') || '',
            diagnostico: formData.get('diagnostico') || '',
            tratamiento: formData.get('tratamiento') || '',
            derivacion: formData.get('derivacion') || '',
            observaciones: formData.get('observaciones') || ''
        };

        try {
            const response = await fetch('/api/atenciones', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                mostrarNotificacion(result.message, 'success');
                e.target.reset();
                establecerFechaActual();
                cargarSiguienteNumero();
                document.querySelectorAll('.tipo-option').forEach((opt, i) => {
                    if (i === 0) opt.classList.add('active');
                    else opt.classList.remove('active');
                });
                document.getElementById('section-atencion-primaria').style.display = 'none';
            } else {
                mostrarNotificacion(result.message, 'error');
            }
        } catch (error) {
            mostrarNotificacion('Error al registrar atención', 'error');
        }
    });

    // Form turnos
    document.getElementById('form-turno').addEventListener('submit', guardarTurno);
}

function limpiarFormulario() {
    document.getElementById('form-atencion').reset();
    establecerFechaActual();
    cargarSiguienteNumero();
    document.querySelectorAll('.tipo-option').forEach((opt, i) => {
        if (i === 0) opt.classList.add('active');
        else opt.classList.remove('active');
    });
    document.getElementById('section-atencion-primaria').style.display = 'none';
}

// ===== BÚSQUEDA =====
async function buscarAtenciones() {
    const filtros = {
        numero: document.getElementById('search-numero').value,
        tipo_atencion: document.getElementById('search-tipo').value,
        especie: document.getElementById('search-especie').value,
        dni: document.getElementById('search-dni').value,
        barrio: document.getElementById('search-barrio').value,
        fecha_desde: document.getElementById('search-fecha-desde').value,
        fecha_hasta: document.getElementById('search-fecha-hasta').value
    };

    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([key, value]) => {
        if (value) params.append(key, value);
    });

    try {
        const response = await fetch(`/api/atenciones?${params}`);
        const resultados = await response.json();

        const container = document.getElementById('resultados-busqueda');

        if (resultados.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">No se encontraron resultados</p>';
            return;
        }

        container.innerHTML = resultados.map(r => `
            <div class="result-item">
                <div class="result-header">
                    <span class="result-number">#${r.numero} - ${r.nombre_animal}</span>
                    <span class="result-tipo ${r.tipo_atencion === 'castracion' ? 'tipo-castracion' : 'tipo-atencion-primaria'}">
                        ${r.tipo_atencion === 'castracion' ? 'Castración' : 'Atención Primaria'}
                    </span>
                </div>
                <div class="result-details">
                    <strong>Fecha:</strong> ${formatearFecha(r.fecha)} | 
                    <strong>Especie:</strong> ${r.especie} ${r.sexo} | 
                    <strong>Edad:</strong> ${r.edad || 'No especificada'}
                    <br>
                    <strong>Tutor:</strong> ${r.tutor.nombre_apellido} (DNI: ${r.tutor.dni}) | 
                    <strong>Teléfono:</strong> ${r.tutor.telefono || 'No registrado'}
                    <br>
                    <strong>Dirección:</strong> ${r.tutor.direccion || 'No registrada'} | 
                    <strong>Barrio:</strong> ${r.tutor.barrio || 'No especificado'}
                    ${r.motivo ? `<br><strong>Motivo:</strong> ${r.motivo}` : ''}
                    ${r.diagnostico ? `<br><strong>Diagnóstico:</strong> ${r.diagnostico}` : ''}
                    ${r.tratamiento ? `<br><strong>Tratamiento:</strong> ${r.tratamiento}` : ''}
                    ${r.derivacion ? `<br><strong>Derivación:</strong> ${r.derivacion}` : ''}
                    ${r.observaciones ? `<br><strong>Observaciones:</strong> ${r.observaciones}` : ''}
                </div>
            </div>
        `).join('');

    } catch (error) {
        mostrarNotificacion('Error en la búsqueda', 'error');
    }
}

// ===== ESTADÍSTICAS =====
async function cargarEstadisticas() {
    const desde = document.getElementById('stats-fecha-desde').value;
    const hasta = document.getElementById('stats-fecha-hasta').value;

    const params = new URLSearchParams();
    if (desde) params.append('fecha_desde', desde);
    if (hasta) params.append('fecha_hasta', hasta);

    try {
        const response = await fetch(`/api/estadisticas?${params}`);
        const stats = await response.json();

        renderizarGraficos(stats);
    } catch (error) {
        mostrarNotificacion('Error al cargar estadísticas', 'error');
    }
}

function renderizarGraficos(stats) {
    // Tipo de atención
    if (stats.por_tipo && stats.por_tipo.length > 0) {
        renderChart('chart-tipo', 'doughnut', {
            labels: stats.por_tipo.map(t => t[0] === 'castracion' ? 'Castración' : 'Atención Primaria'),
            data: stats.por_tipo.map(t => t[1])
        });
    }

    // Especie
    if (stats.por_especie && stats.por_especie.length > 0) {
        renderChart('chart-especie', 'pie', {
            labels: stats.por_especie.map(e => e[0]),
            data: stats.por_especie.map(e => e[1])
        });
    }

    // Sexo
    if (stats.por_sexo && stats.por_sexo.length > 0) {
        renderChart('chart-sexo', 'doughnut', {
            labels: stats.por_sexo.map(s => s[0]),
            data: stats.por_sexo.map(s => s[1])
        });
    }

    // Temporal
    if (stats.por_mes && stats.por_mes.length > 0) {
        renderChart('chart-temporal', 'line', {
            labels: stats.por_mes.map(m => formatearMes(m[0])),
            data: stats.por_mes.map(m => m[1])
        });
    }

    // Barrios
    if (stats.por_barrio && stats.por_barrio.length > 0) {
        renderChart('chart-barrios', 'bar', {
            labels: stats.por_barrio.slice(0, 10).map(b => b[0]),
            data: stats.por_barrio.slice(0, 10).map(b => b[1])
        });
    }
}

function renderChart(canvasId, type, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6',
                    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// ===== TURNOS =====
function mostrarFormularioTurno() {
    document.getElementById('modal-turno').classList.add('show');
}

function cerrarModalTurno() {
    document.getElementById('modal-turno').classList.remove('show');
    document.getElementById('form-turno').reset();
}

async function guardarTurno(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const turno = {
        fecha: formData.get('fecha'),
        hora: formData.get('hora'),
        nombre_animal: formData.get('nombre_animal'),
        tutor_nombre: formData.get('tutor_nombre'),
        telefono: formData.get('telefono'),
        tipo: formData.get('tipo'),
        observaciones: formData.get('observaciones')
    };

    try {
        const response = await fetch('/api/turnos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(turno)
        });

        if (response.ok) {
            mostrarNotificacion('Turno creado exitosamente', 'success');
            cerrarModalTurno();
            cargarDashboard();
        } else {
            mostrarNotificacion('Error al crear turno', 'error');
        }
    } catch (error) {
        mostrarNotificacion('Error al crear turno', 'error');
    }
}

async function actualizarEstadoTurno(id, estado) {
    try {
        const response = await fetch(`/api/turnos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estado })
        });

        if (response.ok) {
            mostrarNotificacion(`Turno ${estado}`, 'success');
            cargarDashboard();
        } else {
            mostrarNotificacion('Error al actualizar turno', 'error');
        }
    } catch (error) {
        mostrarNotificacion('Error al actualizar turno', 'error');
    }
}

async function cargarTodosTurnos() {
    // Implementar carga de todos los turnos si es necesario
    cargarDashboard();
}

// ===== EXPORTAR EXCEL =====
async function exportarExcel() {
    try {
        mostrarNotificacion('Generando archivo Excel...', 'info');

        const response = await fetch('/api/exportar');

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `atenciones_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            mostrarNotificacion('Archivo descargado exitosamente', 'success');
        } else {
            mostrarNotificacion('Error al exportar datos', 'error');
        }
    } catch (error) {
        mostrarNotificacion('Error al exportar datos', 'error');
    }
}

// ===== UTILIDADES =====
function formatearFecha(fecha) {
    const [year, month, day] = fecha.split('-');
    return `${day}/${month}/${year}`;
}

function formatearMes(mes) {
    const [year, month] = mes.split('-');
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return `${meses[parseInt(month) - 1]} ${year}`;
}

function mostrarNotificacion(mensaje, tipo = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = mensaje;
    notification.className = `notification ${tipo} show`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

function logout() {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        window.location.href = '/logout';
    }
}

