"""
Módulo de métricas ejecutivas para el Executive Dashboard
Contiene todas las funciones para KPIs, gráficos y análisis ejecutivo
Integrado con el Design System Crata AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from src.components.sidebar import aplicar_filtros_fecha
from src.config.theme import COLORS as CRATA_COLORS

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

# Eventos definidos como LEADS (actualizados según datos reales)
LEAD_EVENTS = {'form_submit', 'hubspot_form_submit', 'form_start', 'form_bookameeting'}

# Eventos definidos como MEETINGS (actualizados según datos reales)
MEETING_EVENTS = {'form_bookameeting', 'cta_bookameeting'}

# Colores del tema Crata AI - Mapeados desde el Design System central
COLORS = {
    'primary': CRATA_COLORS['chart_primary'],     # Teal Crata
    'secondary': CRATA_COLORS['chart_secondary'], # Amarillo Crata
    'seo': CRATA_COLORS['success'],               # Verde
    'linkedin': '#0077b5', 
    'email': CRATA_COLORS['warning'],             # Naranja
    'eventos': '#6f42c1',
    'paid': CRATA_COLORS['error'],                # Rojo
    'organic': CRATA_COLORS['chart_tertiary'],    # Teal claro
    'social': CRATA_COLORS['info'],               # Azul
    'background': CRATA_COLORS['background_primary'],
    'text': CRATA_COLORS['text_primary'],
}

# ============================================================================
# FUNCIONES HELPER PARA CÁLCULOS TEMPORALES
# ============================================================================

def calcular_mom_robusto(df, columna_fecha, columna_metrica, periodo='M'):
    """
    Calcula la variación mensual (MoM) de forma robusta
    
    Args:
        df: DataFrame con datos temporales
        columna_fecha: str - nombre de la columna de fecha
        columna_metrica: str - nombre de la columna de métrica
        periodo: str - período para agrupar ('M' para mensual, 'D' para diario)
    
    Returns:
        dict: {'valor_actual': float, 'mom_delta': float, 'periodo_actual': str, 'periodo_anterior': str}
    """
    try:
        if df.empty or columna_fecha not in df.columns or columna_metrica not in df.columns:
            return {'valor_actual': 0, 'mom_delta': 0, 'periodo_actual': '', 'periodo_anterior': ''}
        
        # Preparar datos
        df_temp = df.copy()
        df_temp[columna_fecha] = pd.to_datetime(df_temp[columna_fecha])
        
        # Crear columna de período
        if periodo == 'M':
            df_temp['periodo'] = df_temp[columna_fecha].dt.to_period('M')
        elif periodo == 'D':
            df_temp['periodo'] = df_temp[columna_fecha].dt.date
        else:
            df_temp['periodo'] = df_temp[columna_fecha].dt.to_period(periodo)
        
        # Agregar por período
        df_periodo = df_temp.groupby('periodo', as_index=False)[columna_metrica].sum()
        df_periodo = df_periodo.sort_values('periodo')
        
        if len(df_periodo) < 2:
            # Solo hay un período, no se puede calcular MoM
            valor_actual = df_periodo[columna_metrica].iloc[-1] if not df_periodo.empty else 0
            return {'valor_actual': valor_actual, 'mom_delta': 0, 'periodo_actual': str(df_periodo['periodo'].iloc[-1]) if not df_periodo.empty else '', 'periodo_anterior': ''}
        
        # Obtener último período y anterior
        valor_actual = df_periodo[columna_metrica].iloc[-1]
        valor_anterior = df_periodo[columna_metrica].iloc[-2]
        periodo_actual = str(df_periodo['periodo'].iloc[-1])
        periodo_anterior = str(df_periodo['periodo'].iloc[-2])
        
        # Calcular MoM evitando división por cero
        if valor_anterior == 0 or pd.isna(valor_anterior):
            mom_delta = 0
        else:
            mom_delta = ((valor_actual - valor_anterior) / valor_anterior) * 100
        
        return {
            'valor_actual': valor_actual,
            'mom_delta': round(mom_delta, 1),
            'periodo_actual': periodo_actual,
            'periodo_anterior': periodo_anterior
        }
        
    except Exception as e:
        print(f"Error calculando MoM: {str(e)}")
        return {'valor_actual': 0, 'mom_delta': 0, 'periodo_actual': '', 'periodo_anterior': ''}


def calcular_mom_eventos(df_eventos, columna_fecha, eventos_lista, columna_metrica='eventCount'):
    """
    Calcula MoM para eventos específicos
    
    Args:
        df_eventos: DataFrame con eventos
        columna_fecha: str - nombre de la columna de fecha
        eventos_lista: list - lista de eventos a filtrar
        columna_metrica: str - nombre de la columna de métrica
    
    Returns:
        dict: {'valor_actual': float, 'mom_delta': float, 'periodo_actual': str, 'periodo_anterior': str}
    """
    try:
        if df_eventos.empty or columna_fecha not in df_eventos.columns:
            return {'valor_actual': 0, 'mom_delta': 0, 'periodo_actual': '', 'periodo_anterior': ''}
        
        # Filtrar eventos específicos
        df_filtrado = df_eventos[df_eventos['eventName'].isin(eventos_lista)].copy()
        
        if df_filtrado.empty:
            return {'valor_actual': 0, 'mom_delta': 0, 'periodo_actual': '', 'periodo_anterior': ''}
        
        # Calcular MoM usando la función robusta
        return calcular_mom_robusto(df_filtrado, columna_fecha, columna_metrica, periodo='M')
        
    except Exception as e:
        print(f"Error calculando MoM de eventos: {str(e)}")
        return {'valor_actual': 0, 'mom_delta': 0, 'periodo_actual': '', 'periodo_anterior': ''}


# ============================================================================
# CÁLCULOS ADICIONALES: YOY y ROLLING
# ============================================================================

def calcular_yoy_robusto(df, columna_fecha, columna_metrica):
    """Calcula YoY entre el último período (por día) y el mismo rango del año previo."""
    try:
        if df.empty or columna_fecha not in df.columns or columna_metrica not in df.columns:
            return 0.0
        df_tmp = df.copy()
        df_tmp[columna_fecha] = pd.to_datetime(df_tmp[columna_fecha])
        fecha_fin = df_tmp[columna_fecha].max()
        fecha_ini = fecha_fin - pd.Timedelta(days=27)
        rango_actual = df_tmp[(df_tmp[columna_fecha] >= fecha_ini) & (df_tmp[columna_fecha] <= fecha_fin)]
        # Mismo rango LY
        fecha_ini_ly = fecha_ini - pd.DateOffset(years=1)
        fecha_fin_ly = fecha_fin - pd.DateOffset(years=1)
        rango_ly = df_tmp[(df_tmp[columna_fecha] >= fecha_ini_ly) & (df_tmp[columna_fecha] <= fecha_fin_ly)]
        v_act = rango_actual[columna_metrica].sum()
        v_ly = rango_ly[columna_metrica].sum()
        if v_ly == 0 or pd.isna(v_ly):
            return None
        return round(((v_act - v_ly) / v_ly) * 100, 1)
    except Exception:
        return 0.0


def rolling_sum(df, columna_fecha, columna_metrica, window_days=7):
    if df.empty or columna_fecha not in df.columns or columna_metrica not in df.columns:
        return pd.Series(dtype='float')
    tmp = df.copy()
    tmp[columna_fecha] = pd.to_datetime(tmp[columna_fecha])
    tmp = tmp.sort_values(columna_fecha)
    return tmp[columna_metrica].rolling(window=window_days, min_periods=1).sum()


def rango_28d(df, columna_fecha='date'):
    if df.empty or columna_fecha not in df.columns:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    d = df.copy()
    d[columna_fecha] = pd.to_datetime(d[columna_fecha])
    end = d[columna_fecha].max()
    start = end - pd.Timedelta(days=27)
    prev_end = start - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=27)
    ly_start = start - pd.DateOffset(years=1)
    ly_end = end - pd.DateOffset(years=1)
    cur = d[(d[columna_fecha] >= start) & (d[columna_fecha] <= end)]
    prev = d[(d[columna_fecha] >= prev_start) & (d[columna_fecha] <= prev_end)]
    ly = d[(d[columna_fecha] >= ly_start) & (d[columna_fecha] <= ly_end)]
    return (cur, prev, ly)


def fmt_delta_pct(cur_val, prev_val):
    if prev_val is None or prev_val == 0 or pd.isna(prev_val):
        return "—"
    return f"{((cur_val - prev_val) / prev_val) * 100:+.1f}%"


def mini_sparkline(series):
    if series is None or len(series) == 0:
        return None
    fig = go.Figure(go.Scatter(y=series, mode='lines', line=dict(color=COLORS['primary'], width=2)))
    fig.update_layout(height=60, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False), template='plotly_dark')
    return fig


# ============================================================================
# FUNCIONES DE KPIs DEL HEADER
# ============================================================================

def calcular_total_traffic(datos_temporales, datos_engagement):
    """
    Calcula el tráfico total con comparaciones MoM robustas
    
    Args:
        datos_temporales: DataFrame con datos temporales
        datos_engagement: DataFrame con datos de engagement
    
    Returns:
        dict: {'valor': int, 'mom_delta': float, 'yoy_delta': float, 'tendencia': str}
    """
    try:
        # Usar datos_temporales como fuente principal
        if not datos_temporales.empty and 'sessions' in datos_temporales.columns and 'date' in datos_temporales.columns:
            mom_data = calcular_mom_robusto(datos_temporales, 'date', 'sessions', periodo='M')
            traffic_actual = int(mom_data['valor_actual'])
            mom_delta = mom_data['mom_delta']
            
        elif not datos_engagement.empty and 'sessions' in datos_engagement.columns and 'date' in datos_engagement.columns:
            mom_data = calcular_mom_robusto(datos_engagement, 'date', 'sessions', periodo='M')
            traffic_actual = int(mom_data['valor_actual'])
            mom_delta = mom_data['mom_delta']
        else:
            traffic_actual = 0
            mom_delta = 0
        
        # YoY se puede implementar más adelante
        yoy_delta = 0
        
        tendencia = "📈" if mom_delta > 0 else "📉" if mom_delta < 0 else "➡️"
        
        return {
            'valor': traffic_actual,
            'mom_delta': mom_delta,
            'yoy_delta': round(yoy_delta, 1),
            'tendencia': tendencia
        }
        
    except Exception as e:
        st.error(f"Error calculando tráfico total: {str(e)}")
        return {'valor': 0, 'mom_delta': 0, 'yoy_delta': 0, 'tendencia': '❌'}


def calcular_leads_generados(datos_conversiones, datos_engagement):
    """
    Calcula los leads generados usando eventos específicos con MoM robusto
    
    Args:
        datos_conversiones: DataFrame con datos de conversiones
        datos_engagement: DataFrame con datos de engagement
    
    Returns:
        dict: {'valor': int, 'mom_delta': float, 'yoy_delta': float, 'tendencia': str}
    """
    try:
        leads_actual = 0
        mom_delta = 0
        
        if not datos_conversiones.empty and 'eventName' in datos_conversiones.columns and 'date' in datos_conversiones.columns:
            # Usar eventos específicos de lead detectados con MoM
            mom_data = calcular_mom_eventos(datos_conversiones, 'date', list(LEAD_EVENTS), 'eventCount')
            leads_actual = int(mom_data['valor_actual'])
            mom_delta = mom_data['mom_delta']
            
        elif not datos_engagement.empty and 'conversions' in datos_engagement.columns and 'date' in datos_engagement.columns:
            # Fallback a conversions de engagement con MoM
            mom_data = calcular_mom_robusto(datos_engagement, 'date', 'conversions', periodo='M')
            leads_actual = int(mom_data['valor_actual'])
            mom_delta = mom_data['mom_delta']
        
        # YoY se puede implementar más adelante
        yoy_delta = 0
        
        tendencia = "📈" if mom_delta > 0 else "📉" if mom_delta < 0 else "➡️"
        
        return {
            'valor': leads_actual,
            'mom_delta': mom_delta,
            'yoy_delta': round(yoy_delta, 1),
            'tendencia': tendencia
        }
        
    except Exception as e:
        st.error(f"Error calculando leads: {str(e)}")
        return {'valor': 0, 'mom_delta': 0, 'yoy_delta': 0, 'tendencia': '❌'}


def detectar_eventos_meeting(datos_conversiones):
    """
    Detecta automáticamente eventos de reuniones basándose en patrones
    
    Args:
        datos_conversiones: DataFrame con datos de conversiones
    
    Returns:
        list: Lista de eventos de reuniones detectados
    """
    if datos_conversiones.empty or 'eventName' not in datos_conversiones.columns:
        return []
    
    eventos_unicos = datos_conversiones['eventName'].unique()
    
    # Patrones comunes para eventos de reuniones
    patrones_meeting = [
        'meeting', 'calendly', 'book', 'schedule', 'appointment', 
        'demo', 'call', 'consultation', 'meet', 'calendar'
    ]
    
    eventos_meeting = []
    for evento in eventos_unicos:
        evento_lower = str(evento).lower()
        if any(patron in evento_lower for patron in patrones_meeting):
            eventos_meeting.append(evento)
    
    return eventos_meeting


def calcular_reuniones_agendadas(datos_conversiones):
    """
    Calcula las reuniones agendadas usando eventos específicos con MoM robusto
    
    Args:
        datos_conversiones: DataFrame con datos de conversiones
    
    Returns:
        dict: {'valor': int, 'mom_delta': float, 'yoy_delta': float, 'tendencia': str, 'eventos_detectados': list}
    """
    try:
        meetings_actual = 0
        mom_delta = 0
        eventos_detectados = []
        
        if not datos_conversiones.empty and 'eventName' in datos_conversiones.columns:
            # Filtrar eventos de meeting
            df_meetings = datos_conversiones[
                datos_conversiones['eventName'].isin(MEETING_EVENTS)
            ]
            meetings_actual = df_meetings['eventCount'].sum() if 'eventCount' in df_meetings.columns else 0
            eventos_detectados = list(MEETING_EVENTS)
            
            # Intentar calcular MoM si hay columna date
            if 'date' in datos_conversiones.columns:
                mom_data = calcular_mom_eventos(datos_conversiones, 'date', list(MEETING_EVENTS), 'eventCount')
                mom_delta = mom_data['mom_delta']
            else:
                # Sin columna date, mostrar mensaje informativo
                mom_delta = 0
                st.info("ℹ️ MoM no disponible: datos_conversiones necesita columna 'date'. Recarga los datos para habilitar filtros temporales.")
        
        # YoY se puede implementar más adelante
        yoy_delta = 0
        
        tendencia = "📈" if mom_delta > 0 else "📉" if mom_delta < 0 else "➡️"
        
        return {
            'valor': meetings_actual,
            'mom_delta': mom_delta,
            'yoy_delta': round(yoy_delta, 1),
            'tendencia': tendencia,
            'eventos_detectados': eventos_detectados
        }
        
    except Exception as e:
        st.error(f"Error calculando reuniones: {str(e)}")
        return {'valor': 0, 'mom_delta': 0, 'yoy_delta': 0, 'tendencia': '❌', 'eventos_detectados': []}


def calcular_conversion_visita_lead(traffic_data, leads_data):
    """
    Calcula la conversión de visita a lead
    
    Args:
        traffic_data: dict con datos de tráfico
        leads_data: dict con datos de leads
    
    Returns:
        dict: {'valor': float, 'mom_delta': float, 'yoy_delta': float, 'tendencia': str}
    """
    try:
        traffic = traffic_data['valor']
        leads = leads_data['valor']
        
        conversion_rate = (leads / traffic * 100) if traffic > 0 else 0
        
        mom_delta = 0  # Se puede calcular comparando períodos
        yoy_delta = 0
        
        tendencia = "📈" if mom_delta > 0 else "📉" if mom_delta < 0 else "➡️"
        
        return {
            'valor': round(conversion_rate, 2),
            'mom_delta': round(mom_delta, 1),
            'yoy_delta': round(yoy_delta, 1),
            'tendencia': tendencia
        }
        
    except Exception as e:
        st.error(f"Error calculando conversión: {str(e)}")
        return {'valor': 0, 'mom_delta': 0, 'yoy_delta': 0, 'tendencia': '❌'}


def calcular_growth_index(traffic_data, leads_data, meetings_data, datos_temporales):
    """
    Calcula el Growth Index (0-100) combinando tráfico, leads y reuniones
    
    Args:
        traffic_data: dict con datos de tráfico
        leads_data: dict con datos de leads
        meetings_data: dict con datos de reuniones
        datos_temporales: DataFrame para normalización histórica
    
    Returns:
        dict: {'valor': float, 'mom_delta': float, 'yoy_delta': float, 'tendencia': str}
    """
    try:
        # Valores actuales
        traffic_actual = traffic_data['valor']
        leads_actual = leads_data['valor']
        meetings_actual = meetings_data['valor']
        
        # Normalización simple (se puede mejorar con datos históricos)
        # Por ahora usamos valores relativos básicos
        max_traffic = max(traffic_actual, 1000)  # Valor mínimo de referencia
        max_leads = max(leads_actual, 50)
        max_meetings = max(meetings_actual, 10)
        
        z_traffic = traffic_actual / max_traffic
        z_leads = leads_actual / max_leads
        z_meetings = meetings_actual / max_meetings
        
        # Growth Index con ponderaciones: 40% tráfico, 35% leads, 25% meetings
        growth_index = 100 * (0.4 * z_traffic + 0.35 * z_leads + 0.25 * z_meetings)
        
        mom_delta = 0  # Se puede implementar con datos históricos
        yoy_delta = 0
        
        tendencia = "📈" if mom_delta > 0 else "📉" if mom_delta < 0 else "➡️"
        
        return {
            'valor': round(min(growth_index, 100), 1),  # Cap a 100
            'mom_delta': round(mom_delta, 1),
            'yoy_delta': round(yoy_delta, 1),
            'tendencia': tendencia
        }
        
    except Exception as e:
        st.error(f"Error calculando Growth Index: {str(e)}")
        return {'valor': 0, 'mom_delta': 0, 'yoy_delta': 0, 'tendencia': '❌'}


def crear_header_kpis(analytics_data):
    """
    Crea las tarjetas de KPIs del header
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        None (renderiza directamente en Streamlit)
    """
    try:
        # Obtener datos necesarios
        datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
        datos_engagement = analytics_data.get('datos_engagement', pd.DataFrame())
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        # 28D current/prev/LY
        kpis_df = datos_temporales.copy() if not datos_temporales.empty else pd.DataFrame()
        cur, prev, ly = rango_28d(kpis_df) if not kpis_df.empty else (pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        agg_cols = ['sessions','totalUsers','newUsers','screenPageViews','conversions','totalRevenue','engagedSessions','averageSessionDuration','engagementRate','bounceRate','sessionsPerUser','eventCount']
        sums = {c: cur[c].sum() for c in agg_cols if c in cur.columns}
        sums_prev = {c: prev[c].sum() for c in agg_cols if c in prev.columns}
        sums_ly = {c: ly[c].sum() for c in agg_cols if c in ly.columns}

        # Derivadas negocio
        views_per_session = _safe_div(sums.get('screenPageViews',0), sums.get('sessions',0))
        conv_rate_sessions_28 = _safe_div(sums.get('conversions',0), sums.get('sessions',0)) * 100
        lp1k = _safe_div(1000 * sums.get('conversions',0), sums.get('sessions',0))
        new_users_share = _safe_div(sums.get('newUsers',0), sums.get('totalUsers',0)) * 100

        # Calidad (avg 28D) – si vienen ya como medios en GA4, usar mean; si no, proxy con suma/suma
        engagement_rate_avg = cur['engagementRate'].mean() if 'engagementRate' in cur.columns and not cur.empty else 0
        bounce_rate_avg = cur['bounceRate'].mean() if 'bounceRate' in cur.columns and not cur.empty else 0
        avg_session_duration = cur['averageSessionDuration'].mean() if 'averageSessionDuration' in cur.columns and not cur.empty else 0

        engaged_sessions_share = _safe_div(sums.get('engagedSessions',0), sums.get('sessions',0)) * 100
        views_per_session_28 = views_per_session

        # Apoyo
        avg_engagement_time = cur['userEngagementDuration'].mean() if 'userEngagementDuration' in cur.columns and not cur.empty else None
        sessions_per_user = cur['sessionsPerUser'].mean() if 'sessionsPerUser' in cur.columns and not cur.empty else _safe_div(sums.get('sessions',0), sums.get('totalUsers',0))
        events_per_session = _safe_div(sums.get('eventCount',0), sums.get('sessions',0)) if 'eventCount' in sums else None
        
        # Crear layout de KPIs
        st.markdown("### 🧱 Hero KPIs")
        # Bloque A — Negocio (Sessions, Conversions + CR/LP1k, Total Users + %New, Engaged Sessions + Share)
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            cur_ses = int(sums.get('sessions',0))
            prev_ses = int(sums_prev.get('sessions',0)) if 'sessions' in sums_prev else None
            ly_ses = int(sums_ly.get('sessions',0)) if 'sessions' in sums_ly else None
            st.metric("🌐 Sessions (28D)", f"{cur_ses:,}", delta=fmt_delta_pct(cur_ses, prev_ses), help=f"YoY: {fmt_delta_pct(cur_ses, ly_ses)}")
            # sparkline sessions (28D rolling7)
            ses_series = cur['sessions'].rolling(7,1).sum() if not cur.empty and 'sessions' in cur.columns else None
            sp = mini_sparkline(ses_series)
            if sp:
                st.plotly_chart(sp, use_container_width=True)
        with a2:
            cur_conv = int(sums.get('conversions',0))
            prev_conv = int(sums_prev.get('conversions',0)) if 'conversions' in sums_prev else None
            st.metric("🎯 Conversions (28D)", f"{cur_conv:,}", delta=fmt_delta_pct(cur_conv, prev_conv), help=f"CR: {conv_rate_sessions_28:.1f}% | LP1k: {lp1k:.1f}")
            conv_series = cur['conversions'].rolling(7,1).sum() if not cur.empty and 'conversions' in cur.columns else None
            sp2 = mini_sparkline(conv_series)
            if sp2:
                st.plotly_chart(sp2, use_container_width=True)
        with a3:
            cur_users = int(sums.get('totalUsers',0))
            st.metric("👤 Total Users (28D)", f"{cur_users:,}", help=f"% New: {new_users_share:.1f}%")
            users_series = cur['totalUsers'].rolling(7,1).sum() if not cur.empty and 'totalUsers' in cur.columns else None
            sp3 = mini_sparkline(users_series)
            if sp3:
                st.plotly_chart(sp3, use_container_width=True)
        with a4:
            cur_eng = int(sums.get('engagedSessions',0))
            st.metric("✅ Engaged Sessions (28D)", f"{cur_eng:,}", help=f"Engaged Share: {engaged_sessions_share:.1f}%")
            eng_series = cur['engagedSessions'].rolling(7,1).sum() if not cur.empty and 'engagedSessions' in cur.columns else None
            sp4 = mini_sparkline(eng_series)
            if sp4:
                st.plotly_chart(sp4, use_container_width=True)

        # Bloque B — Engagement / Calidad
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.metric("⚡ Engagement Rate (avg 28D)", f"{engagement_rate_avg:.1f}%")
        with b2:
            st.metric("⏱️ Avg Session Duration", f"{avg_session_duration:.0f}s")
        with b3:
            st.metric("↩️ Bounce Rate (avg 28D)", f"{bounce_rate_avg:.1f}%")
        with b4:
            st.metric("👁️ Views/Session", f"{views_per_session_28:.2f}")

        # Bloque C — Apoyo (opcional)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("👁️ Views/Session", f"{views_per_session_28:.2f}")
        with c2:
            if avg_engagement_time is not None:
                st.metric("🕒 Avg Engagement Time", f"{avg_engagement_time:.0f}s")
        with c3:
            st.metric("👥 Sessions/User (avg)", f"{sessions_per_user:.2f}")
        with c4:
            if events_per_session is not None:
                st.metric("🎛️ Events/Session", f"{events_per_session:.2f}")
        
    except Exception as e:
        st.error(f"Error creando header KPIs: {str(e)}")


# ============================================================================
# FUNCIONES DE GRÁFICOS DE EVOLUCIÓN TEMPORAL
# ============================================================================

def crear_grafico_evolucion_temporal(analytics_data):
    """
    Crea el gráfico de evolución temporal de tráfico, leads y reuniones
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        plotly.graph_objects.Figure: Gráfico de evolución
    """
    try:
        datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        if datos_temporales.empty:
            st.warning("⚠️ No hay datos temporales disponibles")
            return None
        
        # Preparar datos temporales
        df_temp = datos_temporales.copy()
        df_temp['date'] = pd.to_datetime(df_temp['date'])
        df_temp = df_temp.sort_values('date')
        
        # Derivados rolling 7
        df_temp['sessions_7d_roll'] = df_temp['sessions'].rolling(window=7, min_periods=1).sum() if 'sessions' in df_temp.columns else 0
        if 'conversions' in df_temp.columns:
            df_temp['conversions_7d_roll'] = df_temp['conversions'].rolling(window=7, min_periods=1).sum()
        if 'totalRevenue' in df_temp.columns:
            df_temp['revenue_7d_roll'] = df_temp['totalRevenue'].rolling(window=7, min_periods=1).sum()

        # Crear gráfico simple
        fig = go.Figure()
        
        # Gráfico de tráfico
        fig.add_trace(
            go.Scatter(
                x=df_temp['date'],
                y=df_temp['sessions'],
                mode='lines+markers',
                name='Tráfico',
                line=dict(color=COLORS['primary'], width=3),
                marker=dict(size=6)
            )
        )
        
        # Líneas adicionales rolling
        if 'conversions_7d_roll' in df_temp.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_temp['date'],
                    y=df_temp['conversions_7d_roll'],
                    mode='lines',
                    name='Conversions (7d roll)',
                    line=dict(color=COLORS['seo'], width=2, dash='dot')
                )
            )
        if 'revenue_7d_roll' in df_temp.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_temp['date'],
                    y=df_temp['revenue_7d_roll'],
                    mode='lines',
                    name='Revenue (7d roll)',
                    line=dict(color=COLORS['email'], width=2, dash='dash')
                )
            )
        
        # Configurar ejes
        fig.update_xaxes(title_text="Fecha")
        fig.update_yaxes(title_text="Sesiones / Rolling")
        
        # Configurar layout
        fig.update_layout(
            title="Evolución Temporal del Tráfico",
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            template='plotly_dark'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creando gráfico de evolución temporal: {str(e)}")
        return None


# ============================================================================
# FUNCIONES DE FUENTES DE OPORTUNIDAD POR CANAL
# ============================================================================

def derivar_canal(source, medium):
    """
    Deriva el canal basado en source y medium
    
    Args:
        source: str - fuente de tráfico
        medium: str - medio de tráfico
    
    Returns:
        str: Canal derivado
    """
    source_lower = str(source).lower()
    medium_lower = str(medium).lower()
    
    if 'linkedin' in source_lower or 'linkedin' in medium_lower:
        return 'LinkedIn'
    elif 'google' in source_lower and 'organic' in medium_lower:
        return 'SEO'
    elif 'email' in medium_lower or 'mail' in medium_lower:
        return 'Email'
    elif 'event' in source_lower or 'event' in medium_lower:
        return 'Eventos'
    elif 'cpc' in medium_lower or 'paid' in medium_lower:
        return 'Paid'
    elif 'social' in medium_lower:
        return 'Social'
    elif 'organic' in medium_lower:
        return 'SEO'
    else:
        return 'Otros'


def crear_grafico_fuentes_oportunidad(analytics_data):
    """
    Crea el gráfico de fuentes de oportunidad por canal
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        plotly.graph_objects.Figure: Gráfico de fuentes
    """
    try:
        datos_trafico = analytics_data.get('datos_trafico', pd.DataFrame())
        datos_campanas = analytics_data.get('datos_campanas', pd.DataFrame())
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        if datos_trafico.empty:
            st.warning("⚠️ No hay datos de tráfico disponibles")
            return None
        
        # Preparar datos de sesiones por canal
        df_trafico = datos_trafico.copy()
        
        # Derivar canal si no existe sessionDefaultChannelGrouping
        if 'sessionDefaultChannelGrouping' not in df_trafico.columns:
            if 'sessionSource' in df_trafico.columns and 'sessionMedium' in df_trafico.columns:
                df_trafico['canal'] = df_trafico.apply(
                    lambda row: derivar_canal(row['sessionSource'], row['sessionMedium']), 
                    axis=1
                )
            else:
                st.warning("⚠️ No se pueden derivar canales sin source/medium")
                return None
        else:
            df_trafico['canal'] = df_trafico['sessionDefaultChannelGrouping']
        
        # Agregar sesiones por canal
        sesiones_por_canal = df_trafico.groupby('canal')['sessions'].sum().reset_index()
        sesiones_por_canal = sesiones_por_canal.sort_values('sessions', ascending=True)
        
        # Preparar datos de leads por canal (simplificado)
        leads_por_canal = pd.DataFrame()
        if not datos_conversiones.empty:
            # Para simplificar, distribuimos leads proporcionalmente por sesiones
            total_leads = datos_conversiones[
                datos_conversiones['eventName'].str.lower().isin([e.lower() for e in LEAD_EVENTS])
            ]['eventCount'].sum()
            
            if total_leads > 0:
                leads_por_canal = sesiones_por_canal.copy()
                leads_por_canal['leads'] = (leads_por_canal['sessions'] / sesiones_por_canal['sessions'].sum() * total_leads).round()
        
        # Crear gráfico de barras horizontales
        fig = go.Figure()
        
        # Barras de sesiones
        fig.add_trace(go.Bar(
            y=sesiones_por_canal['canal'],
            x=sesiones_por_canal['sessions'],
            name='Sesiones',
            orientation='h',
            marker_color=COLORS['primary'],
            opacity=0.7
        ))
        
        # Barras de leads si están disponibles
        if not leads_por_canal.empty:
            fig.add_trace(go.Bar(
                y=leads_por_canal['canal'],
                x=leads_por_canal['leads'],
                name='Leads',
                orientation='h',
                marker_color=COLORS['seo'],
                opacity=0.8
            ))
        
        # Configurar layout
        fig.update_layout(
            title="Fuentes de Oportunidad por Canal",
            xaxis_title="Cantidad",
            yaxis_title="Canal",
            height=400,
            barmode='group',
            template='plotly_dark',
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creando gráfico de fuentes de oportunidad: {str(e)}")
        return None


# ============================================================================
# FUNCIONES DE EMBUDO GLOBAL
# ============================================================================

def crear_grafico_embudo_global(analytics_data):
    """
    Crea el gráfico de embudo global
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        plotly.graph_objects.Figure: Gráfico de embudo
    """
    try:
        datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        if datos_temporales.empty:
            st.warning("⚠️ No hay datos temporales disponibles")
            return None
        
        # Calcular etapas del embudo
        visitas = datos_temporales['sessions'].sum()
        
        leads = 0
        if not datos_conversiones.empty and 'eventName' in datos_conversiones.columns:
            df_leads = datos_conversiones[
                datos_conversiones['eventName'].str.lower().isin([e.lower() for e in LEAD_EVENTS])
            ]
            leads = df_leads['eventCount'].sum() if 'eventCount' in df_leads.columns else 0
        
        meetings = 0
        if not datos_conversiones.empty and 'eventName' in datos_conversiones.columns:
            df_meetings = datos_conversiones[
                datos_conversiones['eventName'].str.lower().isin([e.lower() for e in MEETING_EVENTS])
            ]
            meetings = df_meetings['eventCount'].sum() if 'eventCount' in df_meetings.columns else 0
        
        # Crear datos del embudo
        etapas = ['Visitas', 'Leads', 'Reuniones']
        valores = [visitas, leads, meetings]
        
        # Calcular tasas de conversión
        tasa_visit_lead = (leads / visitas * 100) if visitas > 0 else 0
        tasa_lead_meeting = (meetings / leads * 100) if leads > 0 else 0
        tasa_visit_meeting = (meetings / visitas * 100) if visitas > 0 else 0
        
        # Crear gráfico de embudo
        fig = go.Figure(go.Funnel(
            y=etapas,
            x=valores,
            textinfo="value+percent initial",
            marker=dict(
                color=[COLORS['primary'], COLORS['seo'], COLORS['linkedin']],
                line=dict(width=2, color="white")
            ),
            connector=dict(line=dict(color="royalblue", dash="dot", width=3))
        ))
        
        # Configurar layout
        fig.update_layout(
            title="Embudo Global de Conversión",
            height=400,
            template='plotly_dark',
            showlegend=False
        )
        
        # Agregar anotaciones con tasas
        fig.add_annotation(
            x=leads/2, y=1.5,
            text=f"V→L: {tasa_visit_lead:.1f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor="white"
        )
        
        fig.add_annotation(
            x=meetings/2, y=0.5,
            text=f"L→M: {tasa_lead_meeting:.1f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor="white"
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creando gráfico de embudo global: {str(e)}")
        return None


# ============================================================================
# GRÁFICOS ADICIONALES: GEO MAPA, CANALES SHARE, CONTENIDO TOP
# ============================================================================

def crear_mapa_geo(analytics_data):
    """
    Choropleth mundial por país (sesiones) estilo GA.
    """
    try:
        datos_geo = analytics_data.get('datos_geograficos', pd.DataFrame())
        if datos_geo.empty or 'country' not in datos_geo.columns or 'sessions' not in datos_geo.columns:
            return None
        df = datos_geo.copy()
        # Agregar por país
        geo = df.groupby('country', as_index=False)['sessions'].sum()
        fig = px.choropleth(
            geo,
            locations='country',
            locationmode='country names',
            color='sessions',
            color_continuous_scale=px.colors.sequential.Blues,
            title='Sesiones por País',
        )
        fig.update_layout(height=420, template='plotly_dark')
        return fig
    except Exception as e:
        st.error(f"Error creando mapa geo: {str(e)}")
        return None


def crear_chart_canales_share(analytics_data, top_n=10):
    """Bar chart de share de sesiones por canal."""
    datos_trafico = analytics_data.get('datos_trafico', pd.DataFrame())
    if datos_trafico.empty:
        return None
    df = datos_trafico.copy()
    if 'sessionDefaultChannelGrouping' in df.columns:
        df['canal'] = df['sessionDefaultChannelGrouping']
    elif 'sessionSource' in df.columns and 'sessionMedium' in df.columns:
        df['canal'] = df.apply(lambda r: derivar_canal(r['sessionSource'], r['sessionMedium']), axis=1)
    else:
        return None
    grp = df.groupby('canal', as_index=False)['sessions'].sum()
    total = grp['sessions'].sum()
    if total == 0:
        return None
    grp['share'] = grp['sessions'] / total * 100
    grp = grp.sort_values('sessions', ascending=True).tail(top_n)
    fig = px.bar(grp, x='sessions', y='canal', orientation='h', color='share',
                 color_continuous_scale=px.colors.sequential.Blues,
                 title='Sesiones por Canal (share %)')
    fig.update_layout(height=420, template='plotly_dark')
    fig.update_traces(hovertemplate='%{y}<br>Sessions=%{x:,}<br>Share=%{marker.color:.1f}%')
    return fig


def crear_chart_top_contenido(analytics_data, top_n=15):
    """Bar chart top páginas por vistas."""
    datos_contenido = analytics_data.get('datos_contenido', pd.DataFrame())
    if datos_contenido.empty or 'pagePath' not in datos_contenido.columns:
        return None
    df = datos_contenido.copy()
    if 'screenPageViews' not in df.columns and 'sessions' in df.columns:
        df['screenPageViews'] = df['sessions']
    grp = df.groupby('pagePath', as_index=False)['screenPageViews'].sum()
    grp = grp.sort_values('screenPageViews', ascending=True).tail(top_n)
    fig = px.bar(grp, x='screenPageViews', y='pagePath', orientation='h', title='Top Contenido por PageViews')
    fig.update_layout(height=600, template='plotly_dark')
    fig.update_traces(marker_color=COLORS['primary'])
    return fig


# ============================================================================
# VISUALES: DUMBBELL (Actual vs LY) y BULLET (metas)
# ============================================================================

def crear_dumbbell_actual_vs_ly(analytics_data):
    """
    Dumbbell chart: LY vs Actual para KPIs clave (Sessions, Conversions, Revenue, Engagement Rate)
    """
    datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
    if datos_temporales.empty or 'date' not in datos_temporales.columns:
        return None
    df = datos_temporales.copy()
    df['date'] = pd.to_datetime(df['date'])
    cur, _, ly = rango_28d(df)
    kpis = []
    # Sessions
    if 'sessions' in df.columns:
        kpis.append(('Sessions', cur['sessions'].sum(), ly['sessions'].sum() if not ly.empty else 0))
    # Conversions
    if 'conversions' in df.columns:
        kpis.append(('Conversions', cur['conversions'].sum(), ly['conversions'].sum() if not ly.empty else 0))
    # Revenue
    if 'totalRevenue' in df.columns:
        kpis.append(('Revenue', cur['totalRevenue'].sum(), ly['totalRevenue'].sum() if not ly.empty else 0))
    # Engagement Rate (avg)
    if 'engagementRate' in df.columns:
        kpis.append(('Engagement Rate', cur['engagementRate'].mean() if not cur.empty else 0, ly['engagementRate'].mean() if not ly.empty else 0))

    if not kpis:
        return None

    names = [k[0] for k in kpis]
    actuals = [k[1] for k in kpis]
    lys = [k[2] for k in kpis]

    fig = go.Figure()
    for i, name in enumerate(names):
        # línea conectora
        fig.add_shape(type='line', x0=lys[i], x1=actuals[i], y0=i, y1=i, line=dict(color='#777', width=3))
        # LY punto
        fig.add_trace(go.Scatter(x=[lys[i]], y=[i], mode='markers', marker=dict(color='#bbb', size=10), name='LY' if i==0 else None, showlegend=(i==0), hovertemplate=f"{name} LY: %{{x}}<extra></extra>"))
        # Actual punto
        fig.add_trace(go.Scatter(x=[actuals[i]], y=[i], mode='markers', marker=dict(color=COLORS['primary'], size=12), name='Actual' if i==0 else None, showlegend=(i==0), hovertemplate=f"{name} Actual: %{{x}}<extra></extra>"))

    fig.update_yaxes(tickvals=list(range(len(names))), ticktext=names)
    fig.update_layout(title='Actual vs LY (28D)', height=360 + 20*len(names), template='plotly_dark')
    return fig


def crear_bullets_engagement_bounce(analytics_data):
    """
    Bullet charts para Engagement Rate y Bounce Rate contra mediana 6 meses.
    """
    datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
    if datos_temporales.empty or 'date' not in datos_temporales.columns:
        return None
    df = datos_temporales.copy()
    df['date'] = pd.to_datetime(df['date'])
    six_months_ago = df['date'].max() - pd.DateOffset(months=6)
    hist = df[df['date'] >= six_months_ago]
    cur, _, _ = rango_28d(df)
    figs = []
    for kpi, label in [('engagementRate', 'Engagement Rate'), ('bounceRate', 'Bounce Rate')]:
        if kpi in df.columns and not cur.empty and not hist.empty:
            target = hist[kpi].median()
            actual = cur[kpi].mean()
            # Bullet como bar + shape de objetivo
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[actual], y=[label], orientation='h', marker_color=COLORS['primary'], name='Actual'))
            fig.add_shape(type='line', x0=target, x1=target, y0=-0.4, y1=0.4, line=dict(color='white', width=3))
            fig.update_layout(title=f'{label} vs Target (6M median)', height=120, template='plotly_dark', showlegend=False)
            figs.append(fig)
    return figs if figs else None


# ============================================================================
# HEATMAP: Lead Rate por hora (fallback a Engaged Share si no hay conversions)
# ============================================================================

def crear_heatmap_cr_por_hora(analytics_data):
    """
    Heatmap de Lead Rate (%) por hour. Si no hay conversions por hora,
    usa engagedSessions/sessions como proxy (Engaged Share %).
    """
    try:
        datos_hora = analytics_data.get('datos_horarios', pd.DataFrame())
        if datos_hora.empty or 'hour' not in datos_hora.columns or 'sessions' not in datos_hora.columns:
            return None, None
        df = datos_hora.copy()
        # Normalizar hour a 0-23 si viene como string
        df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
        df = df.dropna(subset=['hour'])
        df['hour'] = df['hour'].astype(int) % 24

        titulo = 'Lead Rate (%) por Hora'
        if 'conversions' in df.columns:
            df['lead_rate'] = df.apply(lambda r: _safe_div(r.get('conversions', 0), r.get('sessions', 0)) * 100, axis=1)
        elif 'engagedSessions' in df.columns:
            df['lead_rate'] = df.apply(lambda r: _safe_div(r.get('engagedSessions', 0), r.get('sessions', 0)) * 100, axis=1)
            titulo = 'Engaged Share (%) por Hora'
        else:
            return None, None

        # Agregar por hora (promedio si hay múltiples fechas)
        heat = df.groupby('hour', as_index=False)['lead_rate'].mean()
        heat = heat.sort_values('hour').reset_index(drop=True)
        heat['lead_rate'] = heat['lead_rate'].fillna(0)

        z_vals = [heat['lead_rate'].values]
        fig = go.Figure(data=go.Heatmap(
            z=z_vals,
            x=heat['hour'].values,
            y=[''],
            colorscale='Blues',
            colorbar=dict(title='%'),
            zmin=0,
            zmax=100
        ))
        fig.update_layout(title=titulo, height=240, template='plotly_dark', yaxis=dict(showticklabels=False))
        return fig, titulo
    except Exception as e:
        st.error(f"Error creando heatmap por hora: {str(e)}")
        return None, None

# ============================================================================
# FUNCIONES DE TABLA EJECUTIVA
# ============================================================================

def crear_tabla_ejecutiva(analytics_data):
    """
    Crea la tabla ejecutiva comparativa por canal
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        pandas.DataFrame: Tabla ejecutiva
    """
    try:
        datos_trafico = analytics_data.get('datos_trafico', pd.DataFrame())
        datos_campanas = analytics_data.get('datos_campanas', pd.DataFrame())
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        if datos_trafico.empty:
            st.warning("⚠️ No hay datos de tráfico disponibles")
            return pd.DataFrame()
        
        # Preparar datos de sesiones por canal
        df_trafico = datos_trafico.copy()
        
        # Derivar canal
        if 'sessionDefaultChannelGrouping' not in df_trafico.columns:
            if 'sessionSource' in df_trafico.columns and 'sessionMedium' in df_trafico.columns:
                df_trafico['canal'] = df_trafico.apply(
                    lambda row: derivar_canal(row['sessionSource'], row['sessionMedium']), 
                    axis=1
                )
            else:
                return pd.DataFrame()
        else:
            df_trafico['canal'] = df_trafico['sessionDefaultChannelGrouping']
        
        # Agregar datos por canal
        tabla_ejecutiva = df_trafico.groupby('canal').agg({
            'sessions': 'sum',
            'totalUsers': 'sum',
            'conversions': 'sum' if 'conversions' in df_trafico.columns else lambda x: 0,
            'engagedSessions': 'sum' if 'engagedSessions' in df_trafico.columns else lambda x: 0
        }).reset_index()
        
        # Calcular métricas derivadas
        tabla_ejecutiva['Conv_V→L'] = (
            tabla_ejecutiva['conversions'] / tabla_ejecutiva['sessions'] * 100
        ).round(2)
        
        tabla_ejecutiva['Engagement_Rate'] = (
            tabla_ejecutiva['engagedSessions'] / tabla_ejecutiva['sessions'] * 100
        ).round(2)
        
        # Renombrar columnas
        tabla_ejecutiva.columns = [
            'Canal', 'Sesiones', 'Usuarios', 'Conversiones', 'Sesiones_Engaged',
            'Conv_V→L (%)', 'Engagement_Rate (%)'
        ]
        
        # Ordenar por sesiones
        tabla_ejecutiva = tabla_ejecutiva.sort_values('Sesiones', ascending=False)
        
        return tabla_ejecutiva
        
    except Exception as e:
        st.error(f"Error creando tabla ejecutiva: {str(e)}")
        return pd.DataFrame()


# ============================================================================
# TABLAS ADICIONALES SEGÚN ESQUEMA (daily traffic, contenido, campañas)
# ============================================================================

def _safe_div(numerador, denominador):
    if denominador is None or denominador == 0 or pd.isna(denominador):
        return 0
    return numerador / denominador


def crear_tabla_daily_traffic(analytics_data):
    """
    Tabla de fact_daily_traffic (grano diario) con métricas derivadas clave.
    """
    datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
    if datos_temporales.empty or 'date' not in datos_temporales.columns:
        return pd.DataFrame()

    df = datos_temporales.copy()
    # Asegurar tipos
    df['date'] = pd.to_datetime(df['date'])
    # Derivadas
    df['views_per_session'] = df.apply(lambda r: _safe_div(r.get('screenPageViews', 0), r.get('sessions', 0)), axis=1)
    df['engaged_sessions_share'] = df.apply(lambda r: _safe_div(r.get('engagedSessions', 0), r.get('sessions', 0)), axis=1)
    df['conv_rate_sessions'] = df.apply(lambda r: _safe_div(r.get('conversions', 0), r.get('sessions', 0)), axis=1)
    df['conv_rate_users'] = df.apply(lambda r: _safe_div(r.get('conversions', 0), r.get('totalUsers', 0)), axis=1)
    df['revenue_per_user'] = df.apply(lambda r: _safe_div(r.get('totalRevenue', 0), r.get('totalUsers', 0)), axis=1)
    df['revenue_per_session'] = df.apply(lambda r: _safe_div(r.get('totalRevenue', 0), r.get('sessions', 0)), axis=1)

    columnas = [
        'date', 'sessions', 'totalUsers', 'newUsers', 'screenPageViews', 'conversions', 'totalRevenue',
        'views_per_session', 'engaged_sessions_share', 'conv_rate_sessions', 'conv_rate_users',
        'averageSessionDuration', 'engagementRate', 'bounceRate', 'sessionsPerUser'
    ]
    columnas_presentes = [c for c in columnas if c in df.columns]
    tabla = df[columnas_presentes].sort_values('date', ascending=False)
    # Formateos porcentuales a posteriori en UI
    return tabla


def crear_tabla_top_contenido(analytics_data):
    """
    Tabla de fact_content por página con métricas derivadas.
    """
    datos_contenido = analytics_data.get('datos_contenido', pd.DataFrame())
    if datos_contenido.empty or 'pagePath' not in datos_contenido.columns:
        return pd.DataFrame()

    df = datos_contenido.copy()
    df['views_per_session'] = df.apply(lambda r: _safe_div(r.get('screenPageViews', 0), r.get('sessions', 0)), axis=1)
    df['avg_time_on_page_proxy'] = df.apply(lambda r: _safe_div(r.get('userEngagementDuration', 0), r.get('screenPageViews', 0)), axis=1)
    df['engaged_share'] = df.apply(lambda r: _safe_div(r.get('engagedSessions', 0), r.get('sessions', 0)), axis=1)

    columnas = [
        'pagePath', 'pageTitle', 'landingPage', 'screenPageViews', 'sessions',
        'views_per_session', 'avg_time_on_page_proxy', 'engaged_share', 'bounceRate', 'averageSessionDuration'
    ]
    columnas_presentes = [c for c in columnas if c in df.columns]
    tabla = df[columnas_presentes].sort_values('screenPageViews', ascending=False).head(50)
    return tabla


def crear_tabla_campanas(analytics_data):
    """
    Tabla de fact_campaigns con métricas derivadas.
    """
    datos_campanas = analytics_data.get('datos_campanas', pd.DataFrame())
    if datos_campanas.empty:
        return pd.DataFrame()

    df = datos_campanas.copy()
    df['conv_rate_sessions'] = df.apply(lambda r: _safe_div(r.get('conversions', 0), r.get('sessions', 0)), axis=1)
    df['revenue_per_session'] = df.apply(lambda r: _safe_div(r.get('totalRevenue', 0), r.get('sessions', 0)), axis=1)
    df['revenue_per_user'] = df.apply(lambda r: _safe_div(r.get('totalRevenue', 0), r.get('totalUsers', 0)), axis=1)
    df['engaged_sessions_share'] = df.apply(lambda r: _safe_div(r.get('engagedSessions', 0), r.get('sessions', 0)), axis=1)

    columnas = [
        'sessionCampaignName', 'sessionSource', 'sessionMedium', 'landingPagePlusQueryString',
        'sessions', 'conversions', 'totalRevenue', 'conv_rate_sessions', 'revenue_per_session',
        'revenue_per_user', 'engagedSessions', 'engaged_sessions_share', 'bounceRate'
    ]
    columnas_presentes = [c for c in columnas if c in df.columns]
    tabla = df[columnas_presentes].sort_values('sessions', ascending=False).head(50)
    return tabla


# ============================================================================
# FUNCIONES DE INSIGHT CARDS
# ============================================================================

def generar_insights_automaticos(analytics_data):
    """
    Genera insights automáticos basados en los datos
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        list: Lista de insights en formato texto
    """
    try:
        insights = []
        
        datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
        datos_trafico = analytics_data.get('datos_trafico', pd.DataFrame())
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        # Insight 1: Canal con mayor tráfico
        if not datos_trafico.empty:
            if 'sessionDefaultChannelGrouping' in datos_trafico.columns:
                canal_top = datos_trafico.groupby('sessionDefaultChannelGrouping')['sessions'].sum().idxmax()
                sessions_top = datos_trafico.groupby('sessionDefaultChannelGrouping')['sessions'].sum().max()
                insights.append(f"🔹 {canal_top} lidera el tráfico con {sessions_top:,} sesiones")
        
        # Insight 2: Tendencia de conversión
        if not datos_conversiones.empty and 'eventName' in datos_conversiones.columns:
            total_leads = datos_conversiones[
                datos_conversiones['eventName'].str.lower().isin([e.lower() for e in LEAD_EVENTS])
            ]['eventCount'].sum()
            
            if total_leads > 0:
                insights.append(f"🔹 Se generaron {total_leads:,} leads en el período analizado")
        
        # Insight 3: Engagement rate
        if not datos_temporales.empty and 'engagementRate' in datos_temporales.columns:
            avg_engagement = datos_temporales['engagementRate'].mean()
            insights.append(f"🔹 Engagement rate promedio: {avg_engagement:.1f}%")
        
        # Insight 4: Bounce rate
        if not datos_temporales.empty and 'bounceRate' in datos_temporales.columns:
            avg_bounce = datos_temporales['bounceRate'].mean()
            if avg_bounce < 50:
                insights.append(f"🔹 Bounce rate bajo ({avg_bounce:.1f}%) - buen engagement")
            else:
                insights.append(f"🔹 Bounce rate alto ({avg_bounce:.1f}%) - revisar contenido")
        
        return insights
        
    except Exception as e:
        st.error(f"Error generando insights: {str(e)}")
        return ["🔹 Error generando insights automáticos"]


def mostrar_insight_cards(analytics_data):
    """
    Muestra las tarjetas de insights automáticos
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        None (renderiza directamente en Streamlit)
    """
    try:
        insights = generar_insights_automaticos(analytics_data)
        
        st.markdown("### 💬 Insights Automáticos")
        
        for insight in insights:
            st.info(insight)
        
    except Exception as e:
        st.error(f"Error mostrando insight cards: {str(e)}")


# ============================================================================
# FUNCIÓN PRINCIPAL DE RENDERIZADO
# ============================================================================

def debug_eventos_disponibles(analytics_data):
    """
    Función de debug para mostrar todos los eventos disponibles
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        None (renderiza directamente en Streamlit)
    """
    try:
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        if datos_conversiones.empty:
            st.warning("⚠️ No hay datos de conversiones disponibles")
            return
        
        st.markdown("### 🔍 Debug: Eventos Disponibles")
        
        if 'eventName' in datos_conversiones.columns:
            eventos_unicos = datos_conversiones['eventName'].unique()
            st.write(f"**Total de eventos únicos:** {len(eventos_unicos)}")
            st.write("**Eventos encontrados:**")
            for evento in sorted(eventos_unicos):
                st.write(f"- {evento}")
            
            # Buscar eventos relacionados con meetings
            eventos_meeting = [e for e in eventos_unicos if any(palabra in e.lower() for palabra in ['meeting', 'calendly', 'book', 'schedule', 'appointment'])]
            if eventos_meeting:
                st.success(f"✅ Eventos de reuniones encontrados: {eventos_meeting}")
            else:
                st.warning("⚠️ No se encontraron eventos específicos de reuniones")
                
            # Buscar eventos relacionados con leads
            eventos_lead = [e for e in eventos_unicos if any(palabra in e.lower() for palabra in ['lead', 'form', 'submit', 'contact'])]
            if eventos_lead:
                st.info(f"ℹ️ Eventos de leads encontrados: {eventos_lead}")
        else:
            st.error("❌ No hay columna 'eventName' en datos_conversiones")
            
    except Exception as e:
        st.error(f"Error en debug de eventos: {str(e)}")


def debug_reuniones_detallado(analytics_data):
    """
    Debug detallado para diagnosticar por qué las reuniones dan 0
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        None (renderiza directamente en Streamlit)
    """
    try:
        datos_conversiones = analytics_data.get('datos_conversiones', pd.DataFrame())
        
        st.markdown("### 🔍 Debug Detallado: Reuniones")
        
        if datos_conversiones.empty:
            st.error("❌ datos_conversiones está vacío")
            return
        
        st.write(f"**Total de filas en datos_conversiones:** {len(datos_conversiones)}")
        st.write(f"**Columnas disponibles:** {list(datos_conversiones.columns)}")
        
        # Verificar eventos de meeting
        if 'eventName' in datos_conversiones.columns:
            eventos_meeting = datos_conversiones[
                datos_conversiones['eventName'].isin(MEETING_EVENTS)
            ]
            st.write(f"**Filas con eventos de meeting:** {len(eventos_meeting)}")
            
            if not eventos_meeting.empty:
                st.write("**Eventos de meeting encontrados:**")
                st.dataframe(eventos_meeting[['eventName', 'eventCount']].head(10))
                
                total_meetings = eventos_meeting['eventCount'].sum() if 'eventCount' in eventos_meeting.columns else 0
                st.write(f"**Total de meetings (suma eventCount):** {total_meetings}")
            else:
                st.warning("⚠️ No se encontraron filas con eventos de meeting")
                st.write("**Eventos disponibles:**")
                st.write(datos_conversiones['eventName'].unique())
        else:
            st.error("❌ No hay columna 'eventName' en datos_conversiones")
        
        # Verificar columna date
        if 'date' in datos_conversiones.columns:
            st.write(f"**Columna date existe:** ✅")
            st.write(f"**Tipo de datos date:** {datos_conversiones['date'].dtype}")
            st.write(f"**Primeras fechas:** {datos_conversiones['date'].head().tolist()}")
        else:
            st.warning("⚠️ No hay columna 'date' en datos_conversiones")
            st.write("**Esto explicaría por qué MoM da 0**")
        
    except Exception as e:
        st.error(f"Error en debug de reuniones: {str(e)}")


def renderizar_executive_dashboard(analytics_data):
    """
    Función principal que renderiza todo el Executive Dashboard
    
    Args:
        analytics_data: dict con todos los datos de analytics
    
    Returns:
        None (renderiza directamente en Streamlit)
    """
    try:
        # Verificar que hay datos
        if not analytics_data or all(df.empty for df in analytics_data.values() if isinstance(df, pd.DataFrame)):
            st.warning("⚠️ No hay datos de Google Analytics disponibles")
            return
        
        # Tabs según esquema
        tab_overview, tab_tendencias, tab_canales, tab_contenido, tab_geo, tab_placeholder = st.tabs([
            "📊 Overview", "📈 Tendencias", "🧭 Canales", "📝 Contenido", "🌍 Geo", "🤝 Leads/Reuniones"
        ])

        with tab_overview:
            crear_header_kpis(analytics_data)
            st.markdown("---")
            # Serie 56D: actual (rolling7), prev (dash), LY (dot)
            datos_temporales = analytics_data.get('datos_temporales', pd.DataFrame())
            if not datos_temporales.empty and 'date' in datos_temporales.columns:
                df = datos_temporales.copy()
                df['date'] = pd.to_datetime(df['date'])
                end = df['date'].max()
                start_56 = end - pd.Timedelta(days=55)
                df56 = df[(df['date'] >= start_56) & (df['date'] <= end)].sort_values('date')
                # Prev 28 rango
                prev_end = (end - pd.Timedelta(days=28))
                prev_start = prev_end - pd.Timedelta(days=27)
                df_prev = df[(df['date'] >= prev_start) & (df['date'] <= prev_end)].sort_values('date')
                # LY alineado
                df_ly = df.copy()
                df_ly['date_ly'] = df_ly['date'] + pd.DateOffset(years=1)
                df_ly = df_ly[(df_ly['date_ly'] >= start_56) & (df_ly['date_ly'] <= end)].sort_values('date_ly')

                fig = go.Figure()
                if 'sessions' in df56.columns:
                    fig.add_trace(go.Scatter(x=df56['date'], y=df56['sessions'].rolling(7,1).sum(), name='Sessions (actual,7d)', line=dict(width=3, color=COLORS['primary'])))
                if not df_prev.empty and 'sessions' in df_prev.columns:
                    fig.add_trace(go.Scatter(x=df_prev['date'], y=df_prev['sessions'].rolling(7,1).sum(), name='Prev 28D', line=dict(width=2, dash='dash', color='#888')))
                if not df_ly.empty and 'sessions' in df_ly.columns:
                    fig.add_trace(go.Scatter(x=df_ly['date_ly'], y=df_ly['sessions'].rolling(7,1).sum(), name='LY', line=dict(width=2, dash='dot', color='#bbb')))
                # Conversions + CR en eje secundario
                y2 = None
                if 'conversions' in df56.columns and 'sessions' in df56.columns:
                    conv_roll = df56['conversions'].rolling(7,1).sum()
                    fig.add_trace(go.Scatter(x=df56['date'], y=conv_roll, name='Conversions (7d)', line=dict(width=2, color=COLORS['seo'])))
                    lead_rate = (conv_roll / df56['sessions'].rolling(7,1).sum())*100
                    y2 = lead_rate
                if y2 is not None:
                    fig.add_trace(go.Scatter(x=df56['date'], y=y2, name='Lead Rate (%, 7d)', line=dict(width=2, color='#FFD166', dash='dot'), yaxis='y2'))
                    fig.update_layout(yaxis2=dict(title='Lead Rate %', overlaying='y', side='right'))
                fig.update_layout(title='56D Trend: Sessions, Conversions, Lead Rate', height=420, template='plotly_dark', hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            # Waterfall ΔConversions MoM por canal (Top 6 + Otros)
            datos_trafico = analytics_data.get('datos_trafico', pd.DataFrame())
            if not datos_trafico.empty and 'date' in datos_trafico.columns and 'sessions' in datos_trafico.columns:
                df = datos_trafico.copy()
                df['date'] = pd.to_datetime(df['date'])
                cur, prev, _ = rango_28d(df)
                if 'sessionDefaultChannelGrouping' in df.columns and 'conversions' in df.columns:
                    cur_grp = cur.groupby('sessionDefaultChannelGrouping')['conversions'].sum()
                    prev_grp = prev.groupby('sessionDefaultChannelGrouping')['conversions'].sum()
                    canales = list(set(cur_grp.index).union(prev_grp.index))
                    diffs = []
                    for c in canales:
                        diffs.append({'canal': c, 'delta': cur_grp.get(c,0) - prev_grp.get(c,0)})
                    diffs_df = pd.DataFrame(diffs).sort_values('delta', ascending=False)
                    top = diffs_df.head(6)
                    otros = diffs_df.iloc[6:]['delta'].sum() if len(diffs_df) > 6 else 0
                    if otros != 0:
                        top = pd.concat([top, pd.DataFrame([{'canal':'Otros','delta':otros}])], ignore_index=True)
                    # Construir waterfall
                    base = 0
                    measures = []
                    x = []
                    y = []
                    for _, r in top.iterrows():
                        measures.append('relative')
                        x.append(r['canal'])
                        y.append(r['delta'])
                    total_delta = sum(y)
                    measures.append('total'); x.append('Δ Total'); y.append(total_delta)
                    fig_w = go.Figure(go.Waterfall(name='ΔConversions 28D vs Prev', orientation='v', measure=measures, x=x, y=y))
                    fig_w.update_layout(title='Waterfall: Δ Conversions por Canal (MoM)', template='plotly_dark', height=420)
                    st.plotly_chart(fig_w, use_container_width=True)

            st.markdown("---")
            # Dumbbell: Actual vs LY
            fig_db = crear_dumbbell_actual_vs_ly(analytics_data)
            if fig_db:
                st.plotly_chart(fig_db, use_container_width=True)

            # Bullets: Engagement y Bounce vs mediana 6M
            figs_bullets = crear_bullets_engagement_bounce(analytics_data)
            if figs_bullets:
                for fb in figs_bullets:
                    st.plotly_chart(fb, use_container_width=True)

            st.markdown("---")
            st.markdown("### ⏰ Heatmap por Hora")
            # Heatmap por hora (Lead Rate o Engaged Share)
            # Debug siempre visible del dataset horario
            _df_hora_dbg = analytics_data.get('datos_horarios', pd.DataFrame())
            try:
                _cols = list(_df_hora_dbg.columns) if isinstance(_df_hora_dbg, pd.DataFrame) and not _df_hora_dbg.empty else []
                _rows = len(_df_hora_dbg) if isinstance(_df_hora_dbg, pd.DataFrame) else 0
                st.caption(f"datos_horarios → filas: {_rows} | columnas: {_cols}")
            except Exception:
                st.caption("datos_horarios → no disponible")
            try:
                fig_hm, titulo_hm = crear_heatmap_cr_por_hora(analytics_data)
                if fig_hm:
                    st.plotly_chart(fig_hm, use_container_width=True)
                else:
                    datos_hora_dbg = analytics_data.get('datos_horarios', pd.DataFrame())
                    # Debug mínimo siempre visible
                    if isinstance(datos_hora_dbg, pd.DataFrame):
                        st.caption(f"datos_horarios → filas: {len(datos_hora_dbg)} | columnas: {list(datos_hora_dbg.columns) if not datos_hora_dbg.empty else []}")
                    if datos_hora_dbg is None or datos_hora_dbg.empty:
                        st.warning("⚠️ No hourly data available (dataset vacío). Ve a Analytics Overview y pulsa 'Recargar Datos'.")
                    else:
                        faltan = [c for c in ['hour','sessions'] if c not in datos_hora_dbg.columns]
                        if faltan:
                            st.warning(f"⚠️ Faltan columnas requeridas en datos_horarios: {faltan}")
            except Exception as e:
                st.error(f"Error renderizando heatmap hora: {str(e)}")

        with tab_tendencias:
            st.markdown("### 📈 Evolución Temporal")
            fig_evolucion = crear_grafico_evolucion_temporal(analytics_data)
            if fig_evolucion:
                st.plotly_chart(fig_evolucion, use_container_width=True)
            st.markdown("---")
            st.markdown("#### 📅 Daily Traffic")
            tabla_daily = crear_tabla_daily_traffic(analytics_data)
            if not tabla_daily.empty:
                st.dataframe(tabla_daily, use_container_width=True)

        with tab_canales:
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown("### 🧭 Fuentes de Oportunidad")
                fig_fuentes = crear_chart_canales_share(analytics_data)
                if fig_fuentes:
                    st.plotly_chart(fig_fuentes, use_container_width=True)
            with col2:
                st.markdown("### 📊 Tabla Ejecutiva por Canal")
                tabla_ejecutiva = crear_tabla_ejecutiva(analytics_data)
                if not tabla_ejecutiva.empty:
                    st.dataframe(tabla_ejecutiva, use_container_width=True)

        with tab_contenido:
            st.markdown("### 📝 Top Contenido")
            fig_top_content = crear_chart_top_contenido(analytics_data)
            if fig_top_content:
                st.plotly_chart(fig_top_content, use_container_width=True)
            with st.expander("Tabla (detallada)", expanded=False):
                tabla_contenido = crear_tabla_top_contenido(analytics_data)
                if not tabla_contenido.empty:
                    st.dataframe(tabla_contenido, use_container_width=True)

        with tab_geo:
            st.markdown("### 🌍 Geo (país/ciudad)")
            fig_geo = crear_mapa_geo(analytics_data)
            if fig_geo:
                st.plotly_chart(fig_geo, use_container_width=True)
            with st.expander("Tabla (resumen)", expanded=False):
                datos_geo = analytics_data.get('datos_geograficos', pd.DataFrame())
                if not datos_geo.empty:
                    df = datos_geo.copy()
                    if 'conversions' in df.columns and 'sessions' in df.columns:
                        df['conv_rate_sessions'] = df.apply(lambda r: (r['conversions']/r['sessions']) if r['sessions'] else 0, axis=1)
                    cols = [c for c in ['country','city','sessions','screenPageViews','conversions','engagedSessions','conv_rate_sessions'] if c in df.columns]
                    if cols:
                        show = df[cols].groupby(['country'] if 'country' in cols else ['city']).sum().reset_index()
                        st.dataframe(show.sort_values('sessions', ascending=False).head(50), use_container_width=True)
                else:
                    st.info("Sin datos geográficos disponibles.")

        with tab_placeholder:
            st.markdown("### 🤝 Leads / Reuniones")
            st.info("— pronto — (conector CSV/CRM/Calendly)")
            # Embudo global como contexto actual
            fig_embudo = crear_grafico_embudo_global(analytics_data)
            if fig_embudo:
                st.plotly_chart(fig_embudo, use_container_width=True)

        st.markdown("---")
        mostrar_insight_cards(analytics_data)
        
    except Exception as e:
        st.error(f"Error renderizando Executive Dashboard: {str(e)}")
