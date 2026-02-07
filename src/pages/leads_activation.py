"""
Leads & Activation Page
Vista de Leads y Activación del Growth Intelligence Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_all_analytics_data


def main():
    """Función principal de la página de Leads & Activation"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Leads & Activation - Growth Intelligence",
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
            🎯 Leads & Activation
        </h1>
        <p style="color: #CDE3DE; font-size: 1.1rem;">
            Conectar marketing con negocio
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos si no están cargados
    if 'analytics_data' not in st.session_state or not st.session_state['analytics_data']:
        credentials = load_credentials()
        if credentials:
            client = initialize_analytics_client(credentials)
            if client:
                today = datetime.now().date()
                start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
                
                with st.spinner("🔄 Cargando datos de Google Analytics..."):
                    all_data = get_all_analytics_data(client, "381346600", start_date, end_date, DATA_SETS_CONFIG)
                    st.session_state['analytics_data'] = all_data
    
    # Contenido - Por implementar
    st.info("📊 Contenido próximamente...")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Growth Intelligence Dashboard - Leads & Activation</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
