from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# COMPONENTES DE INTERFAZ (MÉTRICAS Y DETALLES)
# ---------------------------------------------------------


def mostrar_metricas_principales(
    dist_optima: float,
    dist_nn: float,
    tiempo_optimo: float,
    tiempo_nn: float,
    gap: float | None = None,
):
    """Muestra las métricas principales en tarjetas en la parte superior derecha."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Distancia Óptima</div>
                <div class="metric-value">{dist_optima:.2f} km</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Distancia Heurística</div>
                <div class="metric-value">{dist_nn:.2f} km</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Tiempo Heurístico</div>
                <div class="metric-value">{tiempo_nn:.4f} s</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        if gap is not None:
            color = "#FF4B4B" if gap > 5 else "#00CC96"
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Gap de Optimalidad</div>
                    <div class="metric-value" style="color: {color}">{gap:.2f} %</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def mostrar_detalle_ruta(ruta: List[str], distancia: float, nombre: str):
    """Muestra el detalle de una ruta específica en un recuadro estilizado."""
    st.markdown(
        f"""
        <div class="route-card">
            <h4>{nombre}</h4>
            <p><strong>Ruta:</strong> {' → '.join(ruta)} → {ruta[0]}</p>
            <p><strong>Distancia total:</strong> {distancia:.2f} km</p>
            <p><strong>Número de ciudades:</strong> {len(ruta)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def construir_tabla_aristas(matriz: pd.DataFrame, ruta: List[str]) -> pd.DataFrame:
    """Construye una tabla con el detalle arista por arista de una ruta.

    Cada fila contiene:
    - Ciudad de origen
    - Ciudad de destino
    - Distancia entre ambas
    """
    filas: list[dict] = []
    n = len(ruta)

    for i in range(n):
        origen = ruta[i]
        destino = ruta[(i + 1) % n]  # siguiente, cerrando ciclo
        distancia = float(matriz.loc[origen, destino])
        filas.append(
            {
                "Desde": origen,
                "Hasta": destino,
                "Distancia (km)": distancia,
            }
        )

    return pd.DataFrame(filas)
