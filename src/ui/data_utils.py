from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from tsp.instances import crear_instancia_desde_dataframe, InstanciaTSP

# ---------------------------------------------------------
# RUTAS Y CARGA DE DATOS
# ---------------------------------------------------------

# Directorio base: carpeta src
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


@st.cache_data
def cargar_instancia_desde_archivo(nombre_archivo: str) -> InstanciaTSP | None:
    """
    Carga un CSV desde la carpeta ``data/`` y lo convierte en InstanciaTSP.

    Mantiene la misma lógica que el app.py original:
    - Lee el archivo CSV.
    - Normaliza nombres de columnas (ciudad, lat, lon → Ciudad, Latitud, Longitud).
    - Construye la instancia TSP.
    """
    try:
        ruta_csv = DATA_DIR / nombre_archivo
        df = pd.read_csv(ruta_csv)

        # Normalizar nombres de columnas (soporta mayúsculas/minúsculas distintas)
        columnas = {c.lower(): c for c in df.columns}
        if {"ciudad", "lat", "lon"}.issubset({c.lower() for c in df.columns}):
            df = df.rename(
                columns={
                    columnas["ciudad"]: "Ciudad",
                    columnas["lat"]: "Latitud",
                    columnas["lon"]: "Longitud",
                }
            )

        instancia = crear_instancia_desde_dataframe(df)
        return instancia
    except Exception as e:
        st.error(f"Error cargando el archivo: {e}")
        return None
