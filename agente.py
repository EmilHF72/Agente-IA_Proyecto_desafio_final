"""
agente.py
---------
Construcción del agente ElectroBot utilizando:
  - ChatGroq como LLM principal (con fallback automático)
  - create_react_agent de LangGraph (Modern LangChain)
"""

import logging
import os
from typing import Any

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq

from chat_memory import crear_memoria
from config import (
    GROQ_MAX_TOKENS,
    GROQ_MODEL_FALLBACK,
    GROQ_MODEL_PRIMARY,
    GROQ_TEMPERATURE,
)
from herramientas import HERRAMIENTAS
from prompts import obtener_prompt_agente

logger = logging.getLogger(__name__)


def _crear_llm(model_name: str) -> ChatGroq:
    """Instancia ChatGroq con el modelo especificado."""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY no está definida. "
            "Agrega tu API key en el archivo .env o en los secrets de Streamlit Cloud."
        )

    return ChatGroq(
        model=model_name,
        temperature=GROQ_TEMPERATURE,
        max_tokens=GROQ_MAX_TOKENS,
        api_key=api_key,
    )


def crear_llm_con_fallback() -> ChatGroq:
    """Intenta crear el LLM con el modelo primario; si falla, usa el de respaldo."""
    try:
        llm = _crear_llm(GROQ_MODEL_PRIMARY)
        logger.info(f"LLM inicializado: {GROQ_MODEL_PRIMARY}")
        return llm
    except Exception as exc:
        logger.warning(
            f"No se pudo inicializar {GROQ_MODEL_PRIMARY}: {exc}. "
            f"Usando fallback: {GROQ_MODEL_FALLBACK}"
        )
        llm = _crear_llm(GROQ_MODEL_FALLBACK)
        logger.info(f"LLM inicializado (fallback): {GROQ_MODEL_FALLBACK}")
        return llm


def construir_agente(checkpointer: MemorySaver) -> Any:
    """
    Construye el agente LangGraph completo de ElectroBot.

    Args:
        checkpointer: Instancia de MemorySaver para la memoria.

    Returns:
        Grafo compilado de LangGraph listo para invocar.
    """
    llm = crear_llm_con_fallback()
    prompt = obtener_prompt_agente()

    agente = create_react_agent(
        model=llm,
        tools=HERRAMIENTAS,
        prompt=prompt,
        checkpointer=checkpointer,
    )

    logger.info("Agente LangGraph construido correctamente.")
    return agente


def invocar_agente(agente: Any, pregunta: str) -> str:
    """
    Invoca el agente con la pregunta del usuario.

    Args:
        agente: Grafo compilado de LangGraph.
        pregunta: Pregunta del usuario en texto libre.

    Returns:
        Respuesta del agente como string.
    """
    # En un entorno real se podría generar dinámicamente un ID de sesión.
    # Como st.session_state maneja sesiones únicas en Streamlit,
    # el hilo puede ser estático por cliente.
    config = {"configurable": {"thread_id": "sesion_streamit_1"}}
    
    try:
        resultado = agente.invoke({"messages": [("human", pregunta)]}, config)
        return resultado["messages"][-1].content
    except Exception as exc:
        logger.error(f"Error al invocar el agente: {exc}")
        return (
            "Lo siento, ocurrió un error al procesar tu consulta. "
            "Por favor intenta nuevamente."
        )
