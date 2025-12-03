"""
Crata AI - Visuals Module
Módulo de visualizaciones especializadas para el Growth Intelligence Dashboard

Este módulo contiene:
- metrics.py: Funciones genéricas de métricas y gráficos
- metrics_ejecutivo.py: Visualizaciones específicas para el Executive Dashboard
"""

from .metrics import (
    create_metric_card,
    create_user_kpis,
    create_user_kpis_optimized,
    create_new_vs_returning_chart,
    create_dashboard_overview,
    create_top_pages_table,
    create_trend_chart,
    create_comparison_chart,
)

from .metrics_ejecutivo import (
    renderizar_executive_dashboard,
    crear_header_kpis,
    crear_grafico_evolucion_temporal,
    crear_grafico_fuentes_oportunidad,
    crear_grafico_embudo_global,
    crear_tabla_ejecutiva,
    generar_insights_automaticos,
    mostrar_insight_cards,
    calcular_mom_robusto,
    calcular_yoy_robusto,
)

__all__ = [
    # Metrics genéricos
    "create_metric_card",
    "create_user_kpis",
    "create_user_kpis_optimized",
    "create_new_vs_returning_chart",
    "create_dashboard_overview",
    "create_top_pages_table",
    "create_trend_chart",
    "create_comparison_chart",
    # Executive Dashboard
    "renderizar_executive_dashboard",
    "crear_header_kpis",
    "crear_grafico_evolucion_temporal",
    "crear_grafico_fuentes_oportunidad",
    "crear_grafico_embudo_global",
    "crear_tabla_ejecutiva",
    "generar_insights_automaticos",
    "mostrar_insight_cards",
    "calcular_mom_robusto",
    "calcular_yoy_robusto",
]
