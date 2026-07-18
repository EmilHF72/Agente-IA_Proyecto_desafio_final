"""
chat_memory.py
--------------
Fábrica de memoria conversacional para el agente ElectroBot.
Utiliza ConversationBufferMemory de LangChain para mantener
el contexto entre turnos de conversación.
"""

import logging

from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)


def crear_memoria() -> MemorySaver:
    """
    Crea una nueva instancia de MemorySaver (LangGraph Checkpointer).
    """
    logger.debug("Creando nueva instancia de MemorySaver.")
    return MemorySaver()


def limpiar_memoria(memoria: MemorySaver) -> None:
    """
    Nota: MemorySaver es persistente por defecto. 
    Para limpiar el historial, es mejor crear una nueva instancia.
    """
    logger.debug("limpiar_memoria llamado (no-op en LangGraph, la app debe reasignar).")
    pass
