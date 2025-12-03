"""
Crata AI - Helpers Module
Módulo de funciones auxiliares para el Growth Intelligence Dashboard

Este módulo contiene:
- analytics_helpers: Funciones para Google Analytics 4
- growth_analytics_helpers: Funciones específicas para métricas de crecimiento
- visualization_helpers: Funciones para crear visualizaciones con Plotly
- file_helpers: Funciones para manejo de archivos
"""

# Analytics helpers
from .analytics_helpers import (
    load_credentials,
    initialize_analytics_client,
    get_analytics_data,
    get_all_analytics_data,
    run_dynamic_report,
    get_top_pages_data,
    get_kpis_data,
    get_traffic_sources_data,
    get_content_performance_data,
    get_custom_events_data,
    get_user_segments_data,
    get_conversion_events_data,
    get_scroll_engagement_data,
    get_user_behavior_data,
    get_conversions_data,
    response_to_dataframe,
)

# Growth Analytics helpers
from .growth_analytics_helpers import (
    get_growth_kpi_data,
    get_conversion_funnel_data,
    get_utm_campaign_data,
    get_lead_generation_data,
    calculate_growth_metrics,
    get_all_growth_data,
    setup_ga4_conversion_tracking,
    setup_utm_parameters,
)

# Visualization helpers
from .visualization_helpers import (
    create_line_chart,
    create_multi_line_chart,
    create_bar_chart,
    create_pie_chart,
    create_funnel_chart,
    create_scatter_plot,
    create_metrics_summary,
    create_kpi_row,
    display_data_preview,
    create_channel_comparison_chart,
)

# File helpers
from .file_helpers import (
    create_zip_file,
    download_csv,
    generate_filename,
    save_data_to_file,
)

__all__ = [
    # Analytics
    "load_credentials",
    "initialize_analytics_client",
    "get_analytics_data",
    "get_all_analytics_data",
    "run_dynamic_report",
    "get_top_pages_data",
    "get_kpis_data",
    "get_traffic_sources_data",
    "get_content_performance_data",
    "get_custom_events_data",
    "get_user_segments_data",
    "get_conversion_events_data",
    "get_scroll_engagement_data",
    "get_user_behavior_data",
    "get_conversions_data",
    "response_to_dataframe",
    # Growth Analytics
    "get_growth_kpi_data",
    "get_conversion_funnel_data",
    "get_utm_campaign_data",
    "get_lead_generation_data",
    "calculate_growth_metrics",
    "get_all_growth_data",
    "setup_ga4_conversion_tracking",
    "setup_utm_parameters",
    # Visualization
    "create_line_chart",
    "create_multi_line_chart",
    "create_bar_chart",
    "create_pie_chart",
    "create_funnel_chart",
    "create_scatter_plot",
    "create_metrics_summary",
    "create_kpi_row",
    "display_data_preview",
    "create_channel_comparison_chart",
    # Files
    "create_zip_file",
    "download_csv",
    "generate_filename",
    "save_data_to_file",
]
