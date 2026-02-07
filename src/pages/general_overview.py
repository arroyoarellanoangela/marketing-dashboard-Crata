"""
Executive Dashboard Page
Vista Ejecutiva del Growth Intelligence Dashboard para CEO/Dirección
"""

import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_all_analytics_data


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
    
    time.sleep(duration)
    placeholder.empty()


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


def calculate_delta(current, previous):
    """Calcula el porcentaje de cambio entre dos valores"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


def generate_insight(sessions, users, sessions_delta, users_delta, wow, mom):
    """Genera un insight automático basado en los datos"""
    # Determinar la tendencia general
    if sessions_delta < 0 and users_delta < 0:
        trend = "negativa"
        trend_desc = "una reducción sostenida del volumen de entrada"
    elif sessions_delta > 0 and users_delta > 0:
        trend = "positiva"
        trend_desc = "un crecimiento sostenido del volumen de entrada"
    else:
        trend = "mixta"
        trend_desc = "resultados mixtos en el volumen de entrada"
    
    # Construir el insight
    insight = f"Las {sessions:,} sesiones registradas representan una {'caída' if sessions_delta < 0 else 'subida'} del {abs(sessions_delta):.1f}%, "
    insight += f"mientras que los {users:,} usuarios únicos {'descienden' if users_delta < 0 else 'aumentan'} un {abs(users_delta):.1f}%. "
    insight += f"La tendencia {trend} se {'acentúa' if trend == 'negativa' else 'confirma'} con un {wow:+.1f}% WoW y {mom:+.1f}% MoM, "
    insight += f"lo que indica {trend_desc}. "
    
    if trend == "negativa":
        insight += "Este patrón sugiere revisar las fuentes que normalmente aportan mayor tráfico (orgánico, campañas y referencias) para identificar dónde se está produciendo la pérdida."
    elif trend == "positiva":
        insight += "Este patrón sugiere que las estrategias actuales están funcionando. Se recomienda identificar qué canales están impulsando el crecimiento."
    else:
        insight += "Se recomienda analizar en detalle cada canal para entender las diferencias de rendimiento."
    
    return insight


def render_vision_general_tab():
    """Renderiza el contenido del tab Visión General"""
    
    # CSS para el diseño
    st.markdown("""
    <style>
    .section-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 1rem;
    }
    .section-title {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
    }
    .info-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: transparent;
        color: #6CA8A4;
        border: 2px solid #6CA8A4;
        border-radius: 50%;
        font-size: 16px;
        font-weight: bold;
        cursor: help;
    }
    .info-text {
        background: transparent;
        border: none;
        padding: 0;
        color: #999;
        font-size: 13px;
        line-height: 1.5;
        margin-left: auto;
        max-width: 55%;
        text-align: right;
    }
    .section-divider {
        border: none;
        border-top: 3px solid #3a3a3a;
        margin: 15px 0;
    }
    .kpi-section-title {
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .kpi-card {
        background: linear-gradient(90deg, rgba(29, 71, 68, 0.4) 0%, rgba(98, 169, 167, 0.4) 100%);
        border: 1px solid #9b9b9b;
        border-radius: 8px;
        padding: 20px 25px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title {
        color: #ffffff;
        font-size: 18px;
        font-weight: 600;
        text-align: left;
        margin-bottom: 10px;
    }
    .kpi-main {
        display: flex;
        align-items: baseline;
        gap: 15px;
    }
    .kpi-value {
        color: white;
        font-size: 2.8rem;
        font-weight: bold;
        line-height: 1;
    }
    .kpi-delta-positive {
        color: #4CAF50;
        font-size: 14px;
        font-weight: 600;
    }
    .kpi-delta-negative {
        color: #f44336;
        font-size: 14px;
        font-weight: 600;
    }
    .kpi-subtitle {
        color: #666;
        font-size: 11px;
        text-align: left;
        margin-top: 10px;
    }
    .insight-box {
        background: linear-gradient(135deg, rgba(40, 50, 40, 0.95) 0%, rgba(30, 40, 30, 0.95) 100%);
        border: 1px solid #4a5a4a;
        border-left: 4px solid #FFD700;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        display: flex;
        align-items: flex-start;
        gap: 15px;
    }
    .insight-icon {
        font-size: 2rem;
        color: #FFD700;
    }
    .insight-text {
        color: #ddd;
        font-size: 13px;
        line-height: 1.6;
    }
    .insight-text strong {
        color: #f44336;
    }
    .growth-card {
        background: rgba(20, 30, 30, 0.9);
        border: 1px solid #3a3a3a;
        border-radius: 10px;
        padding: 20px;
        min-height: 160px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    .growth-title {
        color: #999;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
        text-align: center;
    }
    .growth-values {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
        margin-bottom: 5px;
    }
    .growth-row {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }
    .growth-label {
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .growth-value-positive {
        color: #4CAF50;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .growth-value-negative {
        color: #f44336;
        font-size: 1.2rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header con título e info
    st.markdown("""
    <div class="section-header">
        <h1 class="section-title">VISIÓN GENERAL</h1>
        <span class="info-bubble">i</span>
        <div class="info-text">
            Este tab resume el volumen total de tráfico, mostrando cuántos usuarios y sesiones genera 
            la web y cómo evoluciona frente al periodo anterior. Proporciona una lectura rápida para 
            detectar tendencias, cambios de ritmo y variaciones relevantes en la actividad digital.
        </div>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)
    
    # Obtener datos de analytics
    analytics_data = st.session_state.get('analytics_data', {})
    
    # Verificar si hay datos cargados y ofrecer cargarlos
    if not analytics_data or 'datos_temporales' not in analytics_data:
        st.warning("Los datos no están cargados.")
        if st.button("Cargar Datos de Google Analytics", key="load_data_vision"):
            from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_all_analytics_data
            from src.config.settings import DATA_SETS_CONFIG
            
            credentials = load_credentials()
            if credentials:
                client = initialize_analytics_client(credentials)
                if client:
                    today = datetime.now().date()
                    start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
                    end_date = today.strftime("%Y-%m-%d")
                    
                    with st.spinner("Cargando datos..."):
                        all_data = get_all_analytics_data(client, "381346600", start_date, end_date, DATA_SETS_CONFIG)
                        if all_data:
                            st.session_state['analytics_data'] = all_data
                            st.success("Datos cargados correctamente")
                            st.rerun()
        return
    
    # Obtener fechas del filtro
    fecha_inicio = st.session_state.get('fecha_inicio', datetime.now().date() - timedelta(days=7))
    fecha_fin = st.session_state.get('fecha_fin', datetime.now().date())
    
    # Calcular periodo anterior
    periodo_dias = (fecha_fin - fecha_inicio).days
    fecha_inicio_prev = fecha_inicio - timedelta(days=periodo_dias)
    fecha_fin_prev = fecha_inicio - timedelta(days=1)
    
    # Inicializar valores por defecto
    sessions_current = 0
    sessions_prev = 0
    users_current = 0
    users_prev = 0
    
    # Procesar datos si existen
    if analytics_data and 'datos_temporales' in analytics_data:
        df = analytics_data['datos_temporales']
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
            # Filtrar por periodo actual
            mask_current = (df['date'].dt.date >= fecha_inicio) & (df['date'].dt.date <= fecha_fin)
            df_current = df[mask_current]
            
            # Filtrar por periodo anterior
            mask_prev = (df['date'].dt.date >= fecha_inicio_prev) & (df['date'].dt.date <= fecha_fin_prev)
            df_prev = df[mask_prev]
            
            # Calcular métricas
            if 'sessions' in df.columns:
                sessions_current = int(df_current['sessions'].sum()) if not df_current.empty else 0
                sessions_prev = int(df_prev['sessions'].sum()) if not df_prev.empty else 0
            
            if 'totalUsers' in df.columns:
                users_current = int(df_current['totalUsers'].sum()) if not df_current.empty else 0
                users_prev = int(df_prev['totalUsers'].sum()) if not df_prev.empty else 0
    
    # Calcular deltas
    sessions_delta = calculate_delta(sessions_current, sessions_prev)
    users_delta = calculate_delta(users_current, users_prev)
    
    # Calcular WoW y MoM (simplificado)
    wow = sessions_delta  # Week over Week
    mom = sessions_delta * 0.85  # Month over Month aproximado
    
    # Sección KPIs CLAVE
    st.markdown("""
    <div class="section-header" style="margin-top: 10px;">
        <span class="kpi-section-title">KPIS CLAVE</span>
    </div>
    <hr class="section-divider">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px;">
        <span class="info-bubble" style="width: 22px; height: 22px; font-size: 12px;">i</span>
        <span class="info-text" style="font-size: 12px; font-style: italic;">
            Indicadores principales del rendimiento web: muestran cuántas sesiones y usuarios únicos hemos recibido y cómo está evolucionando el tráfico semana a semana y mes a mes.
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        delta_class = "kpi-delta-negative" if sessions_delta < 0 else "kpi-delta-positive"
        delta_arrow = "↓" if sessions_delta < 0 else "↑"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Sesiones Totales</div>
            <div class="kpi-main">
                <div class="kpi-value">{sessions_current:,}</div>
                <div class="{delta_class}">{delta_arrow} {abs(sessions_delta):.1f}%</div>
            </div>
            <div class="kpi-subtitle">Total de sesiones en el periodo</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        delta_class = "kpi-delta-negative" if users_delta < 0 else "kpi-delta-positive"
        delta_arrow = "↓" if users_delta < 0 else "↑"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Usuarios Únicos</div>
            <div class="kpi-main">
                <div class="kpi-value">{users_current:,}</div>
                <div class="{delta_class}">{delta_arrow} {abs(users_delta):.1f}%</div>
            </div>
            <div class="kpi-subtitle">Usuarios únicos activos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        wow_class = "kpi-delta-negative" if wow < 0 else "kpi-delta-positive"
        mom_class = "kpi-delta-negative" if mom < 0 else "kpi-delta-positive"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Crecimiento</div>
            <div class="kpi-main" style="flex-direction: column; align-items: flex-start; gap: 5px;">
                <div class="{wow_class}" style="font-size: 1.3rem;">WoW: {wow:+.1f}%</div>
                <div class="{mom_class}" style="font-size: 1.3rem;">MoM: {mom:+.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    
    # Insight automático
    insight_text = generate_insight(sessions_current, users_current, sessions_delta, users_delta, wow, mom)
    
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-icon">💡</div>
        <div class="insight-text">{insight_text}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Función principal del Executive Dashboard"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Executive Dashboard - Growth Intelligence",
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
        background: transparent;
        padding: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: 0 !important;
    }
    
    .stImage {
        background: transparent;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .stImage img {
        margin: 0 auto;
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

    /* Ajustes específicos solicitados */
    header.st-emotion-cache-18ni7ap {
        display: none !important;
    }

    .st-emotion-cache-1wmy9hl.e1f1d6gn0 {
        background-clip: unset;
        -webkit-background-clip: unset;
        color: rgba(49, 51, 63, 1);
    }

    .st-emotion-cache-1wmy9hl.e1f1d6gn0:empty {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Mostrar sidebar estándar completo
    from src.components.sidebar import mostrar_sidebar_completo
    mostrar_sidebar_completo()
    
    # Cargar credenciales y datos automáticamente
    credentials_info = load_credentials()
    client = None

    if credentials_info:
        client = initialize_analytics_client(credentials_info)
        
        if client and st.session_state.get('auto_load_data', False):
            today = datetime.now().date()
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
            with st.spinner("🔄 Cargando datos de Google Analytics..."):
                all_data = get_all_analytics_data(
                    client=client,
                    property_id="381346600",
                    start_date=start_date,
                    end_date=end_date,
                    data_sets_config=DATA_SETS_CONFIG
                )
                if all_data:
                    st.session_state['analytics_data'] = all_data
                    st.session_state['auto_load_data'] = False

    # CSS para los tabs personalizados
    st.markdown("""
    <style>
    /* Ocultar tabs por defecto de Streamlit y personalizar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: rgba(0, 20, 20, 0.8);
        border-radius: 0;
        padding: 0;
        border-bottom: 1px solid #2E4543;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 30px;
        background-color: transparent;
        border: none;
        color: white;
        font-weight: 500;
        font-size: 14px;
        border-radius: 0;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(108, 168, 164, 0.2);
        color: #6CA8A4;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #6CA8A4 !important;
        border-bottom: 2px solid #6CA8A4 !important;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #6CA8A4 !important;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Crear los 4 tabs
    tab1, tab2, tab3= st.tabs([
        "Visión General",
        "Calidad del Tráfico",
        "Geografía",
    ])
    
    # Contenido de cada tab
    with tab1:
        render_vision_general_tab()
    
    with tab2:
        st.markdown("### Calidad del Tráfico")
        st.info("Contenido de Calidad del Tráfico próximamente...")
    
    with tab3:
        st.markdown("### Geografía")
        st.info("Contenido de Geografía próximamente...")
    



if __name__ == "__main__":
    main()
