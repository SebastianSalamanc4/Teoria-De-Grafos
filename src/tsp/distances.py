from __future__ import annotations
import math
from typing import Dict
import pandas as pd

from .instances import (
    InstanciaTSP,
    MatrizDistancias,
    NombreCiudad,
)

# ---------------------------------------------------------
# CONSTANTES PARA APROXIMAR DISTANCIAS EN KM
# (distancia aproximada por grado de latitud/longitud)
# ---------------------------------------------------------

KILOMETROS_POR_GRADO_LAT: float = 111.32           # ~ km por grado de latitud
LATITUD_MEDIA: float = -38.5                       # latitud promedio (por ejemplo, Araucanía)
KILOMETROS_POR_GRADO_LON: float = KILOMETROS_POR_GRADO_LAT * math.cos(
    math.radians(LATITUD_MEDIA)
)


# ---------------------------------------------------------
# FUNCIONES BÁSICAS DE DISTANCIA
# ---------------------------------------------------------

def distancia_euclidiana_grados(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Distancia euclidiana en el plano de grados (lat, lon).
    """
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


def distancia_aproximada_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calcula una distancia aproximada en kilómetros entre dos puntos
    dados por (lat, lon) usando una aproximación local.
    """
    dlat = (lat2 - lat1) * KILOMETROS_POR_GRADO_LAT
    dlon = (lon2 - lon1) * KILOMETROS_POR_GRADO_LON
    return math.sqrt(dlat**2 + dlon**2)


# ---------------------------------------------------------
# CONSTRUCCIÓN DE LA MATRIZ DE DISTANCIAS
# ---------------------------------------------------------

def construir_matriz_distancias(
    instancia: InstanciaTSP,
    en_kilometros: bool = True,
) -> MatrizDistancias:
    """
    Construye la matriz de distancias para una InstanciaTSP.

    - Si en_kilometros=True, usa una aproximación en km.
    - Si en_kilometros=False, usa distancia euclidiana en grados.

    La matriz resultante es un DataFrame con:
        - Índices  : nombres de ciudades
        - Columnas : nombres de ciudades
    """
    ciudades = instancia.ciudades
    coordenadas = instancia.coordenadas

    # Matriz numérica (lista de listas) antes de convertir a DataFrame
    matriz_numerica: list[list[float]] = []

    for ciudad_i in ciudades:
        lat_i, lon_i = coordenadas[ciudad_i]
        fila: list[float] = []

        for ciudad_j in ciudades:
            if ciudad_i == ciudad_j:
                distancia = 0.0
            else:
                lat_j, lon_j = coordenadas[ciudad_j]
                if en_kilometros:
                    distancia = distancia_aproximada_km(lat_i, lon_i, lat_j, lon_j)
                else:
                    distancia = distancia_euclidiana_grados(lat_i, lon_i, lat_j, lon_j)

            fila.append(distancia)

        matriz_numerica.append(fila)

    matriz = pd.DataFrame(matriz_numerica, index=ciudades, columns=ciudades)
    return matriz


def asignar_matriz_a_instancia(
    instancia: InstanciaTSP,
    en_kilometros: bool = True,
) -> MatrizDistancias:
    """
    Construye la matriz de distancias y la asigna a la instancia.

    Devuelve también la matriz (por comodidad).
    """
    matriz = construir_matriz_distancias(instancia, en_kilometros=en_kilometros)
    instancia.asignar_matriz_distancias(matriz)
    return matriz



# ---------------------------------------------------------
# FUNCIONES AUXILIARES SOBRE LA MATRIZ
# ---------------------------------------------------------

def distancia_entre_ciudades(
    matriz: MatrizDistancias,
    ciudad_origen: NombreCiudad,
    ciudad_destino: NombreCiudad,
) -> float:
    """
    Devuelve la distancia almacenada entre dos ciudades
    a partir de la matriz de distancias.
    """
    return float(matriz.loc[ciudad_origen, ciudad_destino])
