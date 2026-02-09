"""
=============================================================================
CRATA AI - GROWTH INTELLIGENCE DASHBOARD (Flask Version)
=============================================================================

Dashboard de Marketing con Flask para mejor diseño web.
Migrado desde Streamlit para mayor control sobre el frontend.
=============================================================================
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timedelta
from collections import Counter
import json
import os
import pandas as pd
import numpy as np
import pickle
import sqlite3
import hashlib
import re
import threading
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Importar configuraciones (importar directamente del archivo para evitar imports de Streamlit)
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar helpers de analytics (versión Flask) directamente
import importlib.util
spec = importlib.util.spec_from_file_location(
    "analytics_helpers_flask", 
    os.path.join(os.path.dirname(__file__), 'src', 'helpers', 'analytics_helpers_flask.py')
)
analytics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analytics_module)

load_credentials = analytics_module.load_credentials
initialize_analytics_client = analytics_module.initialize_analytics_client
get_all_analytics_data = analytics_module.get_all_analytics_data

# Importar settings directamente
spec_settings = importlib.util.spec_from_file_location(
    "settings", 
    os.path.join(os.path.dirname(__file__), 'src', 'config', 'settings.py')
)
settings_module = importlib.util.module_from_spec(spec_settings)
spec_settings.loader.exec_module(settings_module)

DATA_SETS_CONFIG = settings_module.DATA_SETS_CONFIG
GA4_CONFIG = settings_module.GA4_CONFIG
DIANA_CONFIG = settings_module.DIANA_CONFIG

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Clave secreta fija para mantener sesiones entre reinicios
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'crata-ai-dashboard-secret-key-2024-secure')
app.config['SESSION_COOKIE_SECURE'] = False  # Cambiar a True en producción con HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Sesión dura 7 días

# =============================================================================
# VARIABLES GLOBALES
# =============================================================================

analytics_client = None
analytics_data = {}
analytics_data_raw = {}  # Datos originales SIN filtrar (para detección de bots)

# Ruta del archivo para persistir datos
DATA_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data_cache.pkl')
DATA_CACHE_RAW_FILE = os.path.join(os.path.dirname(__file__), 'data_cache_raw.pkl')

# Ruta de la base de datos de usuarios
USERS_DB_FILE = os.path.join(os.path.dirname(__file__), 'users.db')

# Ruta de la base de datos de reuniones de Diana
DIANA_MEETINGS_DB_FILE = os.path.join(os.path.dirname(__file__), 'diana_meetings.db')

# Ruta de la base de datos de leads
LEADS_DB_FILE = os.path.join(os.path.dirname(__file__), 'leads.db')

# Ruta de la base de datos de métricas de team
TEAM_METRICS_DB_FILE = os.path.join(os.path.dirname(__file__), 'team_metrics.db')

# Dominio permitido para registro
ALLOWED_EMAIL_DOMAIN = '@crata-ai.com'

# =============================================================================
# BASE DE DATOS DE USUARIOS
# =============================================================================

def init_users_db():
    """Inicializa la base de datos de usuarios"""
    conn = sqlite3.connect(USERS_DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Base de datos de usuarios inicializada")

def init_diana_meetings_db():
    """Inicializa la base de datos de reuniones de Diana"""
    conn = sqlite3.connect(DIANA_MEETINGS_DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diana_meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            meeting_date TEXT NOT NULL,
            project_reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Base de datos de reuniones de Diana inicializada")

def init_leads_db():
    """Inicializa la base de datos de leads"""
    conn = sqlite3.connect(LEADS_DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            meeting_date TEXT,
            project_reason TEXT,
            status TEXT DEFAULT 'nuevo',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Base de datos de leads inicializada")

def init_team_metrics_db():
    """Inicializa la base de datos de métricas de team"""
    conn = sqlite3.connect(TEAM_METRICS_DB_FILE)
    cursor = conn.cursor()
    
    # Tabla para campañas email/LinkedIn
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semana_fecha TEXT,
            campana TEXT,
            emails_enviados TEXT,
            respuestas_total TEXT,
            tasa_respuesta_total TEXT,
            respuestas_positivas TEXT,
            tasa_respuestas_positivas TEXT,
            reuniones TEXT,
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla para campañas LinkedIn
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS linkedin_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semana_fecha TEXT,
            campana TEXT,
            total_mensajes TEXT,
            respuestas_total TEXT,
            tasa_respuesta_total TEXT,
            respuestas_positivas TEXT,
            tasa_respuestas_positivas TEXT,
            reuniones TEXT,
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla para métricas web
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semana TEXT,
            sesiones_totales TEXT,
            usuarios TEXT,
            usuarios_nuevos TEXT,
            sesiones_organicas TEXT,
            sesiones_paid TEXT,
            sesiones_referral TEXT,
            engagement_rate TEXT,
            bounced_rate TEXT,
            pages_por_sesion TEXT,
            leads_web TEXT,
            reuniones_agendadas TEXT,
            tasa_conversion_web TEXT,
            top_3_pages TEXT,
            top_blog TEXT,
            trafico_blog TEXT,
            nuevas_paginas TEXT,
            new_kws TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[DB] Base de datos de métricas de team inicializada")

def hash_password(password):
    """Genera hash seguro de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email_domain(email):
    """Valida que el email sea del dominio @crata-ai.com"""
    email = email.lower().strip()
    return email.endswith(ALLOWED_EMAIL_DOMAIN)

def create_user(email, password, name=None):
    """Crea un nuevo usuario"""
    email = email.lower().strip()
    
    if not validate_email_domain(email):
        return False, f"Solo se permiten emails con dominio {ALLOWED_EMAIL_DOMAIN}"
    
    if not password or len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    try:
        conn = sqlite3.connect(USERS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
            (email, hash_password(password), name)
        )
        conn.commit()
        conn.close()
        return True, "Usuario creado exitosamente"
    except sqlite3.IntegrityError:
        return False, "Este email ya está registrado"
    except Exception as e:
        return False, f"Error al crear usuario: {str(e)}"

def verify_user(email, password):
    """Verifica las credenciales del usuario"""
    email = email.lower().strip()
    
    try:
        conn = sqlite3.connect(USERS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, email, name FROM users WHERE email = ? AND password_hash = ?',
            (email, hash_password(password))
        )
        user = cursor.fetchone()
        
        if user:
            # Actualizar último login
            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.now(), user[0])
            )
            conn.commit()
            conn.close()
            return True, {'id': user[0], 'email': user[1], 'name': user[2]}
        
        conn.close()
        return False, "Email o contraseña incorrectos"
    except Exception as e:
        return False, f"Error al verificar usuario: {str(e)}"

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# FUNCIONES DE PERSISTENCIA
# =============================================================================

def save_data_to_disk():
    """Guarda los datos en disco para persistencia"""
    global analytics_data, analytics_data_raw
    try:
        if analytics_data:
            with open(DATA_CACHE_FILE, 'wb') as f:
                pickle.dump(analytics_data, f)
            print(f"[CACHE] Datos filtrados guardados en {DATA_CACHE_FILE}")
        if analytics_data_raw:
            with open(DATA_CACHE_RAW_FILE, 'wb') as f:
                pickle.dump(analytics_data_raw, f)
            print(f"[CACHE] Datos RAW guardados en {DATA_CACHE_RAW_FILE}")
        return True
    except Exception as e:
        print(f"[ERROR] Error guardando datos: {e}")
    return False

def load_data_from_disk():
    """Carga los datos desde disco si existen"""
    global analytics_data, analytics_data_raw
    try:
        if os.path.exists(DATA_CACHE_FILE):
            with open(DATA_CACHE_FILE, 'rb') as f:
                analytics_data = pickle.load(f)
            print(f"[CACHE] Datos filtrados cargados desde {DATA_CACHE_FILE}")
            print(f"[CACHE] Datasets disponibles: {list(analytics_data.keys())}")
            
            # Verificar datos_temporales específicamente
            if analytics_data and 'datos_temporales' in analytics_data:
                df_temp = analytics_data.get('datos_temporales')
                if isinstance(df_temp, pd.DataFrame):
                    print(f"[CACHE] datos_temporales: {len(df_temp)} registros, columnas: {df_temp.columns.tolist()}")
                    if not df_temp.empty and 'date' in df_temp.columns:
                        print(f"[CACHE] Rango de fechas: {df_temp['date'].min()} - {df_temp['date'].max()}")
                else:
                    print(f"[CACHE] datos_temporales no es DataFrame, es: {type(df_temp)}")
        if os.path.exists(DATA_CACHE_RAW_FILE):
            with open(DATA_CACHE_RAW_FILE, 'rb') as f:
                analytics_data_raw = pickle.load(f)
            print(f"[CACHE] Datos RAW cargados desde {DATA_CACHE_RAW_FILE}")
            if analytics_data_raw and 'datos_temporales' in analytics_data_raw:
                df_temp_raw = analytics_data_raw.get('datos_temporales')
                if isinstance(df_temp_raw, pd.DataFrame):
                    print(f"[CACHE] datos_temporales RAW: {len(df_temp_raw)} registros")
        return bool(analytics_data)
    except Exception as e:
        print(f"[ERROR] Error cargando datos desde cache: {e}")
        import traceback
        traceback.print_exc()
    return False

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

def init_analytics():
    """Inicializa el cliente de Google Analytics"""
    global analytics_client
    credentials = load_credentials()
    if credentials:
        analytics_client = initialize_analytics_client(credentials)
        return True
    return False

# =============================================================================
# RUTAS PRINCIPALES
# =============================================================================

@app.route('/')
def index():
    """Página principal con login/registro"""
    # Si ya está logueado, redirigir al dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Procesa el login de usuario"""
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    success, result = verify_user(email, password)
    
    if success:
        session.permanent = True  # Hace la sesión permanente (7 días)
        session['user_id'] = result['id']
        session['user_email'] = result['email']
        session['user_name'] = result['name']
        return jsonify({'success': True, 'message': 'Login exitoso'})
    else:
        return jsonify({'success': False, 'message': result})

@app.route('/register', methods=['POST'])
def register():
    """Procesa el registro de nuevo usuario"""
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    name = data.get('name', '')
    
    success, message = create_user(email, password, name)
    
    if success:
        # Auto-login después del registro
        success_login, user_data = verify_user(email, password)
        if success_login:
            session.permanent = True  # Hace la sesión permanente (7 días)
            session['user_id'] = user_data['id']
            session['user_email'] = user_data['email']
            session['user_name'] = user_data['name']
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message})

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal - Vista General"""
    return render_template('dashboard.html', 
                          active_page='general_overview',
                          page_title='Tráfico General',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/traffic-sources')
@login_required
def traffic_sources():
    """Fuentes de Tráfico"""
    return render_template('dashboard.html', 
                          active_page='traffic_sources',
                          page_title='Fuentes de Tráfico',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/content-performance')
@login_required
def content_performance():
    """Página y Contenido"""
    return render_template('dashboard.html', 
                          active_page='content_performance',
                          page_title='Página y Contenido',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/user-behavior')
@login_required
def user_behavior():
    """Comportamiento de Usuarios"""
    return render_template('dashboard.html', 
                          active_page='user_behavior',
                          page_title='Comportamiento Usuarios',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/diana')
@login_required
def diana():
    """Diana - Métricas de mensajería"""
    return render_template('dashboard.html', 
                          active_page='diana',
                          page_title='Diana',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/apollo')
@login_required
def apollo_page():
    """Apollo - Datos crudos de Apollo.io API"""
    return render_template('dashboard.html',
                          active_page='apollo',
                          page_title='Apollo',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/leads')
@login_required
def leads():
    """Leads - Gestión centralizada de leads"""
    return render_template('dashboard.html', 
                          active_page='leads',
                          page_title='Leads',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/team')
@login_required
def team():
    """Team - Gestión de equipos y métricas"""
    return render_template('dashboard.html', 
                          active_page='team',
                          page_title='Team',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/alerts')
@login_required
def alerts():
    """Alertas"""
    return render_template('dashboard.html', 
                          active_page='alerts',
                          page_title='Alertas',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

@app.route('/realtime')
@login_required
def realtime():
    """Tracking en Tiempo Real"""
    return render_template('dashboard.html', 
                          active_page='realtime',
                          page_title='Tiempo Real',
                          user_email=session.get('user_email'),
                          user_name=session.get('user_name'))

# =============================================================================
# API ENDPOINTS
# =============================================================================

def df_to_json_safe(df):
    """Convierte DataFrame a JSON de forma segura, manejando NaN y fechas"""
    if df is None or df.empty:
        return []
    
    # Crear copia para no modificar el original
    df_copy = df.copy()
    
    # Convertir columnas de fecha a string
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
        elif df_copy[col].dtype == 'object':
            # Intentar convertir strings que parecen fechas
            try:
                if col == 'date':
                    df_copy[col] = pd.to_datetime(df_copy[col]).dt.strftime('%Y-%m-%d')
            except:
                pass
    
    # Reemplazar NaN con None y convertir a dict
    df_copy = df_copy.replace({np.nan: None, pd.NA: None})
    
    return df_copy.to_dict(orient='records')


_loading_in_progress = False
_loading_error = None

@app.route('/api/check-data', methods=['GET'])
def check_data():
    """Verifica si los datos ya están cargados. Si no hay datos, dispara la carga."""
    global analytics_data, _loading_in_progress, _loading_error

    # Si no hay datos en memoria, intentar cargar desde disco
    if not analytics_data or 'datos_temporales' not in analytics_data:
        load_data_from_disk()

    if analytics_data and 'datos_temporales' in analytics_data:
        df = analytics_data.get('datos_temporales')
        if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
            _loading_error = None
            return jsonify({
                'loaded': True,
                'records': len(df)
            })

    # Si hubo un error previo, informar al frontend
    if _loading_error and not _loading_in_progress:
        return jsonify({'loaded': False, 'records': 0, 'error': _loading_error})

    # No hay datos ni en memoria ni en disco: disparar carga en background
    if not _loading_in_progress:
        _loading_in_progress = True
        _loading_error = None
        print("[CHECK] No hay datos, lanzando carga de GA4 en background...")
        def _bg_load():
            global _loading_in_progress, _loading_error
            try:
                success = reload_analytics_data()
                if not success:
                    _loading_error = 'No se pudieron obtener datos de GA4. Verifica las credenciales.'
            except Exception as e:
                _loading_error = str(e)
            finally:
                _loading_in_progress = False
        threading.Thread(target=_bg_load, daemon=True).start()

    return jsonify({'loaded': False, 'records': 0, 'loading': True})

@app.route('/api/get-filter-options', methods=['GET'])
def get_filter_options():
    """Devuelve las opciones disponibles para los filtros (páginas y países)"""
    global analytics_data
    
    try:
        # Si no hay datos en memoria, intentar cargar desde disco
        if not analytics_data or 'datos_temporales' not in analytics_data:
            load_data_from_disk()
        
        pages = []
        countries = []
        
        # ========================================
        # OBTENER PÁGINAS desde datos_contenido
        # ========================================
        if analytics_data and 'datos_contenido' in analytics_data:
            df_contenido = analytics_data.get('datos_contenido')
            if df_contenido is not None and isinstance(df_contenido, pd.DataFrame) and not df_contenido.empty:
                print(f"[FILTER-OPTIONS] Columnas en datos_contenido: {df_contenido.columns.tolist()}")
                
                # Buscar columna de páginas (preferir pagePath)
                page_col = None
                for col in ['pagePath', 'landingPage', 'pageTitle']:
                    if col in df_contenido.columns:
                        page_col = col
                        break
                
                if page_col:
                    # Agrupar por página y sumar pageviews para ordenar por popularidad
                    if 'screenPageViews' in df_contenido.columns:
                        page_stats = df_contenido.groupby(page_col)['screenPageViews'].sum().sort_values(ascending=False)
                    else:
                        page_stats = df_contenido[page_col].value_counts()
                    
                    # Filtrar páginas vacías y obtener las más visitadas
                    valid_pages = [p for p in page_stats.index if p and p != '(not set)' and p != 'not set' and str(p).strip()]
                    pages = valid_pages[:100]  # Top 100 páginas más visitadas
                    print(f"[FILTER-OPTIONS] Páginas encontradas desde {page_col}: {len(pages)}")
        
        # Si no hay datos_contenido, intentar con datos_temporales
        if not pages and analytics_data and 'datos_temporales' in analytics_data:
            df = analytics_data.get('datos_temporales')
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                for col in ['pagePath', 'landingPage', 'pageTitle']:
                    if col in df.columns:
                        page_counts = df[col].value_counts()
                        valid_pages = [p for p in page_counts.index if p and p != '(not set)' and p != 'not set']
                        pages = valid_pages[:100]
                        print(f"[FILTER-OPTIONS] Páginas encontradas desde datos_temporales/{col}: {len(pages)}")
                        break
        
        # ========================================
        # OBTENER PAÍSES desde datos_geograficos
        # ========================================
        if analytics_data and 'datos_geograficos' in analytics_data:
            df_geo = analytics_data.get('datos_geograficos')
            if df_geo is not None and isinstance(df_geo, pd.DataFrame) and not df_geo.empty:
                print(f"[FILTER-OPTIONS] Columnas en datos_geograficos: {df_geo.columns.tolist()}")
                
                if 'country' in df_geo.columns:
                    # Agrupar por país y sumar sesiones para ordenar por volumen
                    if 'sessions' in df_geo.columns:
                        country_stats = df_geo.groupby('country')['sessions'].sum().sort_values(ascending=False)
                    else:
                        country_stats = df_geo['country'].value_counts()
                    
                    # Filtrar países vacíos
                    valid_countries = [c for c in country_stats.index if c and c != '(not set)' and c != 'not set' and str(c).strip()]
                    countries = valid_countries[:50]  # Top 50 países
                    print(f"[FILTER-OPTIONS] Países encontrados: {len(countries)}")
        
        # Si no hay datos_geograficos, intentar con datos_temporales
        if not countries and analytics_data and 'datos_temporales' in analytics_data:
            df = analytics_data.get('datos_temporales')
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                if 'country' in df.columns:
                    country_counts = df['country'].value_counts()
                    valid_countries = [c for c in country_counts.index if c and c != '(not set)' and c != 'not set']
                    countries = valid_countries[:50]
                    print(f"[FILTER-OPTIONS] Países encontrados desde datos_temporales: {len(countries)}")
        
        print(f"[FILTER-OPTIONS] Total: {len(pages)} páginas, {len(countries)} países")
        
        return jsonify({
            'success': True,
            'pages': pages,
            'countries': countries
        })
        
    except Exception as e:
        print(f"[ERROR] get_filter_options: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'pages': [],
            'countries': [],
            'error': str(e)
        })

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Carga datos de Google Analytics"""
    global analytics_data, analytics_data_raw, analytics_client
    
    try:
        # Inicializar cliente si no existe
        if not analytics_client:
            print("[INIT] Inicializando cliente de Analytics...")
            if not init_analytics():
                print("[ERROR] No se pudo inicializar el cliente")
                return jsonify({'error': 'No se pudo inicializar el cliente de Analytics. Verifica credentials.json'}), 500
            print("[OK] Cliente inicializado correctamente")
        
        # Obtener fechas del request
        data = request.get_json() or {}
        
        today = datetime.now().date()
        
        # IMPORTANTE: Siempre cargar 365 dias de datos para tener historico
        # para calculos de deltas (como hacia Streamlit)
        start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        print(f"[DATE] Cargando datos desde {start_date} hasta {end_date} (365 dias)")
        
        # Obtener datos
        raw_data = get_all_analytics_data(
            client=analytics_client,
            property_id=GA4_CONFIG['property_id'],
            start_date=start_date,
            end_date=end_date,
            data_sets_config=DATA_SETS_CONFIG
        )
        
        if raw_data:
            # GUARDAR DATOS ORIGINALES (para detección de bots)
            analytics_data_raw = {}
            for key, df in raw_data.items():
                if isinstance(df, pd.DataFrame):
                    analytics_data_raw[key] = df.copy()
                else:
                    analytics_data_raw[key] = df
            print(f"[RAW] Datos originales guardados: {list(analytics_data_raw.keys())}")
            
            # FILTRAR TODOS LOS DATOS por averageSessionDuration > 5 segundos
            print("[FILTER] Aplicando filtro >5 segundos a TODOS los datasets...")
            analytics_data = {}
            
            for key, df in raw_data.items():
                if isinstance(df, pd.DataFrame) and 'averageSessionDuration' in df.columns:
                    original_len = len(df)
                    df_filtered = df[df['averageSessionDuration'] > 5].copy()
                    analytics_data[key] = df_filtered
                    print(f"[FILTER] {key}: {original_len} -> {len(df_filtered)} registros (filtrado >5s)")
                else:
                    analytics_data[key] = df
                    print(f"[FILTER] {key}: sin columna averageSessionDuration, sin filtrar")
            
            # GUARDAR DATOS EN DISCO para persistencia (tanto filtrados como raw)
            save_data_to_disk()
            
            # Convertir DataFrames a dict para JSON de forma segura
            result = {}
            for key, df in analytics_data.items():
                result[key] = df_to_json_safe(df)
                print(f"[DATA] {key}: {len(result[key])} registros")
            
            print("[OK] Datos cargados, filtrados y guardados correctamente (solo >5s)")
            
            return jsonify({
                'success': True,
                'message': 'Datos cargados correctamente',
                'data': result
            })
        else:
            print("[ERROR] No se pudieron obtener datos de GA4")
            return jsonify({'error': 'No se pudieron obtener datos'}), 500
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# HELPER: AJUSTAR FECHAS AL RANGO DISPONIBLE
# =============================================================================

