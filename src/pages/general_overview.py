"""
Executive Dashboard Page
Vista Ejecutiva del Growth Intelligence Dashboard para CEO/Dirección
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


def render_kpi_card(title, value, subtitle=None, icon=None, delta=None):
    """Renderiza una tarjeta de KPI con estilo Crata y delta opcional"""
    icon_html = f'<div style="font-size: 2rem; opacity: 0.8;">{icon}</div>' if icon else ''
    subtitle_html = f'<div style="color: #6B7280; font-size: 0.75rem;">{subtitle}</div>' if subtitle else ''
    
    # Delta con color según positivo/negativo
    delta_html = ''
    if delta is not None:
        if delta > 0:
            delta_color = "#22C55E"  # Verde
            delta_arrow = "↑"
        elif delta < 0:
            delta_color = "#EF4444"  # Rojo
            delta_arrow = "↓"
        else:
            delta_color = "#9CA3AF"  # Gris
            delta_arrow = "→"
        delta_html = f'<span style="color: {delta_color}; font-size: 0.85rem; margin-left: 8px;">{delta_arrow} {abs(delta):.1f}%</span>'
    
    return f"""
    <div style="
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid #4B5563;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="color: #9CA3AF; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem;">
                    {title}
                </div>
                <div style="color: #F9FAFB; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem;">
                    {value}{delta_html}
                </div>
                {subtitle_html}
            </div>
            {icon_html}
        </div>
    </div>
    """


def calculate_delta(current_value, previous_value):
    """Calcula el cambio porcentual entre dos valores"""
    if previous_value is None or previous_value == 0:
        return None
    return ((current_value - previous_value) / previous_value) * 100


def create_executive_kpis(analytics_data, fecha_inicio=None, fecha_fin=None):
    """
    Crea los KPIs ejecutivos en el formato especificado:
    - Fila 1 (3 cols): Sesiones totales, Usuarios únicos, Crecimiento YoY/MoM/WoW
    - Fila 2 (5 cols): Tiempo medio, Scroll medio, % >60s, % scroll >75%, % recurrentes
    """
    
    if not analytics_data or 'datos_temporales' not in analytics_data:
        st.warning("No hay datos disponibles para mostrar KPIs")
        return
    
    # DataFrame completo (sin filtrar) para cálculos de crecimiento
    df_full = analytics_data['datos_temporales'].copy()
    if 'date' in df_full.columns:
        df_full['date'] = pd.to_datetime(df_full['date'])
    
    # DataFrame filtrado para los demás KPIs (período actual)
    df = df_full.copy()
    df_prev = pd.DataFrame()  # Período anterior para calcular deltas
    
    if fecha_inicio and fecha_fin and 'date' in df.columns:
        fecha_inicio_ts = pd.Timestamp(fecha_inicio)
        fecha_fin_ts = pd.Timestamp(fecha_fin)
        
        # Calcular duración del período seleccionado
        period_days = (fecha_fin_ts - fecha_inicio_ts).days + 1
        
        # Período actual
        mask_current = (df['date'] >= fecha_inicio_ts) & (df['date'] <= fecha_fin_ts)
        df_current = df[mask_current]
        
        # Período anterior (mismo número de días antes del período actual)
        prev_fecha_fin = fecha_inicio_ts - pd.Timedelta(days=1)
        prev_fecha_inicio = prev_fecha_fin - pd.Timedelta(days=period_days - 1)
        mask_prev = (df['date'] >= prev_fecha_inicio) & (df['date'] <= prev_fecha_fin)
        df_prev = df[mask_prev]
        
        if len(df_current) > 0:
            df = df_current
    
    # =====================
    # Calcular métricas del período ACTUAL
    # =====================
    total_sessions = int(df['sessions'].sum()) if 'sessions' in df.columns else 0
    total_users = int(df['totalUsers'].sum()) if 'totalUsers' in df.columns else 0
    new_users = int(df['newUsers'].sum()) if 'newUsers' in df.columns else 0
    avg_session_duration = df['averageSessionDuration'].mean() if 'averageSessionDuration' in df.columns else 0
    engagement_rate = df['engagementRate'].mean() * 100 if 'engagementRate' in df.columns else 0
    bounce_rate = df['bounceRate'].mean() * 100 if 'bounceRate' in df.columns else 0
    engaged_sessions = int(df['engagedSessions'].sum()) if 'engagedSessions' in df.columns else 0
    pct_engaged = (engaged_sessions / total_sessions * 100) if total_sessions > 0 else 0
    returning_users = total_users - new_users
    pct_returning = (returning_users / total_users * 100) if total_users > 0 else 0
    
    # =====================
    # Calcular métricas del período ANTERIOR (para deltas)
    # =====================
    prev_sessions = int(df_prev['sessions'].sum()) if 'sessions' in df_prev.columns and len(df_prev) > 0 else 0
    prev_users = int(df_prev['totalUsers'].sum()) if 'totalUsers' in df_prev.columns and len(df_prev) > 0 else 0
    prev_new_users = int(df_prev['newUsers'].sum()) if 'newUsers' in df_prev.columns and len(df_prev) > 0 else 0
    prev_avg_duration = df_prev['averageSessionDuration'].mean() if 'averageSessionDuration' in df_prev.columns and len(df_prev) > 0 else 0
    prev_engagement_rate = df_prev['engagementRate'].mean() * 100 if 'engagementRate' in df_prev.columns and len(df_prev) > 0 else 0
    prev_bounce_rate = df_prev['bounceRate'].mean() * 100 if 'bounceRate' in df_prev.columns and len(df_prev) > 0 else 0
    prev_engaged_sessions = int(df_prev['engagedSessions'].sum()) if 'engagedSessions' in df_prev.columns and len(df_prev) > 0 else 0
    prev_pct_engaged = (prev_engaged_sessions / prev_sessions * 100) if prev_sessions > 0 else 0
    prev_returning = prev_users - prev_new_users
    prev_pct_returning = (prev_returning / prev_users * 100) if prev_users > 0 else 0
    
    # =====================
    # Calcular DELTAS
    # =====================
    delta_sessions = calculate_delta(total_sessions, prev_sessions)
    delta_users = calculate_delta(total_users, prev_users)
    delta_duration = calculate_delta(avg_session_duration, prev_avg_duration)
    delta_engagement = calculate_delta(engagement_rate, prev_engagement_rate) if prev_engagement_rate > 0 else None
    delta_pct_engaged = calculate_delta(pct_engaged, prev_pct_engaged) if prev_pct_engaged > 0 else None
    delta_deep_scroll = calculate_delta(100 - bounce_rate, 100 - prev_bounce_rate) if (100 - prev_bounce_rate) > 0 else None
    delta_returning = calculate_delta(pct_returning, prev_pct_returning) if prev_pct_returning > 0 else None
    
    # Formato tiempo
    minutes = int(avg_session_duration // 60)
    seconds = int(avg_session_duration % 60)
    avg_session_str = f"{minutes}m {seconds}s"
    
    # =====================
    # Calcular crecimiento WoW/MoM usando TODOS los datos (sin filtro)
    # =====================
    if 'date' in df_full.columns and len(df_full) > 0:
        df_sorted = df_full.sort_values('date')
        today = df_sorted['date'].max()
        
        # WoW (Week over Week) - semana actual vs semana anterior
        week_start = today - pd.Timedelta(days=6)
        prev_week_start = week_start - pd.Timedelta(days=7)
        prev_week_end = week_start - pd.Timedelta(days=1)
        
        current_week = df_sorted[(df_sorted['date'] >= week_start) & (df_sorted['date'] <= today)]
        prev_week = df_sorted[(df_sorted['date'] >= prev_week_start) & (df_sorted['date'] <= prev_week_end)]
        
        current_week_sessions = current_week['sessions'].sum() if len(current_week) > 0 else 0
        prev_week_sessions = prev_week['sessions'].sum() if len(prev_week) > 0 else 0
        
        wow_change = ((current_week_sessions - prev_week_sessions) / prev_week_sessions * 100) if prev_week_sessions > 0 else 0
        
        # MoM (Month over Month) - mes actual vs mes anterior
        month_start = today - pd.Timedelta(days=29)
        prev_month_start = month_start - pd.Timedelta(days=30)
        prev_month_end = month_start - pd.Timedelta(days=1)
        
        current_month = df_sorted[(df_sorted['date'] >= month_start) & (df_sorted['date'] <= today)]
        prev_month = df_sorted[(df_sorted['date'] >= prev_month_start) & (df_sorted['date'] <= prev_month_end)]
        
        current_month_sessions = current_month['sessions'].sum() if len(current_month) > 0 else 0
        prev_month_sessions = prev_month['sessions'].sum() if len(prev_month) > 0 else 0
        
        mom_change = ((current_month_sessions - prev_month_sessions) / prev_month_sessions * 100) if prev_month_sessions > 0 else 0
        
        growth_str = f"WoW: {wow_change:+.1f}% | MoM: {mom_change:+.1f}%"
    else:
        growth_str = "N/A"
    
    # Variables para % scroll profundo
    deep_scroll_pct = 100 - bounce_rate
    
    # =====================
    # FILA 1: 3 KPIs principales
    # =====================
    st.markdown("### KPIs de Tráfico")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(render_kpi_card(
            title="Sesiones Totales",
            value=f"{total_sessions:,}",
            subtitle="Total de sesiones en el período",
            icon="🌐",
            delta=delta_sessions
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_kpi_card(
            title="Usuarios Únicos",
            value=f"{total_users:,}",
            subtitle="Usuarios únicos activos",
            icon="👥",
            delta=delta_users
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_kpi_card(
            title="Crecimiento",
            value=growth_str,
            subtitle="Variación WoW y MoM",
            icon="📈"
        ), unsafe_allow_html=True)
    
    # =====================
    # FILA 2: 5 KPIs de engagement
    # =====================
    st.markdown("### KPIs de Engagement")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(render_kpi_card(
            title="Tiempo Medio/Sesión",
            value=avg_session_str,
            subtitle="Duración promedio",
            icon="⏱️",
            delta=delta_duration
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_kpi_card(
            title="Engagement Rate",
            value=f"{engagement_rate:.1f}%",
            subtitle="Tasa de engagement",
            icon="📊",
            delta=delta_engagement
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_kpi_card(
            title="% Sesiones >60s",
            value=f"{pct_engaged:.1f}%",
            subtitle="Sesiones engaged",
            icon="⏰",
            delta=delta_pct_engaged
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(render_kpi_card(
            title="% Scroll Profundo",
            value=f"{deep_scroll_pct:.1f}%",
            subtitle="No rebotaron",
            icon="📜",
            delta=delta_deep_scroll
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(render_kpi_card(
            title="% Recurrentes",
            value=f"{pct_returning:.1f}%",
            subtitle="Usuarios que regresan",
            icon="🔄",
            delta=delta_returning
        ), unsafe_allow_html=True)


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
            EXECUTIVE DASHBOARD
        </h1>
        <p style="color: white; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            Vista Ejecutiva - Evolución del Negocio
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

    # =====================
    # TABS PRINCIPALES (arriba, debajo del botón)
    # =====================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Tráfico y Visibilidad",
        "Generación de Demanda",
        "Activación Comercial",
        "Performance de Canales",
        "Embudo General",
        "Indicadores de Intención"
    ])
    
    # =====================
    # TAB 1: TRÁFICO Y VISIBILIDAD
    # =====================
    with tab1:
        if 'analytics_data' in st.session_state and st.session_state['analytics_data']:
            from src.visuals.metrics import create_new_vs_returning_chart
            import plotly.graph_objects as go
            
            if 'datos_temporales' in st.session_state['analytics_data'] and not st.session_state['analytics_data']['datos_temporales'].empty:
                
                # Obtener fechas de filtro
                fecha_inicio = st.session_state.get("fecha_inicio")
                fecha_fin = st.session_state.get("fecha_fin")
                
                # Mostrar KPIs ejecutivos
                create_executive_kpis(
                    st.session_state['analytics_data'],
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin
                )
                
                st.markdown("---")
                
                # Preparar datos completos
                df_full = st.session_state['analytics_data']['datos_temporales'].copy()
                if 'date' in df_full.columns:
                    df_full['date'] = pd.to_datetime(df_full['date'])
                
                # Preparar datos filtrados para el gráfico
                temp_df = df_full.copy()
                if fecha_inicio and fecha_fin and "date" in temp_df.columns:
                    mask = (temp_df["date"] >= pd.Timestamp(fecha_inicio)) & (temp_df["date"] <= pd.Timestamp(fecha_fin))
                    temp_df_filtered = temp_df[mask]
                    if len(temp_df_filtered) > 0:
                        temp_df = temp_df_filtered
                
                # =====================
                # GRÁFICO DE COMPARACIÓN PERÍODO ACTUAL VS ANTERIOR
                # =====================
                st.markdown("### Comparación Período Actual vs Anterior")
                
                # Pre-calcular métricas derivadas en el DataFrame
                if 'engagedSessions' in df_full.columns and 'sessions' in df_full.columns:
                    df_full['pct_sessions_60s'] = (df_full['engagedSessions'] / df_full['sessions'] * 100).fillna(0)
                
                if 'bounceRate' in df_full.columns:
                    # bounceRate viene como decimal (0.xx), convertir a porcentaje
                    df_full['pct_scroll_profundo'] = ((1 - df_full['bounceRate']) * 100).clip(lower=0)
                
                if 'newUsers' in df_full.columns and 'totalUsers' in df_full.columns:
                    df_full['pct_recurrentes'] = ((df_full['totalUsers'] - df_full['newUsers']) / df_full['totalUsers'] * 100).fillna(0)
                
                if 'engagementRate' in df_full.columns:
                    # engagementRate viene como decimal (0.xx), convertir a porcentaje
                    df_full['engagement_rate_pct'] = df_full['engagementRate'] * 100
                
                # DEBUG: Ver valores calculados
                with st.expander("🔍 DEBUG: Valores calculados", expanded=False):
                    calc_cols = ['pct_sessions_60s', 'pct_scroll_profundo', 'pct_recurrentes', 'engagement_rate_pct']
                    for col in calc_cols:
                        if col in df_full.columns:
                            st.write(f"**{col}**: min={df_full[col].min():.2f}, max={df_full[col].max():.2f}, mean={df_full[col].mean():.2f}")
                        else:
                            st.write(f"**{col}**: NO SE CALCULÓ")
                
                # Selector de KPI - Las 8 KPIs de los cuadros
                kpi_options = {
                    "Sesiones Totales": {"col": "sessions", "format": "number", "suffix": ""},
                    "Usuarios Únicos": {"col": "totalUsers", "format": "number", "suffix": ""},
                    "Tiempo Medio/Sesión": {"col": "averageSessionDuration", "format": "duration", "suffix": ""},
                    "Engagement Rate": {"col": "engagement_rate_pct", "format": "percent", "suffix": "%"},
                    "% Sesiones >60s": {"col": "pct_sessions_60s", "format": "percent", "suffix": "%"},
                    "% Scroll Profundo": {"col": "pct_scroll_profundo", "format": "percent", "suffix": "%"},
                    "% Recurrentes": {"col": "pct_recurrentes", "format": "percent", "suffix": "%"},
                }
                
                # Filtrar solo las KPIs disponibles en los datos
                available_kpis = {k: v for k, v in kpi_options.items() if v["col"] in df_full.columns}
                
                # DEBUG: Ver qué KPIs están disponibles
                st.write(f"**DEBUG disponibles**: {list(available_kpis.keys())}")
                st.write(f"**DEBUG columnas df_full**: {list(df_full.columns)}")
                
                selected_kpi_name = st.selectbox(
                    "Selecciona la métrica a comparar:",
                    options=list(available_kpis.keys()),
                    key="kpi_comparison_selector"
                )
                selected_kpi_config = available_kpis[selected_kpi_name]
                selected_kpi = selected_kpi_config["col"]
                
                # Crear gráfico de comparación (período actual vs período anterior)
                if fecha_inicio and fecha_fin:
                    fecha_inicio_ts = pd.Timestamp(fecha_inicio)
                    fecha_fin_ts = pd.Timestamp(fecha_fin)
                    
                    # Calcular duración del período
                    period_days = (fecha_fin_ts - fecha_inicio_ts).days + 1
                    
                    # Datos del período actual
                    mask_current = (df_full['date'] >= fecha_inicio_ts) & (df_full['date'] <= fecha_fin_ts)
                    df_current = df_full[mask_current].copy()
                    
                    # Datos del período anterior (mismo número de días antes del período actual)
                    fecha_fin_prev = fecha_inicio_ts - pd.Timedelta(days=1)
                    fecha_inicio_prev = fecha_fin_prev - pd.Timedelta(days=period_days - 1)
                    mask_prev = (df_full['date'] >= fecha_inicio_prev) & (df_full['date'] <= fecha_fin_prev)
                    df_prev = df_full[mask_prev].copy()
                    
                    # Shiftear las fechas del período anterior para alinear con el actual
                    if not df_prev.empty:
                        df_prev['date_shifted'] = df_prev['date'] + pd.Timedelta(days=period_days)
                    
                    # DEBUG: Verificar columna seleccionada
                    st.write(f"**DEBUG**: selected_kpi = `{selected_kpi}`")
                    st.write(f"**DEBUG**: Columna en df_current? {selected_kpi in df_current.columns}")
                    st.write(f"**DEBUG**: Columna en df_prev? {selected_kpi in df_prev.columns}")
                    if selected_kpi in df_current.columns:
                        st.write(f"**DEBUG**: df_current[{selected_kpi}] = {df_current[selected_kpi].tolist()}")
                    
                    # Crear gráfico
                    fig_comparison = go.Figure()
                    
                    # Línea del período actual
                    if not df_current.empty and selected_kpi in df_current.columns:
                        df_current_sorted = df_current.sort_values('date')
                        fig_comparison.add_trace(go.Scatter(
                            x=df_current_sorted['date'],
                            y=df_current_sorted[selected_kpi],
                            mode='lines+markers',
                            name=f'Período Actual ({fecha_inicio_ts.strftime("%d/%m")} - {fecha_fin_ts.strftime("%d/%m")})',
                            line=dict(color='#A7C9C6', width=3),
                            marker=dict(size=8),
                            fill='tozeroy',
                            fillcolor='rgba(167, 201, 198, 0.2)'
                        ))
                    
                    # Línea del período anterior (shifteada para alinear)
                    if not df_prev.empty and selected_kpi in df_prev.columns:
                        df_prev_sorted = df_prev.sort_values('date_shifted')
                        fig_comparison.add_trace(go.Scatter(
                            x=df_prev_sorted['date_shifted'],
                            y=df_prev_sorted[selected_kpi],
                            mode='lines+markers',
                            name=f'Período Anterior ({fecha_inicio_prev.strftime("%d/%m")} - {fecha_fin_prev.strftime("%d/%m")})',
                            line=dict(color='#E7B400', width=3, dash='dash'),
                            marker=dict(size=8)
                        ))
                    
                    # Configurar layout con fondo transparente
                    fig_comparison.update_layout(
                        title={
                            'text': f'{selected_kpi_name} - Período Actual vs Anterior ({period_days} días)',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 18, 'color': 'white'}
                        },
                        xaxis=dict(
                            title='Fecha',
                            titlefont=dict(color='white'),
                            tickfont=dict(color='white'),
                            gridcolor='rgba(128,128,128,0.3)',
                            showgrid=True
                        ),
                        yaxis=dict(
                            title=selected_kpi_name,
                            titlefont=dict(color='white'),
                            tickfont=dict(color='white'),
                            gridcolor='rgba(128,128,128,0.3)',
                            showgrid=True,
                            zeroline=True,
                            zerolinecolor='rgba(128,128,128,0.5)'
                        ),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                            font=dict(color='white')
                        ),
                        hovermode='x unified',
                        height=400,
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    
                    st.plotly_chart(fig_comparison, use_container_width=True)
                    
                    # Mostrar resumen de comparación
                    if not df_current.empty and not df_prev.empty and selected_kpi in df_current.columns:
                        col1, col2, col3 = st.columns(3)
                        
                        kpi_format = selected_kpi_config["format"]
                        
                        # Para métricas de promedio/porcentaje, usar mean
                        if kpi_format in ["percent", "duration"]:
                            current_total = df_current[selected_kpi].mean()
                            prev_total = df_prev[selected_kpi].mean()
                        else:
                            current_total = df_current[selected_kpi].sum()
                            prev_total = df_prev[selected_kpi].sum()
                        
                        change_pct = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
                        
                        # Función para formatear valores según el tipo de KPI
                        def format_kpi_value(value, fmt):
                            if fmt == "duration":
                                return f"{int(value//60)}m {int(value%60)}s"
                            elif fmt == "percent":
                                return f"{value:.1f}%"
                            else:
                                return f"{int(value):,}"
                        
                        with col1:
                            st.metric("Período Actual", format_kpi_value(current_total, kpi_format))
                        
                        with col2:
                            st.metric("Período Anterior", format_kpi_value(prev_total, kpi_format))
                        
                        with col3:
                            st.metric("Variación", f"{change_pct:+.1f}%")
                    elif df_prev.empty:
                        st.info("No hay datos del período anterior para comparar")
                else:
                    st.info("Selecciona un rango de fechas para ver la comparación")
                
                st.markdown("---")
                
                # Gráfico de usuarios nuevos vs recurrentes
                st.markdown("### Usuarios Nuevos vs Recurrentes")
                if len(temp_df) > 0:
                    chart_fig = create_new_vs_returning_chart(temp_df)
                    if chart_fig:
                        st.plotly_chart(chart_fig, use_container_width=True)
                    else:
                        st.warning("No se pudo crear el gráfico con los datos disponibles")
                else:
                    st.warning("No hay datos para mostrar el gráfico")
            else:
                st.warning("No hay datos temporales disponibles")
        else:
            st.info("Carga los datos para ver las métricas de Tráfico y Visibilidad")
    
    # =====================
    # TAB 2: GENERACIÓN DE DEMANDA (LEADS)
    # =====================
    with tab2:
        st.markdown("### Generación de Demanda (Leads)")
        st.info("Contenido próximamente...")
    
    # =====================
    # TAB 3: ACTIVACIÓN COMERCIAL
    # =====================
    with tab3:
        st.markdown("### Activación Comercial")
        st.info("Contenido próximamente...")
    
    # =====================
    # TAB 4: PERFORMANCE DE CANALES
    # =====================
    with tab4:
        st.markdown("### Performance de Canales")
        st.info("Contenido próximamente...")
    
    # =====================
    # TAB 5: EMBUDO GENERAL
    # =====================
    with tab5:
        st.markdown("### Embudo General")
        st.info("Contenido próximamente...")
    
    # =====================
    # TAB 6: INDICADORES DE INTENCIÓN
    # =====================
    with tab6:
        st.markdown("### Indicadores de Intención")
        st.info("Contenido próximamente...")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Growth Intelligence Dashboard - Executive View</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()