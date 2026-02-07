"""
Crata AI Design System Theme
Sistema de diseño oficial para el Growth Intelligence Dashboard
Basado en el documento de planificación del Dashboard de Marketing
"""

# =============================================================================
# PALETA DE COLORES CRATA AI
# =============================================================================

COLORS = {
    # Fondos principales
    "background_primary": "#0A0A0A",      # Negro volcán - Fondo de toda la app
    "background_secondary": "#1A1A1A",     # Gris grafito - Tarjetas KPI y contenedores
    
    # Texto
    "text_primary": "#FFFFFF",             # Blanco puro - títulos
    "text_secondary": "#CCCCCC",           # Blanco suave - cuerpo
    "text_label": "#BDBDBD",               # Gris claro - labels, subtítulos
    "text_muted": "#999999",               # Gris tenue - auxiliares
    
    # Acentos corporativos
    "accent_teal": "#A7C9C6",              # Teal Inteligente - SEO, engagement, info neutra
    "accent_yellow": "#E7B400",            # Amarillo Crata - Conversiones, CTA, highlights
    
    # Colores de estado
    "success": "#22C55E",                  # Verde para éxito/positivo
    "warning": "#F59E0B",                  # Naranja para advertencia
    "error": "#EF4444",                    # Rojo para error/negativo
    "info": "#3B82F6",                     # Azul para información
    
    # Colores para gráficos
    "chart_primary": "#A7C9C6",            # Línea/barra principal
    "chart_secondary": "#E7B400",          # Línea/barra comparativa
    "chart_tertiary": "#6FA8A3",           # Tercer color para gráficos
    "chart_grid": "rgba(255,255,255,0.04)", # Grid de gráficos
    "chart_axis": "#AAAAAA",               # Color de ejes
    
    # Bordes y sombras
    "border_subtle": "rgba(167,201,198,0.4)",  # Borde sutil
    "shadow_card": "rgba(255,255,255,0.03)",   # Sombra de tarjetas
}

# =============================================================================
# TIPOGRAFÍA
# =============================================================================

TYPOGRAPHY = {
    # Familias de fuentes
    "font_primary": "Montserrat, Inter, Roboto, sans-serif",
    "font_secondary": "Poppins, Inter, sans-serif",
    
    # Escalas tipográficas
    "h1": {"size": "42px", "weight": "800"},      # Título de página
    "h2": {"size": "32px", "weight": "700"},      # Subtítulos
    "h3": {"size": "24px", "weight": "600"},      # Secciones
    "kpi_xl": {"size": "48px", "weight": "700"},  # Métrica principal
    "kpi_lg": {"size": "36px", "weight": "700"},  # Métrica secundaria
    "kpi_label": {"size": "14px", "weight": "400"}, # Nombre del KPI
    "body": {"size": "15px", "weight": "400"},    # Texto general
    "caption": {"size": "12px", "weight": "300"}, # Datos auxiliares
}

# =============================================================================
# ESPACIADO Y GRID
# =============================================================================

SPACING = {
    "section_margin": "40px",      # Margen general entre secciones
    "card_padding": "24px",        # Padding interno de tarjetas
    "card_gap": "24px",            # Espacio entre tarjetas
    "border_radius": "18px",       # Radio de borde para tarjetas
    "button_radius": "10px",       # Radio de borde para botones
}

# =============================================================================
# COMPONENTES UI - ESTILOS CSS
# =============================================================================

# Estilos de tarjetas KPI
KPI_CARD_STYLE = f"""
    background: {COLORS['background_secondary']};
    border-radius: {SPACING['border_radius']};
    padding: {SPACING['card_padding']} 28px;
    color: {COLORS['text_primary']};
    box-shadow: 0px 0px 14px {COLORS['shadow_card']};
"""

# Estilo de botón principal
BUTTON_PRIMARY_STYLE = f"""
    background: {COLORS['accent_yellow']};
    color: {COLORS['background_primary']};
    border-radius: {SPACING['button_radius']};
    padding: 10px 24px;
    font-weight: 600;
    border: none;
"""

