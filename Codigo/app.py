import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
from brutef import tsp_exhaustivo, generar_rutas_exhaustivo 
from nearestn import nearest_neighbor

# ====================================
# Configuración general de la página
# ====================================
st.set_page_config(
    page_title="Grafo de ciudades (layout geográfico)",
    layout="wide"
)

st.title("Grafo de ciudades con layout geográfico (latitud / longitud)")
st.markdown("""
Este aplicativo:
1. Carga **MatrizDistancias_SeisCiudades.csv** (matriz de distancias entre ciudades).
2. Carga **SeisCiudadesDeChile.csv** (latitud y longitud de cada ciudad).
3. Construye un grafo completo y lo dibuja usando la posición real (lon, lat).
4. Permite ejecutar **búsqueda exhaustiva (TSP)** para encontrar la ruta óptima.
""")

# ====================================
# Funciones para cargar datos
# ====================================
@st.cache_data
def load_distance_matrix(path: str) -> pd.DataFrame:
    """
    Lee la matriz de distancias desde un CSV con la forma:

    ,Temuco,Lautaro,...
    Temuco,0.0,...
    Lautaro,...
    """
    df = pd.read_csv(path, index_col=0)
    return df

@st.cache_data
def load_city_coords(path: str) -> pd.DataFrame:
    """
    Lee las coordenadas de ciudades desde un CSV con columnas:
    ciudad,lat,lon
    """
    df = pd.read_csv(path)
    return df

@st.cache_data
def get_rutas_exhaustivas(df_dist, ciudad_inicio):
    """
    Envuelve generar_rutas_exhaustivo y cachea el resultado
    para no recalcular todas las permutaciones cada vez.
    """
    return generar_rutas_exhaustivo(df_dist, ciudad_inicio)

# ====================================
# Cargar archivos
# ====================================
try:
    df_dist = load_distance_matrix("../Datos/MatrizDistancias_SeisCiudades.csv")
except FileNotFoundError:
    st.error("No se encontró **../Datos/MatrizDistancias_SeisCiudades.csv**.")
    st.stop()

try:
    df_ciudades = load_city_coords("../Datos/SeisCiudadesDeChile.csv")
except FileNotFoundError:
    st.error("No se encontró **../Datos/SeisCiudadesDeChile.csv**.")
    st.stop()

st.subheader("Matriz de distancias")
st.dataframe(df_dist.style.format("{:.2f}"), use_container_width=True)

st.subheader("Coordenadas de las ciudades")
st.dataframe(df_ciudades, use_container_width=True)

# ====================================
# Construir el grafo
# ====================================
G = nx.Graph()

# Añadir nodos (ciudades) desde la matriz
for ciudad in df_dist.index:
    G.add_node(ciudad)

# Añadir aristas con pesos (usamos solo parte superior de la matriz)
for i, u in enumerate(df_dist.index):
    for j, v in enumerate(df_dist.columns):
        if j <= i:
            continue
        peso = df_dist.loc[u, v]
        if pd.isna(peso):
            continue
        if float(peso) == 0.0:
            continue
        G.add_edge(u, v, weight=float(peso))

# ====================================
# Construir layout geográfico (lon, lat)
# ====================================
# Creamos un diccionario: ciudad -> (lon, lat)
coord_map = {}
for _, row in df_ciudades.iterrows():
    nombre = row["ciudad"]
    lat = row["lat"]
    lon = row["lon"]
    coord_map[nombre] = (lon, lat)  # x = longitud, y = latitud

# Comprobamos que todas las ciudades de la matriz tengan coordenadas
ciudades_sin_coord = [c for c in G.nodes if c not in coord_map]
if ciudades_sin_coord:
    st.warning(
        "Hay ciudades en la matriz de distancias sin coordenadas en SeisCiudadesDeChile.csv: "
        + ", ".join(ciudades_sin_coord)
    )

# Posiciones finales solo para las ciudades que tienen coord
pos_geo = {c: coord_map[c] for c in G.nodes if c in coord_map}

