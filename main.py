"""
ORGEST - ORGANIZADOR DE ARCHIVOS
Archivo principal que maneja la interfaz de usuario y flujo del programa.
Proporciona menús interactivos para modo automático y personalizable.
"""

import os
import sys
from datetime import datetime

# Agregar la carpeta funciones al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'funciones'))

# Importar funciones específicas de cada módulo
try:
    from funciones.duplicados import eliminar_duplicados, verificar_duplicados
    from funciones.ordenar import organizar_archivos_carpetas
    from funciones.conversiones import convertir_formatos_archivos
    from funciones.extraer import extraer_archivos_raiz
    from funciones.preprocesador import preprocesar_imagenes
    from funciones.limpieza_final import limpiar_carpetas_temporales
except ImportError as e:
    print(f"❌ Error: No se pudieron cargar los módulos necesarios: {e}")
    print("Asegúrate de que todos los archivos estén en la carpeta 'funciones'")
    sys.exit(1)

# Configuración centralizada del programa
CONFIG = {
    'mostrar_banners': True,
    'pausa_entre_pasos': True,  # Valor por defecto - se puede cambiar en modo automático
    'modo_verbose': False,
    'limpiar_consola': True
}

class EstadoPrograma:
    """Clase para trackear el progreso y estado del programa"""
    
    def __init__(self):
        self.ruta_actual = None
        self.pasos_completados = []
        self.errores = []
        self.archivos_procesados = 0
        self.archivos_no_procesables = 0
        self.inicio_tiempo = None
        
    def agregar_paso(self, paso, exitoso=True):
        """Registra un paso completado"""
        self.pasos_completados.append({
            'paso': paso,
            'exitoso': exitoso,
            'timestamp': datetime.now()
        })
        
    def agregar_error(self, error, paso):
        """Registra un error específico"""
        self.errores.append({
            'error': str(error),
            'paso': paso,
            'timestamp': datetime.now()
        })
        
    def mostrar_resumen(self):
        """Muestra un resumen completo del progreso"""
        if not CONFIG['mostrar_banners']:
            return
            
        print(f"\n📊 RESUMEN DEL PROCESO:")
        print(f"   Ruta: {self.ruta_actual}")
        print(f"   Pasos completados: {len([p for p in self.pasos_completados if p['exitoso']])}")
        print(f"   Errores: {len(self.errores)}")
        print(f"   Archivos procesados: {self.archivos_procesados}")
        print(f"   Archivos no procesables: {self.archivos_no_procesables}")
        
        if self.errores:
            print(f"\n⚠️  Errores encontrados:")
            for error in self.errores:
                print(f"   - {error['paso']}: {error['error']}")

def limpiar_consola():
    """Limpia la pantalla de la consola según el sistema operativo"""
    if CONFIG['limpiar_consola']:
        os.system('cls' if os.name == 'nt' else 'clear')

def esperar_continuar():
    """Pausa la ejecución esperando que el usuario presione Enter para continuar"""
    if CONFIG['pausa_entre_pasos']:
        input("\nPresiona Enter para continuar...")

def mostrar_banner():
    """Muestra el banner principal del programa Orgest"""
    if CONFIG['mostrar_banners']:
        limpiar_consola()
        print("=" * 60)
        print("            📁 ORGEST - ORGANIZADOR DE ARCHIVOS")
        print("=" * 60)
        print()

def preguntar_pausas_automatico():
    """
    Pregunta al usuario si quiere pausas entre pasos en modo automático.
    
    Returns:
        bool: True si quiere pausas, False si quiere ejecución continua
    """
    limpiar_consola()
    print("⏰ CONFIGURACIÓN DE PAUSAS - MODO AUTOMÁTICO")
    print("=" * 50)
    print("¿Cómo prefieres que se ejecute el modo automático?")
    print()
    print("1. ⏸️  Con pausas entre pasos")
    print("   (Podrás revisar cada paso antes de continuar)")
    print()
    print("2. 🚀 Ejecución continua") 
    print("   (Todo se ejecutará sin interrupciones)")
    print()
    
    while True:
        opcion = input("Selecciona una opción (1-2): ").strip()
        
        if opcion == "1":
            return True
        elif opcion == "2":
            return False
        else:
            print("❌ Opción no válida. Por favor selecciona 1 o 2.")

