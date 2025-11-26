# implementar la hauristica del vecino mas cercano y de paso un generador de animacion 
from __future__ import annotations
from typing import List, Tuple, Generator

from .instances import (
    NombreCiudad,
    MatrizDistancias,
)
from .bruteforce import distancia_ruta


# heuristica del vecino mas cercano
def vecino_mas_cercano(
    matriz: MatrizDistancias,
    ciudad_inicio: NombreCiudad | None = None
) -> Tuple[List[NombreCiudad], float]:
    """
    Aplica la heurística del vecino más cercano (Nearest Neighbor)
    para construir una ruta TSP.

    Si ciudad_inicio es None, se toma la primera ciudad del índice
    de la matriz como ciudad inicial.

    Retorna:
        (ruta_encontrada, distancia_total_con_ciclo)
    """
    ciudades = list(matriz.index)

    if not ciudades:
        raise ValueError("La matriz de distancias está vacía.")

    if ciudad_inicio is None:
        ciudad_inicio = ciudades[0]
    elif ciudad_inicio not in ciudades:
        raise ValueError(f"La ciudad de inicio '{ciudad_inicio}' no está en la matriz.")

    no_visitadas = set(ciudades)
    no_visitadas.remove(ciudad_inicio)

    ruta: List[NombreCiudad] = [ciudad_inicio]
    ciudad_actual: NombreCiudad = ciudad_inicio

    # Construcción greedy de la ruta
    while no_visitadas:
        ciudad_siguiente = min(
            no_visitadas,
            key=lambda c: float(matriz.loc[ciudad_actual, c])
        )
        ruta.append(ciudad_siguiente)
        no_visitadas.remove(ciudad_siguiente)
        ciudad_actual = ciudad_siguiente

    # Cerramos el ciclo y calculamos la distancia total usando la función común
    distancia_total = distancia_ruta(matriz, ruta)
    return ruta, distancia_total


# ---------------------------------------------------------
# GENERADOR PARA ANIMACIÓN PASO A PASO
# ---------------------------------------------------------

def generar_pasos_vecino_mas_cercano(
    matriz: MatrizDistancias,
    ciudad_inicio: NombreCiudad | None = None
) -> Generator[Tuple[List[NombreCiudad], float], None, None]:
    """
    Genera la construcción paso a paso de la ruta usando la
    heurística del vecino más cercano.

    En cada paso hace yield de:
        (ruta_actual, distancia_actual)

    La distancia_actual se calcula sobre la ruta parcial,
    cerrando el ciclo solo al final.
    """
    ciudades = list(matriz.index)

    if not ciudades:
        raise ValueError("La matriz de distancias está vacía.")

    if ciudad_inicio is None:
        ciudad_inicio = ciudades[0]
    elif ciudad_inicio not in ciudades:
        raise ValueError(f"La ciudad de inicio '{ciudad_inicio}' no está en la matriz.")

    no_visitadas = set(ciudades)
    no_visitadas.remove(ciudad_inicio)

    ruta: List[NombreCiudad] = [ciudad_inicio]
    ciudad_actual: NombreCiudad = ciudad_inicio

    # Primer estado: solo ciudad inicial (distancia 0)
    yield ruta.copy(), 0.0

    # Construimos la ruta paso a paso
    while no_visitadas:
        ciudad_siguiente = min(
            no_visitadas,
            key=lambda c: float(matriz.loc[ciudad_actual, c])
        )
        ruta.append(ciudad_siguiente)
        no_visitadas.remove(ciudad_siguiente)
        ciudad_actual = ciudad_siguiente

        # Distancia parcial sin cerrar el ciclo todavía
        distancia_parcial = 0.0
        if len(ruta) > 1:
            for i in range(len(ruta) - 1):
                distancia_parcial += float(matriz.loc[ruta[i], ruta[i+1]])

        yield ruta.copy(), distancia_parcial

    # Paso final: ruta completa + cierre del ciclo
    distancia_total = distancia_ruta(matriz, ruta)
    yield ruta.copy(), distancia_total
