# Codigo/Distancias.py

import os
import math
import pandas as pd

# -------------------------------
# 1. Parámetros y constantes
# -------------------------------

# Aprox. km por grado de latitud y longitud
KILOMETROS_POR_GRADO_LAT = 111.32  # ~constante
LAT_MEDIA = -38.5  # latitud promedio de tus ciudades (Araucanía)
KILOMETROS_POR_GRADO_LON = 111.32 * math.cos(math.radians(LAT_MEDIA))


# -------------------------------
# 2. Lectura de ciudades
# -------------------------------

def cargar_ciudades(ruta_csv):
    """
    Lee el archivo CSV con columnas: ciudad, lat, lon
    y devuelve un DataFrame de pandas.
    Si las columnas no son las esperadas, retorna un mensaje de error simple.
    """
    df = pd.read_csv(ruta_csv)

    columnas_esperadas = {"ciudad", "lat", "lon"}
    if not columnas_esperadas.issubset(df.columns):
        # Aquí cambiamos el raise por un retorno de texto
        return "columnas inesperadas"

    return df


# -------------------------------
# 3. Distancia euclidiana en km
# -------------------------------

def distancia_euclidiana_km(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia aproximada en km entre dos puntos (lat, lon),
    usando un modelo plano local (bueno para distancias relativamente cortas).
    """
    dx = (lon2 - lon1) * KILOMETROS_POR_GRADO_LON
    dy = (lat2 - lat1) * KILOMETROS_POR_GRADO_LAT
    return math.sqrt(dx**2 + dy**2)


# -------------------------------
# 4. Construcción de la matriz D
# -------------------------------

def matriz_distancias(ciudades):
    """
    Recibe un DataFrame con columnas ciudad, lat, lon
    y retorna un DataFrame D donde D[i,j] es la distancia
    entre ciudad_i y ciudad_j (en km).
    """
    n = len(ciudades)
    nombres = ciudades["ciudad"].tolist()

    # Matriz vacía (lista de listas) construida "a mano"
    D = []

    for i in range(n):
        lat_i = ciudades.loc[i, "lat"]
        lon_i = ciudades.loc[i, "lon"]

        fila = []  # aquí vamos guardando las distancias desde la ciudad i

        for j in range(n):
            if i == j:
                distancia = 0.0
            else:
                lat_j = ciudades.loc[j, "lat"]
                lon_j = ciudades.loc[j, "lon"]
                distancia = distancia_euclidiana_km(lat_i, lon_i, lat_j, lon_j)

            fila.append(distancia)

        # agregamos la fila completa a la matriz
        D.append(fila)

    # DataFrame con nombres de filas y columnas = nombres de ciudades
    D_df = pd.DataFrame(D, index=nombres, columns=nombres)
    return D_df


# -------------------------------
# 5. Script principal (para probar)
# -------------------------------

if __name__ == "__main__":
    # Carpeta raíz del proyecto (un nivel arriba de Codigo/)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Ruta al CSV de ciudades
    ruta_ciudades = os.path.join(BASE_DIR, "Datos", "SeisCiudadesDeChile.csv")

    # 1) Cargar ciudades
    ciudades_df = cargar_ciudades(ruta_ciudades)

    # Si cargar_ciudades devolvió un string, es que hubo problema
    if isinstance(ciudades_df, str):
        print(ciudades_df)  # debería imprimir: columnas inesperadas
    else:
        print("Ciudades cargadas:")
        print(ciudades_df)
        print()

        # 2) Construir matriz de distancias
        D = matriz_distancias(ciudades_df)

        print("Matriz de distancias (km, redondeada a 2 decimales):")
        print(D.round(2))
        print()

        # 3) Guardar la matriz en un CSV (opcional pero útil para el informe)
        ruta_salida = os.path.join(BASE_DIR, "Datos", "MatrizDistancias_SeisCiudades.csv")
        D.to_csv(ruta_salida, index=True)
        print(f"Matriz de distancias guardada en:\n{ruta_salida}")