def obtener_ruta():
    """
    Solicita y valida una ruta de carpeta al usuario.
    
    Returns:
        str or None: Ruta válida o None si el usuario cancela
    """
    limpiar_consola()
    print("📁 INGRESO DE RUTA")
    print("=" * 50)
    
    while True:
        ruta = input("📁 Ingresa la ruta de la carpeta a organizar: ").strip()
        
        if not ruta:
            print("❌ La ruta no puede estar vacía.")
            continue
            
        # Expandir rutas con ~ (usuario)
        ruta = os.path.expanduser(ruta)
        
        if not os.path.exists(ruta):
            print(f"❌ La ruta '{ruta}' no existe.")
            continuar = input("¿Deseas intentar con otra ruta? (s/n): ").strip().lower()
            if continuar not in ('s', 'si', 'sí', 'y', 'yes'):
                return None
        elif not os.path.isdir(ruta):
            print("❌ La ruta especificada no es una carpeta.")
        else:
            return os.path.abspath(ruta)  # Retornar ruta absoluta

def contar_archivos_totales(ruta):
    """
    Cuenta el total de archivos en una carpeta (para estadísticas).
    
    Args:
        ruta (str): Ruta de la carpeta a contar
        
    Returns:
        int: Total de archivos en la carpeta
    """
    total_archivos = 0
    try:
        for root, dirs, files in os.walk(ruta):
            # Excluir carpetas del sistema
            if any(x in root for x in ["basura", "fallos", "sin_edit"]):
                continue
            total_archivos += len(files)
        return total_archivos
    except Exception:
        return 0

