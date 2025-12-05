// Variables globales
let charts = {};
let dashboardData = null;

// ===== MENÚ MÓVIL =====
function toggleMenu() {
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.querySelector('.menu-toggle');
    const menuOverlay = document.querySelector('.menu-overlay');

    sidebar.classList.toggle('active');
    menuToggle.classList.toggle('active');
    menuOverlay.classList.toggle('active');
}

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
    // Cerrar menú móvil si está abierto
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.querySelector('.menu-toggle');
    const menuOverlay = document.querySelector('.menu-overlay');

    if (sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        menuToggle.classList.remove('active');
        menuOverlay.classList.remove('active');
    }

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
        turnos: { title: 'Agenda', subtitle: 'Gestión de turnos' },
        auditoria: { title: 'Historial de Cambios', subtitle: 'Auditoría del sistema' }
    };

    document.getElementById('section-title').textContent = titles[sectionName].title;
    document.getElementById('section-subtitle').textContent = titles[sectionName].subtitle;

    // Cargar datos específicos
    if (sectionName === 'dashboard') cargarDashboard();
    if (sectionName === 'estadisticas') cargarEstadisticas();
    if (sectionName === 'turnos') cargarTodosTurnos();
    if (sectionName === 'auditoria') cargarAuditoria();
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
            let response;
            const isEditing = window.editandoNumero !== undefined;

            if (isEditing) {
                // Modo edición - usar PUT
                response = await fetch(`/api/atenciones/${window.editandoNumero}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            } else {
                // Modo crear nuevo - usar POST
                response = await fetch('/api/atenciones', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            }

            const result = await response.json();

            if (result.success) {
                mostrarNotificacion(result.message, 'success');
                e.target.reset();
                establecerFechaActual();

                // Limpiar modo edición y restaurar título
                if (isEditing) {
                    delete window.editandoNumero;
                    document.getElementById('section-title').textContent = 'Nueva Atención';
                    document.getElementById('section-subtitle').textContent = 'Registrar castración o atención primaria';
                    const submitBtn = document.querySelector('#form-atencion button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.textContent = 'Registrar Atención';
                    }
                    cargarDashboard();
                } else {
                    cargarSiguienteNumero();
                }

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
    document.getElementById('form-turno').addEventListener('submit', (e) => {
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

        fetch('/api/turnos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(turno)
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    mostrarNotificacion('Turno creado exitosamente', 'success');
                    cerrarModalTurno();
                    cargarDashboard();
                } else {
                    mostrarNotificacion('Error al crear turno', 'error');
                }
            })
            .catch(error => {
                mostrarNotificacion('Error al crear turno', 'error');
            });
    });
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
    
    // Restaurar título y botón si estaba editando
    if (window.editandoNumero) {
        delete window.editandoNumero;
        document.getElementById('section-title').textContent = 'Nueva Atención';
        document.getElementById('section-subtitle').textContent = 'Registrar castración o atención primaria';
        const submitBtn = document.querySelector('#form-atencion button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Registrar Atención';
        }
    }
}

// ===== BÚSQUEDA =====
async function editarRegistro(numero) {
    try {
        // Obtener datos del registro
        const response = await fetch(`/api/atenciones/${numero}`);
        const data = await response.json();

        if (!response.ok || !data.numero) {
            mostrarNotificacion(data.message || 'Error al cargar el registro', 'error');
            return;
        }

        // Llenar formulario con datos existentes
        document.getElementById('numero').value = data.numero;

        // Convertir fecha al formato YYYY-MM-DD para el input type="date"
        let fechaFormateada = data.fecha;
        if (data.fecha) {
            // Si viene en formato DD/MM/YYYY o con hora
            if (data.fecha.includes('/')) {
                const partes = data.fecha.split('/');
                if (partes.length === 3) {
                    fechaFormateada = `${partes[2].split(' ')[0]}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}`;
                }
            } else if (data.fecha.includes('T')) {
                // Si viene en formato ISO
                fechaFormateada = data.fecha.split('T')[0];
            } else if (data.fecha.includes(' ')) {
                // Si viene en formato YYYY-MM-DD HH:MM:SS
                fechaFormateada = data.fecha.split(' ')[0];
            } else if (data.fecha.match(/^\d{4}-\d{2}-\d{2}$/)) {
                // Ya está en formato correcto
                fechaFormateada = data.fecha;
            }
        }
        document.getElementById('fecha').value = fechaFormateada;

        // Seleccionar tipo de atención
        const tipoRadios = document.getElementsByName('tipo_atencion');
        tipoRadios.forEach(radio => {
            if (radio.value === data.tipo_atencion) {
                radio.checked = true;
                radio.closest('.tipo-option').classList.add('active');
            } else {
                radio.closest('.tipo-option').classList.remove('active');
            }
        });

        document.getElementById('nombre-animal').value = data.nombre_animal;
        document.getElementById('especie').value = data.especie;
        document.getElementById('sexo').value = data.sexo;
        document.getElementById('edad').value = data.edad || '';
        document.getElementById('nombre-apellido').value = data.tutor.nombre_apellido;
        document.getElementById('dni').value = data.tutor.dni;
        document.getElementById('direccion').value = data.tutor.direccion || '';
        document.getElementById('barrio').value = data.tutor.barrio || '';
        document.getElementById('telefono').value = data.tutor.telefono || '';
        document.getElementById('motivo').value = data.motivo || '';
        document.getElementById('diagnostico').value = data.diagnostico || '';
        document.getElementById('tratamiento').value = data.tratamiento || '';
        document.getElementById('derivacion').value = data.derivacion || '';
        document.getElementById('observaciones').value = data.observaciones || '';

        // Mostrar sección de atención primaria si corresponde
        if (data.tipo_atencion === 'atencion_primaria') {
            document.getElementById('section-atencion-primaria').style.display = 'block';
        } else {
            document.getElementById('section-atencion-primaria').style.display = 'none';
        }

        // Cambiar a sección de registro
        showSection('registro');

        // Cambiar título y apariencia para modo edición
        document.getElementById('section-title').textContent = `Edición de Registro #${numero}`;
        document.getElementById('section-subtitle').textContent = 'Modificar datos de la atención';
        
        // Cambiar texto del botón
        const submitBtn = document.querySelector('#form-atencion button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Guardar Cambios';
        }

        // Guardar número para edición
        window.editandoNumero = numero;

        mostrarNotificacion('Editando registro #' + numero, 'info');
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar el registro', 'error');
    }
}

