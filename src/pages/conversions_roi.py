import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_conversions_data
from src.components.sidebar import mostrar_sidebar_variables, mostrar_filtros_fecha

def main():
    """Página principal para análisis de conversiones y ROI"""
    
    # Configurar la página
    st.set_page_config(
        page_title="Conversions & ROI - Marketing Dashboard",
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
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>💰 CONVERSIONS & ROI</h1>
        <p style='color: #9CA3AF; font-size: 1rem;'>Análisis de conversiones, ROI y métricas de marketing</p>
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
            
            # Obtener datos de conversiones
            conversions_data = get_conversions_data(
                client=client,
                property_id="381346600",
                start_date=start_date,
                end_date=end_date
            )
            
            conversions_df = conversions_data['conversions']
            events_df = conversions_data['events']
            trends_df = conversions_data['trends']
            
            if conversions_df.empty:
                st.warning("⚠️ No se encontraron datos de conversiones para el rango de fechas seleccionado")
                return
            
            # Calcular KPIs principales de conversión
            total_conversions = conversions_df['conversions'].sum() if 'conversions' in conversions_df.columns else 0
            total_revenue = conversions_df['totalRevenue'].sum() if 'totalRevenue' in conversions_df.columns else 0
            total_sessions = conversions_df['sessions'].sum() if 'sessions' in conversions_df.columns else 0
            conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0
            
            # KPIs principales de conversión
            st.markdown("### 📊 Conversion KPIs")
            
            # Crear columnas para KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Conversions",
                    value=f"{total_conversions:,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Conversion Rate",
                    value=f"{conversion_rate:.2f}%",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="Total Revenue",
                    value=f"€{total_revenue:,.2f}",
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Revenue per Session",
                    value=f"€{total_revenue/total_sessions:.2f}" if total_sessions > 0 else "€0.00",
                    delta=None
                )
            
            st.markdown("---")
            
            # Análisis de conversiones por canal
            st.markdown("### 📈 Conversion by Channel")
            
            if 'sessionDefaultChannelGrouping' in conversions_df.columns:
                channel_conversions = conversions_df.groupby('sessionDefaultChannelGrouping').agg({
                    'conversions': 'sum',
                    'totalRevenue': 'sum',
                    'sessions': 'sum',
                    'totalUsers': 'sum'
                }).reset_index()
                
                # Calcular tasa de conversión por canal
                channel_conversions['conversion_rate'] = (channel_conversions['conversions'] / channel_conversions['sessions'] * 100)
                channel_conversions = channel_conversions.sort_values('conversions', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de barras para conversiones por canal
                    fig_channels = px.bar(
                        channel_conversions.head(8),
                        x='conversions',
                        y='sessionDefaultChannelGrouping',
                        orientation='h',
                        title="Conversions by Marketing Channel",
                        color='conversions',
                        color_continuous_scale='Blues'
                    )
                    
                    fig_channels.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        title_font_color='white',
                        height=400
                    )
                    
                    st.plotly_chart(fig_channels, use_container_width=True)
                
                with col2:
                    st.dataframe(
                        channel_conversions.head(8),
                        use_container_width=True,
                        hide_index=True
                    )
            
            # Análisis de eventos de conversión
            st.markdown("### 🎯 Conversion Events")
            
            if not events_df.empty and 'eventName' in events_df.columns:
                # Filtrar eventos relacionados con conversiones
                conversion_events = events_df[events_df['eventName'].str.contains('conversion|purchase|checkout|signup|contact', case=False, na=False)]
                
                if not conversion_events.empty:
                    conversion_events = conversion_events.sort_values('eventCount', ascending=False)
                    
                    fig_events = px.bar(
                        conversion_events.head(6),
                        x='eventCount',
                        y='eventName',
                        orientation='h',
                        title="Top Conversion Events",
                        color='eventCount',
                        color_continuous_scale='Reds'
                    )
                    
                    fig_events.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        title_font_color='white',
                        height=300
                    )
                    
                    st.plotly_chart(fig_events, use_container_width=True)
                else:
                    st.info("No se encontraron eventos específicos de conversión en los datos.")
            
            # Análisis de tendencias de conversión
            st.markdown("### 📊 Conversion Trends")
            
            if not trends_df.empty and 'date' in trends_df.columns:
                trends_df['date'] = pd.to_datetime(trends_df['date'])
                
                # Gráfico de líneas para tendencias
                fig_trends = px.line(
                    trends_df,
                    x='date',
                    y=['conversions', 'totalRevenue'],
                    title="Daily Conversion & Revenue Trends",
                    color_discrete_sequence=['#10B981', '#FFD700']
                )
                
                fig_trends.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white'
                )
                
                st.plotly_chart(fig_trends, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error obteniendo datos de conversiones: {str(e)}")
    
    else:
        st.warning("⚠️ No hay filtros de fecha configurados. Configura las fechas en el sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Marketing Dashboard - Conversions & ROI Analysis</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)
