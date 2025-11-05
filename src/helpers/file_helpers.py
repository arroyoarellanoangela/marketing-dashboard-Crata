"""
File Helper Functions
Funciones auxiliares para manejo de archivos y descargas
"""

import zipfile
import io
import pandas as pd
import streamlit as st
from datetime import datetime


def create_zip_file(all_data, start_date, end_date):
    """Crea un archivo ZIP con todos los datos"""
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for dataset_name, df in all_data.items():
                if not df.empty:
                    csv_data = df.to_csv(index=False)
                    zip_file.writestr(f"{dataset_name}_{start_date}_{end_date}.csv", csv_data)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    except Exception as e:
        st.error(f"❌ Error creando archivo ZIP: {str(e)}")
        return None


def download_csv(df, filename):
    """Crea un archivo CSV para descarga"""
    try:
        csv = df.to_csv(index=False)
        return csv
    except Exception as e:
        st.error(f"❌ Error creando CSV: {str(e)}")
        return None


def generate_filename(dataset_name, start_date, end_date, extension="csv"):
    """Genera un nombre de archivo único"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{dataset_name}_{start_date}_{end_date}_{timestamp}.{extension}"


def save_data_to_file(df, filename, file_format="csv"):
    """Guarda datos en un archivo"""
    try:
        if file_format.lower() == "csv":
            return df.to_csv(index=False)
        elif file_format.lower() == "json":
            return df.to_json(orient="records", indent=2)
        elif file_format.lower() == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()
        else:
            st.error(f"❌ Formato de archivo no soportado: {file_format}")
            return None
    except Exception as e:
        st.error(f"❌ Error guardando archivo: {str(e)}")
        return None
