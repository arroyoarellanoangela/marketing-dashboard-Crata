import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.config.settings import APP_CONFIG, GA4_CONFIG, GA4_METRICS, GA4_DIMENSIONS, DATA_SETS_CONFIG
from src.helpers.analytics_helpers import load_credentials, initialize_analytics_client, get_content_performance_data
from src.components.sidebar import mostrar_sidebar_variables, mostrar_filtros_fecha

def main():
    """Página principal para análisis de rendimiento de blogs"""
    
    # Configurar la página
    st.set_page_config(
        page_title="Blog Performance - Marketing Dashboard",
        page_icon="src/assets/G I D.jpg",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS para diseño mejorado con fondo negro completo
    st.markdown("""
    <style>
    /* Fondo negro para toda la página */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Fondo negro para el contenido principal */
    .main {
        background-color: #000000 !important;
    }
    
    /* Contenedor principal también negro */
    .main .block-container {
        background-color: #000000 !important;
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: none;
    }
    
    .stImage {
        background: transparent;
    }
    
    .stButton > button {
        background: #2E4543 !important;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2E4543 0%, #3A5A58 50%, #4A7C7A 100%) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar sidebar avanzado
    mostrar_sidebar_variables()
    mostrar_filtros_fecha()
    
    # Título de la página
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>📝 BLOG PERFORMANCE</h1>
        <p style='color: #9CA3AF; font-size: 1rem;'>Análisis detallado del rendimiento de blogs y contenido editorial</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar si hay datos disponibles
    if "fecha_inicio" in st.session_state and "fecha_fin" in st.session_state:
        fecha_inicio = st.session_state["fecha_inicio"]
        fecha_fin = st.session_state["fecha_fin"]
        
        # Convertir fechas a string para la API
        start_date = fecha_inicio.strftime("%Y-%m-%d")
        end_date = fecha_fin.strftime("%Y-%m-%d")
        
        try:
            # Cargar credenciales y cliente
            credentials = load_credentials()
            client = initialize_analytics_client(credentials)
            
            # Obtener datos de rendimiento de contenido
            content_data = get_content_performance_data(
                client=client,
                property_id="381346600",
                start_date=start_date,
                end_date=end_date
            )
            
            if content_data.empty:
                st.warning("⚠️ No se encontraron datos de contenido para el rango de fechas seleccionado")
                return
            
            # Filtrar solo blogs (páginas que contengan "blog" en el path o título)
            blog_data = content_data[
                content_data['pagePath'].str.contains('blog|article|post', case=False, na=False) |
                content_data['pageTitle'].str.contains('blog|article|post', case=False, na=False)
            ].copy()
            
            if blog_data.empty:
                st.warning("⚠️ No se encontraron datos de blogs en el rango de fechas seleccionado")
                return
            
            # Calcular KPIs principales de blogs
            total_blog_views = blog_data['screenPageViews'].sum() if 'screenPageViews' in blog_data.columns else 0
            total_blog_users = blog_data['totalUsers'].sum() if 'totalUsers' in blog_data.columns else 0
            avg_blog_time = blog_data['averageSessionDuration'].mean() if 'averageSessionDuration' in blog_data.columns else 0
            avg_blog_bounce = blog_data['bounceRate'].mean() if 'bounceRate' in blog_data.columns else 0
            unique_blogs = blog_data['pageTitle'].nunique() if 'pageTitle' in blog_data.columns else 0
            
            # KPIs principales de blogs
            st.markdown("### 📊 Blog Performance KPIs")
            
            # Crear columnas para KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Blog Views",
                    value=f"{total_blog_views:,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Blog Readers",
                    value=f"{total_blog_users:,}",
                    delta=None
                )
            
            with col3:
                # Formatear tiempo en minutos y segundos
                minutes = int(avg_blog_time // 60)
                seconds = int(avg_blog_time % 60)
                time_str = f"{minutes}m {seconds}s"
                st.metric(
                    label="Avg Reading Time",
                    value=time_str,
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Unique Blog Posts",
                    value=f"{unique_blogs:,}",
                    delta=None
                )
            
            st.markdown("---")
            
            # Top Blogs por rendimiento
            st.markdown("### 🏆 Top Performing Blog Posts")
            
            # Agrupar por blog y calcular métricas
            blog_metrics = blog_data.groupby('pageTitle').agg({
                'screenPageViews': 'sum',
                'totalUsers': 'sum',
                'newUsers': 'sum',
                'bounceRate': 'mean',
                'averageSessionDuration': 'mean'
            }).reset_index()
            
            # Calcular métricas adicionales
            blog_metrics['views_per_user'] = blog_metrics['screenPageViews'] / blog_metrics['totalUsers']
            blog_metrics['engagement_score'] = (blog_metrics['averageSessionDuration'] / 60) * (1 - blog_metrics['bounceRate'] / 100)
            
            # Ordenar por diferentes métricas
            top_by_views = blog_metrics.sort_values('screenPageViews', ascending=False)
            top_by_engagement = blog_metrics.sort_values('engagement_score', ascending=False)
            
            # Mostrar top blogs por views
            st.markdown("#### 📈 Top Blogs by Views")
            st.dataframe(
                top_by_views.head(10)[['pageTitle', 'screenPageViews', 'totalUsers', 'averageSessionDuration', 'bounceRate']],
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de barras para top blogs por views
            fig_views = px.bar(
                top_by_views.head(8),
                x='screenPageViews',
                y='pageTitle',
                orientation='h',
                title="Top 8 Blog Posts by Views",
                color='screenPageViews',
                color_continuous_scale='Blues'
            )
            
            fig_views.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='white',
                height=400
            )
            
            st.plotly_chart(fig_views, use_container_width=True)
            
            # Top blogs por engagement
            st.markdown("#### ⏱️ Top Blogs by Engagement")
            st.dataframe(
                top_by_engagement.head(10)[['pageTitle', 'engagement_score', 'averageSessionDuration', 'bounceRate', 'views_per_user']],
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de engagement
            fig_engagement = px.bar(
                top_by_engagement.head(8),
                x='engagement_score',
                y='pageTitle',
                orientation='h',
                title="Top 8 Blog Posts by Engagement Score",
                color='engagement_score',
                color_continuous_scale='Greens'
            )
            
            fig_engagement.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='white',
                height=400
            )
            
            st.plotly_chart(fig_engagement, use_container_width=True)
            
            # Análisis de categorías de blogs
            st.markdown("### 📂 Blog Categories Analysis")
            
            # Extraer categorías de los títulos de blogs
            blog_data['category'] = blog_data['pageTitle'].str.extract(r'(AI|Machine Learning|Business|Technology|Marketing|Data|Analytics|Tutorial|Guide|News)', case=False)
            blog_data['category'] = blog_data['category'].fillna('Other')
            
            category_analysis = blog_data.groupby('category').agg({
                'screenPageViews': 'sum',
                'totalUsers': 'sum',
                'averageSessionDuration': 'mean',
                'bounceRate': 'mean',
                'pageTitle': 'count'
            }).reset_index()
            
            category_analysis = category_analysis.rename(columns={'pageTitle': 'post_count'})
            category_analysis = category_analysis.sort_values('screenPageViews', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de dona para categorías
                fig_categories = px.pie(
                    category_analysis,
                    values='screenPageViews',
                    names='category',
                    title="Blog Views by Category",
                    hole=0.4
                )
                
                fig_categories.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white'
                )
                
                st.plotly_chart(fig_categories, use_container_width=True)
            
            with col2:
                st.dataframe(
                    category_analysis,
                    use_container_width=True,
                    hide_index=True
                )
            
            # Análisis temporal de blogs
            st.markdown("### 📅 Blog Performance Over Time")
            
            if 'date' in blog_data.columns:
                # Agregar datos por fecha
                daily_blog_data = blog_data.groupby('date').agg({
                    'screenPageViews': 'sum',
                    'totalUsers': 'sum',
                    'averageSessionDuration': 'mean',
                    'bounceRate': 'mean'
                }).reset_index()
                
                daily_blog_data['date'] = pd.to_datetime(daily_blog_data['date'])
                
                # Gráfico de líneas para tendencias
                fig_trends = px.line(
                    daily_blog_data,
                    x='date',
                    y=['screenPageViews', 'totalUsers'],
                    title="Daily Blog Performance Trends",
                    color_discrete_sequence=['#10B981', '#3B82F6']
                )
                
                fig_trends.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white'
                )
                
                st.plotly_chart(fig_trends, use_container_width=True)
            
            # Insights y recomendaciones
            st.markdown("### 💡 Blog Insights & Recommendations")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **📈 Top Performing Content**
                - Focus on high-view topics
                - Replicate successful formats
                - Optimize low-performing posts
                """)
            
            with col2:
                st.markdown("""
                **⏱️ Engagement Optimization**
                - Improve content depth
                - Add interactive elements
                - Optimize reading experience
                """)
            
            with col3:
                st.markdown("""
                **📂 Content Strategy**
                - Balance category distribution
                - Focus on trending topics
                - Regular publishing schedule
                """)
            
            # Métricas adicionales de blogs
            st.markdown("### 📊 Additional Blog Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_views_per_post = total_blog_views / unique_blogs if unique_blogs > 0 else 0
                st.metric(
                    label="Avg Views per Post",
                    value=f"{avg_views_per_post:.0f}",
                    delta=None
                )
            
            with col2:
                avg_users_per_post = total_blog_users / unique_blogs if unique_blogs > 0 else 0
                st.metric(
                    label="Avg Users per Post",
                    value=f"{avg_users_per_post:.0f}",
                    delta=None
                )
            
            with col3:
                avg_views_per_user = total_blog_views / total_blog_users if total_blog_users > 0 else 0
                st.metric(
                    label="Views per Reader",
                    value=f"{avg_views_per_user:.1f}",
                    delta=None
                )
            
            with col4:
                engagement_rate = (1 - avg_blog_bounce / 100) * 100 if avg_blog_bounce > 0 else 0
                st.metric(
                    label="Blog Engagement Rate",
                    value=f"{engagement_rate:.1f}%",
                    delta=None
                )
            
        except Exception as e:
            st.error(f"❌ Error obteniendo datos de blogs: {str(e)}")
    
    else:
        st.warning("⚠️ No hay filtros de fecha configurados. Configura las fechas en el sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Marketing Dashboard - Blog Performance Analysis</p>
        <p><small>Property ID: 381346600 (Crata GA4) | Configurado automáticamente</small></p>
    </div>
    """, unsafe_allow_html=True)
