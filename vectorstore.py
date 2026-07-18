"""
vectorstore.py
--------------
Construcción, persistencia y carga de índices FAISS.
Los índices se persisten en disco para evitar re-indexar en cada reinicio.
Se expone también la función de retriever lista para usar en las herramientas.
"""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings

from config import (
    EMBEDDING_MODEL,
    RETRIEVER_K,
    VECTORSTORE_POLITICAS_PATH,
    VECTORSTORE_RIC10_PATH,
)
from documentos import cargar_y_fragmentar_politicas, cargar_y_fragmentar_ric10

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Singleton de embeddings (se inicializa una sola vez)
# ---------------------------------------------------------------------------
_embeddings: Optional[HuggingFaceEmbeddings] = None


def obtener_embeddings() -> HuggingFaceEmbeddings:
    """Devuelve la instancia compartida de HuggingFaceEmbeddings."""
    global _embeddings
    if _embeddings is None:
        logger.info(f"Cargando modelo de embeddings: {EMBEDDING_MODEL}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embeddings inicializados correctamente.")
    return _embeddings


# ---------------------------------------------------------------------------
# Funciones de construcción / carga de vectorstores
# ---------------------------------------------------------------------------

def _construir_o_cargar(
    ruta: Path,
    fn_fragmentos,
    nombre: str,
) -> FAISS:
    """
    Carga un vectorstore FAISS desde disco si existe,
    o lo construye desde cero y lo persiste.

    Nota: En Windows, FAISS tiene problemas con rutas que contienen espacios
    o caracteres especiales. Por eso usamos un directorio temporal para las
    operaciones de guardar y cargar, y luego copiamos los archivos.

    Args:
        ruta: Directorio donde se guarda/carga el índice FAISS.
        fn_fragmentos: Función que devuelve los fragmentos de texto.
        nombre: Nombre descriptivo para logging.

    Returns:
        Instancia de FAISS cargada o construida.
    """
    embeddings = obtener_embeddings()
    ruta = Path(ruta).resolve()  # Convertir a ruta absoluta
    ruta.mkdir(parents=True, exist_ok=True)

    # Verificar si el índice FAISS ya existe
    index_file = ruta / "index.faiss"
    if index_file.exists():
        logger.info(f"Cargando vectorstore '{nombre}' desde disco...")
        
        # Workaround para FAISS en Windows: copiar a temporal, cargar, y descartar
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Copiar archivos de ruta final a temporal
            logger.info(f"  Copiando archivos a temporal para lectura...")
            for file in ruta.iterdir():
                if file.name != "test_write.tmp":  # Saltar archivo de prueba
                    shutil.copy2(str(file), str(tmppath / file.name))
            
            # Cargar desde temporal (donde FAISS funciona correctamente)
            vs = FAISS.load_local(
                str(tmppath),
                embeddings,
                allow_dangerous_deserialization=True,
            )
        
        logger.info(f"Vectorstore '{nombre}' cargado correctamente.")
    else:
        logger.info(f"Construyendo vectorstore '{nombre}' desde documentos...")
        fragmentos = fn_fragmentos()
        if not fragmentos:
            raise ValueError(f"No se obtuvieron fragmentos para '{nombre}'.")
        vs = FAISS.from_documents(fragmentos, embeddings)
        logger.info(f"Guardando vectorstore en: {ruta}")
        
        # Workaround para FAISS en Windows: usar directorio temporal
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            logger.info(f"  Guardando temporalmente...")
            vs.save_local(str(tmppath))
            
            # Copiar archivos de temporal a destino final
            logger.info(f"  Copiando archivos a destino final...")
            for file in tmppath.iterdir():
                shutil.copy2(str(file), str(ruta / file.name))
        
        logger.info(f"Vectorstore '{nombre}' guardado en: {ruta}")

    return vs


# ---------------------------------------------------------------------------
# Singletons de vectorstores
# ---------------------------------------------------------------------------
_vs_ric10: Optional[FAISS] = None
_vs_politicas: Optional[FAISS] = None


def obtener_vectorstore_ric10() -> FAISS:
    """Devuelve el vectorstore de RIC N°10 (construye si es necesario)."""
    global _vs_ric10
    if _vs_ric10 is None:
        _vs_ric10 = _construir_o_cargar(
            VECTORSTORE_RIC10_PATH,
            cargar_y_fragmentar_ric10,
            "RIC10",
        )
    return _vs_ric10


def obtener_vectorstore_politicas() -> FAISS:
    """Devuelve el vectorstore de Políticas Internas (construye si es necesario)."""
    global _vs_politicas
    if _vs_politicas is None:
        _vs_politicas = _construir_o_cargar(
            VECTORSTORE_POLITICAS_PATH,
            cargar_y_fragmentar_politicas,
            "Políticas",
        )
    return _vs_politicas


# ---------------------------------------------------------------------------
# Retrievers listos para usar
# ---------------------------------------------------------------------------

def obtener_retriever_ric10() -> VectorStoreRetriever:
    """Devuelve el retriever semántico de RIC N°10."""
    return obtener_vectorstore_ric10().as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_K},
    )


def obtener_retriever_politicas() -> VectorStoreRetriever:
    """Devuelve el retriever semántico de Políticas Internas."""
    return obtener_vectorstore_politicas().as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_K},
    )
