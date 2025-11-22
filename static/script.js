// Variables globales para los gráficos
let chartTemporal, chartEspecie, chartSexo, chartEspecieSexo, chartBarrios;
let currentStatsData = null;
let currentTimeView = 'dia';
let dashboardData = null;

// Navegación entre tabs
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    if (tabName === 'estadisticas') {
        cargarEstadisticas();
    }

    if (tabName === 'busqueda') {
        buscarCastraciones();
    }

    if (tabName === 'dashboard') {
        cargarDashboard();
    }
}

// Notificaciones
function mostrarNotificacion(mensaje, tipo = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = mensaje;
    notification.className = `notification ${tipo}`;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

// Cargar siguiente número
async function cargarSiguienteNumero() {
    try {
        const response = await fetch('/api/siguiente-numero');
        const data = await response.json();
        document.getElementById('numero').value = data.numero;
    } catch (error) {
        console.error('Error al cargar siguiente número:', error);
    }
}

// Fecha actual
function establecerFechaActual() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('fecha').value = today;
}

// Formulario de registro
document.getElementById('formRegistro').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const modoEdicion = e.target.dataset.modoEdicion === 'true';
    const numeroOriginal = e.target.dataset.numeroOriginal;

    try {
        let response;

        if (modoEdicion) {
            response = await fetch(`/api/castraciones/${numeroOriginal}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch('/api/castraciones', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }

        const result = await response.json();

        if (result.success) {
            mostrarNotificacion(result.message, 'success');
            limpiarFormulario();
            cargarSiguienteNumero();
        } else {
            mostrarNotificacion(result.message, 'error');
        }
    } catch (error) {
        mostrarNotificacion('Error al guardar el registro', 'error');
        console.error('Error:', error);
    }
});

// Limpiar formulario
function limpiarFormulario() {
    const form = document.getElementById('formRegistro');
    form.reset();
    delete form.dataset.modoEdicion;
    delete form.dataset.numeroOriginal;
    establecerFechaActual();
    cargarSiguienteNumero();
}

// Búsqueda
document.getElementById('formBusqueda').addEventListener('submit', async (e) => {
    e.preventDefault();
    await buscarCastraciones();
});

async function buscarCastraciones() {
    const formData = new FormData(document.getElementById('formBusqueda'));
    const params = new URLSearchParams();

    for (let [key, value] of formData.entries()) {
        if (value) params.append(key, value);
    }

    const resultadosDiv = document.getElementById('resultados');
    resultadosDiv.innerHTML = '<div class="loading">Cargando resultados</div>';

    try {
        const response = await fetch(`/api/castraciones?${params}`);
        const castraciones = await response.json();

        if (castraciones.length === 0) {
            resultadosDiv.innerHTML = '<div class="no-results">No se encontraron registros</div>';
            return;
        }

        resultadosDiv.innerHTML = `<h3>Resultados (${castraciones.length} registro${castraciones.length !== 1 ? 's' : ''})</h3>`;

        castraciones.forEach(cast => {
            const item = document.createElement('div');
            item.className = 'resultado-item';
            item.innerHTML = `
                <h4>N° ${cast.numero} - ${cast.nombre_animal}</h4>
                <div class="resultado-info">
                    <div>
                        <p><strong>Fecha:</strong> ${formatearFecha(cast.fecha)}</p>
                        <p><strong>Especie:</strong> ${cast.especie}</p>
                        <p><strong>Sexo:</strong> ${cast.sexo}</p>
                        <p><strong>Edad:</strong> ${cast.edad || 'No especificada'}</p>
                    </div>
                    <div>
                        <p><strong>Tutor:</strong> ${cast.tutor.nombre_apellido}</p>
                        <p><strong>DNI:</strong> ${cast.tutor.dni}</p>
                        <p><strong>Barrio:</strong> ${cast.tutor.barrio || 'No especificado'}</p>
                        <p><strong>Teléfono:</strong> ${cast.tutor.telefono || 'No especificado'}</p>
                    </div>
                </div>
                <div class="acciones-registro">
                    <button class="btn-accion btn-editar" onclick="editarRegistro(${cast.numero})">✏️ Editar</button>
                    <button class="btn-accion btn-eliminar" onclick="confirmarEliminar(${cast.numero})">🗑️ Eliminar</button>
                </div>
            `;
            resultadosDiv.appendChild(item);
        });
    } catch (error) {
        resultadosDiv.innerHTML = '<div class="no-results">Error al cargar los resultados</div>';
        console.error('Error:', error);
    }
}

function limpiarBusqueda() {
    document.getElementById('formBusqueda').reset();
    document.getElementById('resultados').innerHTML = '';
}

// Editar registro
async function editarRegistro(numero) {
    try {
        const response = await fetch(`/api/castraciones/${numero}`);
        const cast = await response.json();

        if (!cast || !cast.success && cast.success === false) {
            mostrarNotificacion('No se pudo cargar el registro', 'error');
            return;
        }

        document.getElementById('numero').value = cast.numero;
        document.getElementById('fecha').value = cast.fecha;
        document.getElementById('nombre_animal').value = cast.nombre_animal;
        document.getElementById('especie').value = cast.especie;
        document.getElementById('sexo').value = cast.sexo;
        document.getElementById('edad').value = cast.edad || '';
        document.getElementById('nombre_apellido').value = cast.tutor.nombre_apellido;
        document.getElementById('dni').value = cast.tutor.dni;
        document.getElementById('direccion').value = cast.tutor.direccion || '';
        document.getElementById('barrio').value = cast.tutor.barrio || '';
        document.getElementById('telefono').value = cast.tutor.telefono || '';

        document.getElementById('formRegistro').dataset.numeroOriginal = numero;
        document.getElementById('formRegistro').dataset.modoEdicion = 'true';

        document.querySelector('.tab-button').click();

        mostrarNotificacion('Editando registro N° ' + numero, 'info');
    } catch (error) {
        console.error('Error al cargar registro:', error);
        mostrarNotificacion('Error al cargar el registro', 'error');
    }
}

// Eliminar registro
function confirmarEliminar(numero) {
    if (confirm(`¿Está seguro que desea eliminar el registro N° ${numero}?\n\nEsta acción no se puede deshacer.`)) {
        eliminarRegistro(numero);
    }
}

async function eliminarRegistro(numero) {
    try {
        const response = await fetch(`/api/castraciones/${numero}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            mostrarNotificacion(result.message, 'success');
            buscarCastraciones();
        } else {
            mostrarNotificacion(result.message, 'error');
        }
    } catch (error) {
        console.error('Error al eliminar:', error);
        mostrarNotificacion('Error al eliminar el registro', 'error');
    }
}

