# Google Analytics Dashboard - Estructura del Proyecto

## 📁 Estructura de Carpetas

```
marketing-view-crata/
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── config/                   # Configuraciones
│   │   ├── __init__.py
│   │   └── settings.py          # Configuraciones de la app y GA4
│   ├── helpers/                  # Funciones auxiliares
│   │   ├── __init__.py
│   │   ├── analytics_helpers.py  # Helpers para Google Analytics
│   │   ├── visualization_helpers.py # Helpers para visualizaciones
│   │   └── file_helpers.py       # Helpers para archivos
│   ├── pages/                    # Páginas de la aplicación
│   │   ├── __init__.py
│   │   └── dashboard.py          # Página principal del dashboard
│   ├── utils/                    # Utilidades generales
│   │   ├── __init__.py
│   │   └── general_utils.py      # Funciones de utilidad
│   └── assets/                   # Recursos estáticos
│       └── __init__.py
├── app.py                        # Punto de entrada principal
├── requirements.txt              # Dependencias
├── README.md                     # Documentación
├── credentials.json              # Credenciales de Google Analytics
└── activate_env.bat             # Script de activación (Windows)
```

## 🔧 Archivos Principales

### `app.py`
- Punto de entrada principal de la aplicación
- Importa y ejecuta el dashboard principal

### `src/config/settings.py`
- Configuraciones de la aplicación
- Métricas y dimensiones de GA4
- Configuración de conjuntos de datos

### `src/helpers/analytics_helpers.py`
- Funciones para trabajar con Google Analytics API
- Carga de credenciales
- Obtención de datos específicos y masivos

### `src/helpers/visualization_helpers.py`
- Funciones para crear visualizaciones con Plotly
- Gráficos de líneas, barras y pastel
- Resumen de métricas

### `src/helpers/file_helpers.py`
- Funciones para manejo de archivos
- Creación de archivos ZIP
- Descarga de CSV

### `src/pages/dashboard.py`
- Página principal del dashboard
- Interfaz de usuario completa
- Lógica de la aplicación

### `src/utils/general_utils.py`
- Utilidades generales
- Validación de fechas
- Formateo de números

## 🚀 Cómo usar la nueva estructura

1. **Ejecutar la aplicación**:
   ```bash
   streamlit run app.py
   ```

2. **La aplicación funciona igual** que antes, pero ahora está mejor organizada

3. **Para agregar nuevas funcionalidades**:
   - Agregar helpers en `src/helpers/`
   - Agregar páginas en `src/pages/`
   - Agregar configuraciones en `src/config/`

## ✅ Ventajas de la nueva estructura

- **📁 Organización clara**: Cada tipo de código en su carpeta
- **🔧 Mantenibilidad**: Fácil de mantener y actualizar
- **📈 Escalabilidad**: Fácil agregar nuevas funcionalidades
- **👥 Colaboración**: Estructura estándar para equipos
- **🧪 Testing**: Fácil agregar tests en el futuro
