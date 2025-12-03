"""
=============================================================================
CRATA AI - GROWTH INTELLIGENCE DASHBOARD
=============================================================================

Punto de entrada principal de la aplicación.
Dashboard de Marketing para Crata AI con 4 vistas principales:

1. Vista Ejecutiva - CEO/Dirección
2. Vista Marketing/Operaciones - Growth Team
3. Vista de Contenidos - SEO/Content
4. Vista Leads & Activación - Marketing + Ventas

Basado en el documento de planificación del Dashboard de Marketing de Crata AI.
=============================================================================
"""

import streamlit as st

# Importar páginas del dashboard
from src.pages.dashboard import main as dashboard_main
from src.pages.general_overview import main as general_overview_main
from src.pages.data_inspector import main as data_inspector_main
from src.pages.marketing_operations import main as marketing_operations_main
from src.pages.content_performance_growth import main as content_performance_growth_main
from src.pages.leads_activation import main as leads_activation_main


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
        "title": "Executive Dashboard",
        "function": general_overview_main,
        "description": "Vista Ejecutiva - CEO/Dirección"
    },
    "data_inspector": {
        "title": "Data Inspector",
        "function": data_inspector_main,
        "description": "Explorador de datos detallado"
    },
    "marketing_operations": {
        "title": "Marketing Operations",
        "function": marketing_operations_main,
        "description": "Vista Marketing/Operaciones - Growth Team"
    },
    "content_performance_growth": {
        "title": "Content Performance",
        "function": content_performance_growth_main,
        "description": "Vista de Contenidos - SEO/Content"
    },
    "leads_activation": {
        "title": "Leads & Activation",
        "function": leads_activation_main,
        "description": "Vista Leads & Activación - Marketing + Ventas"
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
