#!/usr/bin/env python3
"""
Herramienta para encontrar Property ID de Google Analytics 4
Ejecuta este script para listar todas las propiedades disponibles
"""

import json
from google.analytics.admin import AnalyticsAdminServiceClient
from google.oauth2 import service_account

def find_property_ids():
    """Encuentra todos los Property IDs disponibles"""
    try:
        # Cargar credenciales
        with open('credentials.json', 'r') as f:
            credentials_info = json.load(f)
        
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        # Crear cliente
        client = AnalyticsAdminServiceClient(credentials=credentials)
        
        # Listar todas las propiedades
        print("🔍 Buscando propiedades de Google Analytics...")
        print("=" * 50)
        
        request = client.list_properties()
        properties = list(request)
        
        if not properties:
            print("❌ No se encontraron propiedades")
            print("💡 Asegúrate de que tu cuenta de servicio tenga acceso a Google Analytics")
            return
        
        print(f"✅ Se encontraron {len(properties)} propiedades:")
        print()
        
        for i, property in enumerate(properties, 1):
            print(f"📊 Propiedad {i}:")
            print(f"   Nombre: {property.display_name}")
            print(f"   Property ID: {property.name.split('/')[-1]}")
            print(f"   Tipo: {property.property_type}")
            print(f"   Estado: {property.state}")
            print("-" * 30)
        
        print()
        print("💡 Usa el Property ID (número corto) en la aplicación Streamlit")
        
    except FileNotFoundError:
        print("❌ No se encontró el archivo 'credentials.json'")
        print("💡 Coloca tu archivo credentials.json en el directorio raíz")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Asegúrate de que la API de Google Analytics Admin esté habilitada")

if __name__ == "__main__":
    find_property_ids()