# ====================================
# Controles en sidebar
# ====================================
st.sidebar.header("Opciones de visualización del grafo")

mostrar_pesos = st.sidebar.checkbox(
    "Mostrar pesos (distancias) en las aristas",
    value=True
)

# Umbral para filtrar aristas muy largas (solo efectos visuales)
distancias = df_dist.values
distancias_no_cero = distancias[distancias > 0]

if len(distancias_no_cero) > 0:
    dist_min = float(distancias_no_cero.min())
    dist_max = float(distancias_no_cero.max())
else:
    dist_min, dist_max = 0.0, 1.0

umbral = st.sidebar.slider(
    "Mostrar solo aristas con distancia ≤",
    min_value=dist_min,
    max_value=dist_max,
    value=dist_max
)

# ====================================
# Crear figura con matplotlib (layout geográfico)
# ====================================
fig, ax = plt.subplots(figsize=(7, 7))

# Filtrar aristas según umbral
edges_to_draw = []
edge_weights = {}
for u, v, data in G.edges(data=True):
    w = data.get("weight", 1.0)
    if w <= umbral:
        # Solo dibujamos si ambos nodos tienen posición geográfica
        if u in pos_geo and v in pos_geo:
            edges_to_draw.append((u, v))
            edge_weights[(u, v)] = w

# Dibujar nodos (solo los que tienen coordenadas)
nx.draw_networkx_nodes(
    G,
    pos_geo,
    nodelist=list(pos_geo.keys()),
    node_size=1500,
    node_color="#1f77b4",
    ax=ax
)

# Dibujar etiquetas de nodos
nx.draw_networkx_labels(
    G,
    pos_geo,
    labels={c: c for c in pos_geo.keys()},
    font_size=10,
    font_color="white",
    ax=ax
)

# Dibujar aristas
nx.draw_networkx_edges(
    G,
    pos_geo,
    edgelist=edges_to_draw,
    width=2,
    alpha=0.8,
    ax=ax
)

# Etiquetas de pesos en las aristas
if mostrar_pesos and len(edges_to_draw) > 0:
    edge_labels_fmt = {e: f"{w:.1f}" for e, w in edge_weights.items()}
    nx.draw_networkx_edge_labels(
        G,
        pos_geo,
        edge_labels=edge_labels_fmt,
        font_size=8,
        ax=ax
    )

# Ajustar aspecto para que no se distorsione la forma
ax.set_xlabel("Longitud")
ax.set_ylabel("Latitud")
ax.set_aspect("equal", adjustable="datalim")
ax.grid(True, linestyle="--", alpha=0.4)
ax.set_title("Grafo de ciudades con posición geográfica (lon/lat)")
st.subheader("Visualización del grafo en coordenadas reales")
st.pyplot(fig)

st.markdown("""
**Notas:**
- La posición de cada nodo corresponde a su **longitud (eje X)** y **latitud (eje Y)** reales.
- El slider te permite ocultar aristas con distancia mayor a cierto umbral.
""")

# ====================================
# Búsqueda exhaustiva (TSP) usando brutef.py
# ====================================
st.sidebar.header("Búsqueda exhaustiva (TSP)")

ciudad_inicio = st.sidebar.selectbox(
    "Ciudad de inicio para el TSP",
    list(df_dist.index),
    index=0
)

