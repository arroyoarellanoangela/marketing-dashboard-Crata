"""
Visualization Helper Functions
Funciones auxiliares para crear visualizaciones con Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def create_line_chart(df, x_column, y_column, title):
    """Crea un gráfico de líneas"""
    try:
        fig = px.line(
            df, 
            x=x_column, 
            y=y_column,
            title=title
        )
        fig.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column,
            height=400
        )
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de líneas: {str(e)}")
        return None


def create_bar_chart(df, x_column, y_column, title, max_items=10):
    """Crea un gráfico de barras"""
    try:
        fig = px.bar(
            df.head(max_items), 
            x=x_column, 
            y=y_column,
            title=title
        )
        fig.update_layout(
            xaxis_title=x_column,
            yaxis_title=y_column,
            height=400
        )
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de barras: {str(e)}")
        return None


def create_pie_chart(df, names_column, values_column, title):
    """Crea un gráfico de pastel"""
    try:
        fig = px.pie(
            df, 
            names=names_column, 
            values=values_column,
            title=title
        )
        fig.update_layout(height=400)
        return fig
    except Exception as e:
        st.error(f"❌ Error creando gráfico de pastel: {str(e)}")
        return None


def create_metrics_summary(df, metrics):
    """Crea un resumen de métricas"""
    try:
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                if metric in df.columns:
                    total_value = df[metric].sum()
                    st.metric(
                        label=metric.replace("_", " ").title(),
                        value=f"{total_value:,.0f}"
                    )
    except Exception as e:
        st.error(f"❌ Error creando resumen de métricas: {str(e)}")


def display_data_preview(df, dataset_name, max_rows=10):
    """Muestra una vista previa de los datos"""
    try:
        if not df.empty:
            with st.expander(f"📊 {dataset_name.replace('_', ' ').title()} ({len(df)} registros)"):
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