def ejecutar_modo_automatico(ruta, estado):
    """
    Ejecuta todos los pasos de organización en secuencia automática.
    
    Args:
        ruta (str): Ruta de la carpeta a organizar
        estado (EstadoPrograma): Instancia para trackear el progreso
    """
    # Preguntar sobre las pausas antes de empezar
    CONFIG['pausa_entre_pasos'] = preguntar_pausas_automatico()
    
    # Contar archivos totales para estadísticas
    archivos_totales = contar_archivos_totales(ruta)
    
    # Ahora pedir la ruta
    limpiar_consola()
    print("🔧 MODO AUTOMÁTICO - EJECUTANDO TODOS LOS PASOS")
    print("=" * 50)
    if not CONFIG['pausa_entre_pasos']:
        print("🚀 Modo: EJECUCIÓN CONTINUA (sin pausas)")
    else:
        print("⏸️  Modo: CON PAUSAS ENTRE PASOS")
    print(f"📊 Archivos totales en la carpeta: {archivos_totales}")
    print()
    
    try:
        # Paso 1: Eliminar archivos duplicados
        print("\n" + "="*50)
        print("PASO 1: BUSCAR Y ELIMINAR DUPLICADOS")
        print("="*50)
        resultados = eliminar_duplicados(ruta, modo_automatico=True)
        estado.agregar_paso("Eliminar duplicados")
        if resultados:
            estado.archivos_procesados += resultados.get('duplicados_eliminados', 0)
        esperar_continuar()
        
        # Paso 2: Organizar archivos en carpetas
        if CONFIG['pausa_entre_pasos']:
            limpiar_consola()
            print("🔧 MODO AUTOMÁTICO - EJECUTANDO TODOS LOS PASOS")
            print("=" * 50)
        print("\n" + "="*50)
        print("PASO 2: ORGANIZAR ARCHIVOS EN CARPETAS")
        print("="*50)
        resultados = organizar_archivos_carpetas(ruta)
        estado.agregar_paso("Organizar archivos en carpetas")
        if resultados:
            estado.archivos_procesados += resultados.get('imagenes_movidas', 0)
            estado.archivos_procesados += resultados.get('videos_movidos', 0)
            estado.archivos_procesados += resultados.get('basura_movida', 0)
        esperar_continuar()
        
        # Paso 3: Convertir formatos de archivo
        if CONFIG['pausa_entre_pasos']:
            limpiar_consola()
            print("🔧 MODO AUTOMÁTICO - EJECUTANDO TODOS LOS PASOS")
            print("=" * 50)
        print("\n" + "="*50)
        print("PASO 3: CONVERTIR ARCHIVOS WEBP Y TS")
        print("="*50)
        resultados = convertir_formatos_archivos(ruta)
        estado.agregar_paso("Convertir formatos de archivo")
        if resultados:
            estado.archivos_procesados += resultados.get('webp_convertidos', 0)
            estado.archivos_procesados += resultados.get('ts_convertidos', 0)
        esperar_continuar()
        
        # Paso 4: Extraer archivos de subcarpetas - SIN CONFIRMACIÓN
        if CONFIG['pausa_entre_pasos']:
            limpiar_consola()
            print("🔧 MODO AUTOMÁTICO - EJECUTANDO TODOS LOS PASOS")
            print("=" * 50)
        print("\n" + "="*50)
        print("PASO 4: EXTRAER ARCHIVOS A LA RAIZ")
        print("="*50)
        print("🔄 Ejecutando extracción automáticamente...")
        resultados = extraer_archivos_raiz(ruta, modo_automatico=True)
        estado.agregar_paso("Extraer archivos a la raíz")
        if resultados:
            estado.archivos_procesados += resultados.get('archivos_extraidos', 0)
        esperar_continuar()
        
        # Paso 5: Verificación final de duplicados
        if CONFIG['pausa_entre_pasos']:
            limpiar_consola()
            print("🔧 MODO AUTOMÁTICO - EJECUTANDO TODOS LOS PASOS")
            print("=" * 50)
        print("\n" + "="*50)
        print("VERIFICACIÓN FINAL: BUSCAR DUPLICADOS")
        print("="*50)
        resultados = verificar_duplicados(ruta, modo_automatico=True)
        estado.agregar_paso("Verificación final de duplicados")
        if resultados:
            estado.archivos_procesados += resultados.get('duplicados_eliminados', 0)
        esperar_continuar()
        
        # Paso 6: Pre-procesamiento de imágenes - SIN CONFIRMACIÓN
        if CONFIG['pausa_entre_pasos']:
            limpiar_consola()
            print("🔧 MODO AUTOMÁTICO - EJECUTANDO TODOS LOS PASOS")
            print("=" * 50)
        print("\n" + "="*50)
        print("PASO 6: PRE-PROCESAMIENTO DE IMÁGENES")
        print("="*50)
        print("🖼️  Ejecutando pre-procesamiento automáticamente...")
        resultados = preprocesar_imagenes(ruta, modo_automatico=True)
        estado.agregar_paso("Pre-procesamiento de imágenes")
        if resultados:
            estado.archivos_procesados += resultados.get('procesadas', 0)
        
        # Paso 7: Limpieza final de carpetas temporales
        if CONFIG['pausa_entre_pasos']:
            limpiar_consola()
        resultados = limpiar_carpetas_temporales(ruta)
        estado.agregar_paso("Limpieza final de carpetas temporales")
        
        # Calcular archivos no procesables
        estado.archivos_no_procesables = archivos_totales - estado.archivos_procesados
        
        limpiar_consola()
        print("\n" + "="*50)
        print("🎉 PROCESO AUTOMÁTICO COMPLETADO EXITOSAMENTE!")
        print("="*50)
        print(f"📊 Estadísticas finales:")
        print(f"   📁 Archivos totales en carpeta: {archivos_totales}")
        print(f"   ✅ Archivos procesados: {estado.archivos_procesados}")
        print(f"   ❌ Archivos no procesables: {estado.archivos_no_procesables}")
        
    except Exception as e:
        estado.agregar_error(e, "Modo automático")
        estado.agregar_paso("Modo automático", exitoso=False)
        print(f"\n❌ Error durante el proceso automático: {e}")

def mostrar_menu_personalizado():
    """Muestra el menú de opciones para el modo personalizable"""
    print("\n🔧 MODO PERSONALIZABLE")
    print("=" * 40)
    print("1. 🗑️  Buscar y eliminar duplicados")
    print("2. 📂 Organizar archivos en carpetas")
    print("3. 🔄 Convertir archivos WEBP y TS")
    print("4. 📤 Extraer archivos a la raíz")
    print("5. 🖼️  Pre-procesamiento de imágenes")
    print("6. 🚀 Ejecutar todos los pasos")
    print("0. ↩️  Volver al menú principal")
    print("=" * 40)

