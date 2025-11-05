# Google Analytics Dashboard - Configuración

# Configuración de la aplicación
APP_CONFIG = {
    "title": "Google Analytics Dashboard",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configuración de Google Analytics
GA4_CONFIG = {
    "property_id": "381346600",
    "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
    "credentials_file": "credentials.json"
}

# Métricas disponibles para GA4
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

# Dimensiones disponibles para GA4
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

# Configuración de conjuntos de datos para descarga masiva
DATA_SETS_CONFIG = {
    "datos_temporales": {
        "dimensions": ["date"],
        "metrics": ["sessions", "totalUsers", "newUsers", "screenPageViews", "bounceRate", "averageSessionDuration", "engagementRate", "conversions", "totalRevenue", "engagedSessions"]
    },
    "datos_geograficos": {
        "dimensions": ["country", "city", "region"],
        "metrics": ["sessions", "totalUsers", "screenPageViews", "conversions", "engagedSessions"]
    },
    "datos_dispositivos": {
        "dimensions": ["deviceCategory", "operatingSystem", "browser"],
        "metrics": ["sessions", "totalUsers", "screenPageViews", "bounceRate", "averageSessionDuration", "engagedSessions"]
    },
    "datos_trafico": {
        "dimensions": ["sessionSource", "sessionMedium", "sessionDefaultChannelGrouping", "sessionSourceMedium"],
        "metrics": ["sessions", "totalUsers", "newUsers", "bounceRate", "averageSessionDuration", "conversions", "engagedSessions"]
    },
    "datos_contenido": {
        "dimensions": ["pagePath", "pageTitle", "landingPage"],
        "metrics": ["screenPageViews", "sessions", "bounceRate", "averageSessionDuration", "engagedSessions", "userEngagementDuration"]
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
