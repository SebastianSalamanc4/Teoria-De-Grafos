from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

from tsp.instances import (
    crear_instancia_desde_dataframe,
    InstanciaTSP,
)
from tsp.distances import asignar_matriz_a_instancia
from tsp.bruteforce import resolver_exhaustivo
from tsp.heuristics import vecino_mas_cercano


# ---------------------------------------------------------
# CONFIGURACIÓN BÁSICA DE LA PÁGINA
# ---------------------------------------------------------

st.set_page_config(
    page_title="TSP en Chile - Optimización de Rutas",
    layout="wide",
    page_icon="🗺️",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS
# ---------------------------------------------------------



# ---------------------------------------------------------
# RUTAS Y CARGA DE DATOS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

@st.cache_data
def cargar_instancia_desde_archivo(nombre_archivo: str) -> InstanciaTSP:
    """
    Carga un CSV desde la carpeta data/ y lo convierte en InstanciaTSP.
    """
    try:
        ruta_csv = DATA_DIR / nombre_archivo
        df = pd.read_csv(ruta_csv)

        # Normalizar nombres de columnas
        columnas = {c.lower(): c for c in df.columns}
        if {"ciudad", "lat", "lon"}.issubset({c.lower() for c in df.columns}):
            df = df.rename(columns={
                columnas["ciudad"]: "Ciudad",
                columnas["lat"]: "Latitud",
                columnas["lon"]: "Longitud",
            })

        instancia = crear_instancia_desde_dataframe(df)
        return instancia
    except Exception as e:
        st.error(f"Error cargando el archivo: {e}")
        return None

# ---------------------------------------------------------
# FUNCIONES MEJORADAS PARA MAPA
# ---------------------------------------------------------

def crear_mapa_interactivo(instancia: InstanciaTSP, rutas: dict = None) -> folium.Map:
    """Crea un mapa interactivo mejorado con múltiples rutas."""
    lats = [coord[0] for coord in instancia.coordenadas.values()]
    lons = [coord[1] for coord in instancia.coordenadas.values()]
    centro = (sum(lats) / len(lats), sum(lons) / len(lons))

    mapa = folium.Map(
        location=centro, 
        zoom_start=6,
        tiles='OpenStreetMap',
        width='100%',
        height=600
    )

    # Configuración de colores para diferentes rutas
    colores_rutas = {
        'óptima': {'color': '#FF4B4B', 'peso': 6, 'opacidad': 0.9},
        'heurística': {'color': '#4B78FF', 'peso': 5, 'opacidad': 0.7},
        'comparación': {'color': '#00D4AA', 'peso': 4, 'opacidad': 0.6}
    }

    # Añadir marcadores de ciudades con iconos personalizados
    for ciudad, (lat, lon) in instancia.coordenadas.items():
        folium.Marker(
            location=(lat, lon),
            popup=folium.Popup(f"<b>{ciudad}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}", max_width=200),
            tooltip=ciudad,
            icon=folium.Icon(color='red', icon='map-marker', prefix='fa')
        ).add_to(mapa)

    # Dibujar rutas si están disponibles
    if rutas:
        for nombre_ruta, datos_ruta in rutas.items():
            if datos_ruta['ruta']:
                color_config = colores_rutas.get(nombre_ruta, {'color': '#000000', 'peso': 3, 'opacidad': 0.7})
                puntos = [(instancia.coordenadas[c][0], instancia.coordenadas[c][1]) for c in datos_ruta['ruta']]
                
                # Cerrar el ciclo
                if len(puntos) > 1:
                    puntos.append(puntos[0])
                
                folium.PolyLine(
                    locations=puntos,
                    color=color_config['color'],
                    weight=color_config['peso'],
                    opacity=color_config['opacidad'],
                    tooltip=f"{datos_ruta['nombre']} - {datos_ruta['distancia']:.2f} km",
                    popup=folium.Popup(f"<b>{datos_ruta['nombre']}</b><br>Distancia: {datos_ruta['distancia']:.2f} km", max_width=300)
                ).add_to(mapa)

    # Añadir control de capas
    folium.LayerControl().add_to(mapa)
    
    return mapa

# ---------------------------------------------------------
# FUNCIONES DE VISUALIZACIÓN DE DATOS
# ---------------------------------------------------------

def crear_grafico_comparacion(dist_optima: float, dist_nn: float, tiempo_optimo: float, tiempo_nn: float):
    """Crea gráficos de comparación entre métodos."""
    fig = go.Figure()
    
    # Gráfico de distancias
    fig.add_trace(go.Bar(
        x=['Óptimo', 'Vecino Más Cercano'],
        y=[dist_optima, dist_nn],
        name='Distancia (km)',
        marker_color=['#00CC96', '#FFA15A'],
        text=[f'{dist_optima:.2f} km', f'{dist_nn:.2f} km'],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Comparación de Distancias de Ruta',
        yaxis_title='Distancia (km)',
        showlegend=False
    )
    
    return fig

def crear_grafico_tiempos(tiempo_optimo: float, tiempo_nn: float):
    """Crea gráfico de comparación de tiempos."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Óptimo', 'Vecino Más Cercano'],
        y=[tiempo_optimo, tiempo_nn],
        name='Tiempo (s)',
        marker_color=['#EF553B', '#636EFA'],
        text=[f'{tiempo_optimo:.4f} s', f'{tiempo_nn:.4f} s'],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Comparación de Tiempos de Ejecución',
        yaxis_title='Tiempo (segundos)',
        showlegend=False
    )
    
    return fig

# ---------------------------------------------------------
# COMPONENTES DE INTERFAZ
# ---------------------------------------------------------

def mostrar_metricas_principales(dist_optima: float, dist_nn: float, tiempo_optimo: float, tiempo_nn: float, gap: float = None):
    """Muestra métricas principales en formato de tarjetas."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Distancia Óptima</div>
            <div class="metric-value">{dist_optima:.2f} km</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Distancia Heurística</div>
            <div class="metric-value">{dist_nn:.2f} km</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tiempo Heurístico</div>
            <div class="metric-value">{tiempo_nn:.4f} s</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if gap is not None:
            color = "#FF4B4B" if gap > 5 else "#00CC96"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Gap de Optimalidad</div>
                <div class="metric-value" style="color: {color}">{gap:.2f} %</div>
            </div>
            """, unsafe_allow_html=True)

def mostrar_detalle_ruta(ruta: list[str], distancia: float, nombre: str):
    """Muestra el detalle de una ruta específica."""
    st.markdown(f"""
    <div class="route-card">
        <h4>{nombre}</h4>
        <p><strong>Ruta:</strong> {' → '.join(ruta)} → {ruta[0]}</p>
        <p><strong>Distancia total:</strong> {distancia:.2f} km</p>
        <p><strong>Número de ciudades:</strong> {len(ruta)}</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIÓN AUXILIAR (mantener del código original)
# ---------------------------------------------------------

def construir_tabla_aristas(matriz: pd.DataFrame, ruta: list[str]) -> pd.DataFrame:
    filas = []
    n = len(ruta)
    for i in range(n):
        origen = ruta[i]
        destino = ruta[(i + 1) % n]  # siguiente, cerrando ciclo
        distancia = float(matriz.loc[origen, destino])
        filas.append(
            {
                "Desde": origen,
                "Hasta": destino,
                "Distancia (km)": distancia,
            }
        )
    return pd.DataFrame(filas)

# ---------------------------------------------------------
# INTERFAZ PRINCIPAL MEJORADA
# ---------------------------------------------------------

def main():
    # Header principal mejorado
    st.markdown('<h1 class="main-header">🗺️ Optimizador de Rutas TSP - Chile</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <p style='font-size: 1.2rem; color: #666;'>
        Resuelve el Problema del Viajante (TSP) para ciudades de Chile usando diferentes algoritmos de optimización.
        Visualiza las rutas óptimas y compara métodos en tiempo real.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar mejorado
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        
        st.markdown("### Selección de Instancia")
        opciones_archivos = ["SeisCiudadesDeChile.csv"]
        archivo_seleccionado = st.selectbox(
            "Archivo de datos:",
            options=opciones_archivos,
            help="Selecciona el conjunto de ciudades a analizar"
        )
        
        st.markdown("### Parámetros del Algoritmo")
        metodo = st.radio(
            "Método de solución:",
            options=["Exhaustivo", "Vecino Más Cercano", "Comparar ambos"],
            help="Selecciona el método de resolución del problema TSP"
        )
        
        # Cargar instancia
        instancia = cargar_instancia_desde_archivo(archivo_seleccionado)
        
        if instancia is None:
            st.error("No se pudo cargar la instancia. Verifica que el archivo exista en la carpeta data/")
            return
            
        asignar_matriz_a_instancia(instancia)
        
        ciudad_inicio = st.selectbox(
            "Ciudad de inicio:",
            options=instancia.ciudades,
            index=0,
            help="Ciudad desde donde comienza el recorrido"
        )
        
        # Información de la instancia en sidebar
        st.markdown("### 📊 Información de la Instancia")
        st.info(f"""
        **Ciudades cargadas:** {len(instancia.ciudades)}
        **Archivo:** {archivo_seleccionado}
        **Origen:** {ciudad_inicio}
        """)
    
    # Contenido principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🗾 Mapa de Rutas")
        
        # Mostrar información de ciudades
        with st.expander("📋 Ver lista de ciudades", expanded=True):
            df_ciudades = pd.DataFrame([
                {
                    "Ciudad": c,
                    "Latitud": instancia.coordenadas[c][0],
                    "Longitud": instancia.coordenadas[c][1],
                }
                for c in instancia.ciudades
            ])
            st.dataframe(df_ciudades, use_container_width=True, height=200)
    
    with col2:
        st.markdown("## 📈 Métricas Rápidas")
    
    # Cálculo automático de rutas (sin botón)
    with st.spinner('🔄 Calculando rutas optimizadas...'):
        # Inicializar variables
        ruta_optima, dist_optima, tiempo_optimo = None, None, None
        ruta_nn, dist_nn, tiempo_nn = None, None, None

        """
        Variables resultantes:
         π* --> ruta_optima
         L* --> dist_optima
         π^NN --> ruta_nn
         L^NN --> dist_nn
            
        """
        
        # Ejecutar algoritmos según selección
        if metodo in ["Exhaustivo", "Comparar ambos"]:
            try:
                t0 = time.perf_counter() # Inicio temporizador
                ruta_optima, dist_optima = resolver_exhaustivo(instancia.matriz_distancias, ciudad_inicio)  # # Método exhaustivo (π* y L*)
                tiempo_optimo = time.perf_counter() - t0 # Fin temporizador 
            except Exception as e:
                st.error(f"Error en método exhaustivo: {e}")
        
        if metodo in ["Vecino Más Cercano", "Comparar ambos"]:
            try:
                t0 = time.perf_counter()
                ruta_nn, dist_nn = vecino_mas_cercano(instancia.matriz_distancias, ciudad_inicio) # # Heurística Vecino Más Cercano (π^NN y L^NN)
                tiempo_nn = time.perf_counter() - t0
            except Exception as e:
                st.error(f"Error en método vecino más cercano: {e}")
        
        # Calcular gap si es necesario
        gap = None
        if ruta_optima and ruta_nn and dist_optima > 0:
            gap = ((dist_nn - dist_optima) / dist_optima) * 100.0 # gap = ((L^NN - L*) / L*) * 100%
    
    # Mostrar estado de cálculo
    st.markdown("""
    <div class="success-box">
        <h4>✅ Cálculos completados automáticamente</h4>
        <p>Los resultados se actualizan en tiempo real según los parámetros seleccionados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Actualizar métricas en col2
    with col2:
        if ruta_optima or ruta_nn:
            dist_opt_display = dist_optima if dist_optima else 0
            dist_nn_display = dist_nn if dist_nn else 0
            tiempo_opt_display = tiempo_optimo if tiempo_optimo else 0
            tiempo_nn_display = tiempo_nn if tiempo_nn else 0
            
            mostrar_metricas_principales(
                dist_opt_display, dist_nn_display, 
                tiempo_opt_display, tiempo_nn_display, gap
            )
    
    # Pestañas para organización de contenido
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Mapa Interactivo", "📊 Resultados Detallados", "📈 Análisis Comparativo", "📋 Datos de la Instancia"])
    
    with tab1:
        st.markdown("### Visualización de Rutas en Mapa")
        
        # Preparar datos de rutas para el mapa
        rutas_para_mapa = {}
        if ruta_optima and dist_optima:
            rutas_para_mapa['óptima'] = {
                'ruta': ruta_optima,
                'nombre': 'Ruta Óptima (Exhaustivo)',
                'distancia': dist_optima
            }
        if ruta_nn and dist_nn:
            rutas_para_mapa['heurística'] = {
                'ruta': ruta_nn,
                'nombre': 'Ruta Heurística (Vecino Más Cercano)',
                'distancia': dist_nn
            }
        
        # Crear y mostrar mapa
        mapa = crear_mapa_interactivo(instancia, rutas_para_mapa)
        st_folium(mapa, use_container_width=True, height=600)
        
        # Leyenda del mapa
        st.markdown("""
        **Leyenda del mapa:**
        - 🔴 **Marcadores rojos**: Ciudades
        - 🟥 **Línea roja**: Ruta óptima (método exhaustivo)
        - 🟦 **Línea azul**: Ruta heurística (vecino más cercano)
        """)
    
    with tab2:
        st.markdown("### 📋 Detalles de las Rutas Calculadas")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            if ruta_optima and dist_optima:
                mostrar_detalle_ruta(ruta_optima, dist_optima, "Ruta Óptima - Método Exhaustivo")
                
                with st.expander("📊 Ver tabla de aristas - Ruta Óptima"):
                    df_aristas_opt = construir_tabla_aristas(instancia.matriz_distancias, ruta_optima)
                    st.dataframe(
                        df_aristas_opt.style.format({"Distancia (km)": "{:.2f}"}),
                        use_container_width=True
                    )
            else:
                st.info("Selecciona 'Exhaustivo' o 'Comparar ambos' para ver la ruta óptima")
        
        with col_res2:
            if ruta_nn and dist_nn:
                mostrar_detalle_ruta(ruta_nn, dist_nn, "Ruta Heurística - Vecino Más Cercano")
                
                with st.expander("📊 Ver tabla de aristas - Ruta Heurística"):
                    df_aristas_nn = construir_tabla_aristas(instancia.matriz_distancias, ruta_nn)
                    st.dataframe(
                        df_aristas_nn.style.format({"Distancia (km)": "{:.2f}"}),
                        use_container_width=True
                    )
            else:
                st.info("Selecciona 'Vecino Más Cercano' o 'Comparar ambos' para ver la ruta heurística")
    
    with tab3:
        st.markdown("### 📈 Análisis Comparativo")
        
        if metodo == "Comparar ambos" and ruta_optima and ruta_nn and dist_optima and dist_nn:
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                fig_dist = crear_grafico_comparacion(dist_optima, dist_nn, tiempo_optimo, tiempo_nn)
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col_graf2:
                fig_tiempo = crear_grafico_tiempos(tiempo_optimo, tiempo_nn)
                st.plotly_chart(fig_tiempo, use_container_width=True)
            
            # Análisis de eficiencia
            st.markdown("### 📊 Análisis de Eficiencia")
            if tiempo_nn > 0:
                eficiencia_relativa = (tiempo_optimo / tiempo_nn) 
            else:
                eficiencia_relativa = float('inf')
            
            col_eff1, col_eff2, col_eff3 = st.columns(3)
            
            with col_eff1:
                if tiempo_nn > 0:
                    st.metric("Velocidad relativa", f"{eficiencia_relativa:.1f}x", 
                             delta=f"{eficiencia_relativa-1:.1f}x más rápido" if eficiencia_relativa > 1 else f"{1-eficiencia_relativa:.1f}x más lento")
                else:
                    st.metric("Velocidad relativa", "N/A")
            
            with col_eff2:
                if dist_optima and dist_nn:
                    diferencia_distancia = dist_nn - dist_optima
                    st.metric("Diferencia en distancia", f"{diferencia_distancia:.2f} km", 
                             delta=f"{gap:.2f}%" if gap else "N/A")
            
            with col_eff3:
                if dist_nn and dist_optima:
                    st.metric("Reducción posible", f"{(diferencia_distancia/dist_nn)*100:.2f}%", 
                             delta="Mejora potencial")
        
        else:
            st.info("Selecciona 'Comparar ambos' métodos para ver el análisis comparativo completo.")
    
    with tab4:
        st.markdown("### 📋 Datos Completos de la Instancia")
        
        col_data1, col_data2 = st.columns(2)
        
        with col_data1:
            st.markdown("#### Matriz de Distancias")
            st.dataframe(
                instancia.matriz_distancias.style.format("{:.2f}").background_gradient(cmap='Blues'),
                use_container_width=True,
                height=400
            )
        
        with col_data2:
            st.markdown("#### Estadísticas Descriptivas")
            
            # Calcular estadísticas de la matriz de distancias
            distancias_values = instancia.matriz_distancias.values.flatten()
            distancias_values = distancias_values[distancias_values > 0]  # Excluir ceros (diagonal)
            
            if len(distancias_values) > 0:
                stats_df = pd.DataFrame({
                    'Estadística': ['Mínima', 'Máxima', 'Promedio', 'Desviación Estándar'],
                    'Valor (km)': [
                        f"{distancias_values.min():.2f}",
                        f"{distancias_values.max():.2f}",
                        f"{distancias_values.mean():.2f}",
                        f"{distancias_values.std():.2f}"
                    ]
                })
                
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Mostrar información de la ruta calculada
            st.markdown("#### Resumen de Ejecución")
            info_text = []
            if ruta_optima:
                info_text.append(f"✅ **Ruta óptima encontrada** ({len(ruta_optima)} ciudades)")
                info_text.append(f"⏱️ Tiempo exhaustivo: {tiempo_optimo:.4f}s")
            if ruta_nn:
                info_text.append(f"✅ **Ruta heurística encontrada** ({len(ruta_nn)} ciudades)")
                info_text.append(f"⏱️ Tiempo heurístico: {tiempo_nn:.4f}s")
            
            if info_text:
                st.info("\n\n".join(info_text))
            else:
                st.info("No se han calculado rutas. Ajusta los parámetros en el sidebar.")

# ---------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------------------------------------

if __name__ == "__main__":
    main()