def ejecutar_modo_personalizable(ruta, estado):
    """
    Permite al usuario elegir y ejecutar pasos individuales de organización.
    
    Args:
        ruta (str): Ruta de la carpeta a organizar
        estado (EstadoPrograma): Instancia para trackear el progreso
    """
    while True:
        mostrar_banner()
        print(f"📁 Ruta actual: {ruta}")
        mostrar_menu_personalizado()
        
        try:
            opcion = input("\nSelecciona una opción (0-6): ").strip()
            
            if opcion == "0":
                break
            elif opcion == "1":
                limpiar_consola()
                print("🔧 MODO PERSONALIZABLE")
                print("=" * 50)
                print("\n" + "="*50)
                print("PASO 1: BUSCAR Y ELIMINAR DUPLICADOS")
                print("="*50)
                resultados = eliminar_duplicados(ruta, modo_automatico=False)
                estado.agregar_paso("Eliminar duplicados (personalizado)")
                esperar_continuar()
            elif opcion == "2":
                limpiar_consola()
                print("🔧 MODO PERSONALIZABLE")
                print("=" * 50)
                print("\n" + "="*50)
                print("PASO 2: ORGANIZAR ARCHIVOS EN CARPETAS")
                print("="*50)
                resultados = organizar_archivos_carpetas(ruta)
                estado.agregar_paso("Organizar archivos (personalizado)")
                esperar_continuar()
            elif opcion == "3":
                limpiar_consola()
                print("🔧 MODO PERSONALIZABLE")
                print("=" * 50)
                print("\n" + "="*50)
                print("PASO 3: CONVERTIR ARCHIVOS WEBP Y TS")
                print("="*50)
                resultados = convertir_formatos_archivos(ruta)
                estado.agregar_paso("Convertir formatos (personalizado)")
                esperar_continuar()
            elif opcion == "4":
                limpiar_consola()
                print("🔧 MODO PERSONALIZABLE")
                print("=" * 50)
                print("\n" + "="*50)
                print("PASO 4: EXTRAER ARCHIVOS A LA RAIZ")
                print("="*50)
                resultados = extraer_archivos_raiz(ruta, modo_automatico=False)
                estado.agregar_paso("Extraer archivos (personalizado)")
                esperar_continuar()
            elif opcion == "5":
                limpiar_consola()
                print("🔧 MODO PERSONALIZABLE")
                print("=" * 50)
                resultados = preprocesar_imagenes(ruta, modo_automatico=False)
                estado.agregar_paso("Pre-procesamiento (personalizado)")
            elif opcion == "6":
                # En modo personalizado, ejecutamos el automático pero con pausas activadas
                CONFIG['pausa_entre_pasos'] = True
                ejecutar_modo_automatico(ruta, estado)
                break
            else:
                print("❌ Opción no válida. Por favor selecciona 0-6.")
                esperar_continuar()
                
        except KeyboardInterrupt:
            print("\n\n❌ Operación cancelada por el usuario.")
            estado.agregar_error("Cancelado por usuario", "Modo personalizable")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            estado.agregar_error(e, "Modo personalizable")
            esperar_continuar()

def mostrar_menu_principal():
    """Muestra el menú principal de Orgest con las opciones disponibles"""
    print("¿Cómo deseas usar Orgest?")
    print("=" * 40)
    print("1. 📁 Versión automática")
    print("   (Ejecuta todos los pasos en secuencia)")
    print()
    print("2. 🔧 Versión personalizable") 
    print("   (Elige qué pasos ejecutar)")
    print()
    print("3. ❌ Salir")
    print("=" * 40)

def main():
    """
    Función principal que inicia el programa Orgest.
    Maneja el bucle principal y la navegación entre menús.
    """
    estado = EstadoPrograma()  # Crear instancia para trackear estado
    
    while True:
        mostrar_banner()
        mostrar_menu_principal()
        
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            # Modo automático - ejecuta todos los pasos en secuencia
            # Primero preguntar sobre pausas, luego la ruta
            ruta = obtener_ruta()
            if ruta:
                estado.ruta_actual = ruta
                estado.inicio_tiempo = datetime.now()
                ejecutar_modo_automatico(ruta, estado)
                estado.mostrar_resumen()
                esperar_continuar()
            
        elif opcion == "2":
            # Modo personalizable - usuario elige pasos individuales
            ruta = obtener_ruta()
            if ruta:
                estado.ruta_actual = ruta
                estado.inicio_tiempo = datetime.now()
                ejecutar_modo_personalizable(ruta, estado)
                estado.mostrar_resumen()
            
        elif opcion == "3":
            print("\n👋 ¡Gracias por usar Orgest! Hasta pronto.")
            break
            
        else:
            print("❌ Opción no válida. Por favor selecciona 1-3.")
            esperar_continuar()

if __name__ == "__main__":
    """
    Punto de entrada del programa. Maneja excepciones globales.
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta pronto! Programa interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        input("Presiona Enter para salir...")