import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_content_performance_data
from src.components.sidebar import mostrar_sidebar_variables, mostrar_filtros_fecha

def main():
    """Página principal para análisis de rendimiento de contenido"""
    
    # Configurar la página
    st.set_page_config(
        page_title="Content Performance - Marketing Dashboard",
       page_icon="src/assets/G I D.jpg",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS para diseño mejorado con fondo negro completo
    st.markdown("""
    <style>
    /* Fondo negro para toda la página */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Fondo negro para el contenido principal */
    .main {
        background-color: #000000 !important;
    }
    
    /* Contenedor principal también negro */
    .main .block-container {
        background-color: #000000 !important;
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: none;
    }
    
    .stImage {
        background: transparent;
    }
    
    .stButton > button {
        background: #2E4543 !important;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2E4543 0%, #3A5A58 50%, #4A7C7A 100%) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar sidebar avanzado
    mostrar_sidebar_variables()
    mostrar_filtros_fecha()
    
    # Título de la página
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>📝 CONTENT PERFORMANCE</h1>
        <p style='color: #9CA3AF; font-size: 1rem;'>Análisis de rendimiento de contenido y páginas más visitadas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar si hay datos disponibles
    if "fecha_inicio" in st.session_state and "fecha_fin" in st.session_state:
        fecha_inicio = st.session_state["fecha_inicio"]
        fecha_fin = st.session_state["fecha_fin"]
        
        # Convertir fechas a string para la API
        start_date = fecha_inicio.strftime("%Y-%m-%d")
        end_date = fecha_fin.strftime("%Y-%m-%d")
        
        try:
            # Cargar credenciales y cliente
            credentials = load_credentials()
            client = initialize_analytics_client(credentials)
            
            # Obtener datos de rendimiento de contenido
            content_data = get_content_performance_data(
                client=client,
                property_id="381346600",
                start_date=start_date,
                end_date=end_date
            )
            
            if content_data.empty:
                st.warning("⚠️ No se encontraron datos de contenido para el rango de fechas seleccionado")
                return
            
            # Calcular KPIs principales de contenido
            total_page_views = content_data['screenPageViews'].sum() if 'screenPageViews' in content_data.columns else 0
            total_users = content_data['totalUsers'].sum() if 'totalUsers' in content_data.columns else 0
            avg_time_on_page = content_data['averageSessionDuration'].mean() if 'averageSessionDuration' in content_data.columns else 0
            avg_bounce_rate = content_data['bounceRate'].mean() if 'bounceRate' in content_data.columns else 0
            
            # KPIs principales de contenido
            st.markdown("### 📊 Content KPIs")
            
            # Crear columnas para KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Page Views",
                    value=f"{total_page_views:,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Total Users",
                    value=f"{total_users:,}",
                    delta=None
                )
            
            with col3:
                # Formatear tiempo en minutos y segundos
                minutes = int(avg_time_on_page // 60)
                seconds = int(avg_time_on_page % 60)
                time_str = f"{minutes}m {seconds}s"
                st.metric(
                    label="Avg Time on Page",
                    value=time_str,
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Avg Bounce Rate",
                    value=f"{avg_bounce_rate:.1f}%",
                    delta=None
                )
            
            st.markdown("---")
            
            # Top Pages con métricas detalladas
            st.markdown("### 🏆 Top Performing Pages")
            
            # Preparar datos para mostrar
            if 'pageTitle' in content_data.columns:
                # Agrupar por página y calcular métricas
                page_metrics = content_data.groupby('pageTitle').agg({
                    'screenPageViews': 'sum',
                    'totalUsers': 'sum',
                    'newUsers': 'sum',
                    'bounceRate': 'mean',
                    'averageSessionDuration': 'mean'
                }).reset_index()
                
                page_metrics = page_metrics.sort_values('screenPageViews', ascending=False)
                
                # Mostrar tabla con datos reales
                st.dataframe(
                    page_metrics.head(10),  # Top 10 páginas
                    use_container_width=True,
                    hide_index=True
                )
                
                # Gráfico de barras para page views
                st.markdown("### 📈 Top Pages by Views")
                
                fig_pages = px.bar(
                    page_metrics.head(8),  # Top 8 páginas
                    x='screenPageViews',
                    y='pageTitle',
                    orientation='h',
                    title="Top 8 Pages by Views",
                    color='screenPageViews',
                    color_continuous_scale='Blues'
                )
                
                fig_pages.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white',
                    height=400
                )
                
                st.plotly_chart(fig_pages, use_container_width=True)
            
            # Análisis de contenido más engaging
            st.markdown("### ⏱️ Most Engaging Content")
            
            if 'averageSessionDuration' in content_data.columns and 'pageTitle' in content_data.columns:
                # Filtrar contenido con mayor tiempo de engagement
                engaging_content = content_data.groupby('pageTitle').agg({
                    'averageSessionDuration': 'mean',
                    'screenPageViews': 'sum',
                    'totalUsers': 'sum'
                }).reset_index()
                
                engaging_content = engaging_content.sort_values('averageSessionDuration', ascending=False)
                
                fig_engaging = px.bar(
                    engaging_content.head(5),
                    x='averageSessionDuration',
                    y='pageTitle',
                    orientation='h',
                    title="Top 5 Most Engaging Pages",
                    color='averageSessionDuration',
                    color_continuous_scale='Greens'
                )
                
                fig_engaging.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white',
                    height=300
                )
                
                st.plotly_chart(fig_engaging, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error obteniendo datos de rendimiento de contenido: {str(e)}")
    
    else:
        st.warning("⚠️ No hay filtros de fecha configurados. Configura las fechas en el sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Marketing Dashboard - Content Performance Analysis</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)
