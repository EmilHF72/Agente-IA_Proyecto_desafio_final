"""
app.py
------
Interfaz de usuario de ElectroBot — ElectroHogar Chile SpA.
Implementada con Streamlit con diseño moderno y responsivo.

Características:
  - Modo público: consultas técnicas RIC N°10 sin autenticación.
  - Modo privado: consultas administrativas con login de empleado.
  - Historial de conversación persistente por sesión.
  - Indicadores visuales de estado de sesión.
"""

import logging
import os

import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuración inicial de entorno y logging
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Importaciones del proyecto (después de load_dotenv para que GROQ_API_KEY
# esté disponible cuando se instancien los módulos)
# ---------------------------------------------------------------------------
from agente import construir_agente, invocar_agente
from autenticacion import autenticar
from chat_memory import crear_memoria, limpiar_memoria
from config import EMPRESA_DESCRIPCION, EMPRESA_NOMBRE, MSG_AUTH_REQUERIDA
from herramientas import limpiar_sesion, set_empleado_autenticado
from utils.clasificador import TipoPregunta, clasificar_pregunta
from vectorstore import obtener_vectorstore_politicas, obtener_vectorstore_ric10

# ---------------------------------------------------------------------------
# Configuración de la página Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ElectroBot — ElectroHogar Chile SpA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "ElectroBot v1.0 — Asistente inteligente RAG para ElectroHogar Chile SpA.",
    },
)

# ---------------------------------------------------------------------------
# CSS personalizado — Diseño moderno dark mode
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- Importar fuente ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---- Reset base ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---- Fondo principal ---- */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 50%, #0a1020 100%);
    color: #e2e8f0;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(99, 179, 237, 0.15);
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ---- Título principal ---- */
.electrobot-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}

.electrobot-logo {
    font-size: 4rem;
    line-height: 1;
    filter: drop-shadow(0 0 20px rgba(99, 179, 237, 0.6));
    animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 20px rgba(99, 179, 237, 0.6)); }
    50% { filter: drop-shadow(0 0 35px rgba(99, 179, 237, 0.9)); }
}

.electrobot-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #9f7aea, #63b3ed);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 4s ease infinite;
    margin: 0;
}

@keyframes gradient-shift {
    0% { background-position: 0% center; }
    50% { background-position: 100% center; }
    100% { background-position: 0% center; }
}

.electrobot-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-top: 0.3rem;
    font-weight: 400;
}

/* ---- Tarjetas de chat ---- */
.chat-message-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.75rem 0;
}

.chat-message-bot {
    display: flex;
    justify-content: flex-start;
    margin: 0.75rem 0;
}

.chat-bubble-user {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 0.85rem 1.2rem;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

.chat-bubble-bot {
    background: linear-gradient(135deg, #1e293b, #1a2744);
    color: #e2e8f0;
    border-radius: 18px 18px 18px 4px;
    padding: 0.85rem 1.2rem;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.6;
    border: 1px solid rgba(99, 179, 237, 0.2);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.chat-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}

.avatar-user {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    margin-left: 0.6rem;
}

.avatar-bot {
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    margin-right: 0.6rem;
    box-shadow: 0 0 12px rgba(99, 179, 237, 0.4);
}

/* ---- Área de input ---- */
.stTextInput > div > div > input {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid rgba(99, 179, 237, 0.3) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(99, 179, 237, 0.7) !important;
    box-shadow: 0 0 0 2px rgba(99, 179, 237, 0.15) !important;
}

/* ---- Botones ---- */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ---- Badge de sesión ---- */
.session-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.session-badge-public {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.4);
    color: #93c5fd;
}

.session-badge-auth {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #6ee7b7;
}

/* ---- Separador ---- */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99, 179, 237, 0.3), transparent);
    margin: 1.5rem 0;
}

/* ---- Tarjeta de info ---- */
.info-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(99, 179, 237, 0.15);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}

/* ---- Métricas en sidebar ---- */
.metric-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(99, 179, 237, 0.1);
    font-size: 0.85rem;
}

