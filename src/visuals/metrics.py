"""
Metrics Visualization Functions
Funciones para crear visualizaciones de métricas importantes
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_metric_card(title, value, subtitle=None, icon="📊"):
    """
    Crea una tarjeta de métrica individual con el estilo de la imagen
    
    Args:
        title (str): Título de la métrica
        value (str/int/float): Valor de la métrica
        subtitle (str, optional): Subtítulo descriptivo
        icon (str): Icono para la métrica
    
    Returns:
        None: Renderiza la tarjeta directamente en Streamlit
    """
    
    # Crear contenedor con estilo
    with st.container():
        # CSS para el contenedor
        st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            border: 1px solid #4B5563;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .metric-content {
            flex: 1;
        }
        .metric-title {
            color: #9CA3AF;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        .metric-value {
            color: #F9FAFB;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .metric-subtitle {
            color: #9CA3AF;
            font-size: 0.75rem;
            font-weight: 400;
        }
        .metric-icon {
            font-size: 2.5rem;
            opacity: 0.8;
            margin-left: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Crear HTML de la tarjeta
        subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ''
        
        card_html = f"""
        <div class="metric-card">
            <div class="metric-content">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                {subtitle_html}
            </div>
            <div class="metric-icon">{icon}</div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)


def create_metrics_grid(data_dict, columns=4):
    """
    Crea una cuadrícula de tarjetas de métricas
    
    Args:
        data_dict (dict): Diccionario con las métricas {title: {value, change, change_type, icon}}
        columns (int): Número de columnas en la cuadrícula
    
    Returns:
        None: Renderiza la cuadrícula directamente en Streamlit
    """
    
    # Crear columnas
    cols = st.columns(columns)
    
    # Distribuir métricas en las columnas
    for i, (title, metric_data) in enumerate(data_dict.items()):
        with cols[i % columns]:
            create_metric_card(
                title=title,
                value=metric_data.get("value", "N/A"),
                change=metric_data.get("change"),
                change_type=metric_data.get("change_type", "neutral"),
                icon=metric_data.get("icon", "📊")
            )


def create_kpi_summary(df, metrics_config):
    """
    Crea un resumen de KPIs principales desde un DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame con los datos
        metrics_config (dict): Configuración de métricas a mostrar
    
    Returns:
        None: Renderiza el resumen directamente en Streamlit
    """
    
    st.subheader("📊 KPIs Principales")
    
    # Calcular métricas
    calculated_metrics = {}
    
    for metric_name, config in metrics_config.items():
        column = config.get("column")
        operation = config.get("operation", "sum")
        icon = config.get("icon", "📊")
        
        if column in df.columns:
            if operation == "sum":
                value = df[column].sum()
            elif operation == "mean":
                value = df[column].mean()
            elif operation == "count":
                value = len(df)
            elif operation == "max":
                value = df[column].max()
            elif operation == "min":
                value = df[column].min()
            else:
                value = df[column].sum()
            
            # Formatear valor
            if isinstance(value, float):
                if value >= 1000000:
                    formatted_value = f"{value/1000000:.1f}M"
                elif value >= 1000:
                    formatted_value = f"{value/1000:.1f}K"
                else:
                    formatted_value = f"{value:.0f}"
            else:
                formatted_value = str(value)
            
            calculated_metrics[metric_name] = {
                "value": formatted_value,
                "icon": icon
            }
    
    # Crear cuadrícula
    create_metrics_grid(calculated_metrics)


