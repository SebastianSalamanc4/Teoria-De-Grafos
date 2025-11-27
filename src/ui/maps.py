from __future__ import annotations

from typing import Dict, Any, Optional

import folium

from tsp.instances import InstanciaTSP

# ---------------------------------------------------------
# MAPA INTERACTIVO
# ---------------------------------------------------------


def crear_mapa_interactivo(
    instancia: InstanciaTSP, rutas: Optional[Dict[str, Dict[str, Any]]] = None
) -> folium.Map:
    """Crea un mapa interactivo con las ciudades y, opcionalmente, varias rutas.

    Parámetros
    ----------
    instancia:
        InstanciaTSP con las coordenadas de cada ciudad.
    rutas:
        Diccionario opcional del tipo::

            {
                "óptima": {
                    "ruta": [...lista de ciudades...],
                    "nombre": "Ruta Óptima (Exhaustivo)",
                    "distancia": 123.45,
                },
                "heurística": {...},
            }
    """
    lats = [coord[0] for coord in instancia.coordenadas.values()]
    lons = [coord[1] for coord in instancia.coordenadas.values()]
    centro = (sum(lats) / len(lats), sum(lons) / len(lons))

    mapa = folium.Map(
        location=centro,
        zoom_start=6,
        tiles="OpenStreetMap",
        width="100%",
        height=600,
    )

    # Colores para cada tipo de ruta
    colores_rutas: Dict[str, Dict[str, Any]] = {
        "óptima": {"color": "#FF4B4B", "peso": 6, "opacidad": 0.9},
        "heurística": {"color": "#4B78FF", "peso": 5, "opacidad": 0.7},
        "comparación": {"color": "#00D4AA", "peso": 4, "opacidad": 0.6},
    }

    # Marcadores de ciudades
    for ciudad, (lat, lon) in instancia.coordenadas.items():
        folium.Marker(
            location=(lat, lon),
            popup=folium.Popup(
                f"<b>{ciudad}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
                max_width=200,
            ),
            tooltip=ciudad,
            icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
        ).add_to(mapa)

    # Rutas (si están disponibles)
    if rutas:
        for nombre_ruta, datos_ruta in rutas.items():
            ruta_ciudades = datos_ruta.get("ruta")
            if not ruta_ciudades:
                continue

            color_config = colores_rutas.get(
                nombre_ruta,
                {"color": "#000000", "peso": 3, "opacidad": 0.7},
            )

            puntos = [
                (instancia.coordenadas[c][0], instancia.coordenadas[c][1])
                for c in ruta_ciudades
            ]

            # Cerrar el ciclo
            if len(puntos) > 1:
                puntos.append(puntos[0])

            folium.PolyLine(
                locations=puntos,
                color=color_config["color"],
                weight=color_config["peso"],
                opacity=color_config["opacidad"],
                tooltip=f"{datos_ruta['nombre']} - {datos_ruta['distancia']:.2f} km",
                popup=folium.Popup(
                    f"<b>{datos_ruta['nombre']}</b><br>"
                    f"Distancia: {datos_ruta['distancia']:.2f} km",
                    max_width=300,
                ),
            ).add_to(mapa)

    folium.LayerControl().add_to(mapa)
    return mapa
