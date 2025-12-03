"""
Sidebar Component
Componente de sidebar avanzado para el dashboard de marketing
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.config.settings import GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS


def smart_multiselect(label, options, key, session_key, dentro_de_formulario=False):
    """Multiselect inteligente con expander y persistencia"""
    full_set = set(options)
    previous_selection = st.session_state.get(session_key, set(options))

    if not previous_selection:
        previous_selection = full_set

    temp_selection = st.session_state.get(key, list(previous_selection))
    temp_selection = [opt for opt in temp_selection if opt in options]

    if not temp_selection:
        temp_selection = list(full_set)

    # Dibujo compacto sin expander si está en formulario
    if dentro_de_formulario:
        selection = st.multiselect(
            label=label,
            options=options,
            default=temp_selection,
            key=key
        )
    else:
        # Expander con etiqueta resumida
        if set(temp_selection) == full_set:
            expander_label = f"{label}: All"
        else:
            # Mostrar los valores específicos seleccionados
            if len(temp_selection) <= 3:
                # Si son pocos, mostrar todos
                values_str = ", ".join(map(str, temp_selection))
                expander_label = f"{label}: {values_str}"
            else:
                # Si son muchos, mostrar algunos y el total
                first_values = ", ".join(map(str, temp_selection[:2]))
                expander_label = f"{label}: {first_values}... (+{len(temp_selection)-2} more)"

        with st.sidebar.expander(expander_label, expanded=False):
            selection = st.multiselect(
                label="",
                options=options,
                default=temp_selection,
                key=key
            )

    if not selection:
        selection = list(full_set)

    st.session_state[session_key] = selection
    return selection


def aplicar_filtros_fecha(df):
    """
    Aplica los filtros de fecha del sidebar a un DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame con columna 'date'
    
    Returns:
        pd.DataFrame: DataFrame filtrado por las fechas del sidebar
    """
    if df is None or df.empty:
        return df
    
    # Verificar que hay filtros de fecha configurados
    if "fecha_inicio" not in st.session_state or "fecha_fin" not in st.session_state:
        return df
    
    fecha_inicio = st.session_state["fecha_inicio"]
    fecha_fin = st.session_state["fecha_fin"]
    
    # Verificar que el DataFrame tiene columna de fecha
    if "date" not in df.columns:
        return df
    
    # Crear copia para no modificar el original
    filtered_df = df.copy()
    
    # Convertir fecha a datetime si no lo está
    filtered_df["date"] = pd.to_datetime(filtered_df["date"])
    
    # Aplicar filtro
    mask = (filtered_df["date"] >= pd.Timestamp(fecha_inicio)) & (filtered_df["date"] <= pd.Timestamp(fecha_fin))
    filtered_df = filtered_df[mask]
    
    # Si no hay datos después del filtro, mostrar advertencia pero mantener datos originales
    if len(filtered_df) == 0:
        st.warning("⚠️ No hay datos para el rango de fechas seleccionado. Mostrando todos los datos disponibles.")
        return df
    
    return filtered_df


def aplicar_filtros_a_datos(session_key, data_key=None):
    """
    Aplica filtros de fecha a datos almacenados en session_state
    
    Args:
        session_key (str): Clave del session_state donde están los datos
        data_key (str): Clave específica dentro de los datos (opcional)
    
    Returns:
        DataFrame filtrado o None si no hay datos
    """
    if session_key not in st.session_state or not st.session_state[session_key]:
        return None
    
    data = st.session_state[session_key]
    
    # Si se especifica una clave específica, obtener esos datos
    if data_key and data_key in data:
        df = data[data_key]
    else:
        df = data
    
    # Aplicar filtros de fecha
    return aplicar_filtros_fecha(df)


def mostrar_sidebar_completo():
    """Muestra el sidebar completo estándar para todas las páginas"""
    
    # Header del sidebar
    mostrar_sidebar_variables()
    
    # Mostrar filtros de fecha estándar
    mostrar_filtros_fecha()
    

    # Mostrar mensaje temporal de filtros aplicados
    if st.session_state.get("show_filter_message", False):
        st.sidebar.success("✅ Filters applied successfully!")
        # Limpiar el flag después de mostrar el mensaje
        st.session_state["show_filter_message"] = False


def mostrar_sidebar_variables():
    """Muestra el header del sidebar con logo y estilos"""
    st.sidebar.image("src/assets/logo.png", width=200)
    
    st.sidebar.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500&display=swap');
        .centered-title {
            text-align: center;
            font-family: 'Playfair Display', serif;
            font-size: 40px;
            margin-top: 10px;
            margin-bottom: 20px;
            color: #003A3B;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    <style>
    /* Centrar contenido SOLO en columnas dentro del SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #6CA8A4 !important; /* Color del "padding" */
        padding: 0 !important;
    }

    /* Contenedor interno con margen, como si fuera el contenido separado */
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #000000;  /* Fondo del contenido principal */
        padding: 15px;
        width: 99%;
    }

    /* Botones redondos personalizados */
    div.st-key-go_home button,
    div.st-key-go_overview button,
    div.st-key-go_marketing button,
    div.st-key-go_calendario button {
        height: 60px !important;
        width: 60px !important;
        border-radius: 50% !important;
        font-size: 26px !important;
        background-color: #CDE3DE !important;
        color: #003A3B !important;
        border: 2px solid #1f77b4 !important; /* Azul permanente */
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
        transition: all 0.2s ease-in-out;
        margin: auto !important;
    }

    div.st-key-go_marketing button:hover,
    div.st-key-go_home button:hover,
    div.st-key-go_overview button:hover,
    div.st-key-go_calendario button:hover {
        background-color: #CDE3DE !important;
        transform: scale(1.08);
    }
    </style>
""", unsafe_allow_html=True)

    st.markdown("""
        <style>
        div[data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <hr style='border: 1px solid #6CA8A4; margin: 0.5rem 0 1rem 0;'>
    """, unsafe_allow_html=True)
    
    # Navegación
    st.sidebar.markdown("### Navegación")
    
    # Botones de navegación con estilo personalizado
    st.sidebar.markdown("""
    <style>
    .stSidebar .stButton > button {
        background: #2E4543 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        background-image: none !important;
    }
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #2E4543 0%, #3A5A58 50%, #4A7C7A 100%) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(46, 69, 67, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Navegación

    
    # Botones de navegación con estilo personalizado
    st.sidebar.markdown("""
    <style>
    .stSidebar .stButton > button {
        background: #2E4543 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        background-image: none !important;
    }
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #2E4543 0%, #3A5A58 50%, #4A7C7A 100%) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(46, 69, 67, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Botones de navegación
    if st.sidebar.button("Página Principal", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()
    
    if st.sidebar.button("Executive Dashboard", use_container_width=True):
        st.session_state.page = "general_overview"
        st.rerun()
    

    
    if st.sidebar.button("Marketing Operations", use_container_width=True):
        st.session_state.page = "marketing_operations"
        st.rerun()
    
    if st.sidebar.button("Content Performance", use_container_width=True):
        st.session_state.page = "content_performance_growth"
        st.rerun()
    
    if st.sidebar.button("Leads & Activation", use_container_width=True):
        st.session_state.page = "leads_activation"
        st.rerun()
    if st.sidebar.button("Data Inspector", use_container_width=True):
        st.session_state.page = "data_inspector"
        st.rerun()
    st.sidebar.markdown("---")


def mostrar_sidebar_filtros():
    """Muestra los filtros del sidebar con navegación moderna"""
    
    # Navigation buttons styling - more specific to avoid conflicts
    st.sidebar.markdown("""
    <style>
    .stSidebar div[data-testid="column"] button {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
        color: #F1F5F9 !important;
        border: 2px solid #6FA8A340 !important;
        border-radius: 12px !important;
        padding: 0.5rem 0.75rem !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    .stSidebar div[data-testid="column"] button:hover {
        background: linear-gradient(135deg, #6FA8A3 0%, #4A7C7A 100%) !important;
        border-color: #6FA8A3 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(111, 168, 163, 0.3) !important;
    }
    .stSidebar div[data-testid="column"] button:active {
        transform: translateY(0) !important;
    }
    </style>
    """, unsafe_allow_html=True)
   
    
    # Get current page color based on selection
   
    
    # Modern separator
    st.sidebar.markdown("""
    <div style="height: 2px; background: linear-gradient(90deg, transparent 0%, #6FA8A3 50%, transparent 100%); 
                margin: 1.5rem 0;"></div>
    """, unsafe_allow_html=True)
    
    # Date Filters with modern styling
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                padding: 1rem; border-radius: 15px; margin-bottom: 1rem; text-align: center;
                border: 1px solid #6FA8A340;">
        <h3 style="color: #F1F5F9; margin: 0; font-size: 1.1rem; font-weight: 600;">📅 Date Filters</h3>
    </div>
    """, unsafe_allow_html=True)

    # Obtener año actual
    today = pd.Timestamp.now()
    current_year = today.year
    year_options = list(range(current_year - 4, current_year + 1))

    # Meses abreviados
    month_options = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Inicializar valores por defecto si no existen
    if 'selected_years' not in st.session_state:
        st.session_state['selected_years'] = [current_year, current_year - 1]
    if 'selected_months_abbr' not in st.session_state:
        st.session_state['selected_months_abbr'] = month_options

    # Selectores SIN formulario y con diseño expandible limpio
    selected_years = smart_multiselect(
        label="Years",
        options=year_options,
        key="years_multiselect",
        session_key="selected_years"
    )

    if not selected_years:
        selected_years = [current_year]

    selected_months_abbr = smart_multiselect(
        label="Months",
        options=month_options,
        key="months_multiselect",
        session_key="selected_months_abbr"
    )

    if not selected_months_abbr:
        selected_months_abbr = month_options

    # Actualizar session state con los valores seleccionados
    st.session_state["selected_years"] = selected_years
    st.session_state["selected_months_abbr"] = selected_months_abbr

    # Modern Apply Filters button
    st.sidebar.markdown("""
    <style>
    .stButton > button {
        background: linear-gradient(135deg, #6FA8A3 0%, #4A7C7A 100%);
        color: #F1F5F9;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(111, 168, 163, 0.3);
        border: 1px solid #6FA8A340;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4A7C7A 0%, #6FA8A3 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(111, 168, 163, 0.4);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Apply Filters", use_container_width=True):
        st.session_state["filtro_anios"] = selected_years
        st.session_state["filtro_meses"] = selected_months_abbr
        st.session_state["filters_applied"] = True
        st.session_state["show_filter_message"] = True
        st.rerun()
    
    # Mostrar mensaje temporal de filtros aplicados
    if st.session_state.get("show_filter_message", False):
        st.sidebar.success("✅ Filters applied successfully!")
        # Limpiar el flag después de mostrar el mensaje
        st.session_state["show_filter_message"] = False


def create_sidebar():
    """Crea el sidebar del dashboard"""
    
    # Configuración del sidebar
    st.sidebar.header("⚙️ Configuración")
    
    # Property ID (configurado automáticamente)
    st.sidebar.subheader("🏢 Configuración de Property")
    property_id = GA4_CONFIG["property_id"]
    st.sidebar.info(f"📊 Property ID: `{property_id}`")
    st.sidebar.success("✅ Property ID configurado automáticamente")
    
    # Configuración de fechas
    st.sidebar.subheader("📅 Rango de fechas")
    
    # Fechas por defecto (últimos 30 días)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
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
    
    if property_id:
        # Configuración de métricas y dimensiones
        st.sidebar.subheader("📊 Métricas y Dimensiones")
        
        selected_metrics = st.sidebar.multiselect(
            "Seleccionar métricas",
            GA4_METRICS,
            default=["sessions", "totalUsers", "screenPageViews"]
        )
        
        selected_dimensions = st.sidebar.multiselect(
            "Seleccionar dimensiones",
            GA4_DIMENSIONS,
            default=["date"]
        )
        
        # Botones para obtener datos
        st.sidebar.subheader("🚀 Acciones")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            get_specific_data = st.sidebar.button("🔄 Datos Específicos", type="primary")
        
        with col2:
            get_all_data = st.sidebar.button("📊 TODOS LOS DATOS", type="secondary")
        
        return {
            "property_id": property_id,
            "start_date": start_date_input,
            "end_date": end_date_input,
            "metrics": selected_metrics,
            "dimensions": selected_dimensions,
            "get_specific_data": get_specific_data,
            "get_all_data": get_all_data
        }
    
    return None


def create_analytics_sidebar():
    """Crea el sidebar específico para la página de análisis"""
    
    # Configuración del sidebar
    st.sidebar.header("⚙️ Configuración de Análisis")
    
    # Property ID (configurado automáticamente)
    property_id = GA4_CONFIG["property_id"]
    st.sidebar.info(f"📊 Property ID: `{property_id}` (Crata GA4)")
    
    # Configuración de fechas
    st.sidebar.subheader("📅 Rango de fechas")
    
    # Fechas por defecto (últimos 30 días)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
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
    
    # Botón para obtener TODOS los datos
    st.sidebar.subheader("🚀 Análisis Completo")
    
    get_all_data = st.sidebar.button("📊 Obtener TODOS los datos", type="primary", use_container_width=True)
    
    # Información adicional
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Información")
    st.sidebar.markdown("""
    **Para usar esta aplicación:**

    1. Descarga tu archivo `credentials.json` desde Google Cloud Console
    2. Colócalo en el directorio raíz del proyecto
    3. **✅ Property ID configurado automáticamente:**
    - Property ID: `381346600` (Crata GA4)
    - Ya no necesitas ingresarlo manualmente

    **Notas:**
    - Asegúrate de que tu cuenta de servicio tenga permisos de lectura en Google Analytics
    - El Property ID debe ser de Google Analytics 4 (GA4)
    - Debe ser un número más corto, no el Account ID largo
    """)
    
    return {
        "property_id": property_id,
        "start_date": start_date_input,
        "end_date": end_date_input,
        "get_all_data": get_all_data
    }


def create_navigation_sidebar():
    """Crea el sidebar de navegación"""
    
    st.sidebar.header("Navegación")
    
    # Botones de navegación
    if st.sidebar.button("Página Principal", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()
    
    if st.sidebar.button("Executive Dashboard", use_container_width=True):
        st.session_state.page = "general_overview"
        st.rerun()
    
    if st.sidebar.button("Tables", use_container_width=True):
        st.session_state.page = "tables"
        st.rerun()
    
    # Información del proyecto
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Información del Proyecto")
    st.sidebar.markdown("""
    **Marketing Dashboard**
    
    - Property ID: 381346600
    - Plataforma: Google Analytics 4
    - Desarrollado con Streamlit
    """)


def mostrar_filtros_fecha():
    """Muestra los filtros de fecha en el sidebar"""
    
    # Inicializar fechas por defecto si no existen
    if "fecha_inicio" not in st.session_state or "fecha_fin" not in st.session_state or "filtro_rapido" not in st.session_state:
        today = datetime.now().date()
        st.session_state["fecha_inicio"] = today - timedelta(days=7)
        st.session_state["fecha_fin"] = today
        st.session_state["filtro_rapido"] = "Últimos 7 días"
    
    st.sidebar.markdown("### 📅 Filtros de Fecha")
    
    # Filtros rápidos de fechas
    filtro_rapido = st.sidebar.selectbox(
        "Filtro rápido",
        ["Personalizado", "Últimos 7 días", "Últimos 28 días", "Últimos 30 días", 
         "Últimos 90 días", "Hoy", "Ayer", "Esta semana", "Semana pasada"],
        index=["Personalizado", "Últimos 7 días", "Últimos 28 días", "Últimos 30 días", 
               "Últimos 90 días", "Hoy", "Ayer", "Esta semana", "Semana pasada"].index(st.session_state.get("filtro_rapido", "Últimos 7 días")),
        key="filtro_rapido"
    )
    
    # Calcular fechas según el filtro seleccionado
    today = datetime.now().date()
    
    if filtro_rapido == "Últimos 7 días":
        fecha_inicio = today - timedelta(days=7)
        fecha_fin = today
    elif filtro_rapido == "Últimos 28 días":
        fecha_inicio = today - timedelta(days=28)
        fecha_fin = today
    elif filtro_rapido == "Últimos 30 días":
        fecha_inicio = today - timedelta(days=30)
        fecha_fin = today
    elif filtro_rapido == "Últimos 90 días":
        fecha_inicio = today - timedelta(days=90)
        fecha_fin = today
    elif filtro_rapido == "Hoy":
        fecha_inicio = today
        fecha_fin = today
    elif filtro_rapido == "Ayer":
        fecha_inicio = today - timedelta(days=1)
        fecha_fin = today - timedelta(days=1)
    elif filtro_rapido == "Esta semana":
        # Lunes de esta semana
        fecha_inicio = today - timedelta(days=today.weekday())
        fecha_fin = today
    elif filtro_rapido == "Semana pasada":
        # Lunes de la semana pasada
        fecha_inicio = today - timedelta(days=today.weekday() + 7)
        fecha_fin = fecha_inicio + timedelta(days=6)
    else:  # Personalizado
        fecha_inicio = today - timedelta(days=7)  # Por defecto 7 días
        fecha_fin = today
    
    # Mostrar selectores de fecha solo si es personalizado
    if filtro_rapido == "Personalizado":
        fecha_inicio = st.sidebar.date_input(
            "Fecha inicio",
            value=fecha_inicio,
            help="Fecha de inicio para los datos"
        )
        
        fecha_fin = st.sidebar.date_input(
            "Fecha fin",
            value=fecha_fin,
            help="Fecha de fin para los datos"
        )
    
    # Guardar en session state
    st.session_state["fecha_inicio"] = fecha_inicio
    st.session_state["fecha_fin"] = fecha_fin