def create_trend_chart(df, date_column, metric_column, title="Tendencia"):
    """
    Crea un gráfico de tendencia temporal
    
    Args:
        df (pd.DataFrame): DataFrame con los datos
        date_column (str): Nombre de la columna de fecha
        metric_column (str): Nombre de la columna de métrica
        title (str): Título del gráfico
    
    Returns:
        plotly.graph_objects.Figure: Gráfico de tendencia
    """
    
    if date_column not in df.columns or metric_column not in df.columns:
        st.warning(f"⚠️ Columnas '{date_column}' o '{metric_column}' no encontradas")
        return None
    
    # Convertir fecha si es necesario
    df_copy = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_copy[date_column]):
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    
    # Crear gráfico
    fig = px.line(
        df_copy,
        x=date_column,
        y=metric_column,
        title=title,
        color_discrete_sequence=["#2E4543"]
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='white',
        xaxis_title_font_color='white',
        yaxis_title_font_color='white',
        height=400
    )
    
    return fig


def create_comparison_chart(df, category_column, metric_column, title="Comparación"):
    """
    Crea un gráfico de comparación por categorías
    
    Args:
        df (pd.DataFrame): DataFrame con los datos
        category_column (str): Nombre de la columna de categoría
        metric_column (str): Nombre de la columna de métrica
        title (str): Título del gráfico
    
    Returns:
        plotly.graph_objects.Figure: Gráfico de comparación
    """
    
    if category_column not in df.columns or metric_column not in df.columns:
        st.warning(f"⚠️ Columnas '{category_column}' o '{metric_column}' no encontradas")
        return None
    
    # Crear gráfico de barras
    fig = px.bar(
        df.head(10),  # Top 10
        x=category_column,
        y=metric_column,
        title=title,
        color_discrete_sequence=["#2E4543"]
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='white',
        xaxis_title_font_color='white',
        yaxis_title_font_color='white',
        height=400
    )
    
    return fig


