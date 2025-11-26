# nearestn.py
from brutef import distancia_ruta


def nearest_neighbor(df_dist, ciudad_inicio):
    """
    Heurística del vecino más cercano para el TSP.

    - df_dist: DataFrame de distancias (índice y columnas = ciudades)
    - ciudad_inicio: ciudad fija de partida (str)

    Retorna: (ruta, distancia_total)
    ruta NO incluye el regreso al inicio (se considera implícito al calcular la distancia).
    """
    ciudades = list(df_dist.index)

    if ciudad_inicio not in ciudades:
        raise ValueError(f"La ciudad de inicio '{ciudad_inicio}' no está en la matriz.")

    # Conjunto de ciudades aún no visitadas
    no_visitadas = set(ciudades)
    no_visitadas.remove(ciudad_inicio)

    ruta = [ciudad_inicio]
    actual = ciudad_inicio

    # En cada paso elegimos la ciudad no visitada más cercana
    while no_visitadas:
        siguiente = min(
            no_visitadas,
            key=lambda c: df_dist.loc[actual, c]
        )
        ruta.append(siguiente)
        no_visitadas.remove(siguiente)
        actual = siguiente

    # Distancia total del ciclo (incluyendo regreso a ciudad_inicio)
    dist_total = distancia_ruta(df_dist, ruta)
    return ruta, dist_total
