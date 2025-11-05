"""
GA4 Analytics Helpers for Growth Intelligence Dashboard
Funciones específicas para obtener datos de Google Analytics 4 para el dashboard de crecimiento
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    Filter,
    FilterExpression,
    OrderBy
)
import json
import os


def get_growth_kpi_data(client, property_id, start_date, end_date):
    """Obtiene los KPIs principales para el dashboard de crecimiento"""
    
    try:
        # Métricas principales para KPIs
        metrics = [
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="screenPageViews"),
            Metric(name="conversions"),
            Metric(name="engagementRate"),
            Metric(name="averageSessionDuration")
        ]
        
        # Dimensiones temporales
        dimensions = [
            Dimension(name="date")
        ]
        
        # Solicitud de datos
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))]
        )
        
        response = client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            row_data = {}
            
            # Dimensiones
            for i, dimension in enumerate(dimensions):
                row_data[dimension.name] = row.dimension_values[i].value
            
            # Métricas
            for i, metric in enumerate(metrics):
                row_data[metric.name] = int(row.metric_values[i].value) if row.metric_values[i].value else 0
            
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error obteniendo datos de KPIs: {e}")
        return None


def get_traffic_sources_data(client, property_id, start_date, end_date):
    """Obtiene datos de fuentes de tráfico"""
    
    try:
        # Métricas
        metrics = [
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="conversions")
        ]
        
        # Dimensiones de tráfico
        dimensions = [
            Dimension(name="sessionDefaultChannelGrouping"),
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium")
        ]
        
        # Solicitud de datos
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)]
        )
        
        response = client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            row_data = {}
            
            # Dimensiones
            for i, dimension in enumerate(dimensions):
                row_data[dimension.name] = row.dimension_values[i].value
            
            # Métricas
            for i, metric in enumerate(metrics):
                row_data[metric.name] = int(row.metric_values[i].value) if row.metric_values[i].value else 0
            
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error obteniendo datos de fuentes de tráfico: {e}")
        return None


def get_conversion_funnel_data(client, property_id, start_date, end_date):
    """Obtiene datos del embudo de conversión"""
    
    try:
        # Eventos de conversión específicos
        conversion_events = [
            "page_view",
            "form_start", 
            "form_submit",
            "calendly_click",
            "download"
        ]
        
        # Métricas
        metrics = [
            Metric(name="eventCount"),
            Metric(name="totalUsers")
        ]
        
        # Dimensiones
        dimensions = [
            Dimension(name="eventName")
        ]
        
        # Filtro para eventos de conversión
        filter_expression = FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.CONTAINS,
                    value="form_submit|calendly|download"
                )
            )
        )
        
        # Solicitud de datos
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=filter_expression,
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)]
        )
        
        response = client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            row_data = {}
            
            # Dimensiones
            for i, dimension in enumerate(dimensions):
                row_data[dimension.name] = row.dimension_values[i].value
            
            # Métricas
            for i, metric in enumerate(metrics):
                row_data[metric.name] = int(row.metric_values[i].value) if row.metric_values[i].value else 0
            
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error obteniendo datos del embudo de conversión: {e}")
        return None


def get_content_performance_data(client, property_id, start_date, end_date):
    """Obtiene datos de rendimiento de contenido"""
    
    try:
        # Métricas de contenido
        metrics = [
            Metric(name="screenPageViews"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="averageSessionDuration"),
            Metric(name="engagementRate"),
            Metric(name="conversions")
        ]
        
        # Dimensiones de contenido
        dimensions = [
            Dimension(name="pagePath"),
            Dimension(name="pageTitle"),
            Dimension(name="landingPage")
        ]
        
        # Filtro para páginas de blog y servicios
        filter_expression = FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.CONTAINS,
                    value="/blog/|/services/|/about/"
                )
            )
        )
        
        # Solicitud de datos
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=filter_expression,
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)]
        )
        
        response = client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            row_data = {}
            
            # Dimensiones
            for i, dimension in enumerate(dimensions):
                row_data[dimension.name] = row.dimension_values[i].value
            
            # Métricas
            for i, metric in enumerate(metrics):
                row_data[metric.name] = int(row.metric_values[i].value) if row.metric_values[i].value else 0
            
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error obteniendo datos de rendimiento de contenido: {e}")
        return None


def get_utm_campaign_data(client, property_id, start_date, end_date):
    """Obtiene datos de campañas UTM"""
    
    try:
        # Métricas
        metrics = [
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="conversions"),
            Metric(name="totalRevenue")
        ]
        
        # Dimensiones UTM
        dimensions = [
            Dimension(name="sessionCampaignName"),
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
            Dimension(name="sessionCampaignId")
        ]
        
        # Filtro para campañas UTM
        filter_expression = FilterExpression(
            filter=Filter(
                field_name="sessionCampaignName",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.REGEXP,
                    value=".*"
                )
            )
        )
        
        # Solicitud de datos
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=filter_expression,
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)]
        )
        
        response = client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            row_data = {}
            
            # Dimensiones
            for i, dimension in enumerate(dimensions):
                row_data[dimension.name] = row.dimension_values[i].value
            
            # Métricas
            for i, metric in enumerate(metrics):
                row_data[metric.name] = int(row.metric_values[i].value) if row.metric_values[i].value else 0
            
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error obteniendo datos de campañas UTM: {e}")
        return None


def get_lead_generation_data(client, property_id, start_date, end_date):
    """Obtiene datos específicos de generación de leads"""
    
    try:
        # Eventos de conversión de leads
        lead_events = [
            "form_submit",
            "calendly_click", 
            "download",
            "contact_form_submit"
        ]
        
        # Métricas
        metrics = [
            Metric(name="eventCount"),
            Metric(name="totalUsers"),
            Metric(name="conversions")
        ]
        
        # Dimensiones
        dimensions = [
            Dimension(name="eventName"),
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
            Dimension(name="pagePath")
        ]
        
        # Filtro para eventos de leads
        filter_expression = FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.REGEXP,
                    value="form_submit|calendly|download|contact"
                )
            )
        )
        
        # Solicitud de datos
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=filter_expression,
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)]
        )
        
        response = client.run_report(request)
        
        # Procesar respuesta
        data = []
        for row in response.rows:
            row_data = {}
            
            # Dimensiones
            for i, dimension in enumerate(dimensions):
                row_data[dimension.name] = row.dimension_values[i].value
            
            # Métricas
            for i, metric in enumerate(metrics):
                row_data[metric.name] = int(row.metric_values[i].value) if row.metric_values[i].value else 0
            
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error obteniendo datos de generación de leads: {e}")
        return None


def calculate_growth_metrics(df, metric_name, period_days=30):
    """Calcula métricas de crecimiento (YoY, MoM)"""
    
    if df.empty or metric_name not in df.columns:
        return {"current": 0, "previous": 0, "change": 0}
    
    # Obtener datos actuales y anteriores
    current_period = df.tail(period_days)[metric_name].sum()
    previous_period = df.head(period_days)[metric_name].sum() if len(df) > period_days else current_period
    
    # Calcular cambio porcentual
    if previous_period > 0:
        change_percent = ((current_period - previous_period) / previous_period) * 100
    else:
        change_percent = 0
    
    return {
        "current": int(current_period),
        "previous": int(previous_period),
        "change": round(change_percent, 1)
    }


def get_all_growth_data(client, property_id, start_date, end_date):
    """Obtiene todos los datos necesarios para el Growth Intelligence Dashboard"""
    
    with st.spinner("🔄 Obteniendo datos del Growth Intelligence Dashboard..."):
        
        growth_data = {}
        
        # KPIs principales
        growth_data['kpis'] = get_growth_kpi_data(client, property_id, start_date, end_date)
        
        # Fuentes de tráfico
        growth_data['traffic_sources'] = get_traffic_sources_data(client, property_id, start_date, end_date)
        
        # Embudo de conversión
        growth_data['conversion_funnel'] = get_conversion_funnel_data(client, property_id, start_date, end_date)
        
        # Rendimiento de contenido
        growth_data['content_performance'] = get_content_performance_data(client, property_id, start_date, end_date)
        
        # Campañas UTM
        growth_data['utm_campaigns'] = get_utm_campaign_data(client, property_id, start_date, end_date)
        
        # Generación de leads
        growth_data['lead_generation'] = get_lead_generation_data(client, property_id, start_date, end_date)
        
        return growth_data


def setup_ga4_conversion_tracking():
    """Configuración recomendada para tracking de conversiones en GA4"""
    
    st.markdown("### 🔧 GA4 Conversion Tracking Setup")
    
    st.markdown("""
    **Para implementar el tracking completo de conversiones, configura estos eventos en GA4:**
    
    #### 📊 Eventos de Conversión Recomendados:
    
    1. **CTA Clicks**
       ```javascript
       gtag('event', 'cta_click', {
         'event_category': 'engagement',
         'event_label': 'button_name',
         'page_location': window.location.href
       });
       ```
    
    2. **Form Submissions**
       ```javascript
       gtag('event', 'form_submit', {
         'event_category': 'lead_generation',
         'event_label': 'form_type',
         'value': 1
       });
       ```
    
    3. **Calendly Clicks**
       ```javascript
       gtag('event', 'calendly_click', {
         'event_category': 'lead_generation',
         'event_label': 'meeting_request',
         'value': 1
       });
       ```
    
    4. **Downloads**
       ```javascript
       gtag('event', 'file_download', {
         'event_category': 'engagement',
         'event_label': 'file_name',
         'value': 1
       });
       ```
    
    #### 🚫 Exclusión de IP Interna:
    
    En GA4 Admin → Data Streams → Configure tag settings → Define internal traffic:
    - IP ranges: `192.168.1.0/24`, `10.0.0.0/8`
    - Traffic type name: `Internal`
    
    #### 📈 Configuración de Embudo:
    
    1. **Audiences** (para remarketing):
       - Form viewers (no completers)
       - High-value page visitors
       - Cart abandoners
    
    2. **Conversions**:
       - Marcar eventos como conversiones
       - Configurar valores de conversión
    
    3. **Custom Dimensions**:
       - Lead source quality
       - Content engagement level
       - User intent score
    """)
    
    st.success("✅ Configuración de tracking recomendada mostrada")


def setup_utm_parameters():
    """Configuración estándar de parámetros UTM"""
    
    st.markdown("### 🏷️ UTM Parameters Setup")
    
    st.markdown("""
    **Parámetros UTM estándar para Crata AI:**
    
    #### 📧 Email Marketing:
    ```
    utm_source=email
    utm_medium=newsletter
    utm_campaign=weekly_digest_2024
    utm_content=cta_button
    utm_term=ai_marketing
    ```
    
    #### 💼 LinkedIn Campaigns:
    ```
    utm_source=linkedin
    utm_medium=social
    utm_campaign=ai_consulting_q1_2024
    utm_content=sponsored_post
    utm_term=marketing_automation
    ```
    
    #### 🎪 Events & Webinars:
    ```
    utm_source=event
    utm_medium=referral
    utm_campaign=marketing_summit_2024
    utm_content=speaker_bio
    utm_term=growth_marketing
    ```
    
    #### 📱 Social Media:
    ```
    utm_source=twitter
    utm_medium=social
    utm_campaign=thought_leadership
    utm_content=tweet_thread
    utm_term=ai_trends
    ```
    
    #### 🔍 SEO Content:
    ```
    utm_source=google
    utm_medium=organic
    utm_campaign=content_marketing
    utm_content=blog_post
    utm_term=marketing_automation
    ```
    """)
    
    st.success("✅ Parámetros UTM estándar configurados")
