"""
utils/clasificador.py
---------------------
Clasificador de intenciones basado en palabras clave.
Determina si una pregunta es de naturaleza técnica (RIC N°10)
o administrativa (políticas internas de la empresa).
"""

import re
from enum import Enum


class TipoPregunta(str, Enum):
    TECNICA = "tecnica"
    ADMINISTRATIVA = "administrativa"
    AMBIGUA = "ambigua"


# ---------------------------------------------------------------------------
# Palabras clave por categoría
# ---------------------------------------------------------------------------
KEYWORDS_ADMINISTRATIVA = [
    # Recursos Humanos
    "vacaciones", "vacacion", "dias administrativos", "días administrativos",
    "dias admin", "días admin", "licencia", "licencias", "medica", "médica",
    "feriado", "feriados", "permiso", "permisos", "horario", "horarios",
    "sueldo", "sueldos", "remuneracion", "remuneración", "salario",
    "contrato", "contratos", "bono", "bonos", "aguinaldo",

    # Operaciones / Empresa
    "herramienta", "herramientas", "solicitar herramienta", "inventario",
    "reembolso", "reembolsos", "viatico", "viáticos", "gastos",
    "protocolo", "politica", "política", "políticas", "norma interna",
    "reglamento interno", "procedimiento interno",

    # Identificación empresa
    "empresa", "electrohogar", "administracion", "administración",
    "empleado", "empleados", "funcionario", "funcionarios",
    "trabajador", "trabajadores", "personal",

    # Preguntas directas de RRHH
    "cuantos dias", "cuántos días", "como solicito", "cómo solicito",
    "cual es mi horario", "cuál es mi horario", "tiempo libre",
]

KEYWORDS_TECNICA = [
    # Electricidad general
    "enchufe", "enchufes", "tomacorriente", "tomacorrientes",
    "interruptor", "interruptores", "diferencial", "diferenciales",
    "conductor", "conductores", "cable", "cables", "calibre",
    "seccion", "sección", "corriente", "voltaje", "tension", "tensión",
    "potencia", "watts", "amperios", "amperes", "ohm",

    # Instalaciones
    "instalacion", "instalación", "instalaciones", "circuito", "circuitos",
    "tablero", "tableros", "disyuntor", "disyuntores", "breaker",
    "fusible", "fusibles", "proteccion", "protección",

    # Normativa
    "ric", "ric n°10", "ric 10", "ric10", "norma", "normativa",
    "reglamento", "sec", "certificacion", "certificación",
    "puesta a tierra", "tierra", "earthing", "grounding",

    # Conceptos técnicos
    "artefacto", "artefactos", "carga", "sobrecargas", "cortocircuito",
    "corto circuito", "aislamiento", "conductor neutro", "neutro",
    "fase", "fases", "bifasico", "bifásico", "trifasico", "trifásico",
    "baja tension", "baja tensión", "media tension", "alta tension",
    "luminaria", "iluminacion", "iluminación", "alumbrado",
    "toma de corriente", "punto de luz", "canaleta", "tubo conduit",
    "ducto", "bandeja", "empalme", "conector",
]


def clasificar_pregunta(texto: str) -> TipoPregunta:
    """
    Clasifica una pregunta según su naturaleza.

    Args:
        texto: Pregunta del usuario en texto libre.

    Returns:
        TipoPregunta.TECNICA, TipoPregunta.ADMINISTRATIVA o TipoPregunta.AMBIGUA.
    """
    texto_lower = texto.lower()
    # Eliminar tildes para búsqueda más robusta
    texto_normalizado = _normalizar(texto_lower)

    score_admin = sum(
        1 for kw in KEYWORDS_ADMINISTRATIVA
        if _normalizar(kw) in texto_normalizado
    )
    score_tecnica = sum(
        1 for kw in KEYWORDS_TECNICA
        if _normalizar(kw) in texto_normalizado
    )

    if score_admin > score_tecnica:
        return TipoPregunta.ADMINISTRATIVA
    elif score_tecnica > score_admin:
        return TipoPregunta.TECNICA
    else:
        return TipoPregunta.AMBIGUA


def _normalizar(texto: str) -> str:
    """Elimina tildes y convierte a minúsculas para comparación robusta."""
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n",
    }
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    return texto
