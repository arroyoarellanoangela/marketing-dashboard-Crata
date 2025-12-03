"""
Visualization Helper Functions
Funciones auxiliares para crear visualizaciones con Plotly
Usando el Design System Crata AI
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd

# Importar tema Crata
from src.config.theme import (
    COLORS, 
    PLOTLY_LAYOUT, 
    PLOTLY_COLOR_SEQUENCE,
    apply_plotly_theme,
    get_kpi_card_html,
)


def create_line_chart(df, x_column, y_column, title, color=None, show_markers=True):
    """
    Crea un gráfico de líneas con tema Crata
    
    Args:
        df: DataFrame con los datos
        x_column: Columna para eje X
        y_column: Columna para eje Y
        title: Título del gráfico
        color: Color de la línea (usa accent_teal por defecto)
        show_markers: Mostrar marcadores en la línea
    
    Returns:
        Figura de Plotly
    """
    try:
        line_color = color or COLORS["chart_primary"]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[x_column],
            y=df[y_column],
            mode='lines+markers' if show_markers else 'lines',
            line=dict(color=line_color, width=3),
            marker=dict(size=8, color=line_color),
            name=y_column,
            hovertemplate=f'<b>{y_column}</b><br>' +
                         f'{x_column}: %{{x}}<br>' +
                         'Value: %{y}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': COLORS['text_primary']}
            },
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title(),
            height=400,
            **PLOTLY_LAYOUT
        )
        
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de líneas: {str(e)}")
        return None


def create_multi_line_chart(df, x_column, y_columns, title, colors=None):
    """
    Crea un gráfico de múltiples líneas con tema Crata
    
    Args:
        df: DataFrame con los datos
        x_column: Columna para eje X
        y_columns: Lista de columnas para eje Y
        title: Título del gráfico
        colors: Lista de colores (usa paleta Crata por defecto)
    
    Returns:
        Figura de Plotly
    """
    try:
        colors = colors or PLOTLY_COLOR_SEQUENCE
        
        fig = go.Figure()
        
        for i, y_col in enumerate(y_columns):
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='lines+markers',
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8, color=colors[i % len(colors)]),
                name=y_col.replace('_', ' ').title(),
            ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': COLORS['text_primary']}
            },
            xaxis_title=x_column.replace('_', ' ').title(),
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            **PLOTLY_LAYOUT
        )
        
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de líneas múltiples: {str(e)}")
        return None


def create_bar_chart(df, x_column, y_column, title, max_items=10, horizontal=False, color=None):
    """
    Crea un gráfico de barras con tema Crata
    
    Args:
        df: DataFrame con los datos
        x_column: Columna para eje X
        y_column: Columna para eje Y
        title: Título del gráfico
        max_items: Número máximo de items a mostrar
        horizontal: Si el gráfico debe ser horizontal
        color: Color de las barras
    
    Returns:
        Figura de Plotly
    """
    try:
        bar_color = color or COLORS["chart_primary"]
        data = df.head(max_items)
        
        if horizontal:
            fig = go.Figure(go.Bar(
                x=data[y_column],
                y=data[x_column],
                orientation='h',
                marker_color=bar_color,
            ))
        else:
            fig = go.Figure(go.Bar(
                x=data[x_column],
                y=data[y_column],
                marker_color=bar_color,
            ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': COLORS['text_primary']}
            },
            xaxis_title=x_column.replace('_', ' ').title() if not horizontal else y_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title() if not horizontal else x_column.replace('_', ' ').title(),
            height=400,
            **PLOTLY_LAYOUT
        )
        
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de barras: {str(e)}")
        return None


def create_pie_chart(df, names_column, values_column, title, hole=0.4):
    """
    Crea un gráfico de pastel/donut con tema Crata
    
    Args:
        df: DataFrame con los datos
        names_column: Columna para nombres/categorías
        values_column: Columna para valores
        title: Título del gráfico
        hole: Tamaño del hueco central (0 para pie, >0 para donut)
    
    Returns:
        Figura de Plotly
    """
    try:
        fig = go.Figure(go.Pie(
            labels=df[names_column],
            values=df[values_column],
            hole=hole,
            marker=dict(colors=PLOTLY_COLOR_SEQUENCE),
            textinfo='percent+label',
            textposition='outside',
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': COLORS['text_primary']}
            },
            height=400,
            showlegend=True,
            legend=dict(
                font=dict(color=COLORS['text_secondary']),
                bgcolor='rgba(0,0,0,0)'
            ),
            plot_bgcolor=COLORS['background_primary'],
            paper_bgcolor=COLORS['background_primary'],
        )
        
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de pastel: {str(e)}")
        return None


def create_funnel_chart(stages, values, title="Funnel de Conversión"):
    """
    Crea un gráfico de embudo con tema Crata
    
    Args:
        stages: Lista de nombres de etapas
        values: Lista de valores por etapa
        title: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    try:
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(
                color=PLOTLY_COLOR_SEQUENCE[:len(stages)],
                line=dict(width=2, color=COLORS['background_primary'])
            ),
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': COLORS['text_primary']}
            },
            height=400,
            plot_bgcolor=COLORS['background_primary'],
            paper_bgcolor=COLORS['background_primary'],
            font=dict(color=COLORS['text_secondary']),
        )
        
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de embudo: {str(e)}")
        return None