if st.sidebar.button("Calcular ruta óptima (búsqueda exhaustiva)"):
    mejor_ruta, mejor_dist = tsp_exhaustivo(df_dist, ciudad_inicio=ciudad_inicio)

    st.subheader("Resultado de la búsqueda exhaustiva (TSP)")
    if mejor_ruta is not None:
        # Ruta cerrada (regresando al inicio)
        ruta_cerrada = mejor_ruta + [mejor_ruta[0]]

        st.write("**Mejor ruta encontrada:**")
        st.write(" → ".join(ruta_cerrada))
        st.write(f"**Distancia total L★:** {mejor_dist:.2f} unidades")

        # Gráfico con la mejor ruta resaltada
        fig2, ax2 = plt.subplots(figsize=(7, 7))

        # Dibujar todos los nodos
        nx.draw_networkx_nodes(
            G, pos_geo,
            nodelist=list(pos_geo.keys()),
            node_size=1500,
            node_color="#1f77b4",
            ax=ax2
        )
        nx.draw_networkx_labels(
            G, pos_geo,
            font_size=10,
            font_color="white",
            ax=ax2
        )

        # Todas las aristas en gris clarito
        nx.draw_networkx_edges(
            G, pos_geo,
            edge_color="#cccccc",
            width=1,
            alpha=0.4,
            ax=ax2
        )

        # Aristas de la mejor ruta en rojo y más gruesas
        ruta_edges = [(ruta_cerrada[i], ruta_cerrada[i+1])
                      for i in range(len(ruta_cerrada) - 1)]

        nx.draw_networkx_edges(
            G, pos_geo,
            edgelist=ruta_edges,
            width=3,
            edge_color="red",
            ax=ax2
        )

        ax2.set_xlabel("Longitud")
        ax2.set_ylabel("Latitud")
        ax2.set_aspect("equal", adjustable="datalim")
        ax2.grid(True, linestyle="--", alpha=0.4)
        ax2.set_title("Mejor ruta TSP (búsqueda exhaustiva)")
        st.pyplot(fig2)
    else:
        st.warning("No se encontró ninguna ruta. Revisa la matriz de distancias.")
    
# ====================================
# Heurística: vecino más cercano (Nearest Neighbour)
# ====================================
st.sidebar.header("Heurística: vecino más cercano")

if st.sidebar.button("Calcular ruta heurística (Nearest Neighbour)"):
    try:
        ruta_h, dist_h = nearest_neighbor(df_dist, ciudad_inicio=ciudad_inicio)
    except ValueError as e:
        st.error(str(e))
    else:
        st.subheader("Resultado de la heurística del vecino más cercano")
        ruta_cerrada_h = ruta_h + [ruta_h[0]]

        st.write("**Ruta heurística encontrada (vecino más cercano):**")
        st.write(" → ".join(ruta_cerrada_h))
        st.write(f"**Distancia total Lₕ:** {dist_h:.2f} unidades")

        # Gráfico con la ruta heurística resaltada
        fig3, ax3 = plt.subplots(figsize=(7, 7))

        # Dibujar todos los nodos
        nx.draw_networkx_nodes(
            G, pos_geo,
            nodelist=list(pos_geo.keys()),
            node_size=1500,
            node_color="#1f77b4",
            ax=ax3
        )
        nx.draw_networkx_labels(
            G, pos_geo,
            font_size=10,
            font_color="white",
            ax=ax3
        )

        # Todas las aristas en gris clarito
        nx.draw_networkx_edges(
            G, pos_geo,
            edge_color="#cccccc",
            width=1,
            alpha=0.4,
            ax=ax3
        )

        # Aristas de la ruta heurística en otro color (por ejemplo, verde)
        ruta_edges_h = [
            (ruta_cerrada_h[i], ruta_cerrada_h[i+1])
            for i in range(len(ruta_cerrada_h) - 1)
        ]

        nx.draw_networkx_edges(
            G, pos_geo,
            edgelist=ruta_edges_h,
            width=3,
            edge_color="green",
            ax=ax3
        )

        ax3.set_xlabel("Longitud")
        ax3.set_ylabel("Latitud")
        ax3.set_aspect("equal", adjustable="datalim")
        ax3.grid(True, linestyle="--", alpha=0.4)
        ax3.set_title("Ruta TSP heurística (vecino más cercano)")
        st.pyplot(fig3)

# ====================================
# Animación automática de la búsqueda exhaustiva
# ====================================
st.sidebar.header("Animación automática (exhaustivo)")

activar_anim = st.sidebar.checkbox("Activar animación automática")

