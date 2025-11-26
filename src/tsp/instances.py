# este archivo define la estructura de datos para representar instancias del problema del viajante de comercio (TSP)

from __future__ import annotations  # permite usar la clase en anotaciones de tipo
from dataclasses import dataclass   # para definir clases de datos
from typing import List, Dict, Tuple
import pandas as pd                 # para manejar dataframes


NombreCiudad = str                              # alias para el tipo nombre de ciudad
Coordenada = Tuple[float, float]                # (latitud, longitud)
CoordenadasCiudades = Dict[NombreCiudad, Coordenada]  # ciudad -> (lat, lon)

MatrizDistancias = pd.DataFrame                 # DataFrame para la matriz de distancias
ListaCiudades = List[NombreCiudad]              # lista de nombres de ciudades


@dataclass
class InstanciaTSP:
    ciudades: ListaCiudades                    # lista de nombres de ciudades
    coordenadas: CoordenadasCiudades          # ciudad -> (lat, lon)
    matriz_distancias: MatrizDistancias | None = None  # matriz de distancias (opcional)

    def asignar_matriz_distancias(self, matriz: MatrizDistancias) -> None:
        self.matriz_distancias = matriz # asigna la matriz de distancias a la instancia

    def __repr__(self) -> str:
        return (
            f"InstanciaTSP(ciudades={self.ciudades}, "
            f"num_ciudades={len(self.ciudades)}, "
            f"matriz_lista={'Sí' if self.matriz_distancias is not None else 'No'})"
        )

# carfgar ciudades y coordenadas desde un archivo CSV
def cargar_ciudades_desde_csv(ruta: str) -> InstanciaTSP:
    df = pd.read_csv(ruta)

    columnas_requeridas = {"Ciudad", "Latitud", "Longitud"}
    if not columnas_requeridas.issubset(df.columns):
        raise ValueError(f"El CSV debe contener las columnas: {columnas_requeridas}")

    ciudades: ListaCiudades = df["Ciudad"].tolist()

    coordenadas: CoordenadasCiudades = {
        fila["Ciudad"]: (fila["Latitud"], fila["Longitud"])
        for _, fila in df.iterrows() # iterar sobre filas del DataFrame 
    }

    return InstanciaTSP(ciudades=ciudades, coordenadas=coordenadas)



# crear instancia desde un DataFrame
def crear_instancia_desde_dataframe(df: pd.DataFrame) -> InstanciaTSP:
    columnas_requeridas = {"Ciudad", "Latitud", "Longitud"}
    if not columnas_requeridas.issubset(df.columns):
        raise ValueError(f"El DataFrame debe contener las columnas: {columnas_requeridas}")

    ciudades: ListaCiudades = df["Ciudad"].tolist()

    coordenadas: CoordenadasCiudades = {
        fila["Ciudad"]: (fila["Latitud"], fila["Longitud"])
        for _, fila in df.iterrows() # iterar sobre filas del DataFrame
    }

    return InstanciaTSP(ciudades=ciudades, coordenadas=coordenadas)
