"""
=============================================================================
CRATA AI - GROWTH INTELLIGENCE DASHBOARD
=============================================================================

Punto de entrada principal de la aplicación.
Dashboard de Marketing para Crata AI con 4 vistas principales:

1. Tráfico General
2. Fuentes de Tráfico
3. Página y Contenido
4. Comportamiento Usuarios

Basado en el documento de planificación del Dashboard de Marketing de Crata AI.
=============================================================================
"""

import streamlit as st

# Importar páginas del dashboard
from src.pages.dashboard import main as dashboard_main
from src.pages.general_overview import main as general_overview_main
from src.pages.traffic_sources import main as traffic_sources_main
from src.pages.content_performance import main as content_performance_main
from src.pages.user_behavior import main as user_behavior_main
from src.pages.alerts import main as alerts_main


# =============================================================================
# CONFIGURACIÓN DE NAVEGACIÓN
# =============================================================================

# Mapeo de páginas disponibles
PAGES = {
    "dashboard": {
        "title": "Página Principal",
        "function": dashboard_main,
        "description": "Página de inicio del dashboard"
    },
    "general_overview": {
        "title": "Tráfico General",
        "function": general_overview_main,
        "description": "Vista general de tráfico"
    },
    "traffic_sources": {
        "title": "Fuentes de Tráfico",
        "function": traffic_sources_main,
        "description": "Análisis de fuentes de tráfico"
    },
    "content_performance": {
        "title": "Página y Contenido",
        "function": content_performance_main,
        "description": "Rendimiento de páginas y contenido"
    },
    "user_behavior": {
        "title": "Comportamiento Usuarios",
        "function": user_behavior_main,
        "description": "Análisis de comportamiento de usuarios"
    },
    "alerts": {
        "title": "Alertas",
        "function": alerts_main,
        "description": "Sistema de alertas y notificaciones"
    },
}


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """
    Función principal que maneja la navegación entre páginas.
    Utiliza session_state para mantener el estado de la navegación.
    """
    
    # Inicializar session state para navegación
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Obtener la página actual
    current_page = st.session_state.page
    
    # Verificar que la página existe
    if current_page not in PAGES:
        current_page = "dashboard"
        st.session_state.page = current_page
    
    # Ejecutar la función de la página actual
    page_config = PAGES[current_page]
    page_function = page_config["function"]
    
    # Llamar a la función de la página
    page_function()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    main()