velocidad = st.sidebar.slider(
    "Velocidad (segundos entre pasos)",
    min_value=0.1,
    max_value=2.0,
    value=0.5,
    step=0.1
)

iniciar_anim = st.sidebar.button("Iniciar animación")

if activar_anim and iniciar_anim:
    try:
        rutas = get_rutas_exhaustivas(df_dist, ciudad_inicio)
    except ValueError as e:
        st.error(str(e))
    else:
        num_pasos = len(rutas)

        st.subheader("Animación de la búsqueda exhaustiva")
        st.write(
            f"Total de rutas evaluadas (ciclos Hamiltonianos con ciudad de inicio fija): "
            f"**{num_pasos}**"
        )

        # Placeholder para ir sobreescribiendo el contenido en cada frame
        placeholder = st.empty()

        mejor_hasta_ahora = None
        mejor_dist_hasta_ahora = float("inf")

        for k, (ruta_actual, dist_actual) in enumerate(rutas, start=1):
            # Actualizar mejor ruta hasta este paso
            if dist_actual < mejor_dist_hasta_ahora:
                mejor_dist_hasta_ahora = dist_actual
                mejor_hasta_ahora = ruta_actual

            ruta_cerrada_actual = ruta_actual + [ruta_actual[0]]
            ruta_cerrada_mejor = mejor_hasta_ahora + [mejor_hasta_ahora[0]]

            with placeholder.container():
                st.markdown(f"### Paso {k} / {num_pasos}")
                st.markdown(
                    f"- **Ruta actual:** {' → '.join(ruta_cerrada_actual)}  \n"
                    f"- **Distancia ruta actual:** `{dist_actual:.2f}`  \n"
                    f"- **Mejor distancia hasta ahora L★(k):** `{mejor_dist_hasta_ahora:.2f}`  \n"
                    f"- **Mejor ruta hasta ahora:** {' → '.join(ruta_cerrada_mejor)}"
                )

                # Figura animada
                fig_anim, ax_anim = plt.subplots(figsize=(7, 7))

                # Nodos
                nx.draw_networkx_nodes(
                    G, pos_geo,
                    nodelist=list(pos_geo.keys()),
                    node_size=1500,
                    node_color="#1f77b4",
                    ax=ax_anim
                )
                nx.draw_networkx_labels(
                    G, pos_geo,
                    font_size=10,
                    font_color="white",
                    ax=ax_anim
                )

                # Aristas de fondo en gris
                nx.draw_networkx_edges(
                    G, pos_geo,
                    edge_color="#cccccc",
                    width=1,
                    alpha=0.4,
                    ax=ax_anim
                )

                # Mejor ruta hasta ahora en rojo
                edges_mejor = [
                    (ruta_cerrada_mejor[i], ruta_cerrada_mejor[i+1])
                    for i in range(len(ruta_cerrada_mejor) - 1)
                ]
                nx.draw_networkx_edges(
                    G, pos_geo,
                    edgelist=edges_mejor,
                    width=3,
                    edge_color="red",
                    alpha=0.8,
                    ax=ax_anim
                )

                # Ruta actual en naranjo punteado
                edges_actual = [
                    (ruta_cerrada_actual[i], ruta_cerrada_actual[i+1])
                    for i in range(len(ruta_cerrada_actual) - 1)
                ]
                nx.draw_networkx_edges(
                    G, pos_geo,
                    edgelist=edges_actual,
                    width=3,
                    edge_color="orange",
                    alpha=0.9,
                    style="dashed",
                    ax=ax_anim
                )

                ax_anim.set_xlabel("Longitud")
                ax_anim.set_ylabel("Latitud")
                ax_anim.set_aspect("equal", adjustable="datalim")
                ax_anim.grid(True, linestyle="--", alpha=0.4)
                ax_anim.set_title("Búsqueda exhaustiva: ruta actual vs mejor hasta ahora")
                st.pyplot(fig_anim)

            time.sleep(velocidad)
