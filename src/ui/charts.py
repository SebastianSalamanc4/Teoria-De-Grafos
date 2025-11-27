from __future__ import annotations

import plotly.graph_objects as go

# ---------------------------------------------------------
# GRÁFICOS COMPARATIVOS
# ---------------------------------------------------------


def crear_grafico_comparacion(
    dist_optima: float,
    dist_nn: float,
    tiempo_optimo: float,
    tiempo_nn: float,
):
    """Crea un gráfico de barras comparando las distancias de ambas rutas."""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["Óptimo", "Vecino Más Cercano"],
            y=[dist_optima, dist_nn],
            name="Distancia (km)",
            marker_color=["#00CC96", "#FFA15A"],
            text=[f"{dist_optima:.2f} km", f"{dist_nn:.2f} km"],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="Comparación de Distancias de Ruta",
        yaxis_title="Distancia (km)",
        showlegend=False,
    )

    return fig


def crear_grafico_tiempos(tiempo_optimo: float, tiempo_nn: float):
    """Crea un gráfico de barras comparando los tiempos de ejecución."""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["Óptimo", "Vecino Más Cercano"],
            y=[tiempo_optimo, tiempo_nn],
            name="Tiempo (s)",
            marker_color=["#EF553B", "#636EFA"],
            text=[f"{tiempo_optimo:.4f} s", f"{tiempo_nn:.4f} s"],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="Comparación de Tiempos de Ejecución",
        yaxis_title="Tiempo (segundos)",
        showlegend=False,
    )

    return fig
