import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

def main():
    """Página para inspeccionar datos de Google Analytics"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Data Inspector - Google Analytics",
        page_icon="src/assets/G I D.jpg",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS para diseño mejorado
    st.markdown("""
    <style>
    .stApp {
        background-color: #000000 !important;
    }
    
    .main {
        background-color: #000000 !important;
    }
    
    .main .block-container {
        background-color: #000000 !important;
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: none;
    }
    
    .stButton > button {
        background: #2E4543 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2E4543 0%, #3A5A58 50%, #4A7C7A 100%) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar estándar completo
    from src.components.sidebar import mostrar_sidebar_completo
    mostrar_sidebar_completo()
    
    # Título principal
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: bold;">
            🔍 Data Inspector
        </h1>
        <p style="color: #CDE3DE; font-size: 1.1rem;">
            Inspeccionar datos de Google Analytics sin filtrar
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar si hay datos cargados
    if 'analytics_data' not in st.session_state or not st.session_state['analytics_data']:
        st.warning("⚠️ No hay datos de Google Analytics cargados. Ve a 'Analytics Overview' y carga los datos primero.")
        return
    
    analytics_data = st.session_state['analytics_data']
    
    # Información general
    st.markdown("### 📊 Información General de los Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📁 Datasets Disponibles",
            value=len(analytics_data.keys()),
            help="Número de datasets cargados"
        )
    
    with col2:
        total_rows = sum(len(df) for df in analytics_data.values() if isinstance(df, pd.DataFrame))
        st.metric(
            label="📈 Total de Filas",
            value=f"{total_rows:,}",
            help="Suma de todas las filas en todos los datasets"
        )
    
    with col3:
        st.metric(
            label="🕒 Última Actualización",
            value="Ahora",
            help="Datos cargados en esta sesión"
        )
    
    st.markdown("---")
    
    # Lista de datasets disponibles
    st.markdown("### 📋 Datasets Disponibles")
    
    dataset_names = list(analytics_data.keys())
    selected_dataset = st.selectbox(
        "Selecciona un dataset para inspeccionar:",
        dataset_names,
        help="Elige qué dataset quieres examinar en detalle"
    )
    
    if selected_dataset:
        dataset = analytics_data[selected_dataset]
        
        st.markdown(f"#### 🔍 Inspeccionando: `{selected_dataset}`")
        
        # Información del dataset seleccionado
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filas", len(dataset))
        
        with col2:
            st.metric("Columnas", len(dataset.columns))
        
        with col3:
            st.metric("Memoria", f"{dataset.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        with col4:
            if 'date' in dataset.columns:
                date_range = f"{dataset['date'].min()} a {dataset['date'].max()}"
                st.metric("Rango de Fechas", date_range)
            else:
                st.metric("Rango de Fechas", "N/A")
        
        st.markdown("---")
        
        # Información de columnas
        st.markdown("#### 📝 Información de Columnas")
        
        col_info = pd.DataFrame({
            'Columna': dataset.columns,
            'Tipo': [str(dtype) for dtype in dataset.dtypes],
            'Valores Únicos': [dataset[col].nunique() for col in dataset.columns],
            'Valores Nulos': [dataset[col].isnull().sum() for col in dataset.columns],
            'Ejemplo': [str(dataset[col].iloc[0]) if len(dataset) > 0 else "N/A" for col in dataset.columns]
        })
        
        st.dataframe(col_info, use_container_width=True)
        
        st.markdown("---")
        
        # Estadísticas descriptivas
        st.markdown("#### 📊 Estadísticas Descriptivas")
        
        # Solo mostrar estadísticas para columnas numéricas
        numeric_cols = dataset.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.dataframe(dataset[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("No hay columnas numéricas en este dataset")
        
        st.markdown("---")
        
        # Primeras filas
        st.markdown("#### 👀 Primeras 10 Filas")
        st.dataframe(dataset.head(10), use_container_width=True)
        
        st.markdown("---")
        
        # Últimas filas
        st.markdown("#### 👀 Últimas 10 Filas")
        st.dataframe(dataset.tail(10), use_container_width=True)
        
        st.markdown("---")
        
        # Valores únicos por columna
        st.markdown("#### 🎯 Valores Únicos por Columna")
        
        for col in dataset.columns:
            unique_values = dataset[col].unique()
            st.markdown(f"**{col}** ({len(unique_values)} valores únicos):")
            
            if len(unique_values) <= 20:
                # Mostrar todos los valores si son pocos
                st.write(f"`{list(unique_values)}`")
            else:
                # Mostrar solo los primeros 10 si son muchos
                st.write(f"`{list(unique_values[:10])}` ... (+{len(unique_values)-10} más)")
            
            st.markdown("")
    
    st.markdown("---")
    
    # Resumen de todos los datasets
    st.markdown("### 📋 Resumen de Todos los Datasets")
    
    summary_data = []
    for name, df in analytics_data.items():
        summary_data.append({
            'Dataset': name,
            'Filas': len(df),
            'Columnas': len(df.columns),
            'Columnas': ', '.join(df.columns.tolist()),
            'Tiene Fecha': 'date' in df.columns,
            'Memoria (KB)': f"{df.memory_usage(deep=True).sum() / 1024:.1f}"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    st.markdown("---")
    
    # Botón para exportar datos
    st.markdown("### 💾 Exportar Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Exportar Resumen como CSV"):
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Descargar Resumen",
                data=csv,
                file_name=f"analytics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🔍 Exportar Dataset Seleccionado"):
            if selected_dataset:
                csv = analytics_data[selected_dataset].to_csv(index=False)
                st.download_button(
                    label=f"Descargar {selected_dataset}",
                    data=csv,
                    file_name=f"{selected_dataset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Data Inspector - Google Analytics</p>
        <p><small>Herramienta para inspeccionar y entender la estructura de los datos</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