def create_user_kpis_optimized():
    """
    Crea cajas de KPIs específicas para métricas de usuarios usando consulta optimizada
    
    Returns:
        None: Renderiza las cajas de KPIs directamente en Streamlit
    """
    
    from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_kpis_data
    
    # Obtener fechas de filtro
    if "fecha_inicio" in st.session_state and "fecha_fin" in st.session_state:
        fecha_inicio = st.session_state["fecha_inicio"]
        fecha_fin = st.session_state["fecha_fin"]
        
        # Convertir fechas a string para la API
        start_date = fecha_inicio.strftime("%Y-%m-%d")
        end_date = fecha_fin.strftime("%Y-%m-%d")
        
        try:
            # Cargar credenciales y cliente
            credentials = load_credentials()
            client = initialize_analytics_client(credentials)
            
            # Obtener KPIs optimizados
            kpis_data = get_kpis_data(
                client=client,
                property_id="381346600",
                start_date=start_date,
                end_date=end_date
            )
            
            # Crear las cajas de KPIs
            st.markdown("### 👥 User KPIs")
            
            # Crear 4 columnas para los KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                create_metric_card(
                    title="Active Users",
                    value=f"{kpis_data['active_users']:,}",
                    subtitle="Total active users",
                    icon="👥"
                )
            
            with col2:
                create_metric_card(
                    title="New Users", 
                    value=f"{kpis_data['new_users']:,}",
                    subtitle="First-time users",
                    icon="🆕"
                )
            
            with col3:
                # Formatear tiempo en minutos y segundos
                avg_time = kpis_data['avg_engagement_time']
                minutes = int(avg_time // 60)
                seconds = int(avg_time % 60)
                time_str = f"{minutes}m {seconds}s"
                
                create_metric_card(
                    title="Avg Engagement Time",
                    value=time_str,
                    subtitle="Per active user",
                    icon="⏱️"
                )
            
            with col4:
                create_metric_card(
                    title="Event Count",
                    value=f"{kpis_data['event_count']:,}",
                    subtitle="Total events (all types)",
                    icon="📊"
                )
                
        except Exception as e:
            st.error(f"❌ Error obteniendo KPIs optimizados: {str(e)}")
            # Fallback a la lógica anterior si falla
            st.warning("⚠️ Usando datos de respaldo...")
    else:
        st.warning("⚠️ No hay filtros de fecha configurados para KPIs")


def create_user_kpis(df, all_datasets=None):
    """
    Crea cajas de KPIs específicas para métricas de usuarios
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de usuarios (datos temporales)
        all_datasets (dict): Diccionario con todos los datasets para calcular Event Count total
    
    Returns:
        None: Renderiza las cajas de KPIs directamente en Streamlit
    """
    
    st.markdown("### 👥 User KPIs")
    
    # Calcular métricas de usuarios
    kpis = {}
    
    # Active Users (usuarios totales) - buscar diferentes nombres posibles
    active_users_cols = ["totalUsers", "users", "activeUsers", "total_users"]
    active_users_col = None
    for col in active_users_cols:
        if col in df.columns:
            active_users_col = col
            break
    
    if active_users_col:
        active_users = df[active_users_col].sum()
        kpis["Active Users"] = {
            "value": f"{active_users:,.0f}" if active_users >= 1000 else f"{active_users:.0f}",
            "icon": "👤",
            "description": "Total active users"
        }
    
    # New Users - buscar diferentes nombres posibles
    new_users_cols = ["newUsers", "new_users", "firstTimeUsers"]
    new_users_col = None
    for col in new_users_cols:
        if col in df.columns:
            new_users_col = col
            break
    
    if new_users_col:
        new_users = df[new_users_col].sum()
        kpis["New Users"] = {
            "value": f"{new_users:,.0f}" if new_users >= 1000 else f"{new_users:.0f}",
            "icon": "🆕",
            "description": "First-time users"
        }
    
    # Average Engagement Time per Active User - buscar diferentes nombres posibles
    engagement_cols = ["averageSessionDuration", "avgSessionDuration", "sessionDuration", "avg_session_duration"]
    sessions_cols = ["sessions", "sessionCount", "session_count"]
    
    engagement_col = None
    sessions_col = None
    
    for col in engagement_cols:
        if col in df.columns:
            engagement_col = col
            break
    
    for col in sessions_cols:
        if col in df.columns:
            sessions_col = col
            break
    
    if engagement_col and active_users_col:
        # Calcular el tiempo total de engagement: averageSessionDuration * sessions
        if sessions_col:
            total_engagement_time = (df[engagement_col] * df[sessions_col]).sum()
            total_active_users = df[active_users_col].sum()
            
            if total_active_users > 0:
                avg_engagement_per_user = total_engagement_time / total_active_users
            else:
                avg_engagement_per_user = df[engagement_col].mean()
        else:
            # Fallback: usar promedio simple si no hay sessions
            avg_engagement_per_user = df[engagement_col].mean()
        
        # Convertir a minutos y segundos
        minutes = int(avg_engagement_per_user // 60)
        seconds = int(avg_engagement_per_user % 60)
        kpis["Avg Engagement Time"] = {
            "value": f"{minutes}m {seconds}s",
            "icon": "⏱️",
            "description": "Per active user"
        }
    
    # Event Count - suma de TODOS los eventos de TODOS los datasets
    total_event_count = 0
    
    if all_datasets:
        # Buscar eventos en todos los datasets
        for dataset_name, dataset_df in all_datasets.items():
            if not dataset_df.empty:
                # Buscar diferentes nombres posibles para event count
                event_cols = ["eventCount", "totalEvents", "events", "eventCounts", "screenPageViews", "pageViews"]
                for col in event_cols:
                    if col in dataset_df.columns:
                        total_event_count += dataset_df[col].sum()
                        break
    
    # Si no encontramos eventos específicos, usar screenPageViews como proxy del dataset actual
    if total_event_count == 0:
        pageview_cols = ["screenPageViews", "pageViews", "pageviews", "views"]
        for col in pageview_cols:
            if col in df.columns:
                total_event_count = df[col].sum()
                break
    
    # Formatear el Event Count
    if total_event_count > 0:
        if total_event_count >= 1000000:
            formatted_count = f"{total_event_count/1000000:.1f}M"
        elif total_event_count >= 1000:
            formatted_count = f"{total_event_count/1000:.1f}K"
        else:
            formatted_count = f"{total_event_count:,.0f}"
        
        kpis["Event Count"] = {
            "value": formatted_count,
            "icon": "📊",
            "description": "Total events (all types)"
        }
    
    # Crear las cajas de KPIs
    if kpis:
        cols = st.columns(len(kpis))
        
        for i, (title, data) in enumerate(kpis.items()):
            with cols[i]:
                st.markdown(f"""
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
                                {data['value']}
                            </div>
                            <div style="color: #6B7280; font-size: 0.75rem;">
                                {data['description']}
                            </div>
                        </div>
                        <div style="font-size: 2rem; opacity: 0.8;">
                            {data['icon']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No se encontraron métricas de usuarios en los datos")


def create_new_vs_returning_chart(df):
    """
    Crea un gráfico de línea mostrando New vs. Returning users
    
    Args:
        df (pd.DataFrame): DataFrame con datos de usuarios que debe contener:
            - date: columna de fechas
            - newUsers: usuarios nuevos
            - totalUsers: usuarios totales (para calcular returning)
    
    Returns:
        plotly.graph_objects.Figure: Gráfico de líneas
    """
    
    if df.empty:
        st.warning("⚠️ No hay datos para mostrar el gráfico")
        return None
    
    # Verificar que tenemos las columnas necesarias
    required_cols = ['date', 'newUsers', 'totalUsers']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.warning(f"⚠️ Faltan columnas necesarias: {missing_cols}")
        return None
    
    # Preparar los datos
    chart_df = df.copy()
    
    # Convertir fecha a datetime si es necesario
    chart_df['date'] = pd.to_datetime(chart_df['date'])
    
    # Calcular returning users (totalUsers - newUsers)
    chart_df['returningUsers'] = chart_df['totalUsers'] - chart_df['newUsers']
    
    # Asegurar que no haya valores negativos
    chart_df['returningUsers'] = chart_df['returningUsers'].clip(lower=0)
    
    # Ordenar por fecha
    chart_df = chart_df.sort_values('date')
    
    # Crear el gráfico con Plotly
    fig = go.Figure()
    
    # Línea para New Users (azul)
    fig.add_trace(go.Scatter(
        x=chart_df['date'],
        y=chart_df['newUsers'],
        mode='lines+markers',
        name='new',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate='<b>New Users</b><br>' +
                     'Date: %{x}<br>' +
                     'Users: %{y}<br>' +
                     '<extra></extra>'
    ))
    
    # Línea para Returning Users (verde)
    fig.add_trace(go.Scatter(
        x=chart_df['date'],
        y=chart_df['returningUsers'],
        mode='lines+markers',
        name='returning',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8, color='#2ca02c', symbol='square'),
        hovertemplate='<b>Returning Users</b><br>' +
                     'Date: %{x}<br>' +
                     'Users: %{y}<br>' +
                     '<extra></extra>'
    ))
    
    # Configurar el layout
    fig.update_layout(
        title={
            'text': 'New vs. Returning users',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'white'}
        },
        xaxis=dict(
            title='Date',
            titlefont=dict(color='white'),
            tickfont=dict(color='white'),
            gridcolor='rgba(128,128,128,0.3)',
            showgrid=True
        ),
        yaxis=dict(
            title='Number of Users',
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
    
    # Formatear las fechas en el eje X
    fig.update_xaxes(
        tickformat='%d %b',
        dtick='D1'  # Mostrar cada día
    )
    
    return fig


def create_dashboard_overview(all_data):
    """
    Crea una vista general del dashboard con métricas principales
    
    Args:
        all_data (dict): Diccionario con todos los datasets
    
    Returns:
        None: Renderiza el dashboard completo
    """
    
    st.markdown("## 📊 Dashboard Overview")
    
    # Configuración de métricas principales
    main_metrics = {
        "Sessions": {"column": "sessions", "operation": "sum", "icon": "👥"},
        "Users": {"column": "totalUsers", "operation": "sum", "icon": "👤"},
        "Page Views": {"column": "screenPageViews", "operation": "sum", "icon": "📄"},
        "Bounce Rate": {"column": "bounceRate", "operation": "mean", "icon": "📈"}
    }
    
    # Mostrar métricas de cada dataset
    for dataset_name, df in all_data.items():
        if not df.empty:
            st.markdown(f"### 📈 {dataset_name.replace('_', ' ').title()}")
            create_kpi_summary(df, main_metrics)
            
            # Mostrar gráficos si hay datos temporales
            if "date" in df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    if "sessions" in df.columns:
                        fig = create_trend_chart(df, "date", "sessions", f"Sessions - {dataset_name}")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if "totalUsers" in df.columns:
                        fig = create_trend_chart(df, "date", "totalUsers", f"Users - {dataset_name}")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")


def create_top_pages_table(all_datasets):
    """
    Crea una tabla de las páginas más visitadas con métricas usando consulta optimizada
    
    Args:
        all_datasets (dict): Diccionario con todos los datasets de Google Analytics
    
    Returns:
        None: Renderiza la tabla directamente en Streamlit
    """
    
    import streamlit as st
    import pandas as pd
    from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_top_pages_data
    
    # Obtener fechas de filtro
    if "fecha_inicio" in st.session_state and "fecha_fin" in st.session_state:
        fecha_inicio = st.session_state["fecha_inicio"]
        fecha_fin = st.session_state["fecha_fin"]
        
        # Convertir fechas a string para la API
        start_date = fecha_inicio.strftime("%Y-%m-%d")
        end_date = fecha_fin.strftime("%Y-%m-%d")
        
        try:
            # Cargar credenciales y cliente
            credentials = load_credentials()
            client = initialize_analytics_client(credentials)
            
            # Obtener datos optimizados para Top Pages
            top_pages_data = get_top_pages_data(
                client=client,
                property_id="381346600",
                start_date=start_date,
                end_date=end_date
            )
            
            if top_pages_data.empty:
                st.warning("⚠️ No se encontraron datos de páginas para el rango de fechas seleccionado")
                return
            
            # Usar los datos optimizados directamente
            page_metrics = top_pages_data
            
        except Exception as e:
            st.error(f"❌ Error obteniendo datos optimizados: {str(e)}")
            # Fallback a la lógica anterior si falla
            page_metrics = None
    else:
        st.warning("⚠️ No hay filtros de fecha configurados")
        return
    
    if page_metrics is None or page_metrics.empty:
        st.warning("⚠️ No se encontraron datos de páginas")
        return
    
    # Los datos ya vienen optimizados de la consulta, no necesitamos procesamiento adicional
    
    # Los datos ya vienen con las columnas correctas y ordenados de la consulta optimizada
    # Solo necesitamos renombrar para la tabla
    rename_dict = {'pageTitle': 'PAGE TITLE AND SCREEN CLASS'}
    
    if 'screenPageViews' in page_metrics.columns:
        rename_dict['screenPageViews'] = 'VIEWS'
    
    if 'totalUsers' in page_metrics.columns:
        rename_dict['totalUsers'] = 'ACTIVE USERS'
    
    if 'eventCount' in page_metrics.columns:
        rename_dict['eventCount'] = 'EVENT COUNT'
    
    if 'bounceRate' in page_metrics.columns:
        rename_dict['bounceRate'] = 'BOUNCE RATE'
    
    page_metrics = page_metrics.rename(columns=rename_dict)
    
    # Formatear BOUNCE RATE como porcentaje (si existe)
    if 'BOUNCE RATE' in page_metrics.columns:
        page_metrics['BOUNCE RATE'] = page_metrics['BOUNCE RATE'].astype(str) + '%'
    
    # Crear la tabla con estilo
    st.markdown("### 📄 Top Pages/Screens")
    
    # Mostrar filtros aplicados si existen
    if "fecha_inicio" in st.session_state and "fecha_fin" in st.session_state:
        fecha_inicio = st.session_state["fecha_inicio"]
        fecha_fin = st.session_state["fecha_fin"]
       
    
    # Crear tabla con barras de progreso usando HTML/CSS
    table_html = """
    <style>
    .top-pages-table {
        width: 100%;
        border-collapse: collapse;
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .top-pages-table th {
        background: #2E4543;
        color: white;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .top-pages-table td {
        padding: 0.75rem;
        color: white;
        border-bottom: 1px solid #4B5563;
        font-size: 0.875rem;
    }
    
    .top-pages-table tr:hover {
        background: rgba(46, 69, 67, 0.3);
    }
    
    .page-title {
        font-weight: 500;
        font-size: 0.875rem;
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .metric-cell {
        position: relative;
        min-width: 120px;
    }
    
    .metric-value {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
    }
    
    .progress-bar {
        height: 6px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3B82F6, #1D4ED8);
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    </style>
    
    <table class="top-pages-table">
        <thead>
            <tr>
                <th>PAGE TITLE AND SCREEN CLASS</th>
                <th>VIEWS</th>
                <th>ACTIVE USERS</th>
                <th>EVENT COUNT</th>
                <th>BOUNCE RATE</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Calcular valores máximos para las barras de progreso
    max_views = page_metrics['VIEWS'].max() if 'VIEWS' in page_metrics.columns else 1
    max_users = page_metrics['ACTIVE USERS'].max() if 'ACTIVE USERS' in page_metrics.columns else 1
    max_events = page_metrics['EVENT COUNT'].max() if 'EVENT COUNT' in page_metrics.columns else 1
    
    # Agregar filas de datos dinámicamente
    for _, row in page_metrics.iterrows():
        table_html += "<tr>"
        
        # PAGE TITLE siempre está presente
        table_html += f'<td class="page-title" title="{row["PAGE TITLE AND SCREEN CLASS"]}">{row["PAGE TITLE AND SCREEN CLASS"]}</td>'
        
        # VIEWS
        if 'VIEWS' in page_metrics.columns:
            views_pct = (row['VIEWS'] / max_views) * 100
            table_html += f'<td class="metric-cell"><div class="metric-value">{row["VIEWS"]:,.0f}</div><div class="progress-bar"><div class="progress-fill" style="width: {views_pct}%"></div></div></td>'
        else:
            table_html += '<td class="metric-cell"><div class="metric-value">-</div></td>'
        
        # ACTIVE USERS
        if 'ACTIVE USERS' in page_metrics.columns:
            users_pct = (row['ACTIVE USERS'] / max_users) * 100
            table_html += f'<td class="metric-cell"><div class="metric-value">{row["ACTIVE USERS"]:,.0f}</div><div class="progress-bar"><div class="progress-fill" style="width: {users_pct}%"></div></div></td>'
        else:
            table_html += '<td class="metric-cell"><div class="metric-value">-</div></td>'
        
        # EVENT COUNT
        if 'EVENT COUNT' in page_metrics.columns:
            events_pct = (row['EVENT COUNT'] / max_events) * 100
            table_html += f'<td class="metric-cell"><div class="metric-value">{row["EVENT COUNT"]:,.0f}</div><div class="progress-bar"><div class="progress-fill" style="width: {events_pct}%"></div></div></td>'
        else:
            table_html += '<td class="metric-cell"><div class="metric-value">-</div></td>'
        
        # BOUNCE RATE
        if 'BOUNCE RATE' in page_metrics.columns:
            table_html += f'<td class="metric-cell"><div class="metric-value">{row["BOUNCE RATE"]}</div></td>'
        else:
            table_html += '<td class="metric-cell"><div class="metric-value">-</div></td>'
        
        table_html += "</tr>"
    
    table_html += """
        </tbody>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)
