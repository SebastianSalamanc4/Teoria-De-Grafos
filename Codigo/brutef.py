# brutef.py
import itertools
import numpy as np


def distancia_ruta(df_dist, ruta):
    """
    Calcula la distancia total de una ruta cerrada (ciclo hamiltoniano),
    volviendo al punto de inicio.
    """
    total = 0.0
    for i in range(len(ruta) - 1):
        total += df_dist.loc[ruta[i], ruta[i+1]]
    total += df_dist.loc[ruta[-1], ruta[0]]
    return float(total)


def tsp_exhaustivo(df_dist, ciudad_inicio=None):
    """
    Búsqueda exhaustiva (fuerza bruta) para el TSP.
    Retorna (mejor_ruta, mejor_distancia).
    """
    ciudades = list(df_dist.index)

    if ciudad_inicio is None:
        mejor_ruta = None
        mejor_dist = np.inf
        for perm in itertools.permutations(ciudades):
            ruta = list(perm)
            dist = distancia_ruta(df_dist, ruta)
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_ruta = ruta
        return mejor_ruta, mejor_dist

    if ciudad_inicio not in ciudades:
        raise ValueError(f"La ciudad de inicio '{ciudad_inicio}' no está en la matriz.")

    restantes = [c for c in ciudades if c != ciudad_inicio]

    mejor_ruta = None
    mejor_dist = np.inf

    for perm in itertools.permutations(restantes):
        ruta = [ciudad_inicio] + list(perm)
        dist = distancia_ruta(df_dist, ruta)
        if dist < mejor_dist:
            mejor_dist = dist
            mejor_ruta = ruta

    return mejor_ruta, mejor_dist


def generar_rutas_exhaustivo(df_dist, ciudad_inicio):
    """
    Genera TODAS las rutas que evalúa la búsqueda exhaustiva,
    en el orden en que se exploran, con su longitud.

    Retorna una lista de tuplas:
        [(ruta1, dist1), (ruta2, dist2), ...]
    """
    ciudades = list(df_dist.index)

    if ciudad_inicio not in ciudades:
        raise ValueError(f"La ciudad de inicio '{ciudad_inicio}' no está en la matriz.")

    restantes = [c for c in ciudades if c != ciudad_inicio]

    rutas = []
    for perm in itertools.permutations(restantes):
        ruta = [ciudad_inicio] + list(perm)
        dist = distancia_ruta(df_dist, ruta)
        rutas.append((ruta, dist))

    return rutas
