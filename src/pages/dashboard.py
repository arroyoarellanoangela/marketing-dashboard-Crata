"""
Main Dashboard Page
Página principal del dashboard de Google Analytics
"""

import streamlit as st
import pandas as pd
import base64
from datetime import datetime, timedelta

# Importar configuraciones y helpers
from src.config.settings import APP_CONFIG, GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_analytics_data, get_all_analytics_data
from src.helpers.visualization_helpers import create_line_chart, create_bar_chart, create_metrics_summary, display_data_preview
from src.helpers.file_helpers import create_zip_file, download_csv


def get_base64_video(video_path):
    """Convierte el video a base64 para usar como fondo"""
    with open(video_path, "rb") as video_file:
        video_base64 = base64.b64encode(video_file.read()).decode("utf-8")
    return video_base64


def get_base64_image(image_path):
    """Convierte la imagen a base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def show_video_background():
    """Muestra el video como fondo de la página"""
    try:
        video_base64 = get_base64_video("src/assets/Website Assets (1).mp4")
        
        video_html = f"""
        <style>
        /* Asegurarse de que el contenedor principal esté por encima del video */
        .main, .block-container {{
            position: relative;
            z-index: 2;
        }}

        /* Estilos para el video como fondo */
        .video-background {{
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: 100vw;
            object-fit: cover;
            z-index: -1;
        }}
        
        /* Overlay semitransparente */
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
    """Función principal del dashboard"""
    
    # Configuración de la página
    st.set_page_config(
        page_title=APP_CONFIG["title"],
        page_icon="src/assets/G I D.jpg",
        layout=APP_CONFIG["layout"],
        initial_sidebar_state="collapsed"  # Ocultar sidebar por defecto
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
    # Sidebar oculto en la página principal
    # from src.components.sidebar import mostrar_sidebar_variables
    # mostrar_sidebar_variables()
    
    # Contenido principal simplificado
    st.markdown("<div style='height: 15rem;'></div>", unsafe_allow_html=True)
    
    # Logo centrado
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("src/assets/logo.png", width=300)
    
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    
    # Botón Getting Started centrado
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Getting Started", type="primary", use_container_width=True):
            st.session_state.page = "general_overview"
            st.session_state.auto_load_data = True  # Flag para cargar datos automáticamente
            st.rerun()
    
    st.markdown("<div style='height: 15rem;'></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
