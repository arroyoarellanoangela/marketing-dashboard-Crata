"""
Crata AI - Configuration Module
Módulo de configuración central para el Growth Intelligence Dashboard
"""

from .settings import (
    APP_CONFIG,
    GA4_CONFIG,
    GA4_METRICS,
    GA4_DIMENSIONS,
    DATA_SETS_CONFIG,
    CONVERSION_EVENTS,
    KPI_DEFINITIONS,
    DASHBOARD_VIEWS,
    UTM_TEMPLATES,
)

from .theme import (
    COLORS,
    TYPOGRAPHY,
    SPACING,
    PLOTLY_LAYOUT,
    PLOTLY_COLOR_SEQUENCE,
    get_global_css,
    apply_plotly_theme,
    get_kpi_card_html,
    get_section_header_html,
)

__all__ = [
    # Settings
    "APP_CONFIG",
    "GA4_CONFIG",
    "GA4_METRICS",
    "GA4_DIMENSIONS",
    "DATA_SETS_CONFIG",
    "CONVERSION_EVENTS",
    "KPI_DEFINITIONS",
    "DASHBOARD_VIEWS",
    "UTM_TEMPLATES",
    # Theme
    "COLORS",
    "TYPOGRAPHY",
    "SPACING",
    "PLOTLY_LAYOUT",
    "PLOTLY_COLOR_SEQUENCE",
    "get_global_css",
    "apply_plotly_theme",
    "get_kpi_card_html",
    "get_section_header_html",
]
