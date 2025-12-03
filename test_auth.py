#!/usr/bin/env python3
"""
Script de diagnóstico para verificar autenticación con Google Analytics
"""

import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account

def test_authentication():
    print("🔍 Verificando autenticación con Google Analytics...")
    print("=" * 60)
    
    # Paso 1: Cargar credenciales
    try:
        with open('credentials.json', 'r') as f:
            creds_info = json.load(f)
        print("✅ Archivo credentials.json cargado correctamente")
        print(f"   📧 Email: {creds_info.get('client_email', 'NO ENCONTRADO')}")
        print(f"   🏢 Proyecto: {creds_info.get('project_id', 'NO ENCONTRADO')}")
    except FileNotFoundError:
        print("❌ No se encontró credentials.json")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error en formato JSON: {e}")
        return
    
    # Paso 2: Crear credenciales
    try:
        credentials = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        print("✅ Credenciales creadas correctamente")
    except Exception as e:
        print(f"❌ Error creando credenciales: {e}")
        return
    
    # Paso 3: Crear cliente
    try:
        client = BetaAnalyticsDataClient(credentials=credentials)
        print("✅ Cliente de Analytics creado")
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return
    
    # Paso 4: Probar consulta simple
    property_id = "381346600"
    print(f"\n🔄 Probando consulta a propiedad {property_id}...")
    
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            limit=1
        )
        
        response = client.run_report(request)
        print("✅ ¡CONEXIÓN EXITOSA!")
        print(f"   📊 Filas obtenidas: {len(response.rows)}")
        
        if response.rows:
            print(f"   📅 Última fecha: {response.rows[0].dimension_values[0].value}")
            print(f"   👥 Sesiones: {response.rows[0].metric_values[0].value}")
        
    except Exception as e:
        print(f"\n❌ ERROR DE AUTENTICACIÓN:")
        print(f"   {str(e)}")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Verifica que el email de la cuenta de servicio tenga acceso en GA")
        print("   2. Verifica que el Property ID sea correcto")
        print("   3. Asegúrate que las credenciales sean del proyecto correcto")

if __name__ == "__main__":
    test_authentication()

