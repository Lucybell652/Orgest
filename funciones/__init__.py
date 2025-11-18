"""
Paquete funciones para ORGEST - Organizador de Archivos
Contiene todos los módulos de procesamiento de archivos.
"""

from .duplicados import eliminar_duplicados, verificar_duplicados
from .ordenar import organizar_archivos_carpetas
from .conversiones import convertir_formatos_archivos
from .extraer import extraer_archivos_raiz
from .preprocesador import preprocesar_imagenes
from .limpieza_final import limpiar_carpetas_temporales

__all__ = [
    'eliminar_duplicados',
    'verificar_duplicados', 
    'organizar_archivos_carpetas',
    'convertir_formatos_archivos',
    'extraer_archivos_raiz',
    'preprocesar_imagenes',
    'limpiar_carpetas_temporales'
]