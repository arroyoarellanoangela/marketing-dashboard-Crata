"""
Crata AI - Components Module
Componentes reutilizables de UI para el dashboard
"""

from .sidebar import (
    mostrar_sidebar_completo,
    mostrar_sidebar_variables,
    mostrar_sidebar_filtros,
    mostrar_filtros_fecha,
    aplicar_filtros_fecha,
    aplicar_filtros_a_datos,
    create_sidebar,
    create_analytics_sidebar,
    create_navigation_sidebar,
    smart_multiselect,
)

__all__ = [
    "mostrar_sidebar_completo",
    "mostrar_sidebar_variables",
    "mostrar_sidebar_filtros",
    "mostrar_filtros_fecha",
    "aplicar_filtros_fecha",
    "aplicar_filtros_a_datos",
    "create_sidebar",
    "create_analytics_sidebar",
    "create_navigation_sidebar",
    "smart_multiselect",
]
