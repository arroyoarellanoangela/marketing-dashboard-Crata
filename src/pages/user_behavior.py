import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_user_behavior_data
from src.components.sidebar import mostrar_sidebar_variables, mostrar_filtros_fecha

def main():
    """Página principal para análisis de comportamiento de usuarios"""
    
    # Configurar la página
    st.set_page_config(
        page_title="User Behavior - Marketing Dashboard",
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
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>👥 USER BEHAVIOR</h1>
        <p style='color: #9CA3AF; font-size: 1rem;'>Análisis de comportamiento y engagement de usuarios</p>
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
            
            # Obtener datos de comportamiento de usuarios
            behavior_data = get_user_behavior_data(
                client=client,
                property_id="381346600",
                start_date=start_date,
                end_date=end_date
            )
            
            # Calcular KPIs principales de comportamiento
            users_df = behavior_data['users']
            devices_df = behavior_data['devices']
            geo_df = behavior_data['geo']
            hours_df = behavior_data['hours']
            
            if users_df.empty:
                st.warning("⚠️ No se encontraron datos de comportamiento para el rango de fechas seleccionado")
                return
            
            # Calcular métricas principales
            total_users = users_df['totalUsers'].sum() if 'totalUsers' in users_df.columns else 0
            new_users = users_df['newUsers'].sum() if 'newUsers' in users_df.columns else 0
            returning_users = total_users - new_users
            returning_percentage = (returning_users / total_users * 100) if total_users > 0 else 0
            
            # KPIs principales de comportamiento
            st.markdown("### 📊 User Behavior KPIs")
            
            # Crear columnas para KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Users",
                    value=f"{total_users:,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="New Users",
                    value=f"{new_users:,}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="Returning Users",
                    value=f"{returning_percentage:.1f}%",
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="User Retention",
                    value=f"{returning_percentage:.1f}%",
                    delta=None
                )
            
            st.markdown("---")
            
            # Análisis de usuarios nuevos vs recurrentes
            st.markdown("### 🔄 New vs Returning Users")
            
            if not users_df.empty and 'date' in users_df.columns:
                users_df['date'] = pd.to_datetime(users_df['date'])
                users_df['returning_users'] = users_df['totalUsers'] - users_df['newUsers']
                
                # Gráfico de líneas para usuarios
                fig_users = px.line(
                    users_df,
                    x='date',
                    y=['newUsers', 'returning_users'],
                    title="Daily New vs Returning Users",
                    color_discrete_sequence=['#10B981', '#3B82F6']
                )
                
                fig_users.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white'
                )
                
                st.plotly_chart(fig_users, use_container_width=True)
            
            # Análisis de dispositivos
            st.markdown("### 📱 Device Analysis")
            
            if not devices_df.empty and 'deviceCategory' in devices_df.columns:
                device_summary = devices_df.groupby('deviceCategory').agg({
                    'sessions': 'sum',
                    'totalUsers': 'sum',
                    'bounceRate': 'mean',
                    'averageSessionDuration': 'mean'
                }).reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de dona para dispositivos
                    fig_devices = px.pie(
                        device_summary,
                        values='sessions',
                        names='deviceCategory',
                        title="Sessions by Device Type",
                        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
                    )
                    
                    fig_devices.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        title_font_color='white'
                    )
                    
                    st.plotly_chart(fig_devices, use_container_width=True)
                
                with col2:
                    st.dataframe(
                        device_summary,
                        use_container_width=True,
                        hide_index=True
                    )
            
            # Análisis geográfico
            st.markdown("### 🌍 Geographic Analysis")
            
            if not geo_df.empty and 'country' in geo_df.columns:
                country_summary = geo_df.groupby('country').agg({
                    'sessions': 'sum',
                    'totalUsers': 'sum',
                    'bounceRate': 'mean'
                }).reset_index()
                
                country_summary = country_summary.sort_values('totalUsers', ascending=False)
                
                # Gráfico de barras para países
                fig_geo = px.bar(
                    country_summary.head(8),  # Top 8 países
                    x='totalUsers',
                    y='country',
                    orientation='h',
                    title="Top 8 Countries by Users",
                    color='totalUsers',
                    color_continuous_scale='Viridis'
                )
                
                fig_geo.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white',
                    height=400
                )
                
                st.plotly_chart(fig_geo, use_container_width=True)
            
            # Análisis de horarios de actividad
            st.markdown("### ⏰ Peak Activity Hours")
            
            if not hours_df.empty and 'hour' in hours_df.columns:
                # Gráfico de área para horarios
                fig_hours = px.area(
                    hours_df,
                    x='hour',
                    y='sessions',
                    title="Sessions by Hour of Day",
                    color_discrete_sequence=['#10B981']
                )
                
                fig_hours.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white'
                )
                
                st.plotly_chart(fig_hours, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error obteniendo datos de comportamiento: {str(e)}")
    
    else:
        st.warning("⚠️ No hay filtros de fecha configurados. Configura las fechas en el sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Marketing Dashboard - User Behavior Analysis</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)
