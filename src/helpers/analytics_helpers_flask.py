"""
Google Analytics Helper Functions (Flask Version)
Funciones auxiliares para trabajar con Google Analytics Data API
Sin dependencias de Streamlit
"""

import json
import pandas as pd
import time
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account


def load_credentials():
    """Carga las credenciales desde credentials.json"""
    import os
    
    # Intentar múltiples rutas
    possible_paths = [
        'credentials.json',
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'credentials.json'),
        os.path.join(os.getcwd(), 'credentials.json'),
    ]
    
    for path in possible_paths:
        try:
            abs_path = os.path.abspath(path)
            print(f"[SEARCH] Buscando credentials en: {abs_path}")
            if os.path.exists(abs_path):
                with open(abs_path, 'r') as f:
                    credentials_info = json.load(f)
                print(f"[OK] Credentials encontrado en: {abs_path}")
                return credentials_info
        except Exception as e:
            print(f"[WARN] Error leyendo {path}: {e}")
            continue
    
    # Si no se encontró el archivo, intentar desde variable de entorno
    google_creds_env = os.getenv('GOOGLE_CREDENTIALS')
    if google_creds_env:
        try:
            credentials_info = json.loads(google_creds_env)
            print("[OK] Credentials cargado desde variable de entorno GOOGLE_CREDENTIALS")
            return credentials_info
        except Exception as e:
            print(f"[WARN] Error parseando GOOGLE_CREDENTIALS: {e}")

    print("[ERROR] No se encontro el archivo 'credentials.json' ni la variable GOOGLE_CREDENTIALS")
    return None


def initialize_analytics_client(credentials_info):
    """Inicializa el cliente de Google Analytics"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        client = BetaAnalyticsDataClient(credentials=credentials)
        return client
    except Exception as e:
        print(f"[ERROR] Error al inicializar el cliente de Google Analytics: {str(e)}")
        return None


def get_analytics_data(client, property_id, start_date, end_date, dimensions, metrics):
    """Obtiene datos específicos de Google Analytics"""
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=dim) for dim in dimensions],
            metrics=[Metric(name=metric) for metric in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
        
        response = client.run_report(request)
        return response
    except Exception as e:
        print(f"[ERROR] Error al obtener datos: {str(e)}")
        return None


def get_all_analytics_data(client, property_id, start_date, end_date, data_sets_config):
    """Obtiene TODOS los datos disponibles de Google Analytics con paginación optimizada"""
    
    print(f"[GA4] Iniciando carga de datos para property {property_id}")
    print(f"[GA4] Rango: {start_date} a {end_date}")
    print(f"[GA4] Datasets a cargar: {list(data_sets_config.keys())}")
    
    all_data = {}
    
    for dataset_name, config in data_sets_config.items():
        try:
            print(f"\n[LOAD] Cargando dataset: {dataset_name}")
            print(f"       Dimensions: {config['dimensions']}")
            print(f"       Metrics: {config['metrics']}")
            
            page_size = 10000
            all_rows = []
            offset = 0
            max_retries = 3
            
            while True:
                retry_count = 0
                success = False
                
                while retry_count < max_retries and not success:
                    try:
                        request = RunReportRequest(
                            property=f"properties/{property_id}",
                            dimensions=[Dimension(name=dim) for dim in config["dimensions"]],
                            metrics=[Metric(name=metric) for metric in config["metrics"]],
                            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                            limit=page_size,
                            offset=offset
                        )
                        
                        response = client.run_report(request)
                        success = True
                        
                    except Exception as e:
                        retry_count += 1
                        print(f"       [RETRY] Intento {retry_count}/{max_retries} fallido: {e}")
                        if retry_count >= max_retries:
                            raise e
                        time.sleep(2)
                
                if not response.rows:
                    print(f"       [INFO] Sin mas filas (offset={offset})")
                    break
                
                dim_headers = [d.name for d in response.dimension_headers]
                met_headers = [m.name for m in response.metric_headers]
                
                for row in response.rows:
                    row_data = {}
                    for i, value in enumerate(row.dimension_values):
                        row_data[dim_headers[i]] = value.value
                    for i, value in enumerate(row.metric_values):
                        row_data[met_headers[i]] = value.value
                    
                    all_rows.append(row_data)
                
                print(f"       [DATA] Obtenidas {len(response.rows)} filas (total: {len(all_rows)})")
                
                if response.row_count and offset + page_size >= response.row_count:
                    break
                
                offset += page_size
                time.sleep(0.1)
            
            if all_rows:
                df = pd.DataFrame(all_rows)
                for metric in config["metrics"]:
                    if metric in df.columns:
                        df[metric] = pd.to_numeric(df[metric], errors='coerce')
                all_data[dataset_name] = df
                print(f"       [OK] {dataset_name}: {len(df)} registros")
            else:
                all_data[dataset_name] = pd.DataFrame()
                print(f"       [WARN] {dataset_name}: Sin datos")
            
        except Exception as e:
            print(f"       [ERROR] Error obteniendo {dataset_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            all_data[dataset_name] = pd.DataFrame()
    
    print(f"\n[OK] Carga completada. Datasets: {list(all_data.keys())}")
    return all_data


def run_dynamic_report(client, property_id, start_date, end_date, dimensions, metrics, page_size=100000):
    """Ejecuta una consulta dinámica a GA4 con paginación optimizada"""
    all_rows = []
    offset = 0
    
    while True:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=dim) for dim in dimensions],
            metrics=[Metric(name=metric) for metric in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=page_size,
            offset=offset
        )
        
        response = client.run_report(request)
        
        if not response.rows:
            break
        
        dim_headers = [d.name for d in response.dimension_headers]
        met_headers = [m.name for m in response.metric_headers]
        
        for row in response.rows:
            row_data = {}
            for i, value in enumerate(row.dimension_values):
                row_data[dim_headers[i]] = value.value
            for i, value in enumerate(row.metric_values):
                row_data[met_headers[i]] = value.value
            
            all_rows.append(row_data)
        
        if response.row_count and offset + page_size >= response.row_count:
            break
        
        offset += page_size
    
    if all_rows:
        df = pd.DataFrame(all_rows)
        for metric in metrics:
            if metric in df.columns:
                df[metric] = pd.to_numeric(df[metric], errors='coerce')
        return df
    else:
        return pd.DataFrame()

