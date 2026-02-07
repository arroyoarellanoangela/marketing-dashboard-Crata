"""
Crata AI - Growth Intelligence Dashboard
Configuración central de la aplicación

Este archivo contiene todas las configuraciones de la aplicación:
- Configuración de la app (Streamlit)
- Configuración de Google Analytics 4
- Configuración de Apollo
- Métricas y dimensiones disponibles
- Conjuntos de datos para análisis
"""
import os

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

APP_CONFIG = {
    "title": "Growth Intelligence Dashboard - Crata AI",
    "page_icon": "src/assets/G I D.jpg",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "version": "1.0.0",
}

# =============================================================================
# CONFIGURACIÓN DE GOOGLE ANALYTICS 4
# =============================================================================

GA4_CONFIG = {
    "property_id": "381346600",
    "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
    "credentials_file": "credentials.json",
}

# =============================================================================
# CONFIGURACIÓN DE DIANA
# =============================================================================

DIANA_CONFIG = {
    "api_key": os.getenv("APOLLO_API_KEY", ""),
    "api_url": "https://api.apollo.io/api/v1",
    "timeout": 30
}

# =============================================================================
# MÉTRICAS GA4 DISPONIBLES
# =============================================================================

GA4_METRICS = [
    "sessions",
    "totalUsers", 
    "newUsers",
    "screenPageViews",
    "bounceRate",
    "averageSessionDuration",
    "conversions",
    "totalRevenue",
    "engagementRate",
    "sessionsPerUser",
    "eventCount",
    "userEngagementDuration",
    "engagedSessions",
    "firstTimePurchaserConversionRate",
    "engagedSessionsPerUser",
    "averageEngagementTime"
]

# =============================================================================
# DIMENSIONES GA4 DISPONIBLES
# =============================================================================

GA4_DIMENSIONS = [
    "date",
    "country",
    "city",
    "region",
    "deviceCategory",
    "operatingSystem",
    "browser",
    "sessionSource",
    "sessionMedium",
    "sessionCampaignId",
    "pagePath",
    "pageTitle",
    "landingPage",
    "sessionDefaultChannelGrouping",
    "userGender",
    "userAgeBracket",
    "platform",
    "screenResolution",
    "eventName",
    "hour",
    "sessionSourceMedium",
    "language",
    "landingPagePlusQueryString",
    "sessionCampaignName",
    "sourcePlatform"
]

# =============================================================================
# CONJUNTOS DE DATOS PARA ANÁLISIS
# =============================================================================

DATA_SETS_CONFIG = {
    # Dataset principal con TODAS las dimensiones para filtros
    "datos_temporales": {
        "dimensions": ["date", "country", "pagePath", "sessionDefaultChannelGrouping"],
        "metrics": ["sessions", "totalUsers", "newUsers", "screenPageViews", "bounceRate", "averageSessionDuration", "engagementRate", "conversions", "totalRevenue", "engagedSessions"]
    },
    "datos_geograficos": {
        "dimensions": ["date", "country", "city", "region", "pagePath", "sessionDefaultChannelGrouping"],
        "metrics": ["sessions", "totalUsers", "screenPageViews", "conversions", "engagedSessions", "averageSessionDuration"]
    },
    "datos_dispositivos": {
        "dimensions": ["deviceCategory", "operatingSystem", "browser", "country", "sessionDefaultChannelGrouping"],
        "metrics": ["sessions", "totalUsers", "screenPageViews", "bounceRate", "averageSessionDuration", "engagedSessions"]
    },
    "datos_trafico": {
        "dimensions": ["sessionSource", "sessionMedium", "sessionDefaultChannelGrouping", "sessionSourceMedium", "country", "pagePath"],
        "metrics": ["sessions", "totalUsers", "newUsers", "bounceRate", "averageSessionDuration", "conversions", "engagedSessions"]
    },
    "datos_contenido": {
        "dimensions": ["date", "pagePath", "pageTitle", "landingPage", "country", "sessionDefaultChannelGrouping"],
        "metrics": ["screenPageViews", "sessions", "bounceRate", "averageSessionDuration", "engagedSessions", "userEngagementDuration", "activeUsers", "eventCount"]
    },
    "datos_usuarios": {
        "dimensions": ["date"],
        "metrics": ["totalUsers", "newUsers", "sessions", "userEngagementDuration", "averageSessionDuration", "engagedSessions"]
    },
    "datos_eventos": {
        "dimensions": ["eventName"],
        "metrics": ["eventCount", "totalUsers", "sessions", "engagedSessions"]
    },
    "datos_horarios": {
        "dimensions": ["date", "hour"],
        "metrics": ["sessions", "totalUsers", "screenPageViews", "engagedSessions", "conversions"]
    },
    "datos_demograficos": {
        "dimensions": ["userGender", "userAgeBracket", "language"],
        "metrics": ["totalUsers", "newUsers", "sessions", "engagedSessions"]
    },
    "datos_engagement": {
        "dimensions": ["date"],
        "metrics": ["userEngagementDuration", "engagedSessions", "sessions", "totalUsers", "averageSessionDuration", "engagementRate", "bounceRate", "screenPageViews", "conversions", "totalRevenue"]
    },
    "datos_embudo": {
        "dimensions": ["date", "pagePath", "eventName"],
        "metrics": ["sessions", "totalUsers", "conversions", "engagedSessions", "eventCount", "screenPageViews"]
    },
    "datos_campanas": {
        "dimensions": ["sessionCampaignName", "sessionSource", "sessionMedium", "landingPagePlusQueryString"],
        "metrics": ["sessions", "totalUsers", "conversions", "engagedSessions", "totalRevenue", "bounceRate"]
    },
    "datos_conversiones": {
        "dimensions": ["date", "eventName", "pagePath"],
        "metrics": ["eventCount", "totalUsers", "sessions", "conversions", "engagedSessions"]
    }
}

