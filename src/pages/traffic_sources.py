import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_traffic_sources_data
from src.components.sidebar import mostrar_sidebar_variables, mostrar_filtros_fecha

def main():
    """Página principal para análisis de fuentes de tráfico"""
    
    # Configurar la página
    st.set_page_config(
        page_title="Traffic Sources - Marketing Dashboard",
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
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>🚀 TRAFFIC SOURCES</h1>
        <p style='color: #9CA3AF; font-size: 1rem;'>Análisis de fuentes de tráfico y canales de adquisición</p>
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
            
            # Obtener datos de fuentes de tráfico
            traffic_data = get_traffic_sources_data(
                client=client,
                property_id="381346600",
                start_date=start_date,
                end_date=end_date
            )
            
            if traffic_data.empty:
                st.warning("⚠️ No se encontraron datos de fuentes de tráfico para el rango de fechas seleccionado")
                return
            
            # Calcular KPIs principales de tráfico
            total_sessions = traffic_data['sessions'].sum() if 'sessions' in traffic_data.columns else 0
            total_users = traffic_data['totalUsers'].sum() if 'totalUsers' in traffic_data.columns else 0
            new_users = traffic_data['newUsers'].sum() if 'newUsers' in traffic_data.columns else 0
            avg_bounce_rate = traffic_data['bounceRate'].mean() if 'bounceRate' in traffic_data.columns else 0
            avg_session_duration = traffic_data['averageSessionDuration'].mean() if 'averageSessionDuration' in traffic_data.columns else 0
            
            # KPIs principales de tráfico
            st.markdown("### 📊 Traffic KPIs")
            
            # Crear columnas para KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Sessions",
                    value=f"{total_sessions:,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Total Users",
                    value=f"{total_users:,}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="New Users",
                    value=f"{new_users:,}",
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Avg Bounce Rate",
                    value=f"{avg_bounce_rate:.1f}%",
                    delta=None
                )
            
            st.markdown("---")
            
            # Gráfico de fuentes de tráfico
            st.markdown("### 🌐 Traffic Sources Overview")
            
            # Preparar datos para el gráfico
            if 'sessionDefaultChannelGrouping' in traffic_data.columns:
                channel_data = traffic_data.groupby('sessionDefaultChannelGrouping').agg({
                    'sessions': 'sum',
                    'totalUsers': 'sum',
                    'bounceRate': 'mean'
                }).reset_index()
                
                channel_data = channel_data.sort_values('sessions', ascending=True)
                
                # Gráfico de barras para sesiones por canal
                fig_sessions = px.bar(
                    channel_data, 
                    x='sessions', 
                    y='sessionDefaultChannelGrouping', 
                    orientation='h',
                    title="Sessions by Traffic Channel",
                    color='sessions',
                    color_continuous_scale='Viridis'
                )
                
                fig_sessions.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white'
                )
                
                st.plotly_chart(fig_sessions, use_container_width=True)
            
            # Tabla detallada de fuentes de tráfico
            st.markdown("### 📋 Detailed Traffic Sources")
            
            # Mostrar tabla con datos reales
            display_columns = ['sessionSource', 'sessionMedium', 'sessionDefaultChannelGrouping', 'sessions', 'totalUsers', 'bounceRate']
            available_columns = [col for col in display_columns if col in traffic_data.columns]
            
            if available_columns:
                st.dataframe(
                    traffic_data[available_columns].sort_values('sessions', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.dataframe(
                    traffic_data.sort_values('sessions', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            
            # Gráfico de tendencias temporales (si hay datos de fecha)
            if 'date' in traffic_data.columns:
                st.markdown("### 📈 Traffic Trends Over Time")
                
                # Agregar datos por fecha
                daily_traffic = traffic_data.groupby('date').agg({
                    'sessions': 'sum',
                    'totalUsers': 'sum',
                    'newUsers': 'sum'
                }).reset_index()
                
                daily_traffic['date'] = pd.to_datetime(daily_traffic['date'])
                
                fig_trends = px.line(
                    daily_traffic,
                    x='date',
                    y=['sessions', 'totalUsers'],
                    title="Daily Traffic Trends",
                    color_discrete_sequence=['#10B981', '#3B82F6']
                )
                
                fig_trends.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white'
                )
                
                st.plotly_chart(fig_trends, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error obteniendo datos de fuentes de tráfico: {str(e)}")
    
    else:
        st.warning("⚠️ No hay filtros de fecha configurados. Configura las fechas en el sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Marketing Dashboard - Traffic Sources Analysis</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)
