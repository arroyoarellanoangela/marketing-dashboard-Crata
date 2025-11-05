"""
Main Application Entry Point
Punto de entrada principal de la aplicación con navegación entre páginas
"""

import streamlit as st
from src.pages.dashboard import main as dashboard_main
from src.pages.general_overview import main as general_overview_main
from src.pages.data_inspector import main as data_inspector_main
from src.pages.executive_dashboard import main as executive_dashboard_main
from src.pages.marketing_operations import main as marketing_operations_main
from src.pages.content_performance_growth import main as content_performance_growth_main
from src.pages.leads_activation import main as leads_activation_main

# Inicializar session state para navegación
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Navegación entre páginas
if st.session_state.page == "dashboard":
    dashboard_main()
elif st.session_state.page == "general_overview":
    general_overview_main()
elif st.session_state.page == "data_inspector":
    data_inspector_main()
elif st.session_state.page == "executive_dashboard":
    executive_dashboard_main()
elif st.session_state.page == "marketing_operations":
    marketing_operations_main()
elif st.session_state.page == "content_performance_growth":
    content_performance_growth_main()
elif st.session_state.page == "leads_activation":
    leads_activation_main()