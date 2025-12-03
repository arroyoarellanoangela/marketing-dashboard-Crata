"""
Crata AI - Growth Intelligence Dashboard
=========================================

Sistema de inteligencia de crecimiento para análisis de marketing digital.

Estructura del paquete:
- config/: Configuraciones y tema visual
- helpers/: Funciones auxiliares para analytics y visualización
- components/: Componentes reutilizables de UI (sidebar, etc.)
- pages/: Páginas del dashboard
- utils/: Utilidades generales
- assets/: Recursos estáticos (imágenes, videos)

Vistas principales del Dashboard:
1. Vista Ejecutiva - CEO/Dirección
2. Vista Marketing/Operaciones - Growth Team
3. Vista de Contenidos - SEO/Content
4. Vista Leads & Activación - Marketing + Ventas

Basado en el documento de planificación del Dashboard de Marketing de Crata AI.
"""

__version__ = "1.0.0"
__author__ = "Crata AI"

# Importaciones principales para facilitar el acceso
from .config import (
    APP_CONFIG,
    GA4_CONFIG,
    COLORS,
    get_global_css,
)
