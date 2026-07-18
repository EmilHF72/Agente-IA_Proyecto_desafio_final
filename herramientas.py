"""
herramientas.py
---------------
Definición de las tres herramientas LangChain de ElectroBot:

  1. consulta_RIC10      — Búsqueda semántica en la norma RIC N°10 (pública).
  2. consulta_politicas  — Búsqueda semántica en Políticas Internas (privada).
  3. validar_empleado    — Validación de credenciales de empleado.

Todas son @tool decoradas para ser compatibles con AgentExecutor.
"""

import logging
from typing import Optional

from langchain_core.tools import tool

from autenticacion import validar_credenciales
from config import MSG_ACCESO_DENEGADO, MSG_NO_INFO, MSG_NO_INFO_TECNICA
from vectorstore import obtener_retriever_politicas, obtener_retriever_ric10

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Estado de sesión compartido
# Estado mínimo para que las herramientas sepan si hay un empleado autenticado.
# En la UI de Streamlit se sincroniza con st.session_state.
# ---------------------------------------------------------------------------
_empleado_autenticado: Optional[object] = None


def set_empleado_autenticado(empleado) -> None:
    """Establece el empleado actualmente autenticado (llamado desde app.py)."""
    global _empleado_autenticado
    _empleado_autenticado = empleado


def get_empleado_autenticado() -> Optional[object]:
    """Devuelve el empleado autenticado actual, o None si no hay sesión."""
    return _empleado_autenticado


def limpiar_sesion() -> None:
    """Cierra la sesión del empleado autenticado."""
    global _empleado_autenticado
    _empleado_autenticado = None


# ---------------------------------------------------------------------------
# Herramienta 1: consulta_RIC10
# ---------------------------------------------------------------------------

@tool
def consulta_RIC10(query: str) -> str:
    """
    Busca información técnica en la Norma Técnica Chilena RIC N°10
    sobre instalaciones eléctricas domiciliarias.

    Usa esta herramienta para responder cualquier pregunta relacionada con:
    - Calibre de conductores
    - Tipos de interruptores y protecciones
    - Puesta a tierra
    - Tomacorrientes y puntos de luz
    - Cargas máximas permitidas
    - Certificaciones eléctricas

    Args:
        query: Pregunta técnica del usuario.

    Returns:
        Fragmento(s) relevante(s) de la norma RIC N°10,
        o un mensaje indicando que no se encontró información.
    """
    logger.info(f"[consulta_RIC10] Query: {query!r}")

    try:
        retriever = obtener_retriever_ric10()
        documentos = retriever.invoke(query)

        if not documentos:
            return MSG_NO_INFO_TECNICA

        # Concatenar los fragmentos recuperados
        contexto = "\n\n---\n\n".join(
            f"[Página {doc.metadata.get('page', '?')}]\n{doc.page_content}"
            for doc in documentos
        )
        return contexto

    except Exception as exc:
        logger.error(f"Error en consulta_RIC10: {exc}")
        return f"Error al consultar la documentación técnica: {exc}"


# ---------------------------------------------------------------------------
# Herramienta 2: consulta_politicas
# ---------------------------------------------------------------------------

@tool
def consulta_politicas(query: str) -> str:
    """
    Busca información en las Políticas Internas de ElectroHogar Chile SpA.

    IMPORTANTE: Esta herramienta solo debe usarse si el empleado está
    autenticado. Si no hay sesión activa, retorna un mensaje de acceso denegado.

    Usa esta herramienta para preguntas sobre:
    - Días de vacaciones y permisos
    - Horarios laborales
    - Política de licencias médicas
    - Solicitud de herramientas y materiales
    - Procedimientos internos y reglamentos

    Args:
        query: Pregunta administrativa del empleado.

    Returns:
        Fragmento(s) relevante(s) de las políticas internas,
        o un mensaje de acceso denegado si no hay autenticación.
    """
    logger.info(f"[consulta_politicas] Query: {query!r}")

    # Verificar autenticación
    if _empleado_autenticado is None:
        logger.warning("Intento de acceso a políticas sin autenticación.")
        return (
            "Para acceder a las políticas internas de ElectroHogar, "
            "debes autenticarte primero con tu nombre y clave."
        )

    try:
        retriever = obtener_retriever_politicas()
        documentos = retriever.invoke(query)

        if not documentos:
            return MSG_NO_INFO

        contexto = "\n\n---\n\n".join(
            f"[Página {doc.metadata.get('page', '?')}]\n{doc.page_content}"
            for doc in documentos
        )
        return contexto

    except Exception as exc:
        logger.error(f"Error en consulta_politicas: {exc}")
        return f"Error al consultar las políticas internas: {exc}"


# ---------------------------------------------------------------------------
# Herramienta 3: validar_empleado
# ---------------------------------------------------------------------------

@tool
def validar_empleado(nombre: str, clave: str) -> str:
    """
    Valida las credenciales de un empleado de ElectroHogar Chile SpA.

    Usa esta herramienta cuando el usuario proporcione su nombre y clave
    para autenticarse y acceder a información administrativa.

    Args:
        nombre: Nombre completo del empleado (ej: "Carlos Muñoz").
        clave: Clave secreta de 4 dígitos (ej: "1234").

    Returns:
        Mensaje de bienvenida si las credenciales son correctas,
        o mensaje de acceso denegado si son incorrectas.
    """
    logger.info(f"[validar_empleado] Intento de autenticación para: {nombre!r}")

    empleado = validar_credenciales(nombre, clave)

    if empleado:
        set_empleado_autenticado(empleado)
        return (
            f"Autenticación exitosa. Bienvenido/a, {empleado.nombre} "
            f"({empleado.cargo}). Ya puedes realizar consultas sobre "
            f"las políticas internas de la empresa."
        )

    return MSG_ACCESO_DENEGADO


# ---------------------------------------------------------------------------
# Lista de herramientas para AgentExecutor
# ---------------------------------------------------------------------------
HERRAMIENTAS = [consulta_RIC10, consulta_politicas, validar_empleado]
