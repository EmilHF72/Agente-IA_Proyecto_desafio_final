"""
utils/lector_pdf.py
-------------------
Helper para cargar documentos PDF usando PyPDFLoader de LangChain.
Devuelve una lista de Document objects.
"""

import logging
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def cargar_pdf(ruta_pdf: Path) -> List[Document]:
    """
    Carga un archivo PDF y devuelve sus páginas como lista de Documents.

    Args:
        ruta_pdf: Ruta absoluta o relativa al archivo PDF.

    Returns:
        Lista de Document con contenido y metadata de cada página.

    Raises:
        FileNotFoundError: Si el archivo PDF no existe.
        RuntimeError: Si ocurre un error durante la carga.
    """
    ruta_pdf = Path(ruta_pdf)

    if not ruta_pdf.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo PDF: {ruta_pdf.resolve()}"
        )

    logger.info(f"Cargando PDF: {ruta_pdf.name}")

    try:
        loader = PyPDFLoader(str(ruta_pdf))
        documentos = loader.load()
        logger.info(f"PDF cargado: {len(documentos)} páginas encontradas.")
        return documentos
    except Exception as exc:
        raise RuntimeError(
            f"Error al cargar el PDF '{ruta_pdf.name}': {exc}"
        ) from exc
