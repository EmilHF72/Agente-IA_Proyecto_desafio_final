"""
autenticacion.py
----------------
Módulo de autenticación de empleados de ElectroHogar Chile SpA.
Lee el CSV de empleados y valida credenciales nombre + clave.
"""

import logging
from typing import Optional

import pandas as pd

from config import CSV_EMPLEADOS, MSG_ACCESO_DENEGADO

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipo de retorno para un empleado autenticado
# ---------------------------------------------------------------------------
class Empleado:
    """Representa un empleado autenticado."""

    def __init__(self, nombre: str, cargo: str, sueldo: int) -> None:
        self.nombre = nombre
        self.cargo = cargo
        self.sueldo = sueldo

    def __repr__(self) -> str:
        return f"Empleado(nombre={self.nombre!r}, cargo={self.cargo!r})"


def _cargar_empleados() -> pd.DataFrame:
    """
    Carga el CSV de empleados con manejo de errores.

    Returns:
        DataFrame con columnas: Nombre, Cargo, Sueldo, Clave.

    Raises:
        FileNotFoundError: Si el CSV no existe.
    """
    if not CSV_EMPLEADOS.exists():
        raise FileNotFoundError(
            f"Archivo de empleados no encontrado: {CSV_EMPLEADOS.resolve()}"
        )

    df = pd.read_csv(CSV_EMPLEADOS, dtype={"Clave": str})
    # Normalizar: eliminar espacios en los nombres de columna
    df.columns = [col.strip() for col in df.columns]
    # Normalizar valores de texto
    df["Nombre"] = df["Nombre"].str.strip()
    df["Cargo"] = df["Cargo"].str.strip()
    df["Clave"] = df["Clave"].str.strip().str.zfill(4)  # Asegurar 4 dígitos
    return df


def validar_credenciales(nombre: str, clave: str) -> Optional[Empleado]:
    """
    Valida las credenciales de un empleado.

    La comparación de nombre es case-insensitive y trim.
    La clave se compara exactamente (4 dígitos, con ceros a la izquierda).

    Args:
        nombre: Nombre completo del empleado.
        clave: Clave secreta de 4 dígitos (como string).

    Returns:
        Instancia de Empleado si las credenciales son válidas, None si no.
    """
    nombre_normalizado = nombre.strip().lower()
    clave_normalizada = str(clave).strip().zfill(4)

    try:
        df = _cargar_empleados()
    except FileNotFoundError as exc:
        logger.error(str(exc))
        return None

    coincidencias = df[
        (df["Nombre"].str.lower() == nombre_normalizado)
        & (df["Clave"] == clave_normalizada)
    ]

    if coincidencias.empty:
        logger.warning(f"Intento de autenticación fallido para: {nombre!r}")
        return None

    fila = coincidencias.iloc[0]
    logger.info(f"Empleado autenticado: {fila['Nombre']} — {fila['Cargo']}")
    return Empleado(
        nombre=fila["Nombre"],
        cargo=fila["Cargo"],
        sueldo=int(fila["Sueldo"]),
    )


def autenticar(nombre: str, clave: str) -> tuple[bool, str, Optional[Empleado]]:
    """
    Punto de entrada principal para la UI de autenticación.

    Returns:
        Tupla (éxito: bool, mensaje: str, empleado: Empleado | None).
    """
    empleado = validar_credenciales(nombre, clave)
    if empleado:
        return True, f"Bienvenido/a, {empleado.nombre} ({empleado.cargo}).", empleado
    return False, MSG_ACCESO_DENEGADO, None