// ESTADÍSTICAS
async function cargarEstadisticas() {
    const fechaDesde = document.getElementById('stats-fecha-desde')?.value || '';
    const fechaHasta = document.getElementById('stats-fecha-hasta')?.value || '';

    const params = new URLSearchParams();
    if (fechaDesde) params.append('fecha_desde', fechaDesde);
    if (fechaHasta) params.append('fecha_hasta', fechaHasta);

    try {
        const response = await fetch(`/api/estadisticas?${params}`);
        const stats = await response.json();

        currentStatsData = stats;

        // Actualizar tarjetas de resumen
        document.getElementById('stat-total').textContent = stats.total;

        const caninos = stats.por_especie.find(e => e.especie === 'Canino')?.cantidad || 0;
        const felinos = stats.por_especie.find(e => e.especie === 'Felino')?.cantidad || 0;

        document.getElementById('stat-caninos').textContent = caninos;
        document.getElementById('stat-felinos').textContent = felinos;
        document.getElementById('stat-barrios').textContent = stats.por_barrio.length;

        // Renderizar gráficos
        renderizarGraficos(stats);

    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        mostrarNotificacion('Error al cargar estadísticas', 'error');
    }
}

function limpiarFiltrosEstadisticas() {
    document.getElementById('stats-fecha-desde').value = '';
    document.getElementById('stats-fecha-hasta').value = '';
    cargarEstadisticas();
}

function cambiarVistaTime(vista) {
    currentTimeView = vista;

    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    if (currentStatsData) {
        renderizarGraficoTemporal(currentStatsData);
    }
}

function renderizarGraficos(stats) {
    renderizarGraficoTemporal(stats);
    renderizarGraficoEspecie(stats);
    renderizarGraficoSexo(stats);
    renderizarGraficoEspecieSexo(stats);
    renderizarGraficoBarrios(stats);
}

