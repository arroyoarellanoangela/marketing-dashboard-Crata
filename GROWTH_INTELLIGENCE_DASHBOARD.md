# Growth Intelligence Dashboard - Crata AI

## 🎯 Objetivo General

Medir y activar el crecimiento de Crata AI a través de tres pilares fundamentales:

1. **Visibilidad** – Tráfico, alcance, awareness
2. **Rendimiento de contenidos** – SEO, Blog, LinkedIn, Email  
3. **Generación de negocio** – Leads, reuniones, intención de compra

## 📊 Estructura del Dashboard

### Vista Ejecutiva (CEO / Dirección)
Para validar la evolución del negocio y retorno de marketing

**KPIs Clave:**
- Tráfico total (YoY/MoM)
- Leads generados y reuniones agendadas
- Fuentes de oportunidad (SEO, LinkedIn, Email, Eventos)
- ROI de marketing
- Conversión embudo: Visita → Lead → Reunión

### Vista Marketing / Operaciones
Para optimizar semanal/quincenalmente y detectar cuellos de botella

**Canales Digitales:**
- SEO: tráfico orgánico, ranking, artículos top
- LinkedIn: impresiones, engagement, CTR, followers
- Email marketing: aperturas, clics, leads generados
- Eventos: tráfico y leads post-evento

**Embudo de Conversión:**
- Página visitada → Formulario / Calendly / Descarga
- Identificación de fricción: tráfico sin conversión

### Vista de Contenidos (SEO, Blog, Solutions Pages)
Detectar qué contenido aporta crecimiento, no solo tráfico

**Blog (SEO):**
- Nuevos usuarios
- Tiempo en página > 60s
- Scroll > 75%
- Conversiones generadas (clic CTA, formulario)

**Páginas de Servicios / Solutions:**
- Visitas y scroll depth
- Clics en CTA (Lead / Calendly)
- Intención de compra (repetición de visita o interacción)

### Vista Leads & Activación (Embudo de Negocio)
Para conectar marketing con negocio

**Métricas:**
- Leads totales por canal
- Reuniones agendadas
- Ratio de conversión: Lead → Meeting
- Origen de leads de mayor calidad

## 🔧 Configuración Técnica

### GA4 & Tracking

**Eventos de Conversión Configurados:**
- `cta_click` - Clics en botones de llamada a la acción
- `form_submit` - Envío de formularios
- `calendly_click` - Clics en Calendly
- `file_download` - Descargas de archivos
- `scroll` - Profundidad de scroll

**Exclusión de IP Interna:**
- Configuración en GA4 Admin → Data Streams → Define internal traffic
- Rangos IP: `192.168.1.0/24`, `10.0.0.0/8`, `172.16.0.0/12`

### UTM & Identificación de Campañas

**Parámetros UTM Estándar:**

**Email Marketing:**
```
utm_source=email
utm_medium=newsletter
utm_campaign=weekly_digest_2024
utm_content=cta_button
utm_term=ai_marketing
```

**LinkedIn Campaigns:**
```
utm_source=linkedin
utm_medium=social
utm_campaign=ai_consulting_q1_2024
utm_content=sponsored_post
utm_term=marketing_automation
```

**Events & Webinars:**
```
utm_source=event
utm_medium=referral
utm_campaign=marketing_summit_2024
utm_content=speaker_bio
utm_term=growth_marketing
```

### Integraciones

**LinkedIn API:**
- Client ID y Client Secret
- Access Token para métricas de LinkedIn
- Page ID para datos de empresa

**Email Marketing / CRM:**
- Mailchimp API Key
- HubSpot API Key
- Salesforce Client ID/Secret

**Event Tracking:**
- Configuración de eventos personalizados
- Tracking de conversiones post-evento

## 🚀 Instalación y Uso

### Prerrequisitos
- Python 3.8+
- Google Analytics 4 Property ID: `381346600`
- Credenciales de Google Cloud Console (`credentials.json`)

### Instalación
```bash
# Clonar el repositorio
git clone [repository-url]
cd marketing-view-crata

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py
```

### Configuración Inicial

