# src/tsp/plotting.py

from __future__ import annotations
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import networkx as nx

from .instances import (
    InstanciaTSP,
    NombreCiudad,
)
from .bruteforce import distancia_ruta
from .heuristics import vecino_mas_cercano


# ---------------------------------------------------------
# CONVERTIR COORDENADAS A POSICIONES PARA NETWORKX
# ---------------------------------------------------------

def obtener_posiciones(instancia: InstanciaTSP) -> Dict[NombreCiudad, Tuple[float, float]]:
    """
    Convierte las coordenadas (lat, lon) de la instancia
    a un diccionario {ciudad: (lon, lat)} apto para NetworkX.
    """
    # NOTA IMPORTANTE:
    # NetworkX dibuja en X-Y (horizontal, vertical)
    # Los mapas reales usan lon (X) y lat (Y)
    posiciones = {
        ciudad: (coord[1], coord[0])  # (lon, lat)
        for ciudad, coord in instancia.coordenadas.items()
    }
    return posiciones


# ---------------------------------------------------------
# GRAFO BASE
# ---------------------------------------------------------

def grafo_base(instancia: InstanciaTSP) -> nx.Graph:
    """
    Crea un grafo NetworkX totalmente conectado (Grafo completo)
    a partir de las ciudades de la instancia.
    """
    G = nx.Graph()
    ciudades = instancia.ciudades

    # Añadir nodos
    for ciudad in ciudades:
        G.add_node(ciudad)

    # Añadir aristas entre todas las ciudades
    for i in range(len(ciudades)):
        for j in range(i+1, len(ciudades)):
            G.add_edge(ciudades[i], ciudades[j])

    return G


# ---------------------------------------------------------
# DIBUJAR GRAFO BASE (SIN RUTA)
# ---------------------------------------------------------

def dibujar_grafo(
    instancia: InstanciaTSP,
    ax: plt.Axes | None = None
) -> plt.Axes:
    """
    Dibuja solo las ciudades y sus conexiones (grafo completo),
    sin ruta marcada.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 6))

    G = grafo_base(instancia)
    posiciones = obtener_posiciones(instancia)

    # nodos
    nx.draw_networkx_nodes(G, posiciones, node_size=600, node_color="lightblue", ax=ax)

    # etiquetas
    nx.draw_networkx_labels(G, posiciones, font_size=10, ax=ax)

    # aristas tenues
    nx.draw_networkx_edges(G, posiciones, alpha=0.3, ax=ax)

    ax.set_title("Grafo base (ciudades conectadas)")
    ax.set_axis_off()

    return ax


# ---------------------------------------------------------
# DIBUJAR UNA RUTA COMPLETA
# ---------------------------------------------------------

def dibujar_ruta(
    instancia: InstanciaTSP,
    ruta: List[NombreCiudad],
    color: str = "red",
    ax: plt.Axes | None = None,
    titulo: str | None = None
) -> plt.Axes:
    """
    Dibuja la ruta completa sobre el grafo base.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 6))

    G = grafo_base(instancia)
    posiciones = obtener_posiciones(instancia)

    # dibujar grafo base más tenue
    nx.draw_networkx_edges(G, posiciones, alpha=0.1, ax=ax)
    nx.draw_networkx_nodes(G, posiciones, node_size=600, node_color="lightgray", ax=ax)
    nx.draw_networkx_labels(G, posiciones, font_size=10, ax=ax)

    # construir aristas en orden de la ruta
    aristas_ruta = [(ruta[i], ruta[i+1]) for i in range(len(ruta)-1)]
    aristas_ruta.append((ruta[-1], ruta[0]))  # cierre del ciclo

    # dibujar la ruta
    nx.draw_networkx_edges(
        G,
        posiciones,
        edgelist=aristas_ruta,
        width=3,
        edge_color=color,
        ax=ax
    )

    if titulo:
        ax.set_title(titulo)

    ax.set_axis_off()
    return ax


# ---------------------------------------------------------
# DIBUJAR RUTA PARCIAL (PARA ANIMACIÓN)
# ---------------------------------------------------------

def dibujar_ruta_parcial(
    instancia: InstanciaTSP,
    ruta_parcial: List[NombreCiudad],
    ax: plt.Axes | None = None,
    color: str = "orange",
    titulo: str = "Ruta parcial"
) -> plt.Axes:
    """
    Dibuja una ruta parcial (sin cerrar ciclo).
    Ideal para animaciones paso a paso.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 6))

    G = grafo_base(instancia)
    posiciones = obtener_posiciones(instancia)

    # grafo base tenue
    nx.draw_networkx_edges(G, posiciones, alpha=0.1, ax=ax)
    nx.draw_networkx_nodes(G, posiciones, node_size=600, node_color="lightgray", ax=ax)
    nx.draw_networkx_labels(G, posiciones, font_size=10, ax=ax)

    # aristas parciales
    if len(ruta_parcial) > 1:
        aristas = [(ruta_parcial[i], ruta_parcial[i+1]) for i in range(len(ruta_parcial)-1)]
        nx.draw_networkx_edges(G, posiciones, edgelist=aristas, width=3, edge_color=color, ax=ax)

    ax.set_title(titulo)
    ax.set_axis_off()

    return ax