# Estilo de botón secundario
BUTTON_SECONDARY_STYLE = f"""
    background: transparent;
    color: {COLORS['accent_teal']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: {SPACING['button_radius']};
    padding: 10px 24px;
    font-weight: 600;
"""

# =============================================================================
# CONFIGURACIÓN DE GRÁFICOS PLOTLY
# =============================================================================

PLOTLY_LAYOUT = {
    "plot_bgcolor": COLORS["background_primary"],
    "paper_bgcolor": COLORS["background_primary"],
    "font": {
        "color": COLORS["text_secondary"],
        "family": TYPOGRAPHY["font_primary"],
    },
    "title": {
        "font": {
            "color": COLORS["text_primary"],
            "size": 18,
        }
    },
    "xaxis": {
        "gridcolor": COLORS["chart_grid"],
        "tickfont": {"color": COLORS["chart_axis"]},
        "titlefont": {"color": COLORS["text_label"]},
    },
    "yaxis": {
        "gridcolor": COLORS["chart_grid"],
        "tickfont": {"color": COLORS["chart_axis"]},
        "titlefont": {"color": COLORS["text_label"]},
    },
    "legend": {
        "font": {"color": COLORS["text_secondary"]},
        "bgcolor": "rgba(0,0,0,0)",
    },
}

# Secuencia de colores para gráficos
PLOTLY_COLOR_SEQUENCE = [
    COLORS["chart_primary"],
    COLORS["chart_secondary"],
    COLORS["chart_tertiary"],
    COLORS["info"],
    COLORS["success"],
    COLORS["warning"],
]

# =============================================================================
# CSS GLOBAL PARA STREAMLIT
# =============================================================================