async function eliminarRegistro(numero) {
    if (!confirm(`¿Está seguro de eliminar el registro #${numero}? Esta acción no se puede deshacer.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/atenciones/${numero}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (result.success) {
            mostrarNotificacion('Registro eliminado exitosamente', 'success');
            buscarAtenciones(); // Recargar resultados
            cargarDashboard(); // Actualizar dashboard
        } else {
            mostrarNotificacion(result.message || 'Error al eliminar', 'error');
        }
    } catch (error) {
        mostrarNotificacion('Error al eliminar el registro', 'error');
    }
}

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
                    <div>
                        <span class="result-tipo ${r.tipo_atencion === 'castracion' ? 'tipo-castracion' : 'tipo-atencion-primaria'}">
                            ${r.tipo_atencion === 'castracion' ? 'Castración' : 'Atención Primaria'}
                        </span>
                        <button class="btn-icon btn-edit" onclick="editarRegistro(${r.numero})" title="Editar" style="margin-left: 10px;">✎</button>
                        <button class="btn-icon btn-delete" onclick="eliminarRegistro(${r.numero})" title="Eliminar">🗑</button>
                    </div>
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

        // Actualizar totales en tarjetas
        actualizarTotalesEstadisticas(stats);

        renderizarGraficos(stats);
    } catch (error) {
        mostrarNotificacion('Error al cargar estadísticas', 'error');
    }
}

function actualizarTotalesEstadisticas(stats) {
    // Total de atenciones
    const totalAtenciones = stats.total || 0;
    document.getElementById('total-atenciones').textContent = totalAtenciones;

    // Castraciones y Atención Primaria
    const castraciones = stats.por_tipo ? (stats.por_tipo.find(t => t[0] === 'castracion')?.[1] || 0) : 0;
    const atencionPrimaria = stats.por_tipo ? (stats.por_tipo.find(t => t[0] === 'atencion_primaria')?.[1] || 0) : 0;
    document.getElementById('total-castraciones').textContent = castraciones;
    document.getElementById('total-atencion-primaria').textContent = atencionPrimaria;

    // Caninos y Felinos
    const caninos = stats.por_especie ? (stats.por_especie.find(e => e[0] === 'Canino')?.[1] || 0) : 0;
    const felinos = stats.por_especie ? (stats.por_especie.find(e => e[0] === 'Felino')?.[1] || 0) : 0;
    document.getElementById('total-caninos').textContent = caninos;
    document.getElementById('total-felinos').textContent = felinos;

    // Hembras y Machos
    const hembras = stats.por_sexo ? (stats.por_sexo.find(s => s[0] === 'Hembra')?.[1] || 0) : 0;
    const machos = stats.por_sexo ? (stats.por_sexo.find(s => s[0] === 'Macho')?.[1] || 0) : 0;
    document.getElementById('total-hembras').textContent = hembras;
    document.getElementById('total-machos').textContent = machos;
}

function renderizarGraficos(stats) {
    // Tipo de atención
    if (stats.por_tipo && stats.por_tipo.length > 0) {
        const total = stats.por_tipo.reduce((sum, t) => sum + t[1], 0);
        actualizarTextoMetrica('stats-tipo-texto', `Total de atenciones: ${total}`);
        renderChart('chart-tipo', 'doughnut', {
            labels: stats.por_tipo.map(t => t[0] === 'castracion' ? 'Castración' : 'Atención Primaria'),
            data: stats.por_tipo.map(t => t[1])
        }, 'Tipo de Atención');
    }

    // Especie
    if (stats.por_especie && stats.por_especie.length > 0) {
        const total = stats.por_especie.reduce((sum, e) => sum + e[1], 0);
        const top = stats.por_especie[0];
        actualizarTextoMetrica('stats-especie-texto', `Total: ${total} | Más frecuente: ${top[0]} (${top[1]})`);
        renderChart('chart-especie', 'pie', {
            labels: stats.por_especie.map(e => e[0]),
            data: stats.por_especie.map(e => e[1])
        }, 'Por Especie');
    }

    // Sexo
    if (stats.por_sexo && stats.por_sexo.length > 0) {
        const total = stats.por_sexo.reduce((sum, s) => sum + s[1], 0);
        actualizarTextoMetrica('stats-sexo-texto', `Total: ${total}`);
        renderChart('chart-sexo', 'doughnut', {
            labels: stats.por_sexo.map(s => s[0]),
            data: stats.por_sexo.map(s => s[1])
        }, 'Por Sexo');
    }

    // Temporal
    if (stats.por_mes && stats.por_mes.length > 0) {
        const total = stats.por_mes.reduce((sum, m) => sum + m[1], 0);
        const ultimos = stats.por_mes.length > 1 ? stats.por_mes[stats.por_mes.length - 1][1] : 0;
        actualizarTextoMetrica('stats-temporal-texto', `Total: ${total} | Último mes: ${ultimos}`);
        renderChart('chart-temporal', 'line', {
            labels: stats.por_mes.map(m => formatearMes(m[0])),
            data: stats.por_mes.map(m => m[1])
        }, 'Evolución Mensual');
    }

    // Barrios
    if (stats.por_barrio && stats.por_barrio.length > 0) {
        const top10 = stats.por_barrio.slice(0, 10);
        const total = stats.por_barrio.reduce((sum, b) => sum + b[1], 0);
        const topBarrio = top10[0];
        actualizarTextoMetrica('stats-barrio-texto', `Total: ${total} | Top: ${topBarrio[0]} (${topBarrio[1]})`);
        renderChart('chart-barrios', 'bar', {
            labels: top10.map(b => b[0]),
            data: top10.map(b => b[1])
        }, 'Top 10 Barrios');
    }
}

function actualizarTextoMetrica(elementId, texto) {
    const elem = document.getElementById(elementId);
    if (elem) {
        elem.textContent = texto;
    }
}

function renderChart(canvasId, type, data, title) {
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
                label: title || '',
                data: data.data,
                backgroundColor: [
                    '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6',
                    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 10,
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: title || '',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                }
            }
        }
    });
}

// ===== UTILIDADES =====
function formatearFecha(fecha) {
    if (!fecha) return 'No especificada';

    // Si es un string con formato ISO (2025-11-27) o fecha completa
    if (typeof fecha === 'string') {
        // Si viene en formato GMT (Thu, 27 Nov 2025 00:00:00 GMT)
        if (fecha.includes('GMT') || fecha.includes(',')) {
            const date = new Date(fecha);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        }

        // Extraer solo la parte de la fecha si viene con hora (2025-11-27T00:00:00)
        const soloFecha = fecha.split('T')[0].split(' ')[0];

        // Si tiene formato YYYY-MM-DD
        if (soloFecha.includes('-')) {
            const [year, month, day] = soloFecha.split('-');
            return `${day}/${month}/${year}`;
        }
    }

    // Si es un objeto Date
    if (fecha instanceof Date) {
        const day = String(fecha.getDate()).padStart(2, '0');
        const month = String(fecha.getMonth() + 1).padStart(2, '0');
        const year = fecha.getFullYear();
        return `${day}/${month}/${year}`;
    }

    return fecha.toString();
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

// ===== AUDITORÍA =====
async function cargarAuditoria() {
    try {
        const response = await fetch('/api/auditoria');
        const logs = await response.json();

        const container = document.getElementById('tabla-auditoria');

        if (!logs || logs.length === 0) {
            container.innerHTML = '<p class="info-text">No hay registros de auditoría.</p>';
            return;
        }

        let html = '<table class="audit-table"><thead><tr>';
        html += '<th>Fecha/Hora</th>';
        html += '<th>Operación</th>';
        html += '<th>Usuario</th>';
        html += '<th>Detalles</th>';
        html += '</tr></thead><tbody>';

        logs.forEach(log => {
            // Parsear fecha de forma robusta
            let fechaObj;
            if (log.fecha_hora.includes('T')) {
                // Formato ISO: 2025-11-30T10:15:30 o 2025-11-30T10:15:30.000000
                fechaObj = new Date(log.fecha_hora);
            } else if (log.fecha_hora.includes(' ')) {
                // Formato SQL: 2025-11-30 10:15:30
                fechaObj = new Date(log.fecha_hora.replace(' ', 'T'));
            } else {
                fechaObj = new Date(log.fecha_hora);
            }

            const fecha = fechaObj.toLocaleString('es-AR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });
            const tipo = log.tipo_operacion;
            const badgeClass = tipo === 'DELETE' ? 'delete' : 'update';
            const tipoTexto = tipo === 'DELETE' ? '🗑️ Eliminación' : '✏️ Edición';

            html += '<tr>';
            html += `<td>${fecha}</td>`;
            html += `<td><span class="audit-badge ${badgeClass}">${tipoTexto}</span></td>`;
            html += `<td>${log.usuario}</td>`;
            html += `<td><div style="max-width: 400px; overflow: hidden; text-overflow: ellipsis;">${log.descripcion || ''}<br>`;
            html += `<small style="color: #6b7280;">Anterior: ${log.datos_anteriores || 'N/A'}</small>`;
            if (log.datos_nuevos) {
                html += `<br><small style="color: #059669;">Nuevo: ${log.datos_nuevos}</small>`;
            }
            html += '</div></td>';
            html += '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        mostrarNotificacion('Error al cargar historial', 'error');
    }
}

// ===== FUNCIONES GLOBALES PARA HTML onclick =====
function cargarTodosTurnos() {
    cargarDashboard();
}

function mostrarFormularioTurno() {
    document.getElementById('modal-turno').classList.add('show');
}

function cerrarModalTurno() {
    document.getElementById('modal-turno').classList.remove('show');
    document.getElementById('form-turno').reset();
}

function logout() {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        window.location.href = '/logout';
    }
}

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
