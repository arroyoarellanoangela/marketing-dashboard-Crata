"""
Utility Functions
Funciones de utilidad general para la aplicación
"""

import os
import json
from datetime import datetime, timedelta


def validate_date_range(start_date, end_date):
    """Valida que el rango de fechas sea correcto"""
    if start_date > end_date:
        return False, "La fecha de inicio no puede ser posterior a la fecha de fin"
    
    if end_date > datetime.now().date():
        return False, "La fecha de fin no puede ser posterior a hoy"
    
    days_diff = (end_date - start_date).days
    if days_diff > 365:
        return False, "El rango de fechas no puede ser mayor a 365 días"
    
    return True, "Rango de fechas válido"


def format_number(value):
    """Formatea números para mostrar"""
    try:
        if isinstance(value, (int, float)):
            if value >= 1000000:
                return f"{value/1000000:.1f}M"
            elif value >= 1000:
                return f"{value/1000:.1f}K"
            else:
                return f"{value:,.0f}"
        return str(value)
    except:
        return str(value)


def get_default_date_range(days=30):
    """Obtiene un rango de fechas por defecto"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def check_file_exists(filepath):
    """Verifica si un archivo existe"""
    return os.path.exists(filepath)


def create_directory_if_not_exists(directory):
    """Crea un directorio si no existe"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False


def get_file_size(filepath):
    """Obtiene el tamaño de un archivo en bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0


def format_file_size(size_bytes):
    """Formatea el tamaño de archivo en formato legible"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"
