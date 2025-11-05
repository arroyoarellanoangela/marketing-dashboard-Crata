# 📊 Google Analytics Dashboard con Streamlit

Una aplicación web interactiva para visualizar y analizar datos de Google Analytics usando Streamlit y la API de Google Analytics Data.

## 🚀 Características

- **Conexión segura** a Google Analytics usando credenciales de servicio
- **Interfaz intuitiva** con Streamlit para seleccionar métricas y dimensiones
- **Visualizaciones interactivas** con Plotly
- **Exportación de datos** en formato CSV
- **Dashboard en tiempo real** con métricas resumen
- **Configuración flexible** de rangos de fechas

## 📋 Requisitos Previos

1. **Cuenta de Google Analytics 4 (GA4)**
2. **Proyecto en Google Cloud Console**
3. **Archivo de credenciales JSON** de una cuenta de servicio
4. **Python 3.7+**

## 🛠️ Instalación

### 1. Clonar o descargar el proyecto
```bash
git clone <tu-repositorio>
cd marketing-view-crata
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar credenciales de Google Analytics

#### Paso 1: Crear una cuenta de servicio
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. Ve a "IAM y administración" > "Cuentas de servicio"
4. Haz clic en "Crear cuenta de servicio"
5. Completa los detalles y crea la cuenta

#### Paso 2: Generar clave JSON
1. En la lista de cuentas de servicio, haz clic en la cuenta creada
2. Ve a la pestaña "Claves"
3. Haz clic en "Agregar clave" > "Crear nueva clave"
4. Selecciona "JSON" y descarga el archivo
5. Renombra el archivo a `credentials.json` y colócalo en la raíz del proyecto

#### Paso 3: Habilitar la API de Google Analytics
1. En Google Cloud Console, ve a "APIs y servicios" > "Biblioteca"
2. Busca "Google Analytics Data API"
3. Haz clic en "Habilitar"
4. **IMPORTANTE**: Espera 2-3 minutos para que se propague

**Enlace directo para habilitar la API:**
```
https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=136558401613
```

#### Paso 4: Configurar permisos en Google Analytics
1. Ve a [Google Analytics](https://analytics.google.com/)
2. Selecciona tu propiedad GA4
3. Ve a "Administrar" > "Acceso y datos" > "Cuentas de servicio"
4. Agrega el email de tu cuenta de servicio con permisos de "Lector"

### 4. Obtener Property ID
1. En Google Analytics, ve a "Administrar"
2. En la columna "Propiedad", selecciona tu propiedad GA4
3. Ve a "Configuración de la propiedad"
4. Copia el "ID de propiedad" (número que aparece)

## 🎯 Uso

### Ejecutar la aplicación
```bash
streamlit run app.py
```

### Configurar la aplicación
1. **Credenciales**: La aplicación cargará automáticamente `credentials.json`
2. **Property ID**: Ingresa tu Property ID de GA4 en el sidebar
3. **Fechas**: Selecciona el rango de fechas para los datos
4. **Métricas**: Elige las métricas que quieres analizar
5. **Dimensiones**: Selecciona las dimensiones para segmentar los datos
6. **Obtener datos**: Haz clic en "Obtener Datos" para cargar la información

### Funcionalidades disponibles

#### 📊 Métricas disponibles
- **Sesiones**: Número total de sesiones
- **Usuarios**: Usuarios únicos
- **Usuarios nuevos**: Nuevos usuarios
- **Páginas vistas**: Total de páginas vistas
- **Tasa de rebote**: Porcentaje de rebote
- **Duración promedio de sesión**: Tiempo promedio por sesión
- **Conversiones**: Número de conversiones
- **Ingresos totales**: Revenue total

#### 📈 Dimensiones disponibles
- **Fecha**: Análisis temporal
- **País/Ciudad**: Análisis geográfico
- **Dispositivo**: Análisis por tipo de dispositivo
- **Fuente/Medio**: Análisis de tráfico
- **Página**: Análisis de contenido

#### 📋 Visualizaciones
- **Gráficos de líneas**: Para análisis temporal
- **Gráficos de barras**: Para comparaciones categóricas
- **Métricas resumen**: KPIs principales
- **Tabla de datos**: Vista detallada de todos los datos

#### 💾 Exportación
- **CSV**: Descarga los datos en formato CSV
- **Filtros**: Aplica filtros antes de exportar

## 🔧 Configuración Avanzada

### Personalizar métricas y dimensiones
Edita el archivo `app.py` para agregar más métricas o dimensiones:

```python
available_metrics = [
    "sessions",
    "users",
    # Agregar más métricas aquí
]

available_dimensions = [
    "date",
    "country",
    # Agregar más dimensiones aquí
]
```

### Agregar filtros personalizados
Modifica la función `get_analytics_data` para incluir filtros:

```python
# Ejemplo de filtro por país
filter_expression = FilterExpression(
    filter=Filter(
        field_name="country",
        string_filter=Filter.StringFilter(
            match_type=Filter.StringFilter.MatchType.EXACT,
            value="Spain"
        )
    )
)
```

## 🐛 Solución de Problemas

### Error: "No se encontró el archivo 'credentials.json'"
- Asegúrate de que el archivo `credentials.json` esté en la raíz del proyecto
- Verifica que el archivo tenga el formato JSON correcto

### Error: "No se pudo inicializar el cliente de Google Analytics"
- Verifica que las credenciales sean válidas
- Asegúrate de que la API de Google Analytics Data esté habilitada
- Confirma que la cuenta de servicio tenga permisos de lectura en GA4

### Error: "Google Analytics Data API has not been used in project before or it is disabled"
- **SOLUCIÓN RÁPIDA**: Ve a este enlace y haz clic en "Habilitar":
  ```
  https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=136558401613
  ```
- Espera 2-3 minutos después de habilitar la API
- Verifica que tu cuenta de servicio tenga permisos en Google Analytics

### Error: "User does not have sufficient permissions for this property"
- **SOLUCIÓN**: Agrega tu cuenta de servicio en Google Analytics:
  1. Ve a Google Analytics > Administrar > Acceso y datos > Cuentas de servicio
  2. Agrega: `ga4-streamlit-access@ga4-streamlit-service.iam.gserviceaccount.com`
  3. Asigna rol "Lector"
- Verifica permisos en Google Cloud Console (rol "Lector de datos de Analytics")

### Error: "No se encontraron datos"
- Verifica que el Property ID sea correcto
- Asegúrate de que haya datos en el rango de fechas seleccionado
- Confirma que las métricas y dimensiones seleccionadas sean compatibles

### Error de permisos
- Verifica que la cuenta de servicio tenga acceso a la propiedad de GA4
- Asegúrate de que los permisos sean de nivel "Lector" o superior

## 📚 Recursos Adicionales

- [Documentación de Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Documentación de Streamlit](https://docs.streamlit.io/)
- [Guía de Plotly para Python](https://plotly.com/python/)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Consulta la documentación de Google Analytics
3. Abre un issue en el repositorio

---

**¡Disfruta analizando tus datos de Google Analytics! 📊✨**