# =============================================================================
# EVENTOS DE CONVERSIÓN (GA4)
# =============================================================================

CONVERSION_EVENTS = {
    "cta_click": {
        "name": "cta_click",
        "description": "Clics en botones de llamada a la acción",
        "category": "engagement"
    },
    "form_submit": {
        "name": "form_submit",
        "description": "Envío de formularios",
        "category": "lead_generation"
    },
    "calendly_click": {
        "name": "calendly_click",
        "description": "Clics en Calendly para agendar reuniones",
        "category": "lead_generation"
    },
    "file_download": {
        "name": "file_download",
        "description": "Descargas de archivos",
        "category": "engagement"
    },
    "scroll": {
        "name": "scroll",
        "description": "Eventos de profundidad de scroll",
        "category": "engagement"
    }
}

# =============================================================================
# DEFINICIÓN DE KPIs Y MÉTRICAS CLAVE
# =============================================================================

KPI_DEFINITIONS = {
    # Métricas de High-Intent
    "high_intent_session": {
        "name": "High-Intent Session",
        "description": "Sesión con scroll >75% + tiempo >60s + acción (CTA/form/click)",
        "formula": "scroll_depth > 75 AND session_duration > 60 AND has_action = True"
    },
    "deep_engagement": {
        "name": "Deep Engagement",
        "description": "Scroll >75% Y tiempo >90s",
        "formula": "scroll_depth > 75 AND session_duration > 90"
    },
    
    # Métricas de Conversión
    "visit_to_lead": {
        "name": "Visit → Lead Conversion",
        "description": "Ratio de leads totales sobre sesiones",
        "formula": "total_leads / sessions"
    },
    "lead_to_meeting": {
        "name": "Lead → Meeting",
        "description": "Ratio de reuniones sobre leads",
        "formula": "meetings / total_leads"
    },
    
    # Métricas de Engagement
    "engagement_rate": {
        "name": "Engagement Rate",
        "description": "Porcentaje de sesiones con engagement",
        "formula": "engaged_sessions / sessions"
    },
    "avg_session_duration": {
        "name": "Average Session Duration",
        "description": "Duración promedio de sesión en segundos",
        "formula": "total_session_duration / sessions"
    }
}

# =============================================================================
# CONFIGURACIÓN DE VISTAS DEL DASHBOARD
# =============================================================================

DASHBOARD_VIEWS = {
    "executive": {
        "name": "Vista Ejecutiva",
        "target": "CEO / Dirección",
        "description": "Visión global del negocio digital",
        "page": "executive_dashboard"
    },
    "marketing": {
        "name": "Vista Marketing / Operaciones",
        "target": "Marketing / Growth",
        "description": "Optimización semanal de canales",
        "page": "marketing_operations"
    },
    "content": {
        "name": "Vista de Contenidos",
        "target": "SEO, Content, Growth",
        "description": "Contenido que impulsa crecimiento",
        "page": "content_performance_growth"
    },
    "leads": {
        "name": "Vista Leads & Activación",
        "target": "Marketing + Ventas",
        "description": "Generación y activación de leads",
        "page": "leads_activation"
    }
}

# =============================================================================
# CONFIGURACIÓN DE UTMs ESTÁNDAR
# =============================================================================

UTM_TEMPLATES = {
    "linkedin": {
        "utm_source": "linkedin",
        "utm_medium": "social",
        "utm_campaign": "{campaign_name}",
        "utm_content": "{content_type}",
        "utm_term": "{keyword}"
    },
    "email": {
        "utm_source": "email",
        "utm_medium": "newsletter",
        "utm_campaign": "{campaign_name}",
        "utm_content": "{content_type}",
        "utm_term": "{keyword}"
    },
    "events": {
        "utm_source": "event",
        "utm_medium": "referral",
        "utm_campaign": "{event_name}",
        "utm_content": "{content_type}",
        "utm_term": "{keyword}"
    }
}