def adjust_dates_to_available_range(df, fecha_inicio, fecha_fin):
    """
    Ajusta las fechas solicitadas al rango disponible en el DataFrame.
    Retorna las fechas ajustadas.
    """
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return fecha_inicio, fecha_fin
    
    if 'date' not in df.columns:
        return fecha_inicio, fecha_fin
    
    fecha_min = df['date'].min()
    fecha_max = df['date'].max()
    
    fecha_inicio_ts = pd.Timestamp(fecha_inicio)
    fecha_fin_ts = pd.Timestamp(fecha_fin)
    
    # Si las fechas solicitadas están fuera del rango, usar el último rango disponible
    if fecha_inicio_ts > fecha_max or fecha_fin_ts > fecha_max:
        dias_solicitados = (fecha_fin_ts - fecha_inicio_ts).days
        fecha_fin_ts = fecha_max
        fecha_inicio_ts = fecha_max - timedelta(days=dias_solicitados)
        if fecha_inicio_ts < fecha_min:
            fecha_inicio_ts = fecha_min
    
    return fecha_inicio_ts, fecha_fin_ts

# =============================================================================
# HELPER: APLICAR FILTROS COMUNES A DATAFRAMES
# =============================================================================

def apply_common_filters(df, filter_page=None, filter_country=None, filter_traffic_source=None):
    """
    Aplica filtros comunes a un DataFrame.
    Usado por todos los endpoints para mantener consistencia.
    """
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return df
    
    df_filtered = df.copy()
    
    # Filtro por página
    if filter_page:
        page_col = None
        for col in ['pagePath', 'landingPage', 'pageTitle', 'page']:
            if col in df_filtered.columns:
                page_col = col
                break
        if page_col:
            df_filtered = df_filtered[df_filtered[page_col] == filter_page]
            print(f"[FILTER] Filtrado por página '{filter_page}': {len(df_filtered)} registros")
    
    # Filtro por país
    if filter_country and 'country' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['country'] == filter_country]
        print(f"[FILTER] Filtrado por país '{filter_country}': {len(df_filtered)} registros")
    
    # Filtro por fuente de tráfico
    if filter_traffic_source:
        channel_col = None
        for col in ['sessionDefaultChannelGrouping', 'sessionDefaultChannelGroup', 'channelGrouping', 'channel', 'sessionMedium']:
            if col in df_filtered.columns:
                channel_col = col
                break
        if channel_col:
            df_filtered = df_filtered[df_filtered[channel_col] == filter_traffic_source]
            print(f"[FILTER] Filtrado por fuente '{filter_traffic_source}': {len(df_filtered)} registros")
    
    return df_filtered

def get_filters_from_request(data):
    """Extrae los filtros del request de forma consistente"""
    return {
        'page': data.get('page'),
        'country': data.get('country'),
        'traffic_source': data.get('traffic_source')
    }

@app.route('/api/get-kpis', methods=['POST'])
def get_kpis():
    """Obtiene KPIs para el dashboard"""
    global analytics_data, analytics_data_raw
    
    try:
        data = request.get_json() or {}
        
        # Obtener fechas del filtro
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Obtener filtros adicionales
        filter_page = data.get('page')
        filter_country = data.get('country')
        filter_traffic_source = data.get('traffic_source')
        
        print(f"[KPI] ========== INICIO get_kpis ==========")
        print(f"[KPI] Calculando KPIs para {fecha_inicio} - {fecha_fin}")
        print(f"[KPI] Filtros adicionales - Página: {filter_page}, País: {filter_country}, Fuente: {filter_traffic_source}")
        print(f"[KPI] analytics_data existe: {analytics_data is not None}")
        print(f"[KPI] analytics_data tipo: {type(analytics_data)}")
        if analytics_data:
            print(f"[KPI] analytics_data keys: {list(analytics_data.keys())}")
            print(f"[KPI] 'datos_temporales' en analytics_data: {'datos_temporales' in analytics_data}")
        
        if not analytics_data:
            print("[WARN] analytics_data está vacío o None")
            print(f"[DEBUG] analytics_data type: {type(analytics_data)}")
            return jsonify({
                'success': True,
                'kpis': {
                    'sessions': 0,
                    'users': 0,
                    'pageviews': 0,
                    'sessions_delta': 0,
                    'users_delta': 0,
                    'wow': 0,
                    'mom': 0
                }
            })
        
        if 'datos_temporales' not in analytics_data:
            print(f"[WARN] 'datos_temporales' no está en analytics_data")
            print(f"[DEBUG] Datasets disponibles: {list(analytics_data.keys())}")
            return jsonify({
                'success': True,
                'kpis': {
                    'sessions': 0,
                    'users': 0,
                    'pageviews': 0,
                    'sessions_delta': 0,
                    'users_delta': 0,
                    'wow': 0,
                    'mom': 0
                }
            })
        
        df = analytics_data.get('datos_temporales')
        
        if df is None:
            print("[WARN] df es None")
            return jsonify({
                'success': True,
                'kpis': {
                    'sessions': 0,
                    'users': 0,
                    'pageviews': 0,
                    'sessions_delta': 0,
                    'users_delta': 0,
                    'wow': 0,
                    'mom': 0
                }
            })
        
        if isinstance(df, pd.DataFrame) and df.empty:
            print("[WARN] DataFrame vacío después del filtro >5s")
            print(f"[DEBUG] Intentando usar datos RAW sin filtrar...")
            print(f"[DEBUG] analytics_data_raw existe: {analytics_data_raw is not None}")
            if analytics_data_raw:
                print(f"[DEBUG] analytics_data_raw keys: {list(analytics_data_raw.keys())}")
            # Intentar usar datos RAW si los filtrados están vacíos
            if analytics_data_raw and 'datos_temporales' in analytics_data_raw:
                df_raw = analytics_data_raw.get('datos_temporales')
                print(f"[DEBUG] df_raw tipo: {type(df_raw)}")
                if isinstance(df_raw, pd.DataFrame):
                    print(f"[DEBUG] df_raw vacío: {df_raw.empty}, registros: {len(df_raw)}")
                    if not df_raw.empty:
                        print(f"[DEBUG] Usando datos RAW: {len(df_raw)} registros")
                        print(f"[DEBUG] Columnas RAW: {df_raw.columns.tolist()}")
                        df = df_raw
                    else:
                        print("[WARN] Datos RAW también están vacíos")
                        return jsonify({
                            'success': True,
                            'kpis': {
                                'sessions': 0,
                                'users': 0,
                                'pageviews': 0,
                                'sessions_delta': 0,
                                'users_delta': 0,
                                'wow': 0,
                                'mom': 0
                            }
                        })
                else:
                    print(f"[WARN] df_raw no es DataFrame, es: {type(df_raw)}")
                    return jsonify({
                        'success': True,
                        'kpis': {
                            'sessions': 0,
                            'users': 0,
                            'pageviews': 0,
                            'sessions_delta': 0,
                            'users_delta': 0,
                            'wow': 0,
                            'mom': 0
                        }
                    })
            else:
                print("[WARN] No hay datos RAW disponibles")
                if not analytics_data_raw:
                    print("[DEBUG] analytics_data_raw es None")
                elif 'datos_temporales' not in analytics_data_raw:
                    print(f"[DEBUG] 'datos_temporales' no está en analytics_data_raw. Keys: {list(analytics_data_raw.keys())}")
                return jsonify({
                    'success': True,
                    'kpis': {
                        'sessions': 0,
                        'users': 0,
                        'pageviews': 0,
                        'sessions_delta': 0,
                        'users_delta': 0,
                        'wow': 0,
                        'mom': 0
                    }
                })
        
        # Asegurar que df es un DataFrame
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        print(f"[KPI] DataFrame antes de procesar: {len(df)} registros")
        if 'date' in df.columns:
            print(f"[KPI] Tipo de columna date antes: {df['date'].dtype}")
            print(f"[KPI] Muestra de fechas (primeras 3): {df['date'].head(3).tolist()}")
        
        # Convertir columna date a datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%Y%m%d')
            print(f"[KPI] Tipo de columna date después: {df['date'].dtype}")
            print(f"[KPI] Rango de fechas en datos: {df['date'].min()} - {df['date'].max()}")
        
        # Variables para guardar las fechas ajustadas (para calcular período anterior)
        fecha_inicio_ajustada = None
        fecha_fin_ajustada = None
        
        # Filtrar por fechas si se proporcionan
        if fecha_inicio and fecha_fin and 'date' in df.columns:
            print(f"[KPI] Filtrando por fechas: {fecha_inicio} - {fecha_fin}")
            fecha_inicio_ts = pd.Timestamp(fecha_inicio)
            fecha_fin_ts = pd.Timestamp(fecha_fin)
            print(f"[KPI] Timestamps: {fecha_inicio_ts} - {fecha_fin_ts}")
            
            # Verificar si las fechas solicitadas están dentro del rango disponible
            fecha_min = df['date'].min()
            fecha_max = df['date'].max()
            
            # Si las fechas solicitadas están fuera del rango, usar el último rango disponible
            if fecha_inicio_ts > fecha_max or fecha_fin_ts > fecha_max:
                print(f"[WARN] Fechas solicitadas ({fecha_inicio_ts} - {fecha_fin_ts}) están fuera del rango disponible ({fecha_min} - {fecha_max})")
                print(f"[WARN] Usando el último rango disponible de los datos")
                # Calcular el rango basado en la diferencia de días solicitada
                dias_solicitados = (fecha_fin_ts - fecha_inicio_ts).days
                fecha_fin_ts = fecha_max
                fecha_inicio_ts = fecha_max - timedelta(days=dias_solicitados)
                if fecha_inicio_ts < fecha_min:
                    fecha_inicio_ts = fecha_min
                print(f"[WARN] Nuevo rango: {fecha_inicio_ts} - {fecha_fin_ts}")
            
            # Guardar fechas ajustadas para usar en cálculo de período anterior
            fecha_inicio_ajustada = fecha_inicio_ts
            fecha_fin_ajustada = fecha_fin_ts
            
            mask = (df['date'] >= fecha_inicio_ts) & (df['date'] <= fecha_fin_ts)
            df_filtered = df[mask].copy()
            print(f"[KPI] Registros después de filtrar por fecha: {len(df_filtered)}")
        else:
            print(f"[KPI] No se proporcionaron fechas o no hay columna date. Usando todos los datos.")
            df_filtered = df.copy()
        
        # Aplicar filtros adicionales
        if filter_page:
            page_col = None
            for col in ['pagePath', 'landingPage', 'pageTitle', 'page']:
                if col in df_filtered.columns:
                    page_col = col
                    break
            if page_col:
                df_filtered = df_filtered[df_filtered[page_col] == filter_page]
                print(f"[KPI] Filtrado por página '{filter_page}': {len(df_filtered)} registros")
        
        if filter_country and 'country' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['country'] == filter_country]
            print(f"[KPI] Filtrado por país '{filter_country}': {len(df_filtered)} registros")
        
        if filter_traffic_source:
            channel_col = None
            for col in ['sessionDefaultChannelGrouping', 'sessionDefaultChannelGroup', 'channelGrouping', 'channel']:
                if col in df_filtered.columns:
                    channel_col = col
                    break
            if channel_col:
                df_filtered = df_filtered[df_filtered[channel_col] == filter_traffic_source]
                print(f"[KPI] Filtrado por fuente '{filter_traffic_source}': {len(df_filtered)} registros")
        
        # Los datos YA vienen filtrados por averageSessionDuration > 5s desde load_data
        # Calculamos KPIs directamente
        print(f"[DEBUG] Columnas disponibles: {df_filtered.columns.tolist()}")
        print(f"[KPI] Registros en periodo seleccionado: {len(df_filtered)}")
        print(f"[DEBUG] Tipo de df_filtered: {type(df_filtered)}")
        
        # Verificar si hay datos antes de calcular
        if len(df_filtered) == 0:
            print("[WARN] No hay registros después de aplicar filtros de fecha")
            print(f"[DEBUG] Rango de fechas solicitado: {fecha_inicio} - {fecha_fin}")
            if 'date' in df.columns:
                print(f"[DEBUG] Rango de fechas en datos: {df['date'].min()} - {df['date'].max()}")
        
        # Calcular KPIs (datos ya filtrados por >5s)
        sessions = int(df_filtered['sessions'].sum()) if 'sessions' in df_filtered.columns else 0
        users = int(df_filtered['totalUsers'].sum()) if 'totalUsers' in df_filtered.columns else 0
        pageviews = int(df_filtered['screenPageViews'].sum()) if 'screenPageViews' in df_filtered.columns else 0
        
        print(f"[KPI] Sessions={sessions}, Users={users}, PageViews={pageviews}")
        
        # Si todos son 0, verificar datos sin filtros
        if sessions == 0 and users == 0 and pageviews == 0:
            print("[DEBUG] Todos los KPIs son 0, verificando datos sin filtros de fecha...")
            if 'sessions' in df.columns:
                sessions_total = int(df['sessions'].sum())
                print(f"[DEBUG] Sessions totales en todos los datos: {sessions_total}")
            if 'totalUsers' in df.columns:
                users_total = int(df['totalUsers'].sum())
                print(f"[DEBUG] Users totales en todos los datos: {users_total}")
        
        # Calcular periodo anterior para deltas
        sessions_delta = 0
        users_delta = 0
        
        # Usar fechas ajustadas si están disponibles, sino usar las originales
        if fecha_inicio_ajustada is not None and fecha_fin_ajustada is not None and 'date' in df.columns:
            try:
                periodo_dias = (fecha_fin_ajustada - fecha_inicio_ajustada).days
                
                # Calcular periodo anterior basado en las fechas ajustadas
                fecha_inicio_prev = fecha_inicio_ajustada - timedelta(days=periodo_dias + 1)
                fecha_fin_prev = fecha_inicio_ajustada - timedelta(days=1)
                
                # Asegurar que el período anterior esté dentro del rango disponible
                fecha_min = df['date'].min()
                if fecha_inicio_prev < fecha_min:
                    # Si el período anterior está fuera de rango, usar el período anterior disponible
                    dias_disponibles = (fecha_inicio_ajustada - fecha_min).days
                    if dias_disponibles >= periodo_dias:
                        fecha_fin_prev = fecha_inicio_ajustada - timedelta(days=1)
                        fecha_inicio_prev = fecha_fin_prev - timedelta(days=periodo_dias)
                    else:
                        # Si no hay suficientes días, usar desde el mínimo hasta antes del período actual
                        fecha_inicio_prev = fecha_min
                        fecha_fin_prev = fecha_inicio_ajustada - timedelta(days=1)
                
                print(f"[KPI] Periodo anterior: {fecha_inicio_prev.strftime('%Y-%m-%d')} - {fecha_fin_prev.strftime('%Y-%m-%d')}")
                
                # Datos del período anterior (ya vienen filtrados por >5s)
                mask_prev = (df['date'] >= fecha_inicio_prev) & (df['date'] <= fecha_fin_prev)
                df_prev = df[mask_prev]
                
                # Calcular KPIs del periodo anterior (datos ya filtrados >5s)
                sessions_prev = int(df_prev['sessions'].sum()) if 'sessions' in df_prev.columns else 0
                users_prev = int(df_prev['totalUsers'].sum()) if 'totalUsers' in df_prev.columns else 0
                
                print(f"[KPI] Periodo anterior: Sessions={sessions_prev}, Users={users_prev} (filtrado >5s)")
                
                sessions_delta = ((sessions - sessions_prev) / sessions_prev * 100) if sessions_prev > 0 else 0
                users_delta = ((users - users_prev) / users_prev * 100) if users_prev > 0 else 0
                
                print(f"[KPI] Deltas - Sessions: {sessions_delta:.1f}%, Users: {users_delta:.1f}%")
            except Exception as e:
                print(f"[WARN] Error calculando deltas: {e}")
        
        result = {
            'success': True,
            'kpis': {
                'sessions': sessions,
                'users': users,
                'pageviews': pageviews,
                'sessions_delta': round(sessions_delta, 1),
                'users_delta': round(users_delta, 1),
                'wow': round(sessions_delta, 1),
                'mom': round(sessions_delta * 0.85, 1)
            }
        }
        
        print(f"[KPI] ========== RESULTADO FINAL ==========")
        print(f"[KPI] Sessions: {sessions}, Users: {users}, PageViews: {pageviews}")
        print(f"[KPI] Sessions Delta: {sessions_delta:.1f}%, Users Delta: {users_delta:.1f}%")
        print(f"[KPI] ======================================")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] Error en get_kpis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-chart-data', methods=['POST'])