1. **Credenciales GA4:**
   - Descargar `credentials.json` desde Google Cloud Console
   - Colocar en el directorio raíz del proyecto
   - Asegurar permisos de lectura en Google Analytics

2. **Configuración de Tracking:**
   - Ir a "🔧 Tracking Setup" en el dashboard
   - Configurar eventos de conversión
   - Establecer parámetros UTM
   - Configurar exclusión de IP interna

3. **Carga de Datos:**
   - Ir a "🚀 Growth Intelligence"
   - Seleccionar rango de fechas
   - Hacer clic en "🔄 Load Growth Data"

## 📈 Funcionalidades Implementadas

### ✅ Completado

1. **Estructura del Dashboard**
   - Vista Ejecutiva con KPIs principales
   - Vista Marketing Operations
   - Vista Content Performance  
   - Vista Leads & Activation

2. **Integración con GA4**
   - Consultas específicas para métricas de crecimiento
   - Cálculo automático de tendencias YoY/MoM
   - Datos reales cuando están disponibles, simulados como fallback

3. **Configuración de Tracking**
   - Página completa de setup de GA4
   - Configuración de eventos de conversión
   - Parámetros UTM estándar
   - Exclusión de IP interna

4. **Integraciones Externas**
   - LinkedIn API setup
   - Email marketing platforms
   - CRM integrations

5. **Navegación**
   - Sidebar actualizado con nuevas páginas
   - Navegación fluida entre vistas

### 🔄 En Desarrollo

1. **Datos en Tiempo Real**
   - Actualización automática de métricas
   - Alertas de cambios significativos

2. **Reportes Automatizados**
   - Generación de reportes semanales/mensuales
   - Envío por email

3. **Análisis Predictivo**
   - Predicciones de crecimiento
   - Recomendaciones de optimización

## 📊 Métricas y KPIs

### Métricas Principales
- **Tráfico Total**: Sesiones y usuarios únicos
- **Engagement Rate**: Tasa de engagement promedio
- **Conversiones**: Eventos de conversión totales
- **Leads Generados**: Formularios completados
- **Reuniones Agendadas**: Clics en Calendly
- **ROI Marketing**: Retorno de inversión calculado

### Dimensiones Analizadas
- **Fuentes de Tráfico**: Organic, LinkedIn, Email, Direct, Referral
- **Contenido**: Páginas de blog, servicios, landing pages
- **Dispositivos**: Desktop, Mobile, Tablet
- **Geografía**: País, región, ciudad
- **Temporal**: Día, semana, mes, año

## 🛠️ Arquitectura Técnica

### Estructura de Archivos
```
src/
├── pages/
│   ├── growth_intelligence.py    # Dashboard principal
│   └── tracking_setup.py         # Configuración de tracking
├── helpers/
│   └── growth_analytics_helpers.py  # Funciones específicas GA4
├── components/
│   └── sidebar.py                # Navegación actualizada
└── config/
    └── settings.py              # Configuración GA4
```

### Tecnologías Utilizadas
- **Frontend**: Streamlit
- **Analytics**: Google Analytics Data API v1beta
- **Visualización**: Plotly
- **Datos**: Pandas, NumPy
- **Autenticación**: Google Auth

## 📝 Próximos Pasos

1. **Implementar Alertas**
   - Notificaciones de cambios significativos en métricas
   - Alertas de cuellos de botella en el embudo

2. **Análisis Avanzado**
   - Segmentación de usuarios
   - Análisis de cohortes
   - Attribution modeling

3. **Automatización**
   - Reportes automáticos
   - Dashboards personalizados por rol
   - Integración con Slack/Teams

4. **Optimización**
   - A/B testing de páginas
   - Optimización de embudo de conversión
   - Recomendaciones de contenido

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📞 Soporte

Para soporte técnico o preguntas sobre el dashboard:

- **Email**: [soporte@crata.ai]
- **Documentación**: [link-a-docs]
- **Issues**: [GitHub Issues]

---

**Growth Intelligence Dashboard v1.0** - Desarrollado para Crata AI
*Medir y activar el crecimiento a través de datos inteligentes*
