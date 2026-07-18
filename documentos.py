"""
documentos.py
-------------
Carga y fragmentación de documentos PDF para el sistema RAG.
Utiliza PyPDFLoader y RecursiveCharacterTextSplitter de LangChain.
"""

import logging
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    PDF_POLITICAS,
    PDF_RIC10,
)
from utils.lector_pdf import cargar_pdf

logger = logging.getLogger(__name__)


def _obtener_splitter() -> RecursiveCharacterTextSplitter:
    """Instancia el splitter con la configuración central."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )


def cargar_y_fragmentar_ric10() -> List[Document]:
    """
    Carga el PDF RIC N°10 y lo divide en fragmentos.

    Returns:
        Lista de Document fragments para indexación.
    """
    logger.info("Procesando RIC10.pdf...")
    paginas = cargar_pdf(PDF_RIC10)
    splitter = _obtener_splitter()
    fragmentos = splitter.split_documents(paginas)
    logger.info(f"RIC10: {len(fragmentos)} fragmentos generados.")
    return fragmentos


def cargar_y_fragmentar_politicas() -> List[Document]:
    """
    Carga el PDF de Políticas Internas y lo divide en fragmentos.

    Returns:
        Lista de Document fragments para indexación.
    """
    logger.info("Procesando Politicas_Internas_ElectroHogar.pdf...")
    paginas = cargar_pdf(PDF_POLITICAS)
    splitter = _obtener_splitter()
    fragmentos = splitter.split_documents(paginas)
    logger.info(f"Políticas: {len(fragmentos)} fragmentos generados.")
    return fragmentos