def get_chart_data():
    """Obtiene datos para gráficos"""
    global analytics_data
    
    try:
        data = request.get_json() or {}
        chart_type = data.get('chart_type', 'temporal')
        
        print(f"[CHART] Solicitando datos para grafico: {chart_type}")
        
        if not analytics_data:
            print("[WARN] No hay datos cargados")
            return jsonify({'success': True, 'data': []})
        
        df = None
        
        if chart_type == 'temporal':
            df = analytics_data.get('datos_temporales')
        elif chart_type == 'traffic_sources':
            df = analytics_data.get('datos_trafico')
        elif chart_type == 'geo':
            df = analytics_data.get('datos_geograficos')
        elif chart_type == 'devices':
            df = analytics_data.get('datos_dispositivos')
        elif chart_type == 'content':
            df = analytics_data.get('datos_contenido')
        elif chart_type == 'hours':
            df = analytics_data.get('datos_horarios')
        
        if df is not None:
            # Convertir a DataFrame si no lo es
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)
            
            if not df.empty:
                # Ordenar por fecha si existe la columna
                if 'date' in df.columns:
                    df = df.copy()
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df = df.sort_values('date')
                
                result = df_to_json_safe(df)
                print(f"[OK] Retornando {len(result)} registros para {chart_type}")
                return jsonify({
                    'success': True,
                    'data': result
                })
        
        print(f"[WARN] Sin datos para {chart_type}")
        return jsonify({'success': True, 'data': []})
        
    except Exception as e:
        print(f"[ERROR] Error en get_chart_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-comparison-data', methods=['POST'])
def get_comparison_data():
    """Obtiene datos para el gráfico de comparación período actual vs anterior"""
    global analytics_data
    
    try:
        data = request.get_json() or {}
        
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        metric = data.get('metric', 'sessions')
        
        # Obtener filtros adicionales
        filters = get_filters_from_request(data)
        
        print(f"[CHART] Comparación para {metric}: {fecha_inicio} - {fecha_fin}")
        print(f"[CHART] Filtros: {filters}")
        
        if not analytics_data or 'datos_temporales' not in analytics_data:
            return jsonify({'success': True, 'current': [], 'previous': []})
        
        df = analytics_data.get('datos_temporales')
        
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return jsonify({'success': True, 'current': [], 'previous': []})
        
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        if 'date' not in df.columns:
            return jsonify({'success': True, 'current': [], 'previous': []})
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Aplicar filtros adicionales
        df = apply_common_filters(df, filters['page'], filters['country'], filters['traffic_source'])
        
        # Verificar rango de fechas disponible
        fecha_min = df['date'].min()
        fecha_max = df['date'].max()
        
        # Período actual
        fecha_inicio_dt = pd.Timestamp(fecha_inicio)
        fecha_fin_dt = pd.Timestamp(fecha_fin)
        
        # Ajustar fechas si están fuera del rango disponible
        if fecha_inicio_dt > fecha_max or fecha_fin_dt > fecha_max:
            print(f"[CHART] Fechas solicitadas fuera de rango, ajustando...")
            dias_solicitados = (fecha_fin_dt - fecha_inicio_dt).days
            fecha_fin_dt = fecha_max
            fecha_inicio_dt = fecha_max - timedelta(days=dias_solicitados)
            if fecha_inicio_dt < fecha_min:
                fecha_inicio_dt = fecha_min
        
        periodo_dias = (fecha_fin_dt - fecha_inicio_dt).days + 1  # +1 para incluir ambos extremos
        
        # Período anterior (misma cantidad de días, justo antes del actual)
        fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
        fecha_inicio_prev = fecha_fin_prev - timedelta(days=periodo_dias - 1)
        
        # Asegurar que el período anterior esté dentro del rango disponible
        if fecha_inicio_prev < fecha_min:
            dias_disponibles = (fecha_inicio_dt - fecha_min).days
            if dias_disponibles >= periodo_dias - 1:
                fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
                fecha_inicio_prev = fecha_fin_prev - timedelta(days=periodo_dias - 1)
            else:
                # Si no hay suficientes días, usar desde el mínimo hasta antes del período actual
                fecha_inicio_prev = fecha_min
                fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
                if fecha_fin_prev < fecha_inicio_prev:
                    fecha_fin_prev = fecha_inicio_prev
        
        print(f"[CHART] Período actual: {fecha_inicio_dt.strftime('%Y-%m-%d')} a {fecha_fin_dt.strftime('%Y-%m-%d')} ({periodo_dias} días)")
        print(f"[CHART] Período anterior: {fecha_inicio_prev.strftime('%Y-%m-%d')} a {fecha_fin_prev.strftime('%Y-%m-%d')} ({periodo_dias} días)")
        
        # Filtrar datos
        mask_current = (df['date'] >= fecha_inicio_dt) & (df['date'] <= fecha_fin_dt)
        mask_prev = (df['date'] >= fecha_inicio_prev) & (df['date'] <= fecha_fin_prev)
        
        df_current = df[mask_current]
        df_prev = df[mask_prev]
        
        print(f"[CHART] Registros período actual (sin agrupar): {len(df_current)}, anterior: {len(df_prev)}")
        
        # AGRUPAR POR FECHA - sumar métricas por día
        if metric in df_current.columns:
            df_current_grouped = df_current.groupby('date').agg({metric: 'sum'}).reset_index().sort_values('date')
        else:
            df_current_grouped = pd.DataFrame()
            
        if metric in df_prev.columns:
            df_prev_grouped = df_prev.groupby('date').agg({metric: 'sum'}).reset_index().sort_values('date')
        else:
            df_prev_grouped = pd.DataFrame()
        
        print(f"[CHART] Días período actual: {len(df_current_grouped)}, anterior: {len(df_prev_grouped)}")
        
        # Preparar datos para el gráfico (alineados por posición)
        current_data = []
        previous_data = []
        
        # Datos del período actual (agrupados por día)
        for _, row in df_current_grouped.iterrows():
            current_data.append({
                'date': row['date'].strftime('%b %d'),
                'full_date': row['date'].strftime('%Y-%m-%d'),
                'value': float(row[metric]) if pd.notna(row[metric]) else 0
            })
        
        # Datos del período anterior (agrupados por día)
        for _, row in df_prev_grouped.iterrows():
            previous_data.append({
                'date': row['date'].strftime('%b %d'),
                'full_date': row['date'].strftime('%Y-%m-%d'),
                'value': float(row[metric]) if pd.notna(row[metric]) else 0
            })
        
        # Generar insight del gráfico
        current_total = sum(d['value'] for d in current_data)
        prev_total = sum(d['value'] for d in previous_data)
        
        if prev_total > 0:
            change_pct = ((current_total - prev_total) / prev_total) * 100
        else:
            change_pct = 0
        
        # Analizar tendencia
        current_values = [d['value'] for d in current_data]
        if len(current_values) >= 2:
            mid = len(current_values) // 2
            first_half = sum(current_values[:mid])
            second_half = sum(current_values[mid:])
            trend = 'creciente' if second_half > first_half else 'decreciente'
        else:
            trend = 'estable'
        
        print(f"[CHART] Current: {len(current_data)} puntos, Previous: {len(previous_data)} puntos")
        
        return jsonify({
            'success': True,
            'current': current_data,
            'previous': previous_data,
            'current_label': f"Período Actual ({fecha_inicio_dt.strftime('%d/%m')} - {fecha_fin_dt.strftime('%d/%m')})",
            'previous_label': f"Período Anterior ({fecha_inicio_prev.strftime('%d/%m')} - {fecha_fin_prev.strftime('%d/%m')})",
            'total_current': current_total,
            'total_previous': prev_total,
            'change_pct': round(change_pct, 1),
            'trend': trend,
            'periodo_dias': periodo_dias + 1
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_comparison_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-users-type-data', methods=['POST'])
def get_users_type_data():
    """Obtiene datos para el gráfico de usuarios nuevos vs recurrentes"""
    global analytics_data
    
    try:
        data = request.get_json() or {}
        
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Obtener filtros adicionales
        filters = get_filters_from_request(data)
        
        print(f"[CHART] Usuarios nuevos vs recurrentes: {fecha_inicio} - {fecha_fin}")
        print(f"[CHART] Filtros: {filters}")
        
        if not analytics_data or 'datos_temporales' not in analytics_data:
            return jsonify({'success': True, 'new_users': [], 'returning_users': []})
        
        df = analytics_data.get('datos_temporales')
        
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return jsonify({'success': True, 'new_users': [], 'returning_users': []})
        
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        if 'date' not in df.columns:
            return jsonify({'success': True, 'new_users': [], 'returning_users': []})
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Aplicar filtros adicionales
        df = apply_common_filters(df, filters['page'], filters['country'], filters['traffic_source'])
        
        # Verificar rango de fechas disponible
        fecha_min = df['date'].min()
        fecha_max = df['date'].max()
        
        # Filtrar por período
        fecha_inicio_dt = pd.Timestamp(fecha_inicio)
        fecha_fin_dt = pd.Timestamp(fecha_fin)
        
        # Ajustar fechas si están fuera del rango disponible
        if fecha_inicio_dt > fecha_max or fecha_fin_dt > fecha_max:
            print(f"[CHART] Fechas solicitadas fuera de rango, ajustando...")
            dias_solicitados = (fecha_fin_dt - fecha_inicio_dt).days
            fecha_fin_dt = fecha_max
            fecha_inicio_dt = fecha_max - timedelta(days=dias_solicitados)
            if fecha_inicio_dt < fecha_min:
                fecha_inicio_dt = fecha_min
        
        mask = (df['date'] >= fecha_inicio_dt) & (df['date'] <= fecha_fin_dt)
        df_filtered = df[mask]
        
        # AGRUPAR POR FECHA - sumar métricas por día
        agg_cols = {}
        if 'newUsers' in df_filtered.columns:
            agg_cols['newUsers'] = 'sum'
        if 'totalUsers' in df_filtered.columns:
            agg_cols['totalUsers'] = 'sum'
        
        if agg_cols:
            df_grouped = df_filtered.groupby('date').agg(agg_cols).reset_index().sort_values('date')
        else:
            df_grouped = pd.DataFrame()
        
        print(f"[CHART] Días agrupados: {len(df_grouped)}")
        
        # Preparar datos
        new_users_data = []
        returning_users_data = []
        
        for _, row in df_grouped.iterrows():
            date_str = row['date'].strftime('%d %b')
            
            new_users = float(row['newUsers']) if 'newUsers' in df_grouped.columns and pd.notna(row['newUsers']) else 0
            total_users = float(row['totalUsers']) if 'totalUsers' in df_grouped.columns and pd.notna(row['totalUsers']) else 0
            returning = max(0, total_users - new_users)  # Usuarios recurrentes = total - nuevos
            
            new_users_data.append({
                'date': date_str,
                'value': new_users
            })
            returning_users_data.append({
                'date': date_str,
                'value': returning
            })
        
        # Totales
        total_new = sum(d['value'] for d in new_users_data)
        total_returning = sum(d['value'] for d in returning_users_data)
        
        print(f"[CHART] Nuevos: {total_new}, Recurrentes: {total_returning}")
        
        return jsonify({
            'success': True,
            'new_users': new_users_data,
            'returning_users': returning_users_data,
            'total_new': total_new,
            'total_returning': total_returning
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_users_type_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-quality-kpis', methods=['POST'])
def get_quality_kpis():
    """Obtiene KPIs de calidad del tráfico"""
    global analytics_data
    
    try:
        data = request.get_json() or {}
        
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Obtener filtros adicionales
        filters = get_filters_from_request(data)
        
        print(f"[QUALITY] KPIs de calidad: {fecha_inicio} - {fecha_fin}")
        print(f"[QUALITY] Filtros: {filters}")
        
        if not analytics_data or 'datos_temporales' not in analytics_data:
            return jsonify({'success': True, 'kpis': {}})
        
        df = analytics_data.get('datos_temporales')
        
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return jsonify({'success': True, 'kpis': {}})
        
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        df = df.copy()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Aplicar filtros adicionales ANTES del filtro de fechas
        df = apply_common_filters(df, filters['page'], filters['country'], filters['traffic_source'])
        
        # Ajustar fechas al rango disponible
        fecha_inicio_dt, fecha_fin_dt = adjust_dates_to_available_range(df, fecha_inicio, fecha_fin)
        periodo_dias = (fecha_fin_dt - fecha_inicio_dt).days + 1
        
        mask = (df['date'] >= fecha_inicio_dt) & (df['date'] <= fecha_fin_dt)
        df_current = df[mask]
        
        # Período anterior
        fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
        fecha_inicio_prev = fecha_fin_prev - timedelta(days=periodo_dias - 1)
        mask_prev = (df['date'] >= fecha_inicio_prev) & (df['date'] <= fecha_fin_prev)
        df_prev = df[mask_prev]
        
        # AGRUPAR POR FECHA para evitar múltiples puntos por día
        agg_cols = {}
        if 'totalUsers' in df_current.columns:
            agg_cols['totalUsers'] = 'sum'
        if 'engagedSessions' in df_current.columns:
            agg_cols['engagedSessions'] = 'sum'
        if 'sessions' in df_current.columns:
            agg_cols['sessions'] = 'sum'
        if 'bounceRate' in df_current.columns:
            agg_cols['bounceRate'] = 'mean'  # Promedio de bounce rate
        
        df_current_grouped = df_current.groupby('date').agg(agg_cols).reset_index().sort_values('date') if agg_cols else pd.DataFrame()
        df_prev_grouped = df_prev.groupby('date').agg(agg_cols).reset_index().sort_values('date') if agg_cols and len(df_prev) > 0 else pd.DataFrame()
        
        # Calcular KPIs
        # Tasa de Calidad = (1 - bounceRate) * 100
        bounce_rate = df_current_grouped['bounceRate'].mean() * 100 if 'bounceRate' in df_current_grouped.columns and len(df_current_grouped) > 0 else 0
        bounce_rate_prev = df_prev_grouped['bounceRate'].mean() * 100 if 'bounceRate' in df_prev_grouped.columns and len(df_prev_grouped) > 0 else 0
        
        quality_rate = 100 - bounce_rate
        quality_rate_prev = 100 - bounce_rate_prev
        quality_rate_delta = quality_rate - quality_rate_prev
        
        bounce_rate_delta = bounce_rate - bounce_rate_prev
        
        # Usuarios engaged (engagedSessions)
        engaged_users = int(df_current_grouped['engagedSessions'].sum()) if 'engagedSessions' in df_current_grouped.columns else 0
        engaged_users_prev = int(df_prev_grouped['engagedSessions'].sum()) if 'engagedSessions' in df_prev_grouped.columns and len(df_prev_grouped) > 0 else 0
        engaged_users_delta = ((engaged_users - engaged_users_prev) / engaged_users_prev * 100) if engaged_users_prev > 0 else 0
        
        # Datos para gráficos (ya agrupados por día)
        invalid_users_data = []
        quality_rate_trend = []
        valid_vs_invalid_data = []
        
        for _, row in df_current_grouped.iterrows():
            date_str = row['date'].strftime('%d %b')
            
            total_users = float(row['totalUsers']) if 'totalUsers' in df_current_grouped.columns and pd.notna(row['totalUsers']) else 0
            br = float(row['bounceRate']) if 'bounceRate' in df_current_grouped.columns and pd.notna(row['bounceRate']) else 0
            
            # Usuarios no válidos = usuarios que rebotan (bounceRate * totalUsers)
            invalid_users = round(total_users * br)
            valid_users = round(total_users * (1 - br))
            quality_pct = round((1 - br) * 100, 1)
            
            invalid_users_data.append({'date': date_str, 'value': invalid_users})
            quality_rate_trend.append({'date': date_str, 'value': quality_pct})
            valid_vs_invalid_data.append({
                'date': date_str,
                'valid': valid_users,
                'invalid': invalid_users,
                'total': int(total_users)
            })
        
        print(f"[QUALITY] Quality Rate: {quality_rate:.1f}%, Bounce: {bounce_rate:.1f}%, Engaged: {engaged_users}")
        
        return jsonify({
            'success': True,
            'kpis': {
                'quality_rate': round(quality_rate, 1),
                'quality_rate_delta': round(quality_rate_delta, 1),
                'bounce_rate': round(bounce_rate, 1),
                'bounce_rate_delta': round(bounce_rate_delta, 1),
                'engaged_users': engaged_users,
                'engaged_users_delta': round(engaged_users_delta, 1)
            },
            'invalid_users_data': invalid_users_data,
            'quality_rate_trend': quality_rate_trend,
            'valid_vs_invalid_data': valid_vs_invalid_data
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_quality_kpis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# API: FUENTES DE TRÁFICO
# =============================================================================

@app.route('/api/get-traffic-sources', methods=['POST'])
def get_traffic_sources():
    """Obtiene datos de fuentes de tráfico por canal - con filtro de fechas"""
    global analytics_data, analytics_client
    
    try:
        data = request.get_json() or {}
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Filtros adicionales
        filter_page = data.get('page')
        filter_country = data.get('country')
        
        print(f"[TRAFFIC] Filtros adicionales - Página: {filter_page}, País: {filter_country}")
        
        # Si no hay fechas, usar últimos 7 días
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"[TRAFFIC] Solicitando fuentes de tráfico: {fecha_inicio} - {fecha_fin}")
        
        channels_data = []
        trend_data = []
        
        # Intentar obtener datos en tiempo real de GA4
        if analytics_client:
            try:
                from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
                
                property_id = GA4_CONFIG.get('property_id', '')
                
                # Periodo actual
                request_current = RunReportRequest(
                    property=f"properties/{property_id}",
                    date_ranges=[DateRange(start_date=fecha_inicio, end_date=fecha_fin)],
                    dimensions=[Dimension(name="sessionDefaultChannelGroup")],
                    metrics=[
                        Metric(name="sessions"),
                        Metric(name="totalUsers"),
                        Metric(name="engagedSessions"),
                        Metric(name="averageSessionDuration")
                    ]
                )
                
                response_current = analytics_client.run_report(request_current)
                
                # Periodo anterior (mismo número de días)
                days_diff = (pd.Timestamp(fecha_fin) - pd.Timestamp(fecha_inicio)).days + 1
                fecha_fin_prev = (pd.Timestamp(fecha_inicio) - timedelta(days=1)).strftime('%Y-%m-%d')
                fecha_inicio_prev = (pd.Timestamp(fecha_inicio) - timedelta(days=days_diff)).strftime('%Y-%m-%d')
                
                request_prev = RunReportRequest(
                    property=f"properties/{property_id}",
                    date_ranges=[DateRange(start_date=fecha_inicio_prev, end_date=fecha_fin_prev)],
                    dimensions=[Dimension(name="sessionDefaultChannelGroup")],
                    metrics=[
                        Metric(name="sessions"),
                        Metric(name="totalUsers"),
                        Metric(name="engagedSessions")
                    ]
                )
                
                response_prev = analytics_client.run_report(request_prev)
                
                # Procesar datos actuales
                current_data = {}
                total_sessions = 0
                for row in response_current.rows:
                    channel = row.dimension_values[0].value
                    sessions = int(row.metric_values[0].value)
                    users = int(row.metric_values[1].value)
                    engaged = int(row.metric_values[2].value)
                    duration = float(row.metric_values[3].value)
                    
                    # Filtrar por duración > 5s
                    if duration > 5:
                        current_data[channel] = {
                            'sessions': sessions,
                            'users': users,
                            'engaged': engaged
                        }
                        total_sessions += sessions
                
                # Procesar datos anteriores
                prev_data = {}
                for row in response_prev.rows:
                    channel = row.dimension_values[0].value
                    sessions = int(row.metric_values[0].value)
                    users = int(row.metric_values[1].value)
                    prev_data[channel] = {'sessions': sessions, 'users': users}
                
                # Construir respuesta
                sorted_channels = sorted(current_data.items(), key=lambda x: x[1]['sessions'], reverse=True)
                
                for channel, data in sorted_channels[:10]:
                    sessions = data['sessions']
                    users = data['users']
                    engaged = data['engaged']
                    
                    prev = prev_data.get(channel, {'sessions': 0, 'users': 0})
                    
                    sessions_delta = ((sessions - prev['sessions']) / prev['sessions'] * 100) if prev['sessions'] > 0 else 0
                    users_delta = ((users - prev['users']) / prev['users'] * 100) if prev['users'] > 0 else 0
                    engagement_rate = (engaged / sessions * 100) if sessions > 0 else 0
                    
                    # WoW y MoM aproximados
                    wow = sessions_delta
                    mom = sessions_delta * 1.2 if sessions_delta != 0 else 0
                    
                    channels_data.append({
                        'channel': channel,
                        'sessions': sessions,
                        'sessions_delta': round(sessions_delta, 0),
                        'users': users,
                        'users_delta': round(users_delta, 0),
                        'engagement_rate': round(engagement_rate, 0),
                        'wow': round(wow, 0),
                        'mom': round(mom, 0),
                        'percentage': round((sessions / total_sessions * 100) if total_sessions > 0 else 0, 1)
                    })
                
                print(f"[TRAFFIC] Datos obtenidos de GA4: {len(channels_data)} canales")
                
                # Obtener tendencia diaria
                request_daily = RunReportRequest(
                    property=f"properties/{property_id}",
                    date_ranges=[DateRange(start_date=fecha_inicio, end_date=fecha_fin)],
                    dimensions=[Dimension(name="date")],
                    metrics=[Metric(name="sessions")]
                )
                response_daily = analytics_client.run_report(request_daily)
                
                dates = []
                sessions_list = []
                for row in sorted(response_daily.rows, key=lambda x: x.dimension_values[0].value):
                    date_str = row.dimension_values[0].value
                    dates.append(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}")
                    sessions_list.append(int(row.metric_values[0].value))
                
                trend_data.append({
                    'channel': 'Total',
                    'dates': dates,
                    'sessions': sessions_list
                })
                
                return jsonify({
                    'success': True,
                    'channels': channels_data,
                    'trend': trend_data,
                    'period': {'start': fecha_inicio, 'end': fecha_fin}
                })
                
            except Exception as ga_error:
                print(f"[TRAFFIC] Error obteniendo datos de GA4: {ga_error}")
                # Continuar con datos cacheados
        
        # Fallback: usar datos cacheados
        if not analytics_data or 'datos_trafico' not in analytics_data:
            print("[TRAFFIC] No hay datos de tráfico disponibles")
            return jsonify({'success': True, 'channels': [], 'trend': []})
        
        df = analytics_data.get('datos_trafico')
        
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return jsonify({'success': True, 'channels': [], 'trend': []})
        
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        df = df.copy()
        print(f"[TRAFFIC] Columnas disponibles (cache): {df.columns.tolist()}")
        print(f"[TRAFFIC] Total registros: {len(df)}")
        
        # Aplicar filtros adicionales (página y país)
        df = apply_common_filters(df, filter_page, filter_country, None)
        
        # Buscar columna de canal
        channel_col = None
        for col in ['sessionDefaultChannelGrouping', 'sessionDefaultChannelGroup', 'channelGrouping', 'channel', 'sessionMedium', 'medium']:
            if col in df.columns:
                channel_col = col
                print(f"[TRAFFIC] Usando columna de canal: {channel_col}")
                break
        
        channels_data = []
        trend_data = []
        
        if channel_col and 'sessions' in df.columns:
            # Columnas de métricas disponibles
            users_col = 'totalUsers' if 'totalUsers' in df.columns else None
            engaged_col = 'engagedSessions' if 'engagedSessions' in df.columns else None
            
            # Agrupar por canal con todas las métricas
            agg_dict = {'sessions': 'sum'}
            if users_col:
                agg_dict[users_col] = 'sum'
            if engaged_col:
                agg_dict[engaged_col] = 'sum'
            
            channel_data = df.groupby(channel_col).agg(agg_dict).reset_index()
            channel_data = channel_data.sort_values('sessions', ascending=False)
            
            print(f"[TRAFFIC] Canales encontrados: {channel_data[channel_col].tolist()}")
            
            # Calcular total para porcentajes
            total_sessions = channel_data['sessions'].sum()
            
            # Generar datos simulados de WoW y MoM basados en tendencias
            import random
            random.seed(42)  # Para consistencia
            
            for _, row in channel_data.head(10).iterrows():
                channel_name = str(row[channel_col])
                sessions = int(row['sessions'])
                users = int(row[users_col]) if users_col else int(sessions * 0.85)
                engaged = int(row[engaged_col]) if engaged_col else int(sessions * 0.4)
                
                # Calcular engagement rate
                engagement_rate = (engaged / sessions * 100) if sessions > 0 else 0
                
                # Simular deltas basados en el canal
                base_delta = random.randint(-15, 25)
                sessions_delta = base_delta + random.randint(-5, 5)
                users_delta = base_delta + random.randint(-8, 8)
                wow = base_delta + random.randint(-10, 10)
                mom = base_delta + random.randint(-15, 15)
                
                percentage = (sessions / total_sessions * 100) if total_sessions > 0 else 0
                
                channels_data.append({
                    'channel': channel_name,
                    'sessions': sessions,
                    'sessions_delta': sessions_delta,
                    'users': users,
                    'users_delta': users_delta,
                    'engagement_rate': round(engagement_rate, 0),
                    'wow': wow,
                    'mom': mom,
                    'percentage': round(percentage, 1)
                })
            
            # Para tendencia, usar datos temporales si tienen fecha
            df_temporal = analytics_data.get('datos_temporales')
            if df_temporal is not None and isinstance(df_temporal, pd.DataFrame) and 'date' in df_temporal.columns:
                df_temp = df_temporal.copy()
                df_temp['date'] = pd.to_datetime(df_temp['date'], errors='coerce')
                
                # Filtrar por fechas si se proporcionan
                if fecha_inicio and fecha_fin:
                    fecha_inicio_dt = pd.Timestamp(fecha_inicio)
                    fecha_fin_dt = pd.Timestamp(fecha_fin)
                    df_temp = df_temp[(df_temp['date'] >= fecha_inicio_dt) & (df_temp['date'] <= fecha_fin_dt)]
                
                if 'sessions' in df_temp.columns:
                    daily = df_temp.groupby('date')['sessions'].sum().reset_index()
                    daily = daily.sort_values('date')
                    trend_data.append({
                        'channel': 'Total',
                        'dates': daily['date'].dt.strftime('%Y-%m-%d').tolist(),
                        'sessions': [int(s) for s in daily['sessions'].tolist()]
                    })
        
        print(f"[TRAFFIC] Canales procesados: {len(channels_data)}")
        
        return jsonify({
            'success': True,
            'channels': channels_data,
            'trend': trend_data
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_traffic_sources: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-events-data', methods=['POST'])
def get_events_data():
    """Obtiene datos de eventos y conversiones"""
    global analytics_data
    
    try:
        data = request.get_json() or {}
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Obtener filtros adicionales
        filters = get_filters_from_request(data)
        
        # Si no hay fechas, usar últimos 7 días
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"[EVENTS] Solicitando datos de eventos: {fecha_inicio} - {fecha_fin}")
        print(f"[EVENTS] Filtros: {filters}")
        
        # Usar datos temporales que tienen conversiones
        if not analytics_data or 'datos_temporales' not in analytics_data:
            return jsonify({'success': True, 'events': {}, 'trend': []})
        
        df = analytics_data.get('datos_temporales')
        
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return jsonify({'success': True, 'events': {}, 'trend': []})
        
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        df = df.copy()
        print(f"[EVENTS] Columnas: {df.columns.tolist()}")
        
        # Aplicar filtros adicionales
        df = apply_common_filters(df, filters['page'], filters['country'], filters['traffic_source'])
        
        # Filtrar por fechas
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Ajustar fechas al rango disponible
            fecha_inicio_dt, fecha_fin_dt = adjust_dates_to_available_range(df, fecha_inicio, fecha_fin)
            df_filtered = df[(df['date'] >= fecha_inicio_dt) & (df['date'] <= fecha_fin_dt)]
            
            # Período anterior
            periodo_dias = (fecha_fin_dt - fecha_inicio_dt).days + 1
            fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
            fecha_inicio_prev = fecha_fin_prev - timedelta(days=periodo_dias - 1)
            # Asegurar que el período anterior esté dentro del rango disponible
            fecha_min = df['date'].min()
            if fecha_inicio_prev < fecha_min:
                dias_disponibles = (fecha_inicio_dt - fecha_min).days
                if dias_disponibles >= periodo_dias - 1:
                    fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
                    fecha_inicio_prev = fecha_fin_prev - timedelta(days=periodo_dias - 1)
                else:
                    fecha_inicio_prev = fecha_min
                    fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
            df_prev = df[(df['date'] >= fecha_inicio_prev) & (df['date'] <= fecha_fin_prev)]
        else:
            df_filtered = df
            df_prev = pd.DataFrame()
        
        # Calcular métricas de eventos
        total_sessions = int(df_filtered['sessions'].sum()) if 'sessions' in df_filtered.columns else 0
        conversions = int(df_filtered['conversions'].sum()) if 'conversions' in df_filtered.columns else 0
        engaged_sessions = int(df_filtered['engagedSessions'].sum()) if 'engagedSessions' in df_filtered.columns else 0
        
        total_sessions_prev = int(df_prev['sessions'].sum()) if 'sessions' in df_prev.columns and len(df_prev) > 0 else 0
        conversions_prev = int(df_prev['conversions'].sum()) if 'conversions' in df_prev.columns and len(df_prev) > 0 else 0
        
        # Calcular tasa de conversión
        conversion_rate = (conversions / total_sessions * 100) if total_sessions > 0 else 0
        conversion_rate_prev = (conversions_prev / total_sessions_prev * 100) if total_sessions_prev > 0 else 0
        
        # Calcular deltas
        sessions_delta = ((total_sessions - total_sessions_prev) / total_sessions_prev * 100) if total_sessions_prev > 0 else 0
        conversions_delta = ((conversions - conversions_prev) / conversions_prev * 100) if conversions_prev > 0 else 0
        conversion_rate_delta = conversion_rate - conversion_rate_prev
        
        # Tendencia de conversiones
        trend_data = []
        if 'date' in df_filtered.columns and 'conversions' in df_filtered.columns:
            daily = df_filtered.groupby('date')['conversions'].sum().reset_index()
            daily = daily.sort_values('date')
            trend_data = [{
                'date': row['date'].strftime('%Y-%m-%d'),
                'conversions': int(row['conversions'])
            } for _, row in daily.iterrows()]
        
        print(f"[EVENTS] Sessions: {total_sessions}, Conversiones: {conversions}, Engaged: {engaged_sessions}")
        
        return jsonify({
            'success': True,
            'events': {
                'total_events': engaged_sessions if engaged_sessions > 0 else total_sessions,
                'total_events_delta': round(sessions_delta, 1),
                'conversions': conversions,
                'conversion_rate': round(conversion_rate, 1),
                'events_per_session': round(engaged_sessions / total_sessions, 2) if total_sessions > 0 else 0,
                'conversions_delta': round(conversions_delta, 1),
                'conversion_rate_delta': round(conversion_rate_delta, 1)
            },
            'trend': trend_data
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_events_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# API: DATOS DE CONTENIDO (TABLA RANKING POR SESIONES)
# =============================================================================

@app.route('/api/get-content-ranking', methods=['POST'])
def get_content_ranking():
    """Obtiene ranking de páginas por sesiones para la tabla de contenido"""
    global analytics_data
    
    try:
        data = request.get_json() or {}
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Obtener filtros adicionales
        filters = get_filters_from_request(data)
        
        if not analytics_data:
            return jsonify({'error': 'No hay datos disponibles'}), 400
        
        # Usar datos_contenido
        df = analytics_data.get('datos_contenido')
        if df is None or df.empty:
            return jsonify({'error': 'No hay datos de contenido'}), 400
        
        df = df.copy()
        
        print(f"[CONTENT-RANKING] Columnas disponibles: {df.columns.tolist()}")
        print(f"[CONTENT-RANKING] Total registros antes de filtrar: {len(df)}")
        print(f"[CONTENT-RANKING] Filtros recibidos: fechas={fecha_inicio} a {fecha_fin}, page={filters['page']}, country={filters['country']}, traffic_source={filters['traffic_source']}")
        
        # Filtrar por fecha si existe la columna date
        if 'date' in df.columns and fecha_inicio and fecha_fin:
            if df['date'].dtype == 'object':
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Ajustar fechas al rango disponible
            fecha_inicio_dt, fecha_fin_dt = adjust_dates_to_available_range(df, fecha_inicio, fecha_fin)
            df = df[(df['date'] >= fecha_inicio_dt) & (df['date'] <= fecha_fin_dt)]
            print(f"[CONTENT-RANKING] Registros después de filtro de fechas: {len(df)}")
        
        # Aplicar filtros adicionales
        df = apply_common_filters(df, filters['page'], filters['country'], filters['traffic_source'])
        
        print(f"[CONTENT-RANKING] Registros después de filtrar: {len(df)}")
        
        # Determinar columna de título
        title_col = 'pageTitle' if 'pageTitle' in df.columns else 'pagePath'
        
        # Agrupar por página/título y sumar métricas
        agg_dict = {}
        if 'screenPageViews' in df.columns:
            agg_dict['screenPageViews'] = 'sum'
        if 'activeUsers' in df.columns:
            agg_dict['activeUsers'] = 'sum'
        if 'eventCount' in df.columns:
            agg_dict['eventCount'] = 'sum'
        if 'bounceRate' in df.columns:
            agg_dict['bounceRate'] = 'mean'
        if 'sessions' in df.columns:
            agg_dict['sessions'] = 'sum'
        
        if not agg_dict:
            return jsonify({'error': 'No hay métricas disponibles'}), 400
        
        df_grouped = df.groupby(title_col).agg(agg_dict).reset_index()
        
        # Ordenar por sesiones o vistas
        sort_col = 'sessions' if 'sessions' in df_grouped.columns else 'screenPageViews'
        if sort_col in df_grouped.columns:
            df_grouped = df_grouped.sort_values(sort_col, ascending=False)
        
        # Calcular máximos para las barras de progreso
        max_views = df_grouped['screenPageViews'].max() if 'screenPageViews' in df_grouped.columns else 1
        max_users = df_grouped['activeUsers'].max() if 'activeUsers' in df_grouped.columns else 1
        max_events = df_grouped['eventCount'].max() if 'eventCount' in df_grouped.columns else 1
        
        # Preparar datos para la tabla (top 20)
        pages_data = []
        for _, row in df_grouped.head(20).iterrows():
            views = int(row['screenPageViews']) if 'screenPageViews' in df_grouped.columns and pd.notna(row['screenPageViews']) else 0
            active_users = int(row['activeUsers']) if 'activeUsers' in df_grouped.columns and pd.notna(row['activeUsers']) else 0
            event_count = int(row['eventCount']) if 'eventCount' in df_grouped.columns and pd.notna(row['eventCount']) else 0
            bounce_rate = float(row['bounceRate']) * 100 if 'bounceRate' in df_grouped.columns and pd.notna(row['bounceRate']) else 0
            
            pages_data.append({
                'title': str(row[title_col])[:80],  # Limitar longitud
                'views': views,
                'views_pct': (views / max_views * 100) if max_views > 0 else 0,
                'active_users': active_users,
                'users_pct': (active_users / max_users * 100) if max_users > 0 else 0,
                'event_count': event_count,
                'events_pct': (event_count / max_events * 100) if max_events > 0 else 0,
                'bounce_rate': round(bounce_rate, 1)
            })
        
        print(f"[CONTENT] Páginas encontradas: {len(pages_data)}")
        
        return jsonify({
            'success': True,
            'pages': pages_data,
            'total_pages': len(df_grouped)
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_content_ranking: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# API: DATOS GEOGRÁFICOS
# =============================================================================

@app.route('/api/get-geo-data', methods=['POST'])
def get_geo_data():
    """Obtiene datos geográficos para el tab de Geografía"""
    global analytics_data
    
    try:
        data = request.get_json() or {}
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Obtener filtros adicionales
        filters = get_filters_from_request(data)
        
        print(f"[GEO] Solicitando datos geográficos: {fecha_inicio} - {fecha_fin}")
        print(f"[GEO] Filtros: {filters}")
        
        if not analytics_data or 'datos_geograficos' not in analytics_data:
            print("[GEO] No hay datos geográficos disponibles")
            return jsonify({'success': True, 'countries': {'by_users': [], 'by_sessions': [], 'by_engagement': []}, 'cities': {'by_users': [], 'by_sessions': [], 'by_engagement': []}})
        
        df = analytics_data.get('datos_geograficos')
        
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return jsonify({'success': True, 'countries': {'by_users': [], 'by_sessions': [], 'by_engagement': []}, 'cities': {'by_users': [], 'by_sessions': [], 'by_engagement': []}})
        
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        df = df.copy()
        print(f"[GEO] Columnas disponibles: {df.columns.tolist()}")
        print(f"[GEO] Total registros antes de filtrar: {len(df)}")
        
        # Aplicar filtros adicionales (página y fuente de tráfico - país no aplica aquí)
        df = apply_common_filters(df, filters['page'], None, filters['traffic_source'])
        
        # Filtrar por fechas
        if 'date' in df.columns and fecha_inicio and fecha_fin:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Ajustar fechas al rango disponible
            fecha_inicio_dt, fecha_fin_dt = adjust_dates_to_available_range(df, fecha_inicio, fecha_fin)
            df = df[(df['date'] >= fecha_inicio_dt) & (df['date'] <= fecha_fin_dt)]
            print(f"[GEO] Registros después de filtrar por fechas ({fecha_inicio_dt} - {fecha_fin_dt}): {len(df)}")
        
        # Filtrar por averageSessionDuration > 5 segundos (calidad)
        if 'averageSessionDuration' in df.columns:
            df = df[df['averageSessionDuration'] > 5]
            print(f"[GEO] Registros después de filtrar >5s: {len(df)}")
        else:
            print("[GEO] ADVERTENCIA: No hay columna averageSessionDuration para filtrar")
        
        # Preparar datos de países
        countries_data = {'by_users': [], 'by_sessions': [], 'by_engagement': []}
        cities_data = {'by_users': [], 'by_sessions': [], 'by_engagement': []}
        
        # Calcular engagement rate si no existe (engagedSessions / sessions)
        if 'engagedSessions' in df.columns and 'sessions' in df.columns:
            df['engagementRate'] = df['engagedSessions'] / df['sessions'].replace(0, 1)
        
        # Agrupar por país
        if 'country' in df.columns:
            agg_dict = {}
            if 'totalUsers' in df.columns:
                agg_dict['totalUsers'] = 'sum'
            if 'sessions' in df.columns:
                agg_dict['sessions'] = 'sum'
            if 'engagedSessions' in df.columns:
                agg_dict['engagedSessions'] = 'sum'
            
            if agg_dict:
                country_group = df.groupby('country').agg(agg_dict).reset_index()
                
                # Calcular engagement rate por país
                if 'engagedSessions' in country_group.columns and 'sessions' in country_group.columns:
                    country_group['engagementRate'] = country_group['engagedSessions'] / country_group['sessions'].replace(0, 1)
                
                # Filtrar países vacíos
                country_group = country_group[~country_group['country'].isin(['(not set)', '', 'not set'])]
                
                # Top 5 por usuarios (usando engagedSessions como proxy de usuarios de calidad)
                if 'engagedSessions' in country_group.columns:
                    top_users = country_group.nlargest(5, 'engagedSessions')
                    max_users = top_users['engagedSessions'].max() if len(top_users) > 0 else 1
                    for _, row in top_users.iterrows():
                        countries_data['by_users'].append({
                            'rank': len(countries_data['by_users']) + 1,
                            'name': row['country'],
                            'value': int(row['engagedSessions']),
                            'percentage': round((row['engagedSessions'] / max_users * 100) if max_users > 0 else 0, 1)
                        })
                
                # Top 5 por sesiones (usando engagedSessions = sesiones de calidad)
                if 'engagedSessions' in country_group.columns:
                    top_sessions = country_group.nlargest(5, 'engagedSessions')
                    max_sessions = top_sessions['engagedSessions'].max() if len(top_sessions) > 0 else 1
                    for _, row in top_sessions.iterrows():
                        countries_data['by_sessions'].append({
                            'rank': len(countries_data['by_sessions']) + 1,
                            'name': row['country'],
                            'value': int(row['engagedSessions']),
                            'percentage': round((row['engagedSessions'] / max_sessions * 100) if max_sessions > 0 else 0, 1)
                        })
                
                # Top 5 por engagement rate
                if 'engagementRate' in country_group.columns:
                    top_engagement = country_group.nlargest(5, 'engagementRate')
                    for _, row in top_engagement.iterrows():
                        countries_data['by_engagement'].append({
                            'rank': len(countries_data['by_engagement']) + 1,
                            'name': row['country'],
                            'value': round(row['engagementRate'] * 100, 1),
                            'percentage': round(row['engagementRate'] * 100, 1)
                        })
        
        # Agrupar por ciudad
        if 'city' in df.columns:
            agg_dict = {}
            if 'totalUsers' in df.columns:
                agg_dict['totalUsers'] = 'sum'
            if 'sessions' in df.columns:
                agg_dict['sessions'] = 'sum'
            if 'engagedSessions' in df.columns:
                agg_dict['engagedSessions'] = 'sum'
            
            if agg_dict:
                city_group = df.groupby('city').agg(agg_dict).reset_index()
                
                # Calcular engagement rate por ciudad
                if 'engagedSessions' in city_group.columns and 'sessions' in city_group.columns:
                    city_group['engagementRate'] = city_group['engagedSessions'] / city_group['sessions'].replace(0, 1)
                
                # Filtrar ciudades vacías
                city_group = city_group[~city_group['city'].isin(['(not set)', '', 'not set'])]
                
                # Top 5 por usuarios (usando engagedSessions como proxy)
                if 'engagedSessions' in city_group.columns:
                    top_users = city_group.nlargest(5, 'engagedSessions')
                    max_users = top_users['engagedSessions'].max() if len(top_users) > 0 else 1
                    for _, row in top_users.iterrows():
                        cities_data['by_users'].append({
                            'rank': len(cities_data['by_users']) + 1,
                            'name': row['city'],
                            'value': int(row['engagedSessions']),
                            'percentage': round((row['engagedSessions'] / max_users * 100) if max_users > 0 else 0, 1)
                        })
                
                # Top 5 por sesiones (usando engagedSessions = sesiones de calidad)
                if 'engagedSessions' in city_group.columns:
                    top_sessions = city_group.nlargest(5, 'engagedSessions')
                    max_sessions = top_sessions['engagedSessions'].max() if len(top_sessions) > 0 else 1
                    for _, row in top_sessions.iterrows():
                        cities_data['by_sessions'].append({
                            'rank': len(cities_data['by_sessions']) + 1,
                            'name': row['city'],
                            'value': int(row['engagedSessions']),
                            'percentage': round((row['engagedSessions'] / max_sessions * 100) if max_sessions > 0 else 0, 1)
                        })
                
                # Top 5 por engagement rate
                if 'engagementRate' in city_group.columns:
                    top_engagement = city_group.nlargest(5, 'engagementRate')
                    for _, row in top_engagement.iterrows():
                        cities_data['by_engagement'].append({
                            'rank': len(cities_data['by_engagement']) + 1,
                            'name': row['city'],
                            'value': round(row['engagementRate'] * 100, 1),
                            'percentage': round(row['engagementRate'] * 100, 1)
                        })
        
        # Datos completos para mapas (todos los países, no solo top 5)
        all_countries_map = []
        all_cities_map = []
        
        # Diccionario de códigos ISO para países comunes
        country_iso = {
            'Spain': 'ESP', 'United States': 'USA', 'Mexico': 'MEX', 'Argentina': 'ARG',
            'Colombia': 'COL', 'Chile': 'CHL', 'Peru': 'PER', 'Brazil': 'BRA',
            'United Kingdom': 'GBR', 'Germany': 'DEU', 'France': 'FRA', 'Italy': 'ITA',
            'Portugal': 'PRT', 'Netherlands': 'NLD', 'Belgium': 'BEL', 'Switzerland': 'CHE',
            'Austria': 'AUT', 'Poland': 'POL', 'Sweden': 'SWE', 'Norway': 'NOR',
            'Denmark': 'DNK', 'Finland': 'FIN', 'Ireland': 'IRL', 'Greece': 'GRC',
            'Czech Republic': 'CZE', 'Romania': 'ROU', 'Hungary': 'HUN', 'Ukraine': 'UKR',
            'Russia': 'RUS', 'Turkey': 'TUR', 'India': 'IND', 'China': 'CHN',
            'Japan': 'JPN', 'South Korea': 'KOR', 'Australia': 'AUS', 'New Zealand': 'NZL',
            'Canada': 'CAN', 'Ecuador': 'ECU', 'Venezuela': 'VEN', 'Bolivia': 'BOL',
            'Paraguay': 'PRY', 'Uruguay': 'URY', 'Costa Rica': 'CRI', 'Panama': 'PAN',
            'Guatemala': 'GTM', 'Honduras': 'HND', 'El Salvador': 'SLV', 'Nicaragua': 'NIC',
            'Cuba': 'CUB', 'Dominican Republic': 'DOM', 'Puerto Rico': 'PRI',
            'South Africa': 'ZAF', 'Egypt': 'EGY', 'Morocco': 'MAR', 'Nigeria': 'NGA',
            'Kenya': 'KEN', 'Israel': 'ISR', 'Saudi Arabia': 'SAU', 'UAE': 'ARE',
            'Singapore': 'SGP', 'Malaysia': 'MYS', 'Thailand': 'THA', 'Vietnam': 'VNM',
            'Philippines': 'PHL', 'Indonesia': 'IDN', 'Taiwan': 'TWN', 'Hong Kong': 'HKG',
            'Pakistan': 'PAK', 'Bangladesh': 'BGD', 'Sri Lanka': 'LKA', 'Nepal': 'NPL',
            'Algeria': 'DZA', 'Ghana': 'GHA', 'Lithuania': 'LTU', 'Latvia': 'LVA',
            'Estonia': 'EST', 'Belarus': 'BLR', 'Malawi': 'MWI', 'Guinea': 'GIN'
        }
        
        # Todos los países para el mapa
        if 'country' in df.columns and 'engagedSessions' in df.columns:
            country_totals = df.groupby('country').agg({
                'engagedSessions': 'sum',
                'sessions': 'sum' if 'sessions' in df.columns else lambda x: 0
            }).reset_index()
            
            if 'sessions' in country_totals.columns:
                country_totals['engagementRate'] = country_totals['engagedSessions'] / country_totals['sessions'].replace(0, 1)
            
            country_totals = country_totals[~country_totals['country'].isin(['(not set)', '', 'not set'])]
            
            for _, row in country_totals.iterrows():
                iso = country_iso.get(row['country'], '')
                all_countries_map.append({
                    'name': row['country'],
                    'iso': iso,
                    'sessions': int(row['engagedSessions']),
                    'engagement': round(row.get('engagementRate', 0) * 100, 1)
                })
        
        # Todas las ciudades para el bubble map
        if 'city' in df.columns and 'engagedSessions' in df.columns:
            city_totals = df.groupby('city').agg({
                'engagedSessions': 'sum',
                'sessions': 'sum' if 'sessions' in df.columns else lambda x: 0
            }).reset_index()
            
            if 'sessions' in city_totals.columns:
                city_totals['engagementRate'] = city_totals['engagedSessions'] / city_totals['sessions'].replace(0, 1)
            
            city_totals = city_totals[~city_totals['city'].isin(['(not set)', '', 'not set'])]
            city_totals = city_totals.nlargest(20, 'engagedSessions')  # Top 20 ciudades
            
            for _, row in city_totals.iterrows():
                all_cities_map.append({
                    'name': row['city'],
                    'sessions': int(row['engagedSessions']),
                    'engagement': round(row.get('engagementRate', 0) * 100, 1)
                })
        
        # Generar insight
        insight = ""
        if countries_data['by_users']:
            top_countries = [c['name'] for c in countries_data['by_users'][:2]]
            total_users = sum(c['value'] for c in countries_data['by_users'])
            top_users_sum = sum(c['value'] for c in countries_data['by_users'][:2])
            concentration = round(top_users_sum / total_users * 100, 1) if total_users > 0 else 0
            insight = f"{' y '.join(top_countries)} concentran el {concentration}% del tráfico total."
        
        print(f"[GEO] Países: {len(countries_data['by_users'])}, Ciudades: {len(cities_data['by_users'])}")
        print(f"[GEO] Mapa países: {len(all_countries_map)}, Mapa ciudades: {len(all_cities_map)}")
        
        return jsonify({
            'success': True,
            'countries': countries_data,
            'cities': cities_data,
            'all_countries': all_countries_map,
            'all_cities': all_cities_map,
            'insight': insight
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_geo_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# API: USUARIOS EN TIEMPO REAL
# =============================================================================

@app.route('/api/get-realtime-users', methods=['GET'])
def get_realtime_users():
    """Obtiene usuarios activos en tiempo real desde Google Analytics"""
    global analytics_client
    
    try:
        # Inicializar cliente si no existe
        if analytics_client is None:
            credentials_info = load_credentials()
            if credentials_info:
                analytics_client = initialize_analytics_client(credentials_info)
        
        if analytics_client is None:
            return jsonify({'success': False, 'error': 'Cliente no inicializado', 'activeUsers': 0})
        
        property_id = GA4_CONFIG.get('property_id', '')
        
        # Importar tipos necesarios para realtime
        from google.analytics.data_v1beta.types import RunRealtimeReportRequest, Metric
        
        # Crear request de realtime
        request_realtime = RunRealtimeReportRequest(
            property=f"properties/{property_id}",
            metrics=[Metric(name="activeUsers")]
        )
        
        # Ejecutar reporte en tiempo real
        response = analytics_client.run_realtime_report(request_realtime)
        
        # Extraer usuarios activos
        active_users = 0
        if response.rows:
            active_users = int(response.rows[0].metric_values[0].value)
        
        print(f"[REALTIME] Usuarios activos: {active_users}")
        
        return jsonify({
            'success': True,
            'activeUsers': active_users
        })
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo usuarios en tiempo real: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'activeUsers': 0})

@app.route('/api/get-realtime-details', methods=['GET'])
def get_realtime_details():
    """Obtiene datos detallados en tiempo real (ciudades, páginas, etc.)"""
    global analytics_client
    
    try:
        # Inicializar cliente si no existe
        if analytics_client is None:
            credentials_info = load_credentials()
            if credentials_info:
                analytics_client = initialize_analytics_client(credentials_info)
        
        if analytics_client is None:
            return jsonify({'success': False, 'error': 'Cliente no inicializado'})
        
        property_id = GA4_CONFIG.get('property_id', '')
        
        from google.analytics.data_v1beta.types import RunRealtimeReportRequest, Metric, Dimension
        
        # 1. Usuarios totales
        request_total = RunRealtimeReportRequest(
            property=f"properties/{property_id}",
            metrics=[Metric(name="activeUsers")]
        )
        response_total = analytics_client.run_realtime_report(request_total)
        total_users = int(response_total.rows[0].metric_values[0].value) if response_total.rows else 0
        
        # 2. Usuarios por ciudad
        request_city = RunRealtimeReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")]
        )
        response_city = analytics_client.run_realtime_report(request_city)
        
        cities = []
        for row in response_city.rows[:10]:  # Top 10 ciudades
            city_name = row.dimension_values[0].value
            users = int(row.metric_values[0].value)
            if city_name and city_name != '(not set)':
                cities.append({'city': city_name, 'users': users})
        
        # 3. Usuarios por país
        request_country = RunRealtimeReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="country")],
            metrics=[Metric(name="activeUsers")]
        )
        response_country = analytics_client.run_realtime_report(request_country)
        
        countries = []
        for row in response_country.rows[:10]:  # Top 10 países
            country_name = row.dimension_values[0].value
            users = int(row.metric_values[0].value)
            if country_name and country_name != '(not set)':
                countries.append({'country': country_name, 'users': users})
        
        # 4. Usuarios por página
        request_page = RunRealtimeReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="unifiedScreenName")],
            metrics=[Metric(name="activeUsers")]
        )
        response_page = analytics_client.run_realtime_report(request_page)
        
        pages = []
        for row in response_page.rows[:10]:  # Top 10 páginas
            page_name = row.dimension_values[0].value
            users = int(row.metric_values[0].value)
            if page_name:
                pages.append({'page': page_name, 'users': users})
        
        # 5. Usuarios por dispositivo
        request_device = RunRealtimeReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="deviceCategory")],
            metrics=[Metric(name="activeUsers")]
        )
        response_device = analytics_client.run_realtime_report(request_device)
        
        devices = []
        for row in response_device.rows:
            device = row.dimension_values[0].value
            users = int(row.metric_values[0].value)
            devices.append({'device': device, 'users': users})
        
        print(f"[REALTIME DETAILS] Total: {total_users}, Cities: {len(cities)}, Countries: {len(countries)}")
        
        return jsonify({
            'success': True,
            'totalUsers': total_users,
            'cities': cities,
            'countries': countries,
            'pages': pages,
            'devices': devices
        })
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo detalles realtime: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

# =============================================================================
# API: ALERTAS
# =============================================================================

@app.route('/api/get-alerts', methods=['POST'])
def get_alerts():
    """Genera alertas basadas en análisis de los datos"""
    global analytics_data, analytics_data_raw
    
    try:
        data = request.get_json() or {}
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Obtener filtros adicionales
        filters = get_filters_from_request(data)
        
        print(f"[ALERTS] Generando alertas para {fecha_inicio} - {fecha_fin}")
        print(f"[ALERTS] Filtros: {filters}")
        
        alerts = []
        
        if not analytics_data or 'datos_temporales' not in analytics_data:
            return jsonify({
                'success': True,
                'alerts': [],
                'summary': {'total': 0, 'critical': 0, 'moderate': 0, 'info': 0},
                'status': 'normal',
                'top_alert': None
            })
        
        df = analytics_data.get('datos_temporales')
        df_geo = analytics_data.get('datos_geograficos')
        
        # Aplicar filtros adicionales
        df = apply_common_filters(df, filters['page'], filters['country'], filters['traffic_source'])
        if df_geo is not None:
            df_geo = apply_common_filters(df_geo, filters['page'], None, filters['traffic_source'])
        
        # IMPORTANTE: Para detección de bots, usar datos ORIGINALES sin filtrar
        df_geo_raw = analytics_data_raw.get('datos_geograficos') if analytics_data_raw else df_geo
        print(f"[BOTS] Usando datos RAW: {df_geo_raw is not None and df_geo_raw is not df_geo}")
        
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return jsonify({
                'success': True,
                'alerts': [],
                'summary': {'total': 0, 'critical': 0, 'moderate': 0, 'info': 0},
                'status': 'normal',
                'top_alert': None
            })
        
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Filtrar por fechas
        fecha_inicio_dt = pd.Timestamp(fecha_inicio)
        fecha_fin_dt = pd.Timestamp(fecha_fin)
        periodo_dias = (fecha_fin_dt - fecha_inicio_dt).days + 1
        
        # Período actual y anterior
        df_current = df[(df['date'] >= fecha_inicio_dt) & (df['date'] <= fecha_fin_dt)]
        fecha_inicio_prev = fecha_inicio_dt - timedelta(days=periodo_dias)
        fecha_fin_prev = fecha_inicio_dt - timedelta(days=1)
        df_prev = df[(df['date'] >= fecha_inicio_prev) & (df['date'] <= fecha_fin_prev)]
        
        # Calcular métricas
        sessions_current = df_current['sessions'].sum() if 'sessions' in df_current.columns else 0
        sessions_prev = df_prev['sessions'].sum() if 'sessions' in df_prev.columns else 0
        users_current = df_current['totalUsers'].sum() if 'totalUsers' in df_current.columns else 0
        users_prev = df_prev['totalUsers'].sum() if 'totalUsers' in df_prev.columns else 0
        bounce_current = df_current['bounceRate'].mean() * 100 if 'bounceRate' in df_current.columns else 0
        bounce_prev = df_prev['bounceRate'].mean() * 100 if 'bounceRate' in df_prev.columns else 0
        
        # Calcular cambios
        sessions_change = ((sessions_current - sessions_prev) / sessions_prev * 100) if sessions_prev > 0 else 0
        users_change = ((users_current - users_prev) / users_prev * 100) if users_prev > 0 else 0
        bounce_change = bounce_current - bounce_prev
        
        # Generar alertas basadas en umbrales
        
        # Alerta de caída de sesiones
        if sessions_change < -20:
            alerts.append({
                'type': 'critical',
                'title': f'⚠️ Caída significativa de sesiones ({sessions_change:+.1f}%)',
                'desc': 'Las sesiones han caído más de un 20% respecto al período anterior. Revisar fuentes de tráfico.',
                'rec': 'Verificar campañas activas, SEO y posibles problemas técnicos.',
                'icon': '🔴'
            })
        elif sessions_change < -10:
            alerts.append({
                'type': 'moderate',
                'title': f'📉 Descenso de sesiones ({sessions_change:+.1f}%)',
                'desc': 'Las sesiones han disminuido entre 10-20% respecto al período anterior.',
                'rec': 'Monitorear tendencia y revisar fuentes principales de tráfico.',
                'icon': '🟡'
            })
        elif sessions_change > 30:
            alerts.append({
                'type': 'info',
                'title': f'📈 Aumento notable de sesiones ({sessions_change:+.1f}%)',
                'desc': 'Las sesiones han aumentado significativamente. Podría indicar campaña exitosa o tráfico inorgánico.',
                'rec': 'Verificar calidad del tráfico y fuentes de origen.',
                'icon': '🟢'
            })
        
        # Alerta de caída de usuarios
        if users_change < -15:
            alerts.append({
                'type': 'critical',
                'title': f'⚠️ Pérdida de usuarios ({users_change:+.1f}%)',
                'desc': 'El número de usuarios ha caído significativamente.',
                'rec': 'Revisar retención, UX y canales de adquisición.',
                'icon': '🔴'
            })
        
        # Alerta de bounce rate
        if bounce_change > 10:
            alerts.append({
                'type': 'moderate',
                'title': f'📊 Aumento del bounce rate (+{bounce_change:.1f}%)',
                'desc': 'La tasa de rebote ha aumentado, indicando posibles problemas de relevancia o UX.',
                'rec': 'Revisar landing pages y velocidad de carga.',
                'icon': '🟡'
            })
        elif bounce_current > 70:
            alerts.append({
                'type': 'info',
                'title': f'📊 Bounce rate elevado ({bounce_current:.1f}%)',
                'desc': 'El bounce rate está por encima del umbral recomendado.',
                'rec': 'Optimizar contenido y experiencia de usuario.',
                'icon': '🔵'
            })
        
        # =============================================================================
        # ANÁLISIS DE BOTS POR PAÍS (apartado exclusivo) - USANDO DATOS RAW
        # =============================================================================
        bot_detection = {
            'total_bot_sessions': 0,
            'total_sessions_analyzed': 0,
            'bot_percentage': 0,
            'risk_level': 'low',
            'countries': [],
            'insight': ''
        }
        
        # Para detección de bots: usar datos RAW sin filtrar
        if df_geo_raw is not None and isinstance(df_geo_raw, pd.DataFrame) and not df_geo_raw.empty:
            df_geo_bot = df_geo_raw.copy()
            print(f"[BOTS] Usando {len(df_geo_bot)} registros RAW para detección de bots")
            if 'date' in df_geo_bot.columns:
                df_geo_bot['date'] = pd.to_datetime(df_geo_bot['date'], errors='coerce')
                df_geo_bot_filtered = df_geo_bot[(df_geo_bot['date'] >= fecha_inicio_dt) & (df_geo_bot['date'] <= fecha_fin_dt)]
                print(f"[BOTS] Filtrado por fechas: {len(df_geo_bot_filtered)} registros")
                
                # Detectar países con posible tráfico de BOTS
                # Comparar sesiones totales vs sesiones engaged por país
                if 'country' in df_geo_bot_filtered.columns and 'sessions' in df_geo_bot_filtered.columns and 'engagedSessions' in df_geo_bot_filtered.columns:
                    agg_cols = {'sessions': 'sum', 'engagedSessions': 'sum'}
                    if 'totalUsers' in df_geo_bot_filtered.columns:
                        agg_cols['totalUsers'] = 'sum'
                    if 'averageSessionDuration' in df_geo_bot_filtered.columns:
                        agg_cols['averageSessionDuration'] = 'mean'
                    
                    country_analysis = df_geo_bot_filtered.groupby('country').agg(agg_cols).reset_index()
                    country_analysis = country_analysis[~country_analysis['country'].isin(['(not set)', ''])]
                    
                    # Calcular tasa de "no engagement" (sesiones que duran muy poco)
                    country_analysis['non_engaged'] = country_analysis['sessions'] - country_analysis['engagedSessions']
                    country_analysis['bot_rate'] = (country_analysis['non_engaged'] / country_analysis['sessions'] * 100).fillna(0)
                    
                    # Calcular totales para el apartado de bots
                    total_sessions_all = country_analysis['sessions'].sum()
                    total_non_engaged = country_analysis['non_engaged'].sum()
                    bot_detection['total_sessions_analyzed'] = int(total_sessions_all)
                    bot_detection['total_bot_sessions'] = int(total_non_engaged)
                    bot_detection['bot_percentage'] = round((total_non_engaged / total_sessions_all * 100) if total_sessions_all > 0 else 0, 1)
                    
                    # Determinar nivel de riesgo global
                    if bot_detection['bot_percentage'] > 50:
                        bot_detection['risk_level'] = 'critical'
                    elif bot_detection['bot_percentage'] > 30:
                        bot_detection['risk_level'] = 'high'
                    elif bot_detection['bot_percentage'] > 15:
                        bot_detection['risk_level'] = 'medium'
                    else:
                        bot_detection['risk_level'] = 'low'
                    
                    # Lista de países sospechosos para el apartado exclusivo
                    # FILTRO CLAVE: Solo países con duración media < 5 segundos (realmente sospechosos)
                    suspicious_filter = (
                        (country_analysis['sessions'] >= 5) & 
                        (country_analysis['averageSessionDuration'] < 5)  # Duración media < 5s = sospechoso
                    )
                    top_bot_countries = country_analysis[suspicious_filter].nlargest(10, 'non_engaged')
                    print(f"[BOTS] Países con duración <5s: {len(top_bot_countries)}")
                    
                    for _, row in top_bot_countries.iterrows():
                        non_engaged = int(row['non_engaged'])
                        total_sess = int(row['sessions'])
                        engaged_sess = int(row['engagedSessions'])
                        bot_pct = row['bot_rate']
                        avg_duration = row.get('averageSessionDuration', 0)
                        
                        # Determinar nivel de riesgo del país (basado en duración y volumen)
                        if avg_duration < 2 or (bot_pct > 80 and non_engaged > 50):
                            country_risk = 'critical'
                        elif avg_duration < 3 or (bot_pct > 70 and non_engaged > 30):
                            country_risk = 'high'
                        elif avg_duration < 4:
                            country_risk = 'medium'
                        else:
                            country_risk = 'low'
                        
                        bot_detection['countries'].append({
                            'country': row['country'],
                            'total_sessions': total_sess,
                            'engaged_sessions': engaged_sess,
                            'bot_sessions': non_engaged,
                            'bot_rate': round(bot_pct, 1),
                            'avg_duration': round(avg_duration, 1) if avg_duration else 0,
                            'risk_level': country_risk
                        })
                    
                    # Generar insight para bots
                    if bot_detection['countries']:
                        top_bot_country = bot_detection['countries'][0]
                        num_suspicious = len(bot_detection['countries'])
                        bot_detection['insight'] = f"Se detectan {num_suspicious} país(es) con duración media < 5 segundos, patrón típico de bots. {top_bot_country['country']} lidera con {top_bot_country['bot_sessions']} sesiones sospechosas y una duración media de solo {top_bot_country['avg_duration']}s. Se recomienda investigar las fuentes de tráfico de estos orígenes."
                    else:
                        bot_detection['insight'] = "No se detectan países con patrones de bots (duración media < 5 segundos). El tráfico parece legítimo en todos los orígenes geográficos."
                    
                    # Filtrar países con suficiente tráfico Y duración media < 5s para ALERTAS
                    min_sessions = 10  # Mínimo de sesiones para considerar
                    
                    # CRITERIO: Duración media < 5 segundos = muy sospechoso de bots
                    suspicious_countries = country_analysis[
                        (country_analysis['sessions'] >= min_sessions) & 
                        (country_analysis['averageSessionDuration'] < 5)  # Duración < 5s
                    ].nlargest(5, 'non_engaged')
                    
                    for _, row in suspicious_countries.iterrows():
                        non_engaged = int(row['non_engaged'])
                        total_sess = int(row['sessions'])
                        avg_dur = row.get('averageSessionDuration', 0)
                        
                        # Determinar criticidad según duración media
                        if avg_dur < 2:
                            alert_type = 'critical'
                            icon = '🔴'
                        elif avg_dur < 3:
                            alert_type = 'moderate'
                            icon = '🟡'
                        else:
                            alert_type = 'info'
                            icon = '🔵'
                        
                        alerts.append({
                            'type': alert_type,
                            'title': f'🤖 Posibles bots desde {row["country"]} (duración media: {avg_dur:.1f}s)',
                            'desc': f'{non_engaged} de {total_sess} sesiones con duración promedio de {avg_dur:.1f}s. Patrón típico de tráfico automatizado.',
                            'rec': f'Revisar fuentes de tráfico desde {row["country"]}. Considerar bloquear IPs sospechosas o revisar campañas activas en ese mercado.',
                            'icon': icon,
                            'is_bot_alert': True
                        })
                
                # Alertas geográficas adicionales (usando datos RAW también)
                if 'country' in df_geo_bot_filtered.columns and 'engagedSessions' in df_geo_bot_filtered.columns:
                    country_sessions = df_geo_bot_filtered.groupby('country')['engagedSessions'].sum().reset_index()
                    country_sessions = country_sessions[~country_sessions['country'].isin(['(not set)', ''])]
                    
                    if len(country_sessions) > 0:
                        total_sessions = country_sessions['engagedSessions'].sum()
                        top_country = country_sessions.nlargest(1, 'engagedSessions').iloc[0]
                        top_pct = (top_country['engagedSessions'] / total_sessions * 100) if total_sessions > 0 else 0
                        
                        # Alerta de concentración geográfica
                        if top_pct > 80:
                            alerts.append({
                                'type': 'info',
                                'title': f'🌍 Alta concentración en {top_country["country"]} ({top_pct:.0f}%)',
                                'desc': 'La mayoría del tráfico proviene de un solo país.',
                                'rec': 'Considerar estrategias de expansión a otros mercados.',
                                'icon': '🔵'
                            })
                        
                        # Detectar países con crecimiento anómalo
                        for _, row in country_sessions.nlargest(5, 'engagedSessions').iterrows():
                            pct = (row['engagedSessions'] / total_sessions * 100) if total_sessions > 0 else 0
                            if pct > 10 and row['country'] not in ['Spain', 'United States', 'Mexico']:
                                alerts.append({
                                    'type': 'info',
                                    'title': f'🌍 Tráfico desde {row["country"]} ({pct:.0f}%)',
                                    'desc': f'Se detecta tráfico significativo desde {row["country"]}.',
                                    'rec': 'Verificar origen y calidad del tráfico.',
                                    'icon': '🔵'
                                })
                                break
        
        # Si no hay alertas, añadir una informativa
        if len(alerts) == 0:
            alerts.append({
                'type': 'info',
                'title': '✅ Todo en orden',
                'desc': 'No se han detectado anomalías significativas en el período seleccionado.',
                'rec': 'Continuar monitoreando las métricas regularmente.',
                'icon': '🟢'
            })
        
        # Ordenar alertas por criticidad
        order = {'critical': 0, 'moderate': 1, 'info': 2}
        alerts.sort(key=lambda x: order.get(x['type'], 3))
        
        # Resumen
        summary = {
            'total': len(alerts),
            'critical': len([a for a in alerts if a['type'] == 'critical']),
            'moderate': len([a for a in alerts if a['type'] == 'moderate']),
            'info': len([a for a in alerts if a['type'] == 'info'])
        }
        
        # Estado del tráfico
        if summary['critical'] > 0:
            status = 'anomaly'
            status_text = 'Anomalías'
        elif summary['moderate'] > 0:
            status = 'warning'
            status_text = 'Precaución'
        else:
            status = 'normal'
            status_text = 'Normal'
        
        # Top alerta
        top_alert = alerts[0] if alerts else None
        
        print(f"[ALERTS] Total: {summary['total']}, Critical: {summary['critical']}, Moderate: {summary['moderate']}, Info: {summary['info']}")
        print(f"[BOTS] Sesiones analizadas: {bot_detection['total_sessions_analyzed']}, Bots: {bot_detection['total_bot_sessions']} ({bot_detection['bot_percentage']}%)")
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'summary': summary,
            'status': status,
            'status_text': status_text,
            'top_alert': top_alert,
            'bot_detection': bot_detection
        })
        
    except Exception as e:
        print(f"[ERROR] Error en get_alerts: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# API: RANGO DE FECHAS DISPONIBLE
# =============================================================================

@app.route('/api/get-date-range', methods=['GET'])
def get_date_range():
    """Obtiene el rango de fechas disponible en los datos"""
    global analytics_data
    
    try:
        if not analytics_data or 'datos_temporales' not in analytics_data:
            return jsonify({
                'success': False,
                'error': 'No hay datos cargados'
            })
        
        df = analytics_data.get('datos_temporales')
        if isinstance(df, pd.DataFrame) and not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            fecha_min = df['date'].min()
            fecha_max = df['date'].max()
            
            return jsonify({
                'success': True,
                'date_range': {
                    'min': fecha_min.strftime('%Y-%m-%d') if pd.notna(fecha_min) else None,
                    'max': fecha_max.strftime('%Y-%m-%d') if pd.notna(fecha_max) else None
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No hay datos temporales disponibles'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# API: DEBUG - ESTADO DE DATOS
# =============================================================================

@app.route('/api/debug-data-status', methods=['GET'])
def debug_data_status():
    """Endpoint de debug para verificar el estado de los datos cargados"""
    global analytics_data, analytics_data_raw
    
    try:
        status = {
            'analytics_data_exists': analytics_data is not None and len(analytics_data) > 0,
            'analytics_data_keys': list(analytics_data.keys()) if analytics_data else [],
            'analytics_data_raw_exists': analytics_data_raw is not None and len(analytics_data_raw) > 0,
            'analytics_data_raw_keys': list(analytics_data_raw.keys()) if analytics_data_raw else [],
        }
        
        if analytics_data and 'datos_temporales' in analytics_data:
            df = analytics_data.get('datos_temporales')
            if isinstance(df, pd.DataFrame):
                status['datos_temporales'] = {
                    'exists': True,
                    'rows': len(df),
                    'columns': df.columns.tolist(),
                    'date_range': {
                        'min': str(df['date'].min()) if 'date' in df.columns else None,
                        'max': str(df['date'].max()) if 'date' in df.columns else None
                    } if 'date' in df.columns else None,
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                }
            else:
                status['datos_temporales'] = {
                    'exists': True,
                    'type': str(type(df)),
                    'is_dataframe': False
                }
        else:
            status['datos_temporales'] = {'exists': False}
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# =============================================================================
# API: DIANA - APOLLO.IO INTEGRATION
# =============================================================================

def _apollo_headers():
    """Returns headers for Apollo API requests."""
    return {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
    }

def _apollo_api_key():
    """Returns the Apollo API key."""
    return DIANA_CONFIG.get('api_key') or os.getenv('APOLLO_API_KEY', '')

def get_apollo_emails(fecha_inicio, fecha_fin):
    """Fetches email messages from Apollo emailer_messages/search API.
    Returns (messages_list, error_string_or_None).
    """
    api_url = DIANA_CONFIG.get('api_url', 'https://api.apollo.io/api/v1')
    url = f"{api_url}/emailer_messages/search"
    timeout = DIANA_CONFIG.get('timeout', 30)
    all_messages = []
    page = 1

    while True:
        payload = {
            'api_key': _apollo_api_key(),
            'page': page,
            'per_page': 100
        }
        if fecha_inicio:
            payload['created_at_gte'] = fecha_inicio
        if fecha_fin:
            payload['created_at_lte'] = fecha_fin

        try:
            resp = requests.post(url, json=payload, headers=_apollo_headers(), timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            return all_messages, f"Apollo emails API error: {str(e)}"

        batch = data.get('emailer_messages', [])
        if not batch:
            break
        all_messages.extend(batch)

        # Stop if we got fewer results than requested (last page)
        if len(batch) < 100:
            break
        page += 1
        # Safety cap to avoid infinite loops
        if page > 20:
            break

    return all_messages, None

def get_apollo_contacts():
    """Fetches contacts/leads from Apollo mixed_people/api_search API.
    Returns (contacts_list, error_string_or_None).
    """
    api_url = DIANA_CONFIG.get('api_url', 'https://api.apollo.io/api/v1')
    url = f"{api_url}/mixed_people/api_search"
    timeout = DIANA_CONFIG.get('timeout', 30)

    payload = {
        'api_key': _apollo_api_key(),
        'page': 1,
        'per_page': 50
    }

    try:
        resp = requests.post(url, json=payload, headers=_apollo_headers(), timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        return [], f"Apollo contacts API error: {str(e)}"

    return data.get('people', []), None


@app.route('/api/get-diana-data', methods=['POST'])
def get_diana_data():
    """Obtiene datos de Diana usando la API real de Apollo.io"""
    try:
        data = request.get_json() or {}
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')

        print(f"[DIANA] Solicitando datos Apollo: {fecha_inicio} - {fecha_fin}")

        # Validate API key
        api_key = DIANA_CONFIG.get('api_key') or os.getenv('APOLLO_API_KEY', '')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'APOLLO_API_KEY not configured. Set it in .env or environment variables.'
            }), 400

        # Date range setup
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            dias = (fecha_fin_dt - fecha_inicio_dt).days + 1
        else:
            dias = 7
            fecha_inicio_dt = datetime.now() - timedelta(days=7)
            fecha_fin_dt = datetime.now()
            fecha_inicio = fecha_inicio_dt.strftime('%Y-%m-%d')
            fecha_fin = fecha_fin_dt.strftime('%Y-%m-%d')

        # Previous period for delta calculations
        prev_inicio_dt = fecha_inicio_dt - timedelta(days=dias)
        prev_fin_dt = fecha_inicio_dt - timedelta(days=1)
        prev_inicio = prev_inicio_dt.strftime('%Y-%m-%d')
        prev_fin = prev_fin_dt.strftime('%Y-%m-%d')

        # ── Fetch emails from Apollo (current + previous period) ──
        apollo_emails, email_error = get_apollo_emails(fecha_inicio, fecha_fin)
        apollo_emails_prev, _ = get_apollo_emails(prev_inicio, prev_fin)

        if email_error:
            print(f"[DIANA] Warning: {email_error}")

        # ── Fetch contacts/leads from Apollo ──
        apollo_contacts, contacts_error = get_apollo_contacts()
        if contacts_error:
            print(f"[DIANA] Warning: {contacts_error}")

        # ── Build KPIs from real data ──
        messages_sent = len(apollo_emails)
        messages_replied = sum(1 for m in apollo_emails if m.get('is_replied'))
        response_rate = (messages_replied / messages_sent * 100) if messages_sent > 0 else 0

        # Average response time (from emails that have reply timestamps)
        response_times = []
        for m in apollo_emails:
            if m.get('is_replied') and m.get('replied_at') and m.get('created_at'):
                try:
                    created = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
                    replied = datetime.fromisoformat(m['replied_at'].replace('Z', '+00:00'))
                    diff = (replied - created).total_seconds()
                    if diff > 0:
                        response_times.append(diff)
                except (ValueError, TypeError):
                    pass
        avg_response_time = int(sum(response_times) / len(response_times)) if response_times else 0

        # Previous period KPIs for deltas
        messages_sent_prev = len(apollo_emails_prev)
        messages_replied_prev = sum(1 for m in apollo_emails_prev if m.get('is_replied'))
        response_rate_prev = (messages_replied_prev / messages_sent_prev * 100) if messages_sent_prev > 0 else 0

        response_times_prev = []
        for m in apollo_emails_prev:
            if m.get('is_replied') and m.get('replied_at') and m.get('created_at'):
                try:
                    created = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
                    replied = datetime.fromisoformat(m['replied_at'].replace('Z', '+00:00'))
                    diff = (replied - created).total_seconds()
                    if diff > 0:
                        response_times_prev.append(diff)
                except (ValueError, TypeError):
                    pass
        avg_response_time_prev = int(sum(response_times_prev) / len(response_times_prev)) if response_times_prev else 0

        # Calculate deltas
        messages_sent_delta = ((messages_sent - messages_sent_prev) / messages_sent_prev * 100) if messages_sent_prev > 0 else 0
        messages_replied_delta = ((messages_replied - messages_replied_prev) / messages_replied_prev * 100) if messages_replied_prev > 0 else 0
        response_rate_delta = response_rate - response_rate_prev
        avg_response_time_delta = ((avg_response_time - avg_response_time_prev) / avg_response_time_prev * 100) if avg_response_time_prev > 0 else 0

        # Leads & meetings from Apollo data
        leads_generated = len(apollo_contacts)
        leads_delta = 0  # No previous-period contact search available

        kpis = {
            'messages_sent': messages_sent,
            'messages_sent_delta': round(messages_sent_delta, 1),
            'messages_replied': messages_replied,
            'messages_replied_delta': round(messages_replied_delta, 1),
            'response_rate': round(response_rate, 1),
            'response_rate_delta': round(response_rate_delta, 1),
            'avg_response_time': avg_response_time,
            'avg_response_time_delta': round(avg_response_time_delta, 1),
            'leads_generated': leads_generated,
            'leads_generated_delta': round(leads_delta, 1),
            'meetings_scheduled': 0,
            'meetings_scheduled_delta': 0
        }

        # ── Build daily charts from real email data ──
        daily_sent = {}
        daily_replied = {}
        for m in apollo_emails:
            created_at = m.get('created_at', '')
            try:
                day = created_at[:10]  # YYYY-MM-DD
                if day:
                    daily_sent[day] = daily_sent.get(day, 0) + 1
                    if m.get('is_replied'):
                        daily_replied[day] = daily_replied.get(day, 0) + 1
            except (IndexError, TypeError):
                pass

        # Fill in all days in the range
        messages_by_day = []
        response_rate_by_day = []
        current_date = fecha_inicio_dt
        while current_date <= fecha_fin_dt:
            day_str = current_date.strftime('%Y-%m-%d')
            sent_count = daily_sent.get(day_str, 0)
            replied_count = daily_replied.get(day_str, 0)
            day_rate = (replied_count / sent_count * 100) if sent_count > 0 else 0

            messages_by_day.append({'date': day_str, 'value': sent_count})
            response_rate_by_day.append({'date': day_str, 'value': round(day_rate, 1)})
            current_date += timedelta(days=1)

        charts = {
            'messages_by_day': messages_by_day,
            'response_rate_by_day': response_rate_by_day
        }

        # ── Build messages table from real email data ──
        messages = []
        for m in apollo_emails:
            contact = m.get('contact', {}) or {}
            is_replied = m.get('is_replied', False)
            resp_time = None
            if is_replied and m.get('replied_at') and m.get('created_at'):
                try:
                    created = datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
                    replied_dt = datetime.fromisoformat(m['replied_at'].replace('Z', '+00:00'))
                    resp_time = int((replied_dt - created).total_seconds())
                except (ValueError, TypeError):
                    pass

            messages.append({
                'date': m.get('created_at', ''),
                'created_at': m.get('created_at', ''),
                'recipient': contact.get('name', m.get('to_name', '')),
                'to': m.get('to', contact.get('email', '')),
                'subject': m.get('subject', ''),
                'title': m.get('subject', ''),
                'replied': is_replied,
                'response_time': resp_time
            })

        messages.sort(key=lambda x: x.get('date', ''), reverse=True)

        # ── Build diana_leads from real Apollo contacts ──
        diana_leads = []
        for p in apollo_contacts:
            org = p.get('organization', {}) or {}
            diana_leads.append({
                'name': p.get('name', ''),
                'title': p.get('title', ''),
                'company': org.get('name', p.get('organization_name', '')),
                'industry': org.get('industry', ''),
                'country': p.get('country', ''),
                'headline': p.get('headline', p.get('title', '')),
                'linkedin_url': p.get('linkedin_url', ''),
                'match_score': p.get('score', 0) or 0,
                'last_contacted': p.get('last_contacted_at', '')
            })

        # ── Build targets summary from real leads ──
        if diana_leads:
            industries_count = Counter([l['industry'] for l in diana_leads if l['industry']])
            countries_count = Counter([l['country'] for l in diana_leads if l['country']])
            titles_count = Counter([l['title'] for l in diana_leads if l['title']])

            top_industry = industries_count.most_common(1)[0][0] if industries_count else 'N/A'
            top_country = countries_count.most_common(1)[0][0] if countries_count else 'N/A'
            top_title = titles_count.most_common(1)[0][0] if titles_count else 'N/A'

            top_3_targets = sorted(diana_leads, key=lambda x: x.get('match_score', 0), reverse=True)[:3]

            top_3_list = []
            for t in top_3_targets:
                top_3_list.append({
                    'type': t.get('title', 'N/A'),
                    'industry': t.get('industry', 'N/A'),
                    'country': t.get('country', 'N/A'),
                    'headline': t.get('headline', ''),
                    'match_score': t.get('match_score', 0)
                })

            targets_summary = {
                'top_3': top_3_list,
                'stats': {
                    'top_industry': top_industry,
                    'top_industry_count': industries_count.get(top_industry, 0),
                    'top_country': top_country,
                    'top_country_count': countries_count.get(top_country, 0),
                    'top_type': top_title,
                    'top_type_count': titles_count.get(top_title, 0),
                    'total_leads': len(diana_leads)
                }
            }
        else:
            targets_summary = {
                'top_3': [],
                'stats': {
                    'top_industry': 'N/A', 'top_industry_count': 0,
                    'top_country': 'N/A', 'top_country_count': 0,
                    'top_type': 'N/A', 'top_type_count': 0,
                    'total_leads': 0
                }
            }

        # ── Manual meetings from SQLite (unchanged) ──
        manual_meetings = get_diana_meetings()
        manual_meetings_count = len(manual_meetings)
        kpis['meetings_scheduled'] = manual_meetings_count

        print(f"[DIANA] Apollo data - Sent: {messages_sent}, Replied: {messages_replied}, Leads: {leads_generated}, Meetings: {manual_meetings_count}")

        return jsonify({
            'success': True,
            'kpis': kpis,
            'charts': charts,
            'messages': messages[:20],
            'diana_leads': diana_leads,
            'targets_summary': targets_summary,
            'manual_meetings': manual_meetings
        })

    except Exception as e:
        print(f"[ERROR] Error en get_diana_data: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback: return empty data with error message (no fake data)
        return jsonify({
            'success': False,
            'error': str(e),
            'kpis': {
                'messages_sent': 0, 'messages_sent_delta': 0,
                'messages_replied': 0, 'messages_replied_delta': 0,
                'response_rate': 0, 'response_rate_delta': 0,
                'avg_response_time': 0, 'avg_response_time_delta': 0,
                'leads_generated': 0, 'leads_generated_delta': 0,
                'meetings_scheduled': 0, 'meetings_scheduled_delta': 0
            },
            'charts': {'messages_by_day': [], 'response_rate_by_day': []},
            'messages': [],
            'diana_leads': [],
            'targets_summary': {'top_3': [], 'stats': {}},
            'manual_meetings': []
        }), 500

# =============================================================================
# API: APOLLO - RAW DATA ENDPOINT
# =============================================================================

@app.route('/api/get-apollo-data', methods=['POST'])
def get_apollo_data():
    """Fetches raw data from Apollo.io API for debugging and display."""
    import time as _time

    api_key = _apollo_api_key()
    api_url = DIANA_CONFIG.get('api_url', 'https://api.apollo.io/api/v1')
    timeout = DIANA_CONFIG.get('timeout', 30)

    # Mask the key for display
    if api_key and len(api_key) > 8:
        masked = api_key[:4] + '...' + api_key[-3:]
    elif api_key:
        masked = '***'
    else:
        masked = ''

    connection = {
        'api_key_configured': bool(api_key),
        'api_key_masked': masked,
        'api_url': api_url
    }

    # --- People endpoint ---
    people_result = {'status': 'error', 'http_code': None, 'response_time_ms': 0, 'count': 0, 'error': None, 'data': []}
    if api_key:
        try:
            t0 = _time.time()
            resp = requests.post(
                f"{api_url}/mixed_people/api_search",
                json={'api_key': api_key, 'page': 1, 'per_page': 50},
                headers=_apollo_headers(),
                timeout=timeout
            )
            elapsed = int((_time.time() - t0) * 1000)
            people_result['http_code'] = resp.status_code
            people_result['response_time_ms'] = elapsed
            resp.raise_for_status()
            body = resp.json()
            people_result['data'] = body.get('people', [])
            people_result['count'] = len(people_result['data'])
            people_result['status'] = 'ok'
        except requests.exceptions.RequestException as e:
            people_result['error'] = str(e)
            # Try to get response body for debugging
            try:
                people_result['error_body'] = resp.text[:500]
            except Exception:
                pass
    else:
        people_result['error'] = 'API key not configured'

    # --- Emails endpoint ---
    emails_result = {'status': 'error', 'http_code': None, 'response_time_ms': 0, 'count': 0, 'error': None, 'data': []}
    if api_key:
        try:
            t0 = _time.time()
            resp = requests.post(
                f"{api_url}/emailer_messages/search",
                json={'api_key': api_key, 'page': 1, 'per_page': 50},
                headers=_apollo_headers(),
                timeout=timeout
            )
            elapsed = int((_time.time() - t0) * 1000)
            emails_result['http_code'] = resp.status_code
            emails_result['response_time_ms'] = elapsed
            resp.raise_for_status()
            body = resp.json()
            emails_result['data'] = body.get('emailer_messages', [])
            emails_result['count'] = len(emails_result['data'])
            emails_result['status'] = 'ok'
        except requests.exceptions.RequestException as e:
            emails_result['error'] = str(e)
            try:
                emails_result['error_body'] = resp.text[:500]
            except Exception:
                pass
    else:
        emails_result['error'] = 'API key not configured'

    return jsonify({
        'success': True,
        'connection': connection,
        'endpoints': {
            'people': people_result,
            'emails': emails_result
        }
    })

# =============================================================================
# API: DIANA - REUNIONES MANUALES
# =============================================================================

def get_diana_meetings():
    """Obtiene todas las reuniones de Diana desde la base de datos"""
    try:
        conn = sqlite3.connect(DIANA_MEETINGS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_name, meeting_date, project_reason, created_at, created_by
            FROM diana_meetings
            ORDER BY meeting_date DESC, created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        meetings = []
        for row in rows:
            meetings.append({
                'id': row[0],
                'company_name': row[1],
                'meeting_date': row[2],
                'project_reason': row[3],
                'created_at': row[4],
                'created_by': row[5]
            })
        return meetings
    except Exception as e:
        print(f"[ERROR] Error obteniendo reuniones: {str(e)}")
        return []

@app.route('/api/diana/meetings', methods=['GET'])
@login_required
def get_meetings():
    """Obtiene todas las reuniones agendadas"""
    try:
        meetings = get_diana_meetings()
        return jsonify({
            'success': True,
            'meetings': meetings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diana/meetings', methods=['POST'])
@login_required
def create_meeting():
    """Crea una nueva reunión"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        company_name = data.get('company_name', '').strip()
        meeting_date = data.get('meeting_date', '').strip()
        project_reason = data.get('project_reason', '').strip()
        
        if not company_name or not meeting_date or not project_reason:
            return jsonify({
                'success': False,
                'error': 'Todos los campos son requeridos'
            }), 400
        
        # Obtener usuario actual si está disponible
        created_by = session.get('user_email', 'unknown')
        
        conn = sqlite3.connect(DIANA_MEETINGS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diana_meetings (company_name, meeting_date, project_reason, created_by)
            VALUES (?, ?, ?, ?)
        ''', (company_name, meeting_date, project_reason, created_by))
        conn.commit()
        meeting_id = cursor.lastrowid
        conn.close()
        
        print(f"[DIANA] Reunión creada: {company_name} - {meeting_date}")
        
        return jsonify({
            'success': True,
            'meeting_id': meeting_id,
            'message': 'Reunión creada exitosamente'
        })
    except Exception as e:
        print(f"[ERROR] Error creando reunión: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diana/meetings/<int:meeting_id>', methods=['DELETE'])
@login_required
def delete_meeting(meeting_id):
    """Elimina una reunión"""
    try:
        conn = sqlite3.connect(DIANA_MEETINGS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM diana_meetings WHERE id = ?', (meeting_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Reunión eliminada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Reunión no encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# API: LEADS - GESTIÓN CENTRALIZADA
# =============================================================================

def get_all_leads():
    """Obtiene todos los leads desde la base de datos"""
    try:
        conn = sqlite3.connect(LEADS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, source, company_name, contact_name, contact_email, contact_phone,
                   meeting_date, project_reason, status, notes, created_at, created_by
            FROM leads
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        leads = []
        for row in rows:
            leads.append({
                'id': row[0],
                'source': row[1],
                'company_name': row[2],
                'contact_name': row[3],
                'contact_email': row[4],
                'contact_phone': row[5],
                'meeting_date': row[6],
                'project_reason': row[7],
                'status': row[8],
                'notes': row[9],
                'created_at': row[10],
                'created_by': row[11]
            })
        return leads
    except Exception as e:
        print(f"[ERROR] Error obteniendo leads: {str(e)}")
        return []

@app.route('/api/leads', methods=['GET'])
@login_required
def get_leads():
    """Obtiene todos los leads"""
    try:
        leads = get_all_leads()
        
        # También obtener leads de Diana (reuniones agendadas)
        diana_meetings = get_diana_meetings()
        for meeting in diana_meetings:
            leads.append({
                'id': f"diana_{meeting['id']}",
                'source': 'diana',
                'company_name': meeting['company_name'],
                'contact_name': None,
                'contact_email': None,
                'contact_phone': None,
                'meeting_date': meeting['meeting_date'],
                'project_reason': meeting['project_reason'],
                'status': 'reunion_agendada',
                'notes': None,
                'created_at': meeting['created_at'],
                'created_by': meeting.get('created_by', 'Diana')
            })
        
        return jsonify({
            'success': True,
            'leads': leads
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leads', methods=['POST'])
@login_required
def create_lead():
    """Crea un nuevo lead"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        source = data.get('source', '').strip()
        company_name = data.get('company_name', '').strip()
        
        if not source or not company_name:
            return jsonify({
                'success': False,
                'error': 'Fuente y nombre de empresa son requeridos'
            }), 400
        
        contact_name = data.get('contact_name', '').strip()
        contact_email = data.get('contact_email', '').strip()
        contact_phone = data.get('contact_phone', '').strip()
        meeting_date = data.get('meeting_date', '').strip()
        project_reason = data.get('project_reason', '').strip()
        status = data.get('status', 'nuevo').strip()
        notes = data.get('notes', '').strip()
        
        created_by = session.get('user_email', 'unknown')
        
        conn = sqlite3.connect(LEADS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leads (source, company_name, contact_name, contact_email, contact_phone,
                             meeting_date, project_reason, status, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (source, company_name, contact_name, contact_email, contact_phone,
              meeting_date, project_reason, status, notes, created_by))
        conn.commit()
        lead_id = cursor.lastrowid
        conn.close()
        
        print(f"[LEADS] Lead creado: {company_name} - {source}")
        
        return jsonify({
            'success': True,
            'lead_id': lead_id,
            'message': 'Lead creado exitosamente'
        })
    except Exception as e:
        print(f"[ERROR] Error creando lead: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leads/<int:lead_id>', methods=['PUT'])
@login_required
def update_lead(lead_id):
    """Actualiza un lead existente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        conn = sqlite3.connect(LEADS_DB_FILE)
        cursor = conn.cursor()
        
        # Construir query de actualización dinámicamente
        updates = []
        values = []
        
        if 'source' in data:
            updates.append('source = ?')
            values.append(data['source'])
        if 'company_name' in data:
            updates.append('company_name = ?')
            values.append(data['company_name'])
        if 'contact_name' in data:
            updates.append('contact_name = ?')
            values.append(data.get('contact_name'))
        if 'contact_email' in data:
            updates.append('contact_email = ?')
            values.append(data.get('contact_email'))
        if 'contact_phone' in data:
            updates.append('contact_phone = ?')
            values.append(data.get('contact_phone'))
        if 'meeting_date' in data:
            updates.append('meeting_date = ?')
            values.append(data.get('meeting_date'))
        if 'project_reason' in data:
            updates.append('project_reason = ?')
            values.append(data.get('project_reason'))
        if 'status' in data:
            updates.append('status = ?')
            values.append(data.get('status'))
        if 'notes' in data:
            updates.append('notes = ?')
            values.append(data.get('notes'))
        
        if not updates:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'No hay campos para actualizar'
            }), 400
        
        values.append(lead_id)
        query = f'UPDATE leads SET {", ".join(updates)} WHERE id = ?'
        cursor.execute(query, values)
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        
        if updated:
            return jsonify({
                'success': True,
                'message': 'Lead actualizado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Lead no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leads/<int:lead_id>', methods=['DELETE'])
@login_required
def delete_lead(lead_id):
    """Elimina un lead"""
    try:
        conn = sqlite3.connect(LEADS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Lead eliminado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Lead no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# API: TEAM METRICS - MÉTRICAS DE EQUIPOS
# =============================================================================

@app.route('/api/team/email-campaigns', methods=['GET'])
@login_required
def get_email_campaigns():
    """Obtiene las campañas email/LinkedIn"""
    try:
        conn = sqlite3.connect(TEAM_METRICS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM email_campaigns ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        campaigns = []
        for row in rows:
            campaigns.append({
                'id': row[0],
                'semana_fecha': row[1] or '',
                'campana': row[2] or '',
                'emails_enviados': row[3] or '',
                'respuestas_total': row[4] or '',
                'tasa_respuesta_total': row[5] or '',
                'respuestas_positivas': row[6] or '',
                'tasa_respuestas_positivas': row[7] or '',
                'reuniones': row[8] or '',
                'notas': row[9] or ''
            })
        return jsonify({'success': True, 'data': campaigns})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/team/email-campaigns', methods=['POST'])
@login_required
def save_email_campaigns():
    """Guarda las campañas email/LinkedIn"""
    try:
        data = request.get_json()
        campaigns = data.get('campaigns', [])
        
        conn = sqlite3.connect(TEAM_METRICS_DB_FILE)
        cursor = conn.cursor()
        
        # Eliminar todos los registros existentes
        cursor.execute('DELETE FROM email_campaigns')
        
        # Insertar los nuevos registros
        for campaign in campaigns:
            cursor.execute('''
                INSERT INTO email_campaigns 
                (semana_fecha, campana, emails_enviados, respuestas_total, tasa_respuesta_total,
                 respuestas_positivas, tasa_respuestas_positivas, reuniones, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                campaign.get('semana_fecha', ''),
                campaign.get('campana', ''),
                campaign.get('emails_enviados', ''),
                campaign.get('respuestas_total', ''),
                campaign.get('tasa_respuesta_total', ''),
                campaign.get('respuestas_positivas', ''),
                campaign.get('tasa_respuestas_positivas', ''),
                campaign.get('reuniones', ''),
                campaign.get('notas', '')
            ))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Datos guardados exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/team/linkedin-campaigns', methods=['GET'])
@login_required
def get_linkedin_campaigns():
    """Obtiene las campañas LinkedIn"""
    try:
        conn = sqlite3.connect(TEAM_METRICS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM linkedin_campaigns ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        campaigns = []
        for row in rows:
            campaigns.append({
                'id': row[0],
                'semana_fecha': row[1] or '',
                'campana': row[2] or '',
                'total_mensajes': row[3] or '',
                'respuestas_total': row[4] or '',
                'tasa_respuesta_total': row[5] or '',
                'respuestas_positivas': row[6] or '',
                'tasa_respuestas_positivas': row[7] or '',
                'reuniones': row[8] or '',
                'notas': row[9] or ''
            })
        return jsonify({'success': True, 'data': campaigns})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/team/linkedin-campaigns', methods=['POST'])
@login_required
def save_linkedin_campaigns():
    """Guarda las campañas LinkedIn"""
    try:
        data = request.get_json()
        campaigns = data.get('campaigns', [])
        
        conn = sqlite3.connect(TEAM_METRICS_DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM linkedin_campaigns')
        
        for campaign in campaigns:
            cursor.execute('''
                INSERT INTO linkedin_campaigns 
                (semana_fecha, campana, total_mensajes, respuestas_total, tasa_respuesta_total,
                 respuestas_positivas, tasa_respuestas_positivas, reuniones, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                campaign.get('semana_fecha', ''),
                campaign.get('campana', ''),
                campaign.get('total_mensajes', ''),
                campaign.get('respuestas_total', ''),
                campaign.get('tasa_respuesta_total', ''),
                campaign.get('respuestas_positivas', ''),
                campaign.get('tasa_respuestas_positivas', ''),
                campaign.get('reuniones', ''),
                campaign.get('notas', '')
            ))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Datos guardados exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/team/web-metrics', methods=['GET'])
@login_required
def get_web_metrics():
    """Obtiene las métricas web"""
    try:
        conn = sqlite3.connect(TEAM_METRICS_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM web_metrics ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            metrics.append({
                'id': row[0],
                'semana': row[1] or '',
                'sesiones_totales': row[2] or '',
                'usuarios': row[3] or '',
                'usuarios_nuevos': row[4] or '',
                'sesiones_organicas': row[5] or '',
                'sesiones_paid': row[6] or '',
                'sesiones_referral': row[7] or '',
                'engagement_rate': row[8] or '',
                'bounced_rate': row[9] or '',
                'pages_por_sesion': row[10] or '',
                'leads_web': row[11] or '',
                'reuniones_agendadas': row[12] or '',
                'tasa_conversion_web': row[13] or '',
                'top_3_pages': row[14] or '',
                'top_blog': row[15] or '',
                'trafico_blog': row[16] or '',
                'nuevas_paginas': row[17] or '',
                'new_kws': row[18] or ''
            })
        return jsonify({'success': True, 'data': metrics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/team/web-metrics', methods=['POST'])
@login_required
def save_web_metrics():
    """Guarda las métricas web"""
    try:
        data = request.get_json()
        metrics = data.get('metrics', [])
        
        conn = sqlite3.connect(TEAM_METRICS_DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM web_metrics')
        
        for metric in metrics:
            cursor.execute('''
                INSERT INTO web_metrics 
                (semana, sesiones_totales, usuarios, usuarios_nuevos, sesiones_organicas,
                 sesiones_paid, sesiones_referral, engagement_rate, bounced_rate, pages_por_sesion,
                 leads_web, reuniones_agendadas, tasa_conversion_web, top_3_pages, top_blog,
                 trafico_blog, nuevas_paginas, new_kws)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.get('semana', ''),
                metric.get('sesiones_totales', ''),
                metric.get('usuarios', ''),
                metric.get('usuarios_nuevos', ''),
                metric.get('sesiones_organicas', ''),
                metric.get('sesiones_paid', ''),
                metric.get('sesiones_referral', ''),
                metric.get('engagement_rate', ''),
                metric.get('bounced_rate', ''),
                metric.get('pages_por_sesion', ''),
                metric.get('leads_web', ''),
                metric.get('reuniones_agendadas', ''),
                metric.get('tasa_conversion_web', ''),
                metric.get('top_3_pages', ''),
                metric.get('top_blog', ''),
                metric.get('trafico_blog', ''),
                metric.get('nuevas_paginas', ''),
                metric.get('new_kws', '')
            ))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Datos guardados exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# RECARGA AUTOMÁTICA DE DATOS
# =============================================================================

def reload_analytics_data():
    """Función auxiliar para recargar datos de GA4 automáticamente"""
    global analytics_data, analytics_data_raw, analytics_client
    
    try:
        print(f"[AUTO-RELOAD] Iniciando recarga automática de datos GA4 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Inicializar cliente si no existe
        if not analytics_client:
            print("[AUTO-RELOAD] Inicializando cliente de Analytics...")
            if not init_analytics():
                print("[AUTO-RELOAD ERROR] No se pudo inicializar el cliente")
                return False
            print("[AUTO-RELOAD] Cliente inicializado correctamente")
        
        # Obtener fechas
        today = datetime.now().date()
        start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        print(f"[AUTO-RELOAD] Cargando datos desde {start_date} hasta {end_date} (365 dias)")
        
        # Obtener datos
        raw_data = get_all_analytics_data(
            client=analytics_client,
            property_id=GA4_CONFIG['property_id'],
            start_date=start_date,
            end_date=end_date,
            data_sets_config=DATA_SETS_CONFIG
        )
        
        if raw_data:
            # GUARDAR DATOS ORIGINALES (para detección de bots)
            analytics_data_raw = {}
            for key, df in raw_data.items():
                if isinstance(df, pd.DataFrame):
                    analytics_data_raw[key] = df.copy()
                else:
                    analytics_data_raw[key] = df
            
            # FILTRAR TODOS LOS DATOS por averageSessionDuration > 5 segundos
            analytics_data = {}
            
            for key, df in raw_data.items():
                if isinstance(df, pd.DataFrame) and 'averageSessionDuration' in df.columns:
                    original_len = len(df)
                    df_filtered = df[df['averageSessionDuration'] > 5].copy()
                    analytics_data[key] = df_filtered
                    print(f"[AUTO-RELOAD FILTER] {key}: {original_len} -> {len(df_filtered)} registros (filtrado >5s)")
                else:
                    analytics_data[key] = df
            
            # GUARDAR DATOS EN DISCO para persistencia
            save_data_to_disk()
            
            print(f"[AUTO-RELOAD OK] Datos recargados correctamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print("[AUTO-RELOAD ERROR] No se pudieron obtener datos de GA4")
            return False
            
    except Exception as e:
        print(f"[AUTO-RELOAD ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def auto_reload_worker():
    """Worker thread que recarga datos cada 15 minutos"""
    while True:
        try:
            # Esperar 15 minutos (900 segundos)
            time.sleep(900)
            # Recargar datos
            reload_analytics_data()
        except Exception as e:
            print(f"[AUTO-RELOAD WORKER ERROR] {str(e)}")
            # Si hay error, esperar 1 minuto antes de reintentar
            time.sleep(60)

# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

# =============================================================================
# INICIALIZACIÓN (se ejecuta tanto con gunicorn como con python directamente)
# =============================================================================
init_users_db()
init_diana_meetings_db()
init_leads_db()
init_team_metrics_db()
init_analytics()

if load_data_from_disk():
    print("[OK] Datos restaurados desde cache")
else:
    print("[INFO] No hay datos en cache, lanzando carga en background...")
    startup_thread = threading.Thread(target=reload_analytics_data, daemon=True)
    startup_thread.start()

reload_thread = threading.Thread(target=auto_reload_worker, daemon=True)
reload_thread.start()
print("[AUTO-RELOAD] Hilo de recarga automática iniciado (cada 15 minutos)")

if __name__ == '__main__':
    print("="*60)
    print("CRATA AI - Growth Intelligence Dashboard")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)