def create_scatter_plot(df, x_column, y_column, title, size_column=None, color_column=None):
    """
    Crea un gráfico de dispersión con tema Crata
    Ideal para análisis de tráfico vs intención
    
    Args:
        df: DataFrame con los datos
        x_column: Columna para eje X
        y_column: Columna para eje Y
        title: Título del gráfico
        size_column: Columna para tamaño de puntos (opcional)
        color_column: Columna para color de puntos (opcional)
    
    Returns:
        Figura de Plotly
    """
    try:
        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            size=size_column,
            color=color_column,
            color_continuous_scale=[COLORS['chart_primary'], COLORS['chart_secondary']],
            title=title,
        )
        
        fig.update_layout(
            height=400,
            **PLOTLY_LAYOUT
        )
        
        fig.update_traces(marker=dict(
            line=dict(width=1, color=COLORS['text_muted'])
        ))
        
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de dispersión: {str(e)}")
        return None


def create_metrics_summary(df, metrics):
    """Crea un resumen de métricas con estilo Crata"""
    try:
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                if metric in df.columns:
                    total_value = df[metric].sum()
                    
                    # Formatear valor
                    if total_value >= 1000000:
                        formatted_value = f"{total_value/1000000:.1f}M"
                    elif total_value >= 1000:
                        formatted_value = f"{total_value/1000:.1f}K"
                    else:
                        formatted_value = f"{total_value:,.0f}"
                    
                    st.markdown(
                        get_kpi_card_html(
                            title=metric.replace("_", " ").title(),
                            value=formatted_value,
                            icon="📊"
                        ),
                        unsafe_allow_html=True
                    )
    except Exception as e:
        st.error(f"❌ Error creando resumen de métricas: {str(e)}")


def create_kpi_row(kpis_data):
    """
    Crea una fila de tarjetas KPI
    
    Args:
        kpis_data: Lista de diccionarios con {title, value, subtitle, icon, trend, trend_type}
    """
    cols = st.columns(len(kpis_data))
    
    for i, kpi in enumerate(kpis_data):
        with cols[i]:
            st.markdown(
                get_kpi_card_html(
                    title=kpi.get('title', 'KPI'),
                    value=kpi.get('value', 'N/A'),
                    subtitle=kpi.get('subtitle'),
                    icon=kpi.get('icon', '📊'),
                    trend=kpi.get('trend'),
                    trend_type=kpi.get('trend_type', 'neutral')
                ),
                unsafe_allow_html=True
            )


def display_data_preview(df, dataset_name, max_rows=10):
    """Muestra una vista previa de los datos con estilo Crata"""
    try:
        if not df.empty:
            with st.expander(f"📊 {dataset_name.replace('_', ' ').title()} ({len(df)} registros)"):
                # Aplicar estilo a la tabla
                st.markdown(f"""
                <style>
                .dataframe {{
                    background-color: {COLORS['background_secondary']} !important;
                    color: {COLORS['text_primary']} !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                st.dataframe(df.head(max_rows), use_container_width=True)
                
                # Botón de descarga individual
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Descargar {dataset_name.replace('_', ' ').title()}",
                    data=csv,
                    file_name=f"{dataset_name}.csv",
                    mime="text/csv",
                    key=f"download_{dataset_name}"
                )
    except Exception as e:
        st.error(f"❌ Error mostrando vista previa: {str(e)}")


def create_channel_comparison_chart(df, channel_column, metrics_columns, title):
    """
    Crea un gráfico de comparación de canales
    
    Args:
        df: DataFrame con datos de canales
        channel_column: Columna con nombres de canales
        metrics_columns: Lista de métricas a comparar
        title: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    try:
        fig = go.Figure()
        
        for i, metric in enumerate(metrics_columns):
            if metric in df.columns:
                fig.add_trace(go.Bar(
                    name=metric.replace('_', ' ').title(),
                    x=df[channel_column],
                    y=df[metric],
                    marker_color=PLOTLY_COLOR_SEQUENCE[i % len(PLOTLY_COLOR_SEQUENCE)]
                ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': COLORS['text_primary']}
            },
            barmode='group',
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            **PLOTLY_LAYOUT
        )
        
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de comparación: {str(e)}")
        return None
