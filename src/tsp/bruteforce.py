# src/tsp/bruteforce.py

from __future__ import annotations
import itertools
from typing import List, Tuple, Generator
import pandas as pd

from .instances import (
    NombreCiudad,
    MatrizDistancias,
)


# ---------------------------------------------------------
# FUNCIONES BÁSICAS
# ---------------------------------------------------------

def distancia_ruta(
    matriz: MatrizDistancias,
    ruta: List[NombreCiudad]
) -> float:
    """
    Calcula la distancia total de una ruta (ciclo hamiltoniano):
    ciudad1 -> ciudad2 -> ... -> ciudadN -> ciudad1
    Basicamente calcula el ciclo completo volviendo al inicio.
    """
    distancia_total = 0.0

    for i in range(len(ruta) - 1):
        distancia_total += float(matriz.loc[ruta[i], ruta[i+1]])

    # Cierre del ciclo
    distancia_total += float(matriz.loc[ruta[-1], ruta[0]])

    return distancia_total


# ---------------------------------------------------------
# GENERADOR DE TODAS LAS RUTAS
# ---------------------------------------------------------

def generar_rutas(
    ciudades: List[NombreCiudad],
    ciudad_inicio: NombreCiudad | None = None
) -> Generator[List[NombreCiudad], None, None]:
    """
    Genera todas las rutas posibles (permutaciones).

    - Si ciudad_inicio es None, se generan todas las permutaciones.
    - Si ciudad_inicio se fija, se generan permutaciones del resto,
      reduciendo factorialmente el tamaño de búsqueda. --> n!→(n−1)!

    """
    if ciudad_inicio and ciudad_inicio not in ciudades:
        raise ValueError(f"La ciudad de inicio '{ciudad_inicio}' no está en la lista.")

    if ciudad_inicio is None:
        # Permutar TODAS las ciudades
        for perm in itertools.permutations(ciudades):
            yield list(perm)
    else:
        # Fijar ciudad inicial y permutar el resto
        restantes = [c for c in ciudades if c != ciudad_inicio]
        for perm in itertools.permutations(restantes):
            yield [ciudad_inicio, *perm]


# ---------------------------------------------------------
# ALGORITMO EXHAUSTIVO COMPLETO
# ---------------------------------------------------------

def resolver_exhaustivo(
    matriz: MatrizDistancias,
    ciudad_inicio: NombreCiudad | None = None
) -> Tuple[List[NombreCiudad], float]:
    """
    Basicmente: Recorre todas las rutas → busca el mínimo → retorna mejor ruta y distancia.

    Resuelve el TSP usando búsqueda exhaustiva.

    Retorna:
        (mejor_ruta, distancia_total)
    """
    ciudades = list(matriz.index)

    mejor_ruta: List[NombreCiudad] | None = None
    mejor_distancia: float = float("inf")

    for ruta in generar_rutas(ciudades, ciudad_inicio): # recorrer todas las rutas y evaluar cada una
        dist = distancia_ruta(matriz, ruta)
        if dist < mejor_distancia: # actualizar mejor si se encuentra una mejor
            mejor_distancia = dist
            mejor_ruta = ruta

    return mejor_ruta, mejor_distancia


# generador para animación paso a paso del algoritmo exhaustivo
def generar_exploracion(
    matriz: MatrizDistancias,
    ciudad_inicio: NombreCiudad | None = None
) -> Generator[Tuple[List[NombreCiudad], float], None, None]:
    """
    Genera (ruta_actual, distancia_actual)
    para cada ruta evaluada. 
    """
    ciudades = list(matriz.index)

    for ruta in generar_rutas(ciudades, ciudad_inicio):
        distancia = distancia_ruta(matriz, ruta)
        yield ruta, distancia
