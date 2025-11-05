# Configuración de Google Analytics

Este archivo contiene configuraciones adicionales para la aplicación de Google Analytics.

## Configuración de Métricas Disponibles

### Métricas Básicas
- `sessions`: Número de sesiones
- `users`: Número de usuarios únicos
- `newUsers`: Número de usuarios nuevos
- `pageviews`: Número de páginas vistas

### Métricas de Engagement
- `bounceRate`: Tasa de rebote
- `averageSessionDuration`: Duración promedio de sesión
- `pagesPerSession`: Páginas por sesión
- `sessionDuration`: Duración total de sesión

### Métricas de Conversión
- `conversions`: Número de conversiones
- `totalRevenue`: Ingresos totales
- `purchaseRevenue`: Ingresos por compras
- `transactions`: Número de transacciones

## Configuración de Dimensiones Disponibles

### Dimensiones Temporales
- `date`: Fecha
- `year`: Año
- `month`: Mes
- `day`: Día
- `hour`: Hora

### Dimensiones Geográficas
- `country`: País
- `region`: Región
- `city`: Ciudad
- `continent`: Continente

### Dimensiones de Dispositivo
- `deviceCategory`: Categoría de dispositivo
- `operatingSystem`: Sistema operativo
- `browser`: Navegador
- `screenResolution`: Resolución de pantalla

### Dimensiones de Tráfico
- `source`: Fuente de tráfico
- `medium`: Medio de tráfico
- `campaign`: Campaña
- `keyword`: Palabra clave

### Dimensiones de Contenido
- `pagePath`: Ruta de página
- `pageTitle`: Título de página
- `landingPage`: Página de aterrizaje
- `exitPage`: Página de salida

## Configuración de Filtros

Puedes agregar filtros personalizados modificando la función `get_analytics_data` en `app.py`:

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

## Configuración de Ordenamiento

Puedes configurar el ordenamiento de los resultados:

```python
order_by = [
    OrderBy(
        metric=OrderBy.MetricOrderBy(metric_name="sessions"),
        desc=True
    )
]
```