.metric-label { color: #94a3b8; }
.metric-value { color: #63b3ed; font-weight: 600; }

/* ---- Spinner ---- */
.stSpinner > div {
    border-top-color: #63b3ed !important;
}

/* ---- Ocultar elementos de Streamlit por defecto ---- */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* ---- Área de chat contenedor ---- */
.chat-container {
    background: rgba(10, 20, 40, 0.4);
    border: 1px solid rgba(99, 179, 237, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    min-height: 400px;
    max-height: 550px;
    overflow-y: auto;
}

/* ---- Form de login ---- */
.login-container {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(124, 58, 237, 0.1));
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.login-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #93c5fd;
    margin-bottom: 0.5rem;
}

/* ---- Alertas personalizadas ---- */
.alert-warning {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    color: #fcd34d;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Inicialización del estado de sesión
# ---------------------------------------------------------------------------
def inicializar_sesion():
    """Inicializa las variables de st.session_state si no existen."""
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []  # Lista de {"role": "user"|"bot", "content": str}

    if "empleado" not in st.session_state:
        st.session_state.empleado = None  # None = no autenticado

    if "memoria" not in st.session_state:
        st.session_state.memoria = crear_memoria()

    if "agente" not in st.session_state:
        st.session_state.agente = None

    if "vectorstores_cargados" not in st.session_state:
        st.session_state.vectorstores_cargados = False


# ---------------------------------------------------------------------------
# Carga de vectorstores (cacheada con st.cache_resource)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="⚡ Inicializando base de conocimiento...")
def cargar_vectorstores():
    """Carga ambos vectorstores una sola vez por sesión de Streamlit."""
    logger.info("Iniciando carga de vectorstores...")
    import os
    logger.info(f"Working directory: {os.getcwd()}")
    vs_ric10 = obtener_vectorstore_ric10()
    vs_politicas = obtener_vectorstore_politicas()
    logger.info("Vectorstores cargados y listos.")
    return vs_ric10, vs_politicas


# ---------------------------------------------------------------------------
# Funciones auxiliares de UI
# ---------------------------------------------------------------------------
def renderizar_mensaje(role: str, content: str):
    """Renderiza un mensaje de chat con burbujas estilizadas."""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message-user">
            <div class="chat-bubble-user">{content}</div>
            <div class="chat-avatar avatar-user">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message-bot">
            <div class="chat-avatar avatar-bot">⚡</div>
            <div class="chat-bubble-bot">{content}</div>
        </div>
        """, unsafe_allow_html=True)


def renderizar_sidebar():
    """Renderiza el sidebar con información del sistema y del usuario."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <div style="font-size:2.5rem;">⚡</div>
            <div style="font-weight:700; font-size:1.2rem; color:#63b3ed;">ElectroBot</div>
            <div style="font-size:0.75rem; color:#94a3b8;">v1.0</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Estado de sesión
        if st.session_state.empleado:
            st.markdown(
                '<span class="session-badge session-badge-auth">🟢 Sesión Activa</span>',
                unsafe_allow_html=True,
            )
            emp = st.session_state.empleado
            st.markdown(f"""
            <div class="info-card">
                <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.5rem;">EMPLEADO AUTENTICADO</div>
                <div class="metric-item">
                    <span class="metric-label">Nombre</span>
                    <span class="metric-value">{emp.nombre}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Cargo</span>
                    <span class="metric-value">{emp.cargo}</span>
                </div>
                <div class="metric-item" style="border:none;">
                    <span class="metric-label">Nivel de Acceso</span>
                    <span class="metric-value" style="color:#6ee7b7;">Completo ✓</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Cerrar Sesión", key="btn_logout", use_container_width=True):
                _cerrar_sesion()
                st.rerun()
        else:
            st.markdown(
                '<span class="session-badge session-badge-public">🔵 Modo Público</span>',
                unsafe_allow_html=True,
            )
            st.markdown("""
            <div class="info-card">
                <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.5rem;">ACCESO ACTUAL</div>
                <div style="font-size:0.85rem; color:#93c5fd;">
                    📖 Norma Técnica RIC N°10<br>
                    <span style="color:#94a3b8; font-size:0.8rem;">Consultas técnicas libres</span>
                </div>
                <div style="margin-top:0.5rem; font-size:0.85rem; color:#64748b;">
                    🔒 Políticas Internas<br>
                    <span style="color:#64748b; font-size:0.8rem;">Requiere autenticación</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Estadísticas de conversación
        total_msgs = len(st.session_state.mensajes)
        st.markdown(f"""
        <div class="info-card">
            <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.5rem;">SESIÓN ACTUAL</div>
            <div class="metric-item">
                <span class="metric-label">Mensajes</span>
                <span class="metric-value">{total_msgs}</span>
            </div>
            <div class="metric-item" style="border:none;">
                <span class="metric-label">Intercambios</span>
                <span class="metric-value">{total_msgs // 2}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Fuentes disponibles
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.5rem;">📚 FUENTES DE CONOCIMIENTO</div>
        <div style="font-size:0.8rem; color:#64748b; line-height:1.8;">
            🔓 RIC N°10 — Norma Técnica<br>
            🔐 Políticas Internas ElectroHogar<br>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if st.button("🗑️ Limpiar Historial", key="btn_clear", use_container_width=True):
            st.session_state.mensajes = []
            st.session_state.memoria = crear_memoria()
            st.session_state.agente = construir_agente(st.session_state.memoria)
            st.rerun()

        # Créditos
        st.markdown("""
        <div style="text-align:center; margin-top:2rem; font-size:0.7rem; color:#475569;">
            Powered by LangChain · Groq · FAISS<br>
            ElectroHogar Chile SpA © 2025
        </div>
        """, unsafe_allow_html=True)


def renderizar_header():
    """Renderiza el encabezado principal de la aplicación."""
    st.markdown("""
    <div class="electrobot-header">
        <div class="electrobot-logo">⚡</div>
        <h1 class="electrobot-title">ElectroBot</h1>
        <p class="electrobot-subtitle">Asistente Inteligente · ElectroHogar Chile SpA</p>
    </div>
    """, unsafe_allow_html=True)


def renderizar_login_form():
    """Renderiza el formulario de autenticación."""
    st.markdown("""
    <div class="login-container">
        <div class="login-title">🔐 Acceso para Empleados</div>
        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
            Ingresa tus credenciales para acceder a información interna de la empresa.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form(key="form_login", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            nombre_input = st.text_input(
                "👤 Nombre",
                placeholder="Ej: Carlos Muñoz",
                key="login_nombre",
            )
        with col2:
            clave_input = st.text_input(
                "🔑 Clave",
                type="password",
                placeholder="4 dígitos",
                max_chars=4,
                key="login_clave",
            )

        col_btn1, col_btn2 = st.columns([1, 2])
        with col_btn1:
            submitted = st.form_submit_button(
                "Iniciar Sesión",
                use_container_width=True,
            )

    if submitted:
        if not nombre_input or not clave_input:
            st.error("⚠️ Debes ingresar nombre y clave.")
        else:
            exito, mensaje, empleado = autenticar(nombre_input, clave_input)
            if exito:
                st.session_state.empleado = empleado
                set_empleado_autenticado(empleado)
                # Reconstruir agente con la nueva sesión
                st.session_state.agente = construir_agente(st.session_state.memoria)
                st.success(f"✅ {mensaje}")
                st.rerun()
            else:
                st.error(f"❌ {mensaje}")

    return False


def _cerrar_sesion():
    """Cierra la sesión del empleado y limpia el estado."""
    st.session_state.empleado = None
    limpiar_sesion()  # Limpia el singleton en herramientas.py
    st.session_state.mensajes = []
    st.session_state.memoria = crear_memoria()
    st.session_state.agente = None


def procesar_pregunta(pregunta: str):
    """
    Procesa la pregunta del usuario:
    1. Clasifica la intención.
    2. Si es administrativa y no hay sesión, muestra formulario de login.
    3. Si es técnica o hay sesión, invoca el agente.
    """
    tipo = clasificar_pregunta(pregunta)

    # Agregar mensaje del usuario al historial
    st.session_state.mensajes.append({"role": "user", "content": pregunta})

    # Si es administrativa y no hay sesión activa
    if tipo == TipoPregunta.ADMINISTRATIVA and not st.session_state.empleado:
        respuesta = (
            "🔐 **Esta consulta requiere acceso de empleado.**\n\n"
            "La información sobre políticas internas, horarios, vacaciones y "
            "procedimientos de empresa es de uso exclusivo para empleados autenticados.\n\n"
            "Por favor, **inicia sesión** con tu nombre y clave en el panel inferior."
        )
        st.session_state.mensajes.append({"role": "bot", "content": respuesta})
        st.session_state["mostrar_login"] = True
        return

    # Invocar el agente
    if st.session_state.agente is None:
        st.session_state.agente = construir_agente(st.session_state.memoria)

    with st.spinner("⚡ ElectroBot está procesando tu consulta..."):
        respuesta = invocar_agente(st.session_state.agente, pregunta)

    st.session_state.mensajes.append({"role": "bot", "content": respuesta})
    st.session_state["mostrar_login"] = False


# ---------------------------------------------------------------------------
# Aplicación principal
# ---------------------------------------------------------------------------
def main():
    inicializar_sesion()

    # Sincronizar estado de herramientas.py con st.session_state
    if st.session_state.empleado:
        set_empleado_autenticado(st.session_state.empleado)

    # Construir agente si no existe
    if st.session_state.agente is None:
        st.session_state.agente = construir_agente(st.session_state.memoria)

    # Cargar vectorstores (cacheado)
    try:
        cargar_vectorstores()
    except Exception as e:
        st.error(f"❌ Error al inicializar la base de conocimiento: {e}")
        st.stop()

    # Renderizar sidebar
    renderizar_sidebar()

    # Renderizar header
    renderizar_header()

    # Divisor
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Descripción de la empresa
    col_desc1, col_desc2, col_desc3 = st.columns([1, 4, 1])
    with col_desc2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:1.5rem;">
            <span style="font-size:0.9rem; color:#94a3b8;">
                {EMPRESA_DESCRIPCION}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Área principal de chat
    col_main1, col_main2, col_main3 = st.columns([1, 6, 1])
    with col_main2:

        # Historial de conversación
        if st.session_state.mensajes:
            with st.container():
                for mensaje in st.session_state.mensajes:
                    renderizar_mensaje(mensaje["role"], mensaje["content"])
        else:
            # Mensaje de bienvenida
            st.markdown("""
            <div style="text-align:center; padding:3rem 1rem; color:#64748b;">
                <div style="font-size:3rem; margin-bottom:1rem; opacity:0.5;">⚡</div>
                <div style="font-size:1.1rem; font-weight:500; color:#94a3b8; margin-bottom:0.5rem;">
                    ¡Hola! Soy ElectroBot.
                </div>
                <div style="font-size:0.9rem; line-height:1.7;">
                    Puedo ayudarte con consultas sobre la <strong style="color:#63b3ed;">Norma RIC N°10</strong>
                    o sobre las <strong style="color:#a78bfa;">políticas internas</strong> de ElectroHogar (requiere autenticación).
                </div>
                <div style="margin-top:1.5rem; font-size:0.85rem; color:#475569;">
                    💡 Ejemplos: ¿Qué calibre de cable usar para 20A? · ¿Cuántos días de vacaciones tengo?
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Formulario de pregunta
        with st.form(key="form_pregunta", clear_on_submit=True):
            pregunta_col, btn_col = st.columns([5, 1])
            with pregunta_col:
                pregunta = st.text_input(
                    label="Escribe tu pregunta",
                    placeholder="¿Qué calibre de conductor usar para un circuito de 20A? · ¿Cuántos días de vacaciones tengo?",
                    label_visibility="collapsed",
                    key="input_pregunta",
                )
            with btn_col:
                enviar = st.form_submit_button("Enviar ➤", use_container_width=True)

        if enviar and pregunta.strip():
            procesar_pregunta(pregunta.strip())
            st.rerun()

        # Mostrar formulario de login si se requiere autenticación
        if st.session_state.get("mostrar_login", False) and not st.session_state.empleado:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            renderizar_login_form()

        # Preguntas de ejemplo
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.75rem; color:#64748b; text-align:center; margin-bottom:0.5rem;">
            💡 PREGUNTAS DE EJEMPLO
        </div>
        """, unsafe_allow_html=True)

        ejemplo_col1, ejemplo_col2, ejemplo_col3 = st.columns(3)

        ejemplos_tecnicos = [
            "¿Qué calibre de conductor para 20A?",
            "¿Qué es la puesta a tierra según RIC N°10?",
            "¿Cuándo usar interruptor diferencial?",
        ]
        ejemplos_admin = [
            "¿Cuántos días de vacaciones hay?",
            "¿Cuál es la política de licencias médicas?",
            "¿Cómo solicitar herramientas?",
        ]

        with ejemplo_col1:
            st.markdown(
                '<div style="font-size:0.75rem; color:#63b3ed; text-align:center;">🔓 Técnicas (Públicas)</div>',
                unsafe_allow_html=True,
            )
            for ej in ejemplos_tecnicos:
                if st.button(ej, key=f"ej_{ej[:15]}", use_container_width=True):
                    procesar_pregunta(ej)
                    st.rerun()

        with ejemplo_col2:
            st.markdown(
                '<div style="font-size:0.75rem; color:#a78bfa; text-align:center;">🔐 Administrativas</div>',
                unsafe_allow_html=True,
            )
            for ej in ejemplos_admin:
                if st.button(ej, key=f"ej_{ej[:15]}", use_container_width=True):
                    procesar_pregunta(ej)
                    st.rerun()

        with ejemplo_col3:
            st.markdown(
                '<div style="font-size:0.75rem; color:#34d399; text-align:center;">ℹ️ Cuentas de demo</div>',
                unsafe_allow_html=True,
            )
            st.markdown("""
            <div class="info-card" style="font-size:0.8rem;">
                <div style="color:#94a3b8; margin-bottom:0.3rem;">Empleados de prueba:</div>
                <div style="color:#6ee7b7;">Carlos Muñoz → 1234</div>
                <div style="color:#6ee7b7;">Ana Rojas → 5678</div>
                <div style="color:#6ee7b7;">Luis Herrera → 2468</div>
                <div style="color:#6ee7b7;">Pedro Soto → 4321</div>
                <div style="color:#6ee7b7;">María González → 8765</div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