function renderizarGraficoTemporal(stats) {
    const ctx = document.getElementById('chartTemporal');

    let labels = [];
    let data = [];

    if (currentTimeView === 'dia') {
        labels = stats.por_dia.map(d => formatearFecha(d.dia));
        data = stats.por_dia.map(d => d.cantidad);
    } else if (currentTimeView === 'semana') {
        labels = stats.por_semana.map(d => 'Semana ' + d.semana.split('-W')[1] + '/' + d.semana.split('-')[0]);
        data = stats.por_semana.map(d => d.cantidad);
    } else if (currentTimeView === 'mes') {
        labels = stats.por_mes.map(d => formatearMes(d.mes));
        data = stats.por_mes.map(d => d.cantidad);
    } else if (currentTimeView === 'anio') {
        labels = stats.por_anio.map(d => d.anio);
        data = stats.por_anio.map(d => d.cantidad);
    }

    if (chartTemporal) {
        chartTemporal.destroy();
    }

    chartTemporal = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Castraciones',
                data: data,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#6366f1',
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2.5,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Evolución Temporal de Castraciones',
                    font: { size: 16, weight: 'bold' },
                    color: '#1f2937'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function renderizarGraficoEspecie(stats) {
    const ctx = document.getElementById('chartEspecie');

    if (chartEspecie) {
        chartEspecie.destroy();
    }

    const colores = {
        'Canino': '#3b82f6',
        'Felino': '#8b5cf6',
        'Otro': '#10b981'
    };

    chartEspecie = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: stats.por_especie.map(e => e.especie),
            datasets: [{
                data: stats.por_especie.map(e => e.cantidad),
                backgroundColor: stats.por_especie.map(e => colores[e.especie] || '#6b7280'),
                borderWidth: 2,
                borderColor: '#fff'
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

function renderizarGraficoSexo(stats) {
    const ctx = document.getElementById('chartSexo');

    if (chartSexo) {
        chartSexo.destroy();
    }

    chartSexo = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: stats.por_sexo.map(s => s.sexo),
            datasets: [{
                data: stats.por_sexo.map(s => s.cantidad),
                backgroundColor: ['#6366f1', '#ec4899'],
                borderWidth: 2,
                borderColor: '#fff'
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

function renderizarGraficoEspecieSexo(stats) {
    const ctx = document.getElementById('chartEspecieSexo');

    if (chartEspecieSexo) {
        chartEspecieSexo.destroy();
    }

    const especies = [...new Set(stats.especie_sexo.map(e => e.especie))];
    const machos = especies.map(esp => {
        const item = stats.especie_sexo.find(e => e.especie === esp && e.sexo === 'Macho');
        return item ? item.cantidad : 0;
    });
    const hembras = especies.map(esp => {
        const item = stats.especie_sexo.find(e => e.especie === esp && e.sexo === 'Hembra');
        return item ? item.cantidad : 0;
    });

    chartEspecieSexo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: especies,
            datasets: [
                {
                    label: 'Machos',
                    data: machos,
                    backgroundColor: '#6366f1'
                },
                {
                    label: 'Hembras',
                    data: hembras,
                    backgroundColor: '#ec4899'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function renderizarGraficoBarrios(stats) {
    const ctx = document.getElementById('chartBarrios');

    if (chartBarrios) {
        chartBarrios.destroy();
    }

    chartBarrios = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stats.por_barrio.map(b => b.barrio),
            datasets: [{
                label: 'Castraciones',
                data: stats.por_barrio.map(b => b.cantidad),
                backgroundColor: '#10b981',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Utilidades
function formatearFecha(fecha) {
    const [year, month, day] = fecha.split('-');
    return `${day}/${month}/${year}`;
}

function formatearMes(mes) {
    const [year, month] = mes.split('-');
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return `${meses[parseInt(month) - 1]} ${year}`;
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    establecerFechaActual();
    cargarSiguienteNumero();
    cargarDashboard();
});

// ===== DASHBOARD =====
async function cargarDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        dashboardData = data;

        // Actualizar métricas
        document.getElementById('metric-hoy').textContent = data.castraciones_hoy;
        document.getElementById('metric-semana').textContent = data.castraciones_semana;
        document.getElementById('metric-mes').textContent = data.castraciones_mes;
        document.getElementById('metric-primaria').textContent = data.atencion_primaria;

        // Renderizar turnos de hoy
        renderizarTurnosHoy(data.turnos_hoy);

        // Renderizar cronograma de la semana
        renderizarCronograma(data.turnos_semana);

        // Renderizar últimas castraciones
        renderizarUltimasCastraciones(data.ultimas_castraciones);

    } catch (error) {
        console.error('Error al cargar dashboard:', error);
        mostrarNotificacion('Error al cargar datos del dashboard', 'error');
    }
}

function renderizarTurnosHoy(turnos) {
    const container = document.getElementById('turnos-hoy-list');

    if (!turnos || turnos.length === 0) {
        container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 20px;">No hay turnos programados para hoy</p>';
        return;
    }

    container.innerHTML = turnos.map(turno => `
        <div class="turno-item">
            <div class="turno-info">
                <div class="turno-hora">${turno.hora}</div>
                <div class="turno-detalles">
                    <strong>${turno.nombre_animal}</strong> - ${turno.tutor_nombre}
                    <br>
                    <span class="turno-tipo">${turno.tipo}</span>
                </div>
            </div>
            <div class="turno-actions">
                ${turno.estado === 'pendiente' ? `
                    <button class="btn-icon btn-complete" onclick="actualizarEstadoTurno(${turno.id}, 'completado')" title="Completar">
                        ✓
                    </button>
                    <button class="btn-icon btn-cancel" onclick="actualizarEstadoTurno(${turno.id}, 'cancelado')" title="Cancelar">
                        ✕
                    </button>
                ` : `
                    <span class="estado-badge estado-${turno.estado}">${turno.estado}</span>
                `}
            </div>
        </div>
    `).join('');
}

function renderizarCronograma(turnos) {
    const container = document.getElementById('cronograma-semana');

    if (!turnos || turnos.length === 0) {
        container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 20px;">No hay turnos programados para esta semana</p>';
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

    container.innerHTML = fechasOrdenadas.map(fecha => `
        <div class="cronograma-dia">
            <div class="cronograma-fecha">${formatearFechaCronograma(fecha)}</div>
            <div class="cronograma-turnos">
                ${turnosPorFecha[fecha].map(turno => `
                    <div class="cronograma-turno">
                        <span class="cronograma-turno-hora">${turno.hora}</span>
                        <span>${turno.nombre_animal} - ${turno.tipo}</span>
                        <span class="estado-badge estado-${turno.estado}">${turno.estado}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function renderizarUltimasCastraciones(castraciones) {
    const container = document.getElementById('ultimas-castraciones');

    if (!castraciones || castraciones.length === 0) {
        container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 20px;">No hay registros recientes</p>';
        return;
    }

    container.innerHTML = castraciones.map(c => `
        <div class="ultima-item">
            <div class="ultima-info">
                <div class="ultima-numero">#${c.numero} - ${c.nombre_animal}</div>
                <div class="ultima-detalles">
                    ${formatearFecha(c.fecha)} - ${c.especie} ${c.sexo}
                </div>
            </div>
            <span class="badge-${c.atencion_primaria ? 'primaria' : 'recurrente'}">
                ${c.atencion_primaria ? 'Atención Primaria' : 'Recurrente'}
            </span>
        </div>
    `).join('');
}

function formatearFechaCronograma(fecha) {
    const [year, month, day] = fecha.split('-');
    const fechaObj = new Date(year, month - 1, day);
    const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

    return `${dias[fechaObj.getDay()]} ${day}/${month} - ${meses[parseInt(month) - 1]}`;
}

// ===== GESTIÓN DE TURNOS =====
function mostrarFormularioTurno() {
    document.getElementById('modal-turno').classList.add('show');
}

function cerrarModalTurno() {
    document.getElementById('modal-turno').classList.remove('show');
    document.getElementById('form-turno').reset();
}

async function guardarTurno(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
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
            headers: {
                'Content-Type': 'application/json'
            },
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
        console.error('Error:', error);
        mostrarNotificacion('Error al crear turno', 'error');
    }
}

async function actualizarEstadoTurno(id, estado) {
    try {
        const response = await fetch(`/api/turnos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ estado })
        });

        if (response.ok) {
            mostrarNotificacion(`Turno ${estado}`, 'success');
            cargarDashboard();
        } else {
            mostrarNotificacion('Error al actualizar turno', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al actualizar turno', 'error');
    }
}

async function eliminarTurno(id) {
    if (!confirm('¿Está seguro de eliminar este turno?')) {
        return;
    }

    try {
        const response = await fetch(`/api/turnos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            mostrarNotificacion('Turno eliminado', 'success');
            cargarDashboard();
        } else {
            mostrarNotificacion('Error al eliminar turno', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al eliminar turno', 'error');
    }
}