def get_global_css():
    """Retorna el CSS global para aplicar el tema Crata en Streamlit"""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600&display=swap');
    
    /* Fondo principal de la app */
    .stApp {{
        background-color: {COLORS['background_primary']} !important;
    }}
    
    .main {{
        background-color: {COLORS['background_primary']} !important;
    }}
    
    .main .block-container {{
        background-color: {COLORS['background_primary']} !important;
        padding: 2rem;
        max-width: 1400px;
    }}
    
    /* Títulos */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {TYPOGRAPHY['font_primary']};
        color: {COLORS['text_primary']} !important;
    }}
    
    h1 {{
        font-size: {TYPOGRAPHY['h1']['size']} !important;
        font-weight: {TYPOGRAPHY['h1']['weight']} !important;
    }}
    
    h2 {{
        font-size: {TYPOGRAPHY['h2']['size']} !important;
        font-weight: {TYPOGRAPHY['h2']['weight']} !important;
    }}
    
    h3 {{
        font-size: {TYPOGRAPHY['h3']['size']} !important;
        font-weight: {TYPOGRAPHY['h3']['weight']} !important;
    }}
    
    /* Texto general */
    p, span, div {{
        font-family: {TYPOGRAPHY['font_secondary']};
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['background_secondary']} !important;
    }}
    
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: {COLORS['background_primary']};
        padding: 15px;
    }}
    
    /* Botones */
    .stButton > button {{
        background: linear-gradient(80deg, rgba(29, 71, 68, 1) 0%, rgba(98, 169, 167, 1) 100%) !important;
        color: {COLORS['background_primary']} !important;
        border: none !important;
        border-radius: {SPACING['button_radius']} !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-family: {TYPOGRAPHY['font_primary']} !important;
        transition: all 0.3s ease !important;
        opacity: 0.8 !important;
    }}
    
    .stButton > button:hover {{
        background: {COLORS['accent_yellow']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(231, 180, 0, 0.3) !important;
    }}
    
    /* Tarjetas métricas */
    .metric-card {{
        background: {COLORS['background_secondary']};
        border-radius: {SPACING['border_radius']};
        padding: {SPACING['card_padding']};
        box-shadow: 0px 0px 14px {COLORS['shadow_card']};
        margin-bottom: 1rem;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div {{
        background-color: {COLORS['background_secondary']} !important;
        color: {COLORS['text_primary']} !important;
        border: 1px solid {COLORS['border_subtle']} !important;
        border-radius: 8px !important;
    }}
    
    /* Separadores */
    hr {{
        border: 1px solid {COLORS['accent_teal']} !important;
        opacity: 0.3;
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: {COLORS['background_secondary']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    /* Dataframes */
    .stDataFrame {{
        background-color: {COLORS['background_secondary']} !important;
    }}
    
    /* Alertas */
    .stAlert {{
        background-color: {COLORS['background_secondary']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    /* Hide fullscreen buttons */
    button[data-testid="StyledFullScreenButton"] {{
        visibility: hidden !important;
    }}
    </style>
    """


def apply_plotly_theme(fig):
    """
    Aplica el tema Crata a una figura de Plotly
    
    Args:
        fig: Figura de Plotly
    
    Returns:
        fig: Figura con el tema aplicado
    """
    fig.update_layout(
        plot_bgcolor=PLOTLY_LAYOUT["plot_bgcolor"],
        paper_bgcolor=PLOTLY_LAYOUT["paper_bgcolor"],
        font=PLOTLY_LAYOUT["font"],
        xaxis=PLOTLY_LAYOUT["xaxis"],
        yaxis=PLOTLY_LAYOUT["yaxis"],
        legend=PLOTLY_LAYOUT["legend"],
    )
    return fig


# =============================================================================
# FUNCIONES DE UTILIDAD PARA UI
# =============================================================================

def get_kpi_card_html(title, value, subtitle=None, icon="📊", trend=None, trend_type="neutral"):
    """
    Genera HTML para una tarjeta KPI con estilo Crata
    
    Args:
        title: Título del KPI
        value: Valor principal
        subtitle: Subtítulo descriptivo (opcional)
        icon: Emoji o icono
        trend: Valor del cambio porcentual (opcional)
        trend_type: "positive", "negative", o "neutral"
    
    Returns:
        str: HTML de la tarjeta
    """
    trend_html = ""
    if trend is not None:
        trend_color = COLORS["success"] if trend_type == "positive" else (
            COLORS["error"] if trend_type == "negative" else COLORS["text_muted"]
        )
        trend_arrow = "↑" if trend_type == "positive" else ("↓" if trend_type == "negative" else "→")
        trend_html = f'<span style="color: {trend_color}; font-size: 14px;">{trend_arrow} {trend}%</span>'
    
    subtitle_html = f'<div style="color: {COLORS["text_muted"]}; font-size: 12px; margin-top: 4px;">{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div style="
        background: {COLORS['background_secondary']};
        border-radius: {SPACING['border_radius']};
        padding: {SPACING['card_padding']};
        box-shadow: 0px 0px 14px {COLORS['shadow_card']};
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        min-height: 120px;
    ">
        <div>
            <div style="color: {COLORS['text_label']}; font-size: 14px; font-weight: 500; margin-bottom: 8px;">
                {title}
            </div>
            <div style="color: {COLORS['text_primary']}; font-size: 32px; font-weight: 700; margin-bottom: 4px;">
                {value}
            </div>
            {trend_html}
            {subtitle_html}
        </div>
        <div style="font-size: 32px; opacity: 0.7;">
            {icon}
        </div>
    </div>
    """


def get_section_header_html(title, subtitle=None, icon=None):
    """
    Genera HTML para un encabezado de sección
    
    Args:
        title: Título de la sección
        subtitle: Subtítulo descriptivo (opcional)
        icon: Emoji o icono (opcional)
    
    Returns:
        str: HTML del encabezado
    """
    icon_html = f'<span style="margin-right: 12px;">{icon}</span>' if icon else ''
    subtitle_html = f'<p style="color: {COLORS["text_secondary"]}; font-size: 16px; margin-top: 8px;">{subtitle}</p>' if subtitle else ''
    
    return f"""
    <div style="margin-bottom: 24px; text-align: center;">
        <h2 style="
            color: {COLORS['text_primary']};
            font-size: {TYPOGRAPHY['h2']['size']};
            font-weight: {TYPOGRAPHY['h2']['weight']};
            font-family: {TYPOGRAPHY['font_primary']};
            margin: 0;
        ">
            {icon_html}{title}
        </h2>
        {subtitle_html}
    </div>
    """

