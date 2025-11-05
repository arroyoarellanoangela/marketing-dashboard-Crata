"""
Executive Dashboard Page
Vista Ejecutiva del Growth Intelligence Dashboard para CEO/Dirección
"""

import streamlit as st
import pandas as pd
from src.config.settings import APP_CONFIG, DATA_SETS_CONFIG
from src.components.sidebar import mostrar_sidebar_completo, aplicar_filtros_fecha
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_all_analytics_data
from src.visuals.metrics_ejecutivo import renderizar_executive_dashboard



def main():
    """Función principal de la página del Executive Dashboard"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Executive Dashboard - Growth Intelligence",
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
    mostrar_sidebar_completo()
    
    # Título principal
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold;">
            📊 Executive Dashboard
        </h1>
        <p style="color: #CDE3DE; font-size: 1.1rem;">
            Vista Ejecutiva - Evolución del Negocio y Retorno de Marketing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar si hay datos cargados
    if 'analytics_data' not in st.session_state or not st.session_state['analytics_data']:
        st.warning("⚠️ No hay datos de Google Analytics cargados. Ve a 'Analytics Overview' y carga los datos primero.")
        return
    
    # Obtener datos filtrados
    analytics_data = st.session_state['analytics_data']
    
    # Aplicar filtros de fecha si están configurados
    if 'filtro_rapido' in st.session_state and st.session_state['filtro_rapido']:
        analytics_data_filtrados = {}
        for dataset_name, df in analytics_data.items():
            if isinstance(df, pd.DataFrame) and not df.empty and 'date' in df.columns:
                df_filtrado = aplicar_filtros_fecha(df)
                analytics_data_filtrados[dataset_name] = df_filtrado
            else:
                analytics_data_filtrados[dataset_name] = df
        analytics_data = analytics_data_filtrados
    
    # Renderizar el dashboard ejecutivo
    renderizar_executive_dashboard(analytics_data)


if __name__ == "__main__":
    main()
