"""
Marketing Operations Page
Vista de Marketing y Operaciones del Growth Intelligence Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Importar configuraciones y helpers
from src.config.settings import APP_CONFIG, GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_analytics_data, get_all_analytics_data
from src.helpers.visualization_helpers import create_line_chart, create_bar_chart, create_metrics_summary, display_data_preview
from src.helpers.growth_analytics_helpers import get_all_growth_data, calculate_growth_metrics





def main():
    """Función principal de la página de Marketing Operations"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Marketing Operations - Growth Intelligence",
        page_icon="src/assets/G I D.jpg",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS para diseño mejorado
    st.markdown("""
    <style>
    .stApp {
        background-color: #000000 !important;
    }
    
    .main {
        background-color: #000000 !important;
    }
    
    .main .block-container {
        background-color: #000000 !important;
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: none;
    }
    
    .stButton > button {
        background: #2E4543 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2E4543 0%, #3A5A58 50%, #4A7C7A 100%) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar estándar completo
    from src.components.sidebar import mostrar_sidebar_completo
    mostrar_sidebar_completo()
    
    # Título principal
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold;">
            🚀 Marketing Operations
        </h1>
        <p style="color: #CDE3DE; font-size: 1.1rem;">
            Optimización Semanal/Quincenal y Detección de Cuellos de Botella
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Contenido principal - por implementar
    st.info("🚧 Contenido en desarrollo - Próximamente")


if __name__ == "__main__":
    main()
