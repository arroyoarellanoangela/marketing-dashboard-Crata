import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_all_analytics_data
from src.components.sidebar import mostrar_sidebar_variables, mostrar_sidebar_filtros

def main():
    """Página principal para mostrar todas las tablas de datos de Google Analytics"""
    
    # Configurar la página
    st.set_page_config(
        page_title="Tables - Marketing Dashboard",
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
    from src.components.sidebar import mostrar_sidebar_variables, mostrar_filtros_fecha
    
    # Header del sidebar
    mostrar_sidebar_variables()
    
    # Solo filtros del sidebar (sin navegación)

    # Configuración de fechas
    st.sidebar.subheader("Rango de fechas")
    
    # Filtros rápidos de fechas
    st.sidebar.markdown("**📅 Filtros rápidos:**")
    quick_filters = st.sidebar.selectbox(
        "Seleccionar período",
        ["Personalizado", "Hoy", "Ayer", "Últimos 7 días", "Últimos 28 días", "Últimos 30 días", "Últimos 90 días", "Esta semana", "Semana pasada"],
        help="Selecciona un período predefinido o personalizado"
    )
    
    # Calcular fechas según el filtro seleccionado
    from datetime import datetime, timedelta
    today = datetime.now().date()
    
    if quick_filters == "Hoy":
        start_date = today
        end_date = today
    elif quick_filters == "Ayer":
        start_date = today - timedelta(days=1)
        end_date = today - timedelta(days=1)
    elif quick_filters == "Últimos 7 días":
        start_date = today - timedelta(days=7)
        end_date = today
    elif quick_filters == "Últimos 28 días":
        start_date = today - timedelta(days=28)
        end_date = today
    elif quick_filters == "Últimos 30 días":
        start_date = today - timedelta(days=30)
        end_date = today
    elif quick_filters == "Últimos 90 días":
        start_date = today - timedelta(days=90)
        end_date = today
    elif quick_filters == "Esta semana":
        # Lunes de esta semana
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)
        end_date = today
    elif quick_filters == "Semana pasada":
        # Lunes de la semana pasada
        days_since_monday = today.weekday()
        start_last_week = today - timedelta(days=days_since_monday + 7)
        end_last_week = start_last_week + timedelta(days=6)
        start_date = start_last_week
        end_date = end_last_week
    else:  # Personalizado
        start_date = today - timedelta(days=30)
        end_date = today
    
    # Selectores de fecha (solo si es personalizado)
    if quick_filters == "Personalizado":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date_input = st.date_input(
                "Fecha inicio",
                value=start_date,
                help="Fecha de inicio para los datos"
            )
        with col2:
            end_date_input = st.date_input(
                "Fecha fin",
                value=end_date,
                help="Fecha de fin para los datos"
            )
    else:
        start_date_input = start_date
        end_date_input = end_date

    # Modern Apply Filters button
    st.sidebar.markdown("""
    <style>
    /* Estilos específicos para botones del sidebar */
    .stSidebar .stButton > button {
        background: #2E4543 !important;
        background-image: none !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(46, 69, 67, 0.3) !important;
    }
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #2E4543 0%, #3A5A58 50%, #4A7C7A 100%) !important;
        background-image: none !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46, 69, 67, 0.4) !important;
    }
    .stSidebar .stButton > button:active {
        background: #2E4543 !important;
        background-image: none !important;
        transform: translateY(0) !important;
    }
    .stSidebar .stButton > button:focus {
        background: #2E4543 !important;
        background-image: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚀 Apply Filters", use_container_width=True):
        st.session_state["fecha_inicio"] = start_date_input
        st.session_state["fecha_fin"] = end_date_input
        st.session_state["filters_applied"] = True
        st.success("✅ Filters applied successfully!")
    
    # Título de la página
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>📊 TABLES</h1>
        <p style='color: #888; font-size: 1.2rem;'>Todas las tablas de datos de Google Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos automáticamente si no están cargados
    if 'analytics_data' not in st.session_state or not st.session_state['analytics_data']:
        st.info("🔄 Cargando datos de Google Analytics...")
        
        # Cargar credenciales y inicializar cliente
        credentials = load_credentials()
        if credentials:
            client = initialize_analytics_client(credentials)
            if client:
                # Obtener datos de los últimos 30 días por defecto
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                with st.spinner("📊 Descargando datos de Google Analytics..."):
                    all_data = get_all_analytics_data(client, APP_CONFIG['property_id'], start_date, end_date, DATA_SETS_CONFIG)
                    st.session_state['analytics_data'] = all_data
                    st.toast("🎉 ¡TODOS los datos descargados exitosamente!", icon="✅")
            else:
                st.error("❌ No se pudo inicializar el cliente de Google Analytics")
        else:
            st.error("❌ No se pudieron cargar las credenciales")
    
    # Mostrar todas las tablas de datos
    if 'analytics_data' in st.session_state and st.session_state['analytics_data']:
        
        # Información general
        total_datasets = len([df for df in st.session_state['analytics_data'].values() if not df.empty])
        total_records = sum([len(df) for df in st.session_state['analytics_data'].values() if not df.empty])
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1F2937 0%, #374151 100%); 
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; 
                    border: 1px solid #4B5563;'>
            <h3 style='color: white; margin: 0 0 1rem 0;'>📈 Resumen de Datos</h3>
            <div style='display: flex; gap: 2rem;'>
                <div>
                    <div style='color: #9CA3AF; font-size: 0.875rem;'>Total de Datasets</div>
                    <div style='color: #F9FAFB; font-size: 1.5rem; font-weight: 700;'>{total_datasets}</div>
                </div>
                <div>
                    <div style='color: #9CA3AF; font-size: 0.875rem;'>Total de Registros</div>
                    <div style='color: #F9FAFB; font-size: 1.5rem; font-weight: 700;'>{total_records:,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar cada dataset individualmente
        for dataset_name, df in st.session_state['analytics_data'].items():
            if not df.empty:
                # Aplicar filtros de fecha si están disponibles y el dataset tiene columna 'date'
                filtered_df = df.copy()
                if "fecha_inicio" in st.session_state and "fecha_fin" in st.session_state and "date" in df.columns:
                    fecha_inicio = st.session_state["fecha_inicio"]
                    fecha_fin = st.session_state["fecha_fin"]
                    
                    # Convertir fechas a datetime si es necesario
                    filtered_df["date"] = pd.to_datetime(filtered_df["date"])
                    
                    # Filtrar por rango de fechas
                    mask = (filtered_df["date"] >= pd.Timestamp(fecha_inicio)) & (filtered_df["date"] <= pd.Timestamp(fecha_fin))
                    filtered_df = filtered_df[mask]
                
                # Crear expander para cada tabla
                with st.expander(f"📊 {dataset_name.replace('_', ' ').title()} ({len(filtered_df)} registros)", expanded=True):
                    
                    # Información de la tabla
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Registros", len(filtered_df))
                    with col2:
                        st.metric("Columnas", len(filtered_df.columns))
                    with col3:
                        st.metric("Tamaño", f"{filtered_df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                    
                    # Mostrar columnas disponibles
                    st.write("**Columnas disponibles:**")
                    cols_display = st.columns(min(len(filtered_df.columns), 6))
                    for i, col in enumerate(filtered_df.columns):
                        with cols_display[i % 6]:
                            st.code(col)
                    
                    st.markdown("---")
                    
                    # Mostrar el DataFrame completo
                    st.dataframe(filtered_df, use_container_width=True)
                    
                    # Botón para descargar como CSV
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Descargar {dataset_name.replace('_', ' ').title()} como CSV",
                        data=csv,
                        file_name=f"{dataset_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        # Botón para descargar todos los datos como ZIP
        st.markdown("---")
        st.markdown("### 📦 Descarga Masiva")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📦 Descargar TODOS los datos como ZIP", use_container_width=True):
                import zipfile
                import io
                
                # Crear ZIP en memoria
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for dataset_name, df in st.session_state['analytics_data'].items():
                        if not df.empty:
                            csv_data = df.to_csv(index=False)
                            zip_file.writestr(f"{dataset_name}.csv", csv_data)
                
                zip_buffer.seek(0)
                
                st.download_button(
                    label="📥 Descargar ZIP",
                    data=zip_buffer.getvalue(),
                    file_name=f"google_analytics_data_{datetime.now().strftime('%Y%m%d')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
    
    else:
        st.warning("⚠️ No hay datos de Google Analytics disponibles. Ve a la página principal para cargar los datos.")
    
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Google Analytics Dashboard - Tables</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
