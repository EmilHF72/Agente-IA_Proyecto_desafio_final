"""
config.py
---------
Configuración centralizada de ElectroBot.
Todas las rutas, nombres de modelo y parámetros ajustables se definen aquí.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas base del proyecto
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DOCUMENTOS_DIR = BASE_DIR / "documentos"
DATOS_DIR = BASE_DIR / "datos"
VECTORSTORE_DIR = (BASE_DIR / "vectorstore_cache").resolve()

# ---------------------------------------------------------------------------
# Rutas de documentos
# ---------------------------------------------------------------------------
PDF_RIC10 = DOCUMENTOS_DIR / "RIC10.pdf"
PDF_POLITICAS = DOCUMENTOS_DIR / "Politicas_Internas_ElectroHogar.pdf"
CSV_EMPLEADOS = DATOS_DIR / "empleados.csv"

# ---------------------------------------------------------------------------
# Rutas de caché de vectorstores (ABSOLUTAS)
# ---------------------------------------------------------------------------
VECTORSTORE_RIC10_PATH = (VECTORSTORE_DIR / "ric10").resolve()
VECTORSTORE_POLITICAS_PATH = (VECTORSTORE_DIR / "politicas").resolve()

# ---------------------------------------------------------------------------
# Modelos de lenguaje (LLM via Groq)
# ---------------------------------------------------------------------------
GROQ_MODEL_PRIMARY = "llama-3.3-70b-versatile"
GROQ_MODEL_FALLBACK = "deepseek-r1-distill-llama-70b"
GROQ_TEMPERATURE = 0.0       # Determinismo máximo para respuestas factuales
GROQ_MAX_TOKENS = 1024

# ---------------------------------------------------------------------------
# Embeddings (HuggingFace local, sin API key)
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ---------------------------------------------------------------------------
# Chunking de documentos
# ---------------------------------------------------------------------------
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
RETRIEVER_K = 5              # Número de fragmentos recuperados por consulta

# ---------------------------------------------------------------------------
# Información de la empresa
# ---------------------------------------------------------------------------
EMPRESA_NOMBRE = "ElectroHogar Chile SpA"
EMPRESA_DESCRIPCION = (
    "Empresa dedicada a mantención eléctrica domiciliaria, instalaciones, "
    "reparaciones eléctricas, certificaciones SEC y asesoría técnica basada "
    "en la Norma Técnica Chilena RIC N°10."
)

# ---------------------------------------------------------------------------
# Mensajes de respuesta estándar
# ---------------------------------------------------------------------------
MSG_NO_INFO = "No encontré esa información en la documentación disponible."
MSG_NO_INFO_TECNICA = "No encontré esa información en la documentación técnica disponible."
MSG_ACCESO_DENEGADO = "Acceso denegado. Credenciales inválidas."
MSG_AUTH_REQUERIDA = (
    "Esta consulta corresponde a información interna de la empresa. "
    "Por favor, autentícate primero con tu nombre y clave."
)
