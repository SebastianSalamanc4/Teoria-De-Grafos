"""Componentes de interfaz para la app TSP en Streamlit."""

from .data_utils import cargar_instancia_desde_archivo
from .maps import crear_mapa_interactivo
from .charts import crear_grafico_comparacion, crear_grafico_tiempos
from .components import (
    mostrar_metricas_principales,
    mostrar_detalle_ruta,
    construir_tabla_aristas,
)

__all__ = [
    "cargar_instancia_desde_archivo",
    "crear_mapa_interactivo",
    "crear_grafico_comparacion",
    "crear_grafico_tiempos",
    "mostrar_metricas_principales",
    "mostrar_detalle_ruta",
    "construir_tabla_aristas",
]
