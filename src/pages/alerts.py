"""
Alerts Page
Página de Alertas del Growth Intelligence Dashboard
"""

import streamlit as st
import pandas as pd
import base64
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_all_analytics_data


def get_base64_video(video_path):
    """Convierte el video a base64 para usar como fondo"""
    with open(video_path, "rb") as video_file:
        video_base64 = base64.b64encode(video_file.read()).decode("utf-8")
    return video_base64


def show_video_background():
    """Muestra el video como fondo de la página"""
    try:
        video_base64 = get_base64_video("src/assets/Website Assets (1).mp4")
        
        video_html = f"""
        <style>
        .main, .block-container {{
            position: relative;
            z-index: 2;
        }}

        .video-background {{
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: 100vw;
            object-fit: cover;
            z-index: -1;
        }}
        
        .video-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: 100vw;
            background: rgba(0, 0, 0, 0.3);
            z-index: -1;
        }}
        </style>

        <video autoplay muted loop class="video-background">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
        <div class="video-overlay"></div>
        """
        st.markdown(video_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error cargando el video de fondo: {e}")


def main():
    """Página principal de Alertas"""
    
    # Configurar la página
    st.set_page_config(
        page_title="Alertas - Marketing Dashboard",
        page_icon="src/assets/G I D.jpg",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Mostrar video de fondo
    show_video_background()
    
    # CSS para diseño mejorado
    st.markdown("""
    <style>
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stImage {
        background: transparent;
    }
    
    .stButton > button {
        background: #2E4543;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #3A5A58;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar estándar completo
    from src.components.sidebar import mostrar_sidebar_completo
    mostrar_sidebar_completo()
    
    # Cargar datos si no están cargados
    if 'analytics_data' not in st.session_state or not st.session_state['analytics_data']:
        credentials = load_credentials()
        if credentials:
            client = initialize_analytics_client(credentials)
            if client:
                today = datetime.now().date()
                start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
                
                with st.spinner("Cargando datos de Google Analytics..."):
                    all_data = get_all_analytics_data(client, "381346600", start_date, end_date, DATA_SETS_CONFIG)
                    st.session_state['analytics_data'] = all_data
    
    # Título de la página
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>ALERTAS</h1>
        <p style='color: white; font-size: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>Sistema de alertas y notificaciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Contenido - Por implementar
    st.info("Contenido próximamente...")


if __name__ == "__main__":
    main()

