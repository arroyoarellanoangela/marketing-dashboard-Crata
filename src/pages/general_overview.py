"""
General Overview Page
Página de análisis general de Google Analytics
"""

import streamlit as st
import pandas as pd
import base64
import time
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


def show_temporary_message(message, message_type="success", duration=3):
    """Muestra un mensaje temporal que desaparece automáticamente"""
    placeholder = st.empty()
    
    if message_type == "success":
        placeholder.success(message)
    elif message_type == "info":
        placeholder.info(message)
    elif message_type == "warning":
        placeholder.warning(message)
    else:
        placeholder.error(message)
    
    # Esperar y luego limpiar
    time.sleep(duration)
    placeholder.empty()


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
    """Función principal de la página de Analytics Overview"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="General Overview - Google Analytics Dashboard",
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

    # Mostrar sidebar estándar completo
    from src.components.sidebar import mostrar_sidebar_completo
    mostrar_sidebar_completo()
    
    # Título principal
    st.markdown(f"""
    <div style="text-align: center; margin-top: 1rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            ANALYTICS OVERVIEW
        </h1>
        <p style="color: white; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            Análisis Completo de Datos de Marketing
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Cargar credenciales
    credentials_info = load_credentials()

    if credentials_info:
        # Inicializar cliente
        client = initialize_analytics_client(credentials_info)
        
        if client:
            # Cargar TODOS los datos disponibles una sola vez
            if st.session_state.get('auto_load_data', False):
                # Cargar un rango amplio para obtener todos los datos disponibles
                from datetime import datetime, timedelta
                today = datetime.now().date()
                start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")  # Último año
                end_date = today.strftime("%Y-%m-%d")
                
                with st.spinner("🔄 Cargando TODOS los datos de Google Analytics..."):
                    all_data = get_all_analytics_data(
                        client=client,
                        property_id="381346600",
                        start_date=start_date,
                        end_date=end_date,
                        data_sets_config=DATA_SETS_CONFIG
                    )
                    if all_data:
                        st.session_state['analytics_data'] = all_data
                        st.session_state['auto_load_data'] = False  # Reset flag
                        show_temporary_message("✅ TODOS los datos cargados exitosamente!")
                    else:
                        st.error("❌ No se pudieron cargar los datos de Google Analytics")
    
    # Botón para recargar TODOS los datos
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Recargar TODOS los Datos", use_container_width=True):
            if credentials_info and client:
                from datetime import datetime, timedelta
                today = datetime.now().date()
                start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")  # Último año
                end_date = today.strftime("%Y-%m-%d")
                
                with st.spinner(f"🔄 Cargando TODOS los datos del {start_date} al {end_date}..."):
                    all_data = get_all_analytics_data(
                        client=client,
                        property_id="381346600",
                        start_date=start_date,
                        end_date=end_date,
                        data_sets_config=DATA_SETS_CONFIG
                    )
                    if all_data:
                        st.session_state['analytics_data'] = all_data
                        show_temporary_message("✅ TODOS los datos recargados exitosamente!")
                        st.rerun()
                    else:
                        st.error("❌ No se pudieron cargar los datos de Google Analytics")
            else:
                st.error("❌ Cliente de Google Analytics no disponible")

    # Mostrar solo los KPIs y gráficos (sin tablas)
    if 'analytics_data' in st.session_state and st.session_state['analytics_data']:
        from src.visuals.metrics import create_user_kpis_optimized, create_new_vs_returning_chart, create_top_pages_table
        
        # Mostrar KPIs usando datos temporales (que tienen las métricas principales)
        if 'datos_temporales' in st.session_state['analytics_data'] and not st.session_state['analytics_data']['datos_temporales'].empty:
            
            # Usar datos temporales para KPIs principales
            temp_df = st.session_state['analytics_data']['datos_temporales'].copy()
            
            # Aplicar filtros de fecha localmente
            if "fecha_inicio" in st.session_state and "fecha_fin" in st.session_state:
                fecha_inicio = st.session_state["fecha_inicio"]
                fecha_fin = st.session_state["fecha_fin"]
                
                if "date" in temp_df.columns:
                    temp_df["date"] = pd.to_datetime(temp_df["date"])
                    mask = (temp_df["date"] >= pd.Timestamp(fecha_inicio)) & (temp_df["date"] <= pd.Timestamp(fecha_fin))
                    temp_df = temp_df[mask]
                
                # Si no hay datos después del filtro, mostrar mensaje pero mantener datos originales
                if len(temp_df) == 0:
                    st.warning("⚠️ No hay datos para el rango de fechas seleccionado. Mostrando todos los datos disponibles.")
                    temp_df = st.session_state['analytics_data']['datos_temporales'].copy()
                    temp_df["date"] = pd.to_datetime(temp_df["date"])
            
            # Mostrar KPIs optimizados
            create_user_kpis_optimized()
            
            # Mostrar gráfico de New vs. Returning users
            st.markdown("---")
            if len(temp_df) > 0:
                chart_fig = create_new_vs_returning_chart(temp_df)
                if chart_fig:
                    st.plotly_chart(chart_fig, use_container_width=True)
                else:
                    st.warning("⚠️ No se pudo crear el gráfico con los datos disponibles")
            else:
                st.warning("⚠️ No hay datos para mostrar el gráfico después del filtrado")
            
            # Mostrar tabla de Top Pages
            st.markdown("---")
            create_top_pages_table(st.session_state['analytics_data'])
        else:
            st.warning("⚠️ No hay datos temporales disponibles o están vacíos")
    else:
        st.warning("⚠️ No hay datos de analytics cargados")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Google Analytics Dashboard - General Overview</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()