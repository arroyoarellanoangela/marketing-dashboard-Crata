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
        background: transparent;
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: none;
    }
    
    .stImage {
        background: transparent;
    }
    
    .stButton > button {
        background: linear-gradient(80deg, rgba(29, 71, 68, 1) 0%, rgba(98, 169, 167, 1) 100%) !important;
        color: rgba(255, 255, 255, 1) !important;
        background-clip: unset !important;
        -webkit-background-clip: unset !important;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        opacity: 0.8;
    }
    
    .stButton > button:hover {
        background: linear-gradient(80deg, rgba(29, 71, 68, 1) 0%, rgba(98, 169, 167, 1) 100%) !important;
        opacity: 1;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Ocultar header de Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Centrar todo el contenido del bloque principal */
    .main .block-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Centrar las columnas */
    [data-testid="stHorizontalBlock"] {
        justify-content: center !important;
        width: 100% !important;
    }

    /* Centrar imagen */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        text-align: center;
    }

    [data-testid="stImage"] img {
        margin: 0 auto;
    }

    /* Centrar el botón */
    .stButton {
        display: flex !important;
        justify-content: center !important;
    }

    .stButton > button {
        min-width: 280px;
    }
    </style>
    """, unsafe_allow_html=True)
    # Sidebar oculto en la página principal
    # from src.components.sidebar import mostrar_sidebar_variables
    # mostrar_sidebar_variables()
    
    # Contenido principal simplificado - centrado con contenedor
    st.markdown("<div style='height: 15rem;'></div>", unsafe_allow_html=True)
    
    # Logo centrado usando columnas con espaciadores más grandes
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image("src/assets/logo.png", width=300)
    
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    
    # Botón Getting Started centrado con columnas anchas a los lados
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Getting Started", type="primary", use_container_width=True):
            st.session_state.page = "general_overview"
            st.session_state.auto_load_data = True  # Flag para cargar datos automáticamente
            st.rerun()
    
    st.markdown("<div style='height: 15rem;'></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
