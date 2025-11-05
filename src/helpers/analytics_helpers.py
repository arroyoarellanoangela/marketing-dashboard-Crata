"""
Google Analytics Helper Functions
Funciones auxiliares para trabajar con Google Analytics Data API
"""

import json
import pandas as pd
import time
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account
import streamlit as st


def load_credentials():
    """Carga las credenciales desde credentials.json"""
    try:
        with open('credentials.json', 'r') as f:
            credentials_info = json.load(f)
        return credentials_info
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'credentials.json'")
        st.info("📝 Por favor, coloca tu archivo credentials.json en el directorio raíz del proyecto")
        return None
    except json.JSONDecodeError:
        st.error("❌ El archivo credentials.json no tiene un formato JSON válido")
        return None


def initialize_analytics_client(credentials_info):
    """Inicializa el cliente de Google Analytics"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        client = BetaAnalyticsDataClient(credentials=credentials)
        return client
    except Exception as e:
        st.error(f"❌ Error al inicializar el cliente de Google Analytics: {str(e)}")
        return None


def get_analytics_data(client, property_id, start_date, end_date, dimensions, metrics):
    """Obtiene datos específicos de Google Analytics"""
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=dim) for dim in dimensions],
            metrics=[Metric(name=metric) for metric in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
        
        response = client.run_report(request)
        return response
    except Exception as e:
        st.error(f"❌ Error al obtener datos: {str(e)}")
        return None


def get_all_analytics_data(client, property_id, start_date, end_date, data_sets_config):
    """Obtiene TODOS los datos disponibles de Google Analytics con paginación optimizada y manejo de límites"""
    
    all_data = {}
    
    for dataset_name, config in data_sets_config.items():
        try:
            # Configuración optimizada para cada dataset
            page_size = 10000  # Límite máximo de GA4 API
            all_rows = []
            offset = 0
            max_retries = 3
            
            while True:
                retry_count = 0
                success = False
                
                while retry_count < max_retries and not success:
                    try:
                        request = RunReportRequest(
                            property=f"properties/{property_id}",
                            dimensions=[Dimension(name=dim) for dim in config["dimensions"]],
                            metrics=[Metric(name=metric) for metric in config["metrics"]],
                            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                            limit=page_size,
                            offset=offset
                        )
                        
                        response = client.run_report(request)
                        success = True
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count >= max_retries:
                            raise e
                        time.sleep(2)  # Esperar antes del siguiente intento
                
                # Si no hay más filas, salir del bucle
                if not response.rows:
                    break
                
                # Procesar filas de esta página
                dim_headers = [d.name for d in response.dimension_headers]
                met_headers = [m.name for m in response.metric_headers]
                
                for row in response.rows:
                    row_data = {}
                    # Agregar dimensiones
                    for i, value in enumerate(row.dimension_values):
                        row_data[dim_headers[i]] = value.value
                    # Agregar métricas
                    for i, value in enumerate(row.metric_values):
                        row_data[met_headers[i]] = value.value
                    
                    all_rows.append(row_data)
                
                # Verificar si hay más páginas
                if response.row_count and offset + page_size >= response.row_count:
                    break
                
                offset += page_size
                
                # Evitar rate limiting
                time.sleep(0.1)
            
            # Convertir a DataFrame
            if all_rows:
                df = pd.DataFrame(all_rows)
                # Convertir métricas a numérico
                for metric in config["metrics"]:
                    if metric in df.columns:
                        df[metric] = pd.to_numeric(df[metric], errors='coerce')
                all_data[dataset_name] = df
            else:
                all_data[dataset_name] = pd.DataFrame()
            
        except Exception as e:
            st.warning(f"⚠️ Error obteniendo {dataset_name}: {str(e)}")
            all_data[dataset_name] = pd.DataFrame()
    
    return all_data


def run_dynamic_report(client, property_id, start_date, end_date, dimensions, metrics, page_size=100000):
    """
    Ejecuta una consulta dinámica a GA4 con paginación optimizada
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
        dimensions: Lista de dimensiones
        metrics: Lista de métricas
        page_size: Tamaño de página (default: 100000)
    
    Returns:
        pd.DataFrame: Datos de la consulta
    """
    all_rows = []
    offset = 0
    
    while True:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=dim) for dim in dimensions],
            metrics=[Metric(name=metric) for metric in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=page_size,
            offset=offset
        )
        
        response = client.run_report(request)
        
        # Si no hay más filas, salir del bucle
        if not response.rows:
            break
        
        # Procesar filas de esta página
        dim_headers = [d.name for d in response.dimension_headers]
        met_headers = [m.name for m in response.metric_headers]
        
        for row in response.rows:
            row_data = {}
            # Agregar dimensiones
            for i, value in enumerate(row.dimension_values):
                row_data[dim_headers[i]] = value.value
            # Agregar métricas
            for i, value in enumerate(row.metric_values):
                row_data[met_headers[i]] = value.value
            
            all_rows.append(row_data)
        
        # Verificar si hay más páginas
        if response.row_count and offset + page_size >= response.row_count:
            break
        
        offset += page_size
    
    # Convertir a DataFrame
    if all_rows:
        df = pd.DataFrame(all_rows)
        # Convertir métricas a numérico
        for metric in metrics:
            if metric in df.columns:
                df[metric] = pd.to_numeric(df[metric], errors='coerce')
        return df
    else:
        return pd.DataFrame()


def get_top_pages_data(client, property_id, start_date, end_date):
    """
    Obtiene datos específicos para la tabla de Top Pages/Screens
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        pd.DataFrame: Datos optimizados para Top Pages
    """
    
    # Consulta optimizada para Top Pages/Screens
    dimensions = [
        "pageTitle",           # Título de la página
        "pagePath",            # Ruta de la página
        "landingPage"          # Página de aterrizaje
    ]
    
    metrics = [
        "screenPageViews",     # Views (páginas vistas)
        "totalUsers",          # Active Users (usuarios activos)
        "eventCount",          # Event Count (total de eventos)
        "bounceRate",          # Bounce Rate (porcentaje de rebote)
        "averageSessionDuration", # Duración promedio de sesión
        "sessions"             # Sesiones
    ]
    
    try:
        # Ejecutar consulta con paginación
        df = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            metrics=metrics,
            page_size=100000
        )
        
        if df.empty:
            return pd.DataFrame()
        
        # Limpiar y optimizar los datos
        df = df.dropna(subset=['pageTitle'])  # Eliminar filas sin título
        
        # Agrupar por pageTitle para obtener métricas consolidadas
        agg_dict = {
            'screenPageViews': 'sum',
            'totalUsers': 'sum', 
            'eventCount': 'sum',
            'bounceRate': 'mean',
            'averageSessionDuration': 'mean',
            'sessions': 'sum'
        }
        
        # Agrupar por pageTitle
        top_pages = df.groupby('pageTitle').agg(agg_dict).reset_index()
        
        # Ordenar por screenPageViews descendente
        top_pages = top_pages.sort_values('screenPageViews', ascending=False)
        
        # Limitar a top 10 páginas
        top_pages = top_pages.head(10)
        
        # Formatear bounceRate como porcentaje
        if 'bounceRate' in top_pages.columns:
            top_pages['bounceRate'] = (top_pages['bounceRate'] * 100).round(1)
        
        return top_pages
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de Top Pages: {str(e)}")
        return pd.DataFrame()


def get_kpis_data(client, property_id, start_date, end_date):
    """
    Obtiene datos específicos para los KPIs principales
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        dict: Diccionario con los KPIs calculados
    """
    
    try:
        # Consulta optimizada para KPIs principales
        dimensions = ["date"]  # Solo fecha para agregar por día
        
        metrics = [
            "totalUsers",              # Active Users
            "newUsers",                # New Users
            "averageSessionDuration",  # Para calcular Average Engagement Time
            "sessions",                # Para calcular Average Engagement Time
            "eventCount",              # Event Count
            "screenPageViews",         # Views adicionales
            "bounceRate"               # Bounce Rate adicional
        ]
        
        # Ejecutar consulta con paginación
        df = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            metrics=metrics,
            page_size=100000
        )
        
        if df.empty:
            return {
                'active_users': 0,
                'new_users': 0,
                'avg_engagement_time': 0,
                'event_count': 0
            }
        
        # Calcular KPIs agregados
        kpis = {
            'active_users': df['totalUsers'].sum() if 'totalUsers' in df.columns else 0,
            'new_users': df['newUsers'].sum() if 'newUsers' in df.columns else 0,
            'event_count': df['eventCount'].sum() if 'eventCount' in df.columns else 0
        }
        
        # Calcular Average Engagement Time según GA4
        # Formula: (averageSessionDuration * sessions) / totalUsers
        if all(col in df.columns for col in ['averageSessionDuration', 'sessions', 'totalUsers']):
            total_engagement_time = (df['averageSessionDuration'] * df['sessions']).sum()
            total_users = df['totalUsers'].sum()
            
            if total_users > 0:
                kpis['avg_engagement_time'] = total_engagement_time / total_users
            else:
                kpis['avg_engagement_time'] = 0
        else:
            kpis['avg_engagement_time'] = 0
        
        return kpis
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de KPIs: {str(e)}")
        return {
            'active_users': 0,
            'new_users': 0,
            'avg_engagement_time': 0,
            'event_count': 0
        }


def get_traffic_sources_data(client, property_id, start_date, end_date):
    """
    Obtiene datos de fuentes de tráfico
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame: Datos de fuentes de tráfico
    """
    
    try:
        dimensions = ["sessionSource", "sessionMedium", "sessionDefaultChannelGrouping"]
        metrics = ["sessions", "totalUsers", "newUsers", "bounceRate", "averageSessionDuration"]
        
        df = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            metrics=metrics,
            page_size=100000
        )
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de fuentes de tráfico: {str(e)}")
        return pd.DataFrame()


def get_content_performance_data(client, property_id, start_date, end_date):
    """
    Obtiene datos de rendimiento de contenido
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame: Datos de rendimiento de contenido
    """
    
    try:
        dimensions = ["pagePath", "pageTitle"]
        metrics = ["screenPageViews", "totalUsers", "newUsers", "bounceRate", "averageSessionDuration"]
        
        df = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            metrics=metrics,
            page_size=100000
        )
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de rendimiento de contenido: {str(e)}")
        return pd.DataFrame()


def get_custom_events_data(client, property_id, start_date, end_date):
    """
    Obtiene datos de eventos personalizados con parámetros
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame: Datos de eventos personalizados
    """
    
    try:
        # Eventos personalizados comunes
        custom_events = [
            "form_submit",
            "button_click", 
            "scroll_depth",
            "video_play",
            "download",
            "outbound_click",
            "file_download"
        ]
        
        all_events_data = []
        
        for event in custom_events:
            try:
                request = RunReportRequest(
                    property=f"properties/{property_id}",
                    dimensions=[
                        Dimension(name="eventName"),
                        Dimension(name="eventParameterName"),
                        Dimension(name="eventParameterValue")
                    ],
                    metrics=[
                        Metric(name="eventCount"),
                        Metric(name="totalUsers")
                    ],
                    date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                    dimension_filter={
                        "filter": {
                            "field_name": "eventName",
                            "string_filter": {
                                "match_type": "EXACT",
                                "value": event
                            }
                        }
                    },
                    limit=10000
                )
                
                response = client.run_report(request)
                
                for row in response.rows:
                    event_data = {
                        "eventName": row.dimension_values[0].value,
                        "eventParameterName": row.dimension_values[1].value,
                        "eventParameterValue": row.dimension_values[2].value,
                        "eventCount": int(row.metric_values[0].value),
                        "totalUsers": int(row.metric_values[1].value)
                    }
                    all_events_data.append(event_data)
                    
            except Exception as e:
                print(f"⚠️ No se pudo obtener datos para evento {event}: {str(e)}")
                continue
        
        if all_events_data:
            return pd.DataFrame(all_events_data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Error obteniendo eventos personalizados: {str(e)}")
        return pd.DataFrame()


def get_user_segments_data(client, property_id, start_date, end_date):
    """
    Obtiene datos segmentados por usuarios nuevos vs recurrentes
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame: Datos segmentados por tipo de usuario
    """
    
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="newVsReturning")
            ],
            metrics=[
                Metric(name="totalUsers"),
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="conversions"),
                Metric(name="engagedSessions")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=100000
        )
        
        response = client.run_report(request)
        
        rows_data = []
        for row in response.rows:
            row_data = {
                "date": row.dimension_values[0].value,
                "newVsReturning": row.dimension_values[1].value,
                "totalUsers": int(row.metric_values[0].value),
                "sessions": int(row.metric_values[1].value),
                "screenPageViews": int(row.metric_values[2].value),
                "conversions": int(row.metric_values[3].value),
                "engagedSessions": int(row.metric_values[4].value)
            }
            rows_data.append(row_data)
        
        return pd.DataFrame(rows_data)
        
    except Exception as e:
        print(f"❌ Error obteniendo datos de segmentos: {str(e)}")
        return pd.DataFrame()


def get_conversion_events_data(client, property_id, start_date, end_date):
    """
    Obtiene datos específicos de eventos de conversión (formularios, calendly, etc.)
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame: Datos de eventos de conversión
    """
    
    try:
        # Eventos de conversión específicos para el embudo
        conversion_events = [
            "form_submit",
            "calendly_click", 
            "file_download",
            "button_click",
            "scroll_depth",
            "video_play",
            "outbound_click",
            "purchase",
            "sign_up",
            "login"
        ]
        
        all_conversion_data = []
        
        for event in conversion_events:
            try:
                request = RunReportRequest(
                    property=f"properties/{property_id}",
                    dimensions=[
                        Dimension(name="eventName"),
                        Dimension(name="pagePath"),
                        Dimension(name="eventParameterName"),
                        Dimension(name="eventParameterValue")
                    ],
                    metrics=[
                        Metric(name="eventCount"),
                        Metric(name="totalUsers"),
                        Metric(name="sessions")
                    ],
                    date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                    dimension_filter={
                        "filter": {
                            "field_name": "eventName",
                            "string_filter": {
                                "match_type": "EXACT",
                                "value": event
                            }
                        }
                    },
                    limit=10000
                )
                
                response = client.run_report(request)
                
                for row in response.rows:
                    conversion_data = {
                        "eventName": row.dimension_values[0].value,
                        "pagePath": row.dimension_values[1].value,
                        "eventParameterName": row.dimension_values[2].value,
                        "eventParameterValue": row.dimension_values[3].value,
                        "eventCount": int(row.metric_values[0].value),
                        "totalUsers": int(row.metric_values[1].value),
                        "sessions": int(row.metric_values[2].value)
                    }
                    all_conversion_data.append(conversion_data)
                    
            except Exception as e:
                # Evento no existe o no tiene datos
                continue
        
        if all_conversion_data:
            return pd.DataFrame(all_conversion_data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Error obteniendo eventos de conversión: {str(e)}")
        return pd.DataFrame()


def get_scroll_engagement_data(client, property_id, start_date, end_date):
    """
    Obtiene datos específicos de scroll y engagement para análisis de contenido
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        DataFrame: Datos de scroll y engagement
    """
    
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="pageTitle"),
                Dimension(name="eventName")
            ],
            metrics=[
                Metric(name="eventCount"),
                Metric(name="totalUsers"),
                Metric(name="engagedSessions"),
                Metric(name="userEngagementDuration")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter={
                "filter": {
                    "field_name": "eventName",
                    "string_filter": {
                        "match_type": "CONTAINS",
                        "value": "scroll"
                    }
                }
            },
            limit=10000
        )
        
        response = client.run_report(request)
        
        rows_data = []
        for row in response.rows:
            row_data = {
                "pagePath": row.dimension_values[0].value,
                "pageTitle": row.dimension_values[1].value,
                "eventName": row.dimension_values[2].value,
                "eventCount": int(row.metric_values[0].value),
                "totalUsers": int(row.metric_values[1].value),
                "engagedSessions": int(row.metric_values[2].value),
                "userEngagementDuration": float(row.metric_values[3].value)
            }
            rows_data.append(row_data)
        
        return pd.DataFrame(rows_data)
        
    except Exception as e:
        print(f"❌ Error obteniendo datos de scroll: {str(e)}")
        return pd.DataFrame()


def get_user_behavior_data(client, property_id, start_date, end_date):
    """
    Obtiene datos de comportamiento de usuarios
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        dict: Diccionario con datos de comportamiento
    """
    
    try:
        # Datos de usuarios nuevos vs recurrentes
        dimensions_users = ["date"]
        metrics_users = ["totalUsers", "newUsers"]
        
        df_users = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_users,
            metrics=metrics_users,
            page_size=100000
        )
        
        # Datos de dispositivos
        dimensions_devices = ["deviceCategory", "operatingSystem"]
        metrics_devices = ["sessions", "totalUsers", "bounceRate", "averageSessionDuration"]
        
        df_devices = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_devices,
            metrics=metrics_devices,
            page_size=100000
        )
        
        # Datos geográficos
        dimensions_geo = ["country", "city"]
        metrics_geo = ["sessions", "totalUsers", "bounceRate"]
        
        df_geo = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_geo,
            metrics=metrics_geo,
            page_size=100000
        )
        
        # Datos de horarios
        dimensions_hours = ["hour"]
        metrics_hours = ["sessions", "totalUsers"]
        
        df_hours = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_hours,
            metrics=metrics_hours,
            page_size=100000
        )
        
        return {
            'users': df_users,
            'devices': df_devices,
            'geo': df_geo,
            'hours': df_hours
        }
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de comportamiento: {str(e)}")
        return {
            'users': pd.DataFrame(),
            'devices': pd.DataFrame(),
            'geo': pd.DataFrame(),
            'hours': pd.DataFrame()
        }


def get_conversions_data(client, property_id, start_date, end_date):
    """
    Obtiene datos de conversiones y ROI
    
    Args:
        client: Cliente de GA4
        property_id: ID de la propiedad
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    
    Returns:
        dict: Diccionario con datos de conversiones
    """
    
    try:
        # Datos de conversiones por canal
        dimensions_conversions = ["sessionSource", "sessionMedium", "sessionDefaultChannelGrouping"]
        metrics_conversions = ["conversions", "totalRevenue", "sessions", "totalUsers"]
        
        df_conversions = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_conversions,
            metrics=metrics_conversions,
            page_size=100000
        )
        
        # Datos de eventos de conversión
        dimensions_events = ["eventName"]
        metrics_events = ["eventCount", "totalUsers"]
        
        df_events = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_events,
            metrics=metrics_events,
            page_size=100000
        )
        
        # Datos de tendencias de conversión
        dimensions_trends = ["date"]
        metrics_trends = ["conversions", "totalRevenue", "sessions"]
        
        df_trends = run_dynamic_report(
            client=client,
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions_trends,
            metrics=metrics_trends,
            page_size=100000
        )
        
        return {
            'conversions': df_conversions,
            'events': df_events,
            'trends': df_trends
        }
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de conversiones: {str(e)}")
        return {
            'conversions': pd.DataFrame(),
            'events': pd.DataFrame(),
            'trends': pd.DataFrame()
        }


def response_to_dataframe(response):
    """Convierte la respuesta de Google Analytics a DataFrame"""
    rows = []
    for row in response.rows:
        row_data = {}
        for i, dimension in enumerate(response.dimension_headers):
            row_data[dimension.name] = row.dimension_values[i].value
        for i, metric in enumerate(response.metric_headers):
            row_data[metric.name] = float(row.metric_values[i].value)
        rows.append(row_data)
    
    return pd.DataFrame(rows)
