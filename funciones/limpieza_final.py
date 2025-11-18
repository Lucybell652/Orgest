import os
import shutil

def limpiar_consola():
    """Limpia la consola según el sistema operativo"""
    from main import CONFIG  # Importar configuración
    if CONFIG['limpiar_consola']:
        os.system('cls' if os.name == 'nt' else 'clear')

def calcular_tamanio_carpeta(ruta_carpeta):
    """Calcula el tamaño total de una carpeta en MB"""
    from main import CONFIG  # ✅ CORRECCIÓN: Importar CONFIG
    
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(ruta_carpeta):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        tamanio_mb = total_size / (1024 * 1024)  # Convertir a MB
        
        if CONFIG['modo_verbose']:
            print(f"   📏 Tamaño calculado para {os.path.basename(ruta_carpeta)}: {tamanio_mb:.2f} MB")
            
        return tamanio_mb
    except Exception as e:
        if CONFIG['modo_verbose']:
            print(f"   ❌ Error calculando tamaño de {ruta_carpeta}: {e}")
        return 0

def contar_archivos_en_carpeta(ruta_carpeta):
    """Cuenta el número de archivos en una carpeta"""
    from main import CONFIG  # ✅ CORRECCIÓN: Importar CONFIG
    
    try:
        count = 0
        for root, dirs, files in os.walk(ruta_carpeta):
            count += len(files)
        
        if CONFIG['modo_verbose']:
            print(f"   📊 Archivos contados en {os.path.basename(ruta_carpeta)}: {count}")
            
        return count
    except Exception as e:
        if CONFIG['modo_verbose']:
            print(f"   ❌ Error contando archivos en {ruta_carpeta}: {e}")
        return 0

def mostrar_info_carpetas(ruta):
    """Muestra información sobre las carpetas que se pueden eliminar"""
    from main import CONFIG  # ✅ CORRECCIÓN: Importar CONFIG
    
    if CONFIG['modo_verbose']:
        print("🔍 BUSCANDO CARPETAS TEMPORALES...")
    
    carpeta_basura = os.path.join(ruta, "basura")
    carpeta_sin_edit = os.path.join(ruta, "sin_edit")
    
    info = {}
    
    if os.path.exists(carpeta_basura):
        if CONFIG['modo_verbose']:
            print(f"   📁 Carpeta 'basura' encontrada: {carpeta_basura}")
            
        tamanio_basura = calcular_tamanio_carpeta(carpeta_basura)
        archivos_basura = contar_archivos_en_carpeta(carpeta_basura)
        info['basura'] = {
            'ruta': carpeta_basura,
            'tamanio_mb': tamanio_basura,
            'archivos': archivos_basura,
            'existe': True
        }
    else:
        if CONFIG['modo_verbose']:
            print("   ℹ️  Carpeta 'basura' no encontrada")
        info['basura'] = {'existe': False}
    
    if os.path.exists(carpeta_sin_edit):
        if CONFIG['modo_verbose']:
            print(f"   📁 Carpeta 'sin_edit' encontrada: {carpeta_sin_edit}")
            
        tamanio_sin_edit = calcular_tamanio_carpeta(carpeta_sin_edit)
        archivos_sin_edit = contar_archivos_en_carpeta(carpeta_sin_edit)
        info['sin_edit'] = {
            'ruta': carpeta_sin_edit,
            'tamanio_mb': tamanio_sin_edit,
            'archivos': archivos_sin_edit,
            'existe': True
        }
    else:
        if CONFIG['modo_verbose']:
            print("   ℹ️  Carpeta 'sin_edit' no encontrada")
        info['sin_edit'] = {'existe': False}
    
    if CONFIG['modo_verbose']:
        print("✅ BÚSQUEDA DE CARPETAS COMPLETADA")
    
    return info

def eliminar_carpeta_segura(ruta_carpeta, nombre_carpeta):
    """Elimina una carpeta de forma segura con confirmación"""
    from main import CONFIG  # ✅ CORRECCIÓN: Importar CONFIG
    
    try:
        if os.path.exists(ruta_carpeta):
            # Calcular tamaño antes de eliminar para el resumen
            tamanio_mb = calcular_tamanio_carpeta(ruta_carpeta)
            
            if CONFIG['modo_verbose']:
                print(f"   🗑️  Eliminando carpeta: {ruta_carpeta}")
                
            shutil.rmtree(ruta_carpeta)
            
            if CONFIG['modo_verbose']:
                print(f"   ✅ Carpeta '{nombre_carpeta}' eliminada exitosamente")
            else:
                print(f"✅ Carpeta '{nombre_carpeta}' eliminada exitosamente")
                
            return True, tamanio_mb
        else:
            if CONFIG['modo_verbose']:
                print(f"   ℹ️  La carpeta '{nombre_carpeta}' no existe")
            else:
                print(f"ℹ️  La carpeta '{nombre_carpeta}' no existe")
            return False, 0
    except Exception as e:
        if CONFIG['modo_verbose']:
            print(f"   ❌ ERROR eliminando '{nombre_carpeta}': {e}")
        else:
            print(f"❌ Error al eliminar la carpeta '{nombre_carpeta}': {e}")
        return False, 0

def mostrar_info_carpeta_individual(info_carpeta, nombre_carpeta):
    """Muestra información de una carpeta individual con formato limpio"""
    from main import CONFIG  # Importar configuración
    
    if CONFIG['mostrar_banners']:
        limpiar_consola()
        print("🧹 LIMPIEZA FINAL")
        print("="*50)
        print(f"📊 INFORMACIÓN DE CARPETA: {nombre_carpeta.upper()}")
        print("="*50)
    
    if nombre_carpeta == 'basura':
        print(f"\n🗑️  CARPETA '{nombre_carpeta.upper()}':")
        print(f"   📊 Archivos: {info_carpeta['archivos']}")
        print(f"   💾 Tamaño: {info_carpeta['tamanio_mb']:.2f} MB")
        if CONFIG['modo_verbose']:
            print(f"   📍 Ruta: {info_carpeta['ruta']}")
    else:  # sin_edit
        print(f"\n📦 CARPETA '{nombre_carpeta.upper()}':")
        print(f"   📊 Archivos: {info_carpeta['archivos']}")
        print(f"   💾 Tamaño: {info_carpeta['tamanio_mb']:.2f} MB")
        if CONFIG['modo_verbose']:
            print(f"   📍 Ruta: {info_carpeta['ruta']}")
    
    if CONFIG['mostrar_banners']:
        print("\n" + "="*50)

def preguntar_limpieza_simple(ruta):
    """Versión simple con confirmación individual para cada carpeta"""
    from main import CONFIG  # Importar configuración
    
    if CONFIG['modo_verbose']:
        print("🧹 INICIANDO PROCESO DE LIMPIEZA FINAL...")
        print(f"📁 Ruta: {ruta}")
    
    # Limpiar consola al inicio si está configurado
    if CONFIG['mostrar_banners']:
        limpiar_consola()
    
    if CONFIG['mostrar_banners']:
        print("🧹 LIMPIEZA FINAL")
        print("="*50)
        print("Se han detectado las siguientes carpetas temporales:")
        print("="*50)
    
    info_carpetas = mostrar_info_carpetas(ruta)
    
    carpetas_encontradas = False
    espacio_liberado_total = 0
    eliminaciones_realizadas = 0
    resultados = {
        'carpetas_encontradas': 0,
        'carpetas_eliminadas': 0,
        'espacio_liberado_mb': 0,
        'detalles': {}
    }
    
    # Preguntar por carpeta basura
    if info_carpetas['basura']['existe']:
        carpetas_encontradas = True
        resultados['carpetas_encontradas'] += 1
        basura_info = info_carpetas['basura']
        
        # Mostrar información individual de basura
        mostrar_info_carpeta_individual(basura_info, 'basura')
        
        respuesta = input("¿Eliminar la carpeta 'basura'? (s/n): ").strip().lower()
        if respuesta in ('s', 'si', 'sí', 'y', 'yes'):
            if CONFIG['modo_verbose']:
                print("\n🗑️  ELIMINANDO CARPETA 'BASURA'...")
            else:
                print("\n🗑️  Eliminando carpeta 'basura'...")
                
            eliminada, espacio = eliminar_carpeta_segura(basura_info['ruta'], 'basura')
            if eliminada:
                espacio_liberado_total += espacio
                eliminaciones_realizadas += 1
                resultados['carpetas_eliminadas'] += 1
                resultados['espacio_liberado_mb'] += espacio
                resultados['detalles']['basura'] = {
                    'eliminada': True,
                    'espacio_liberado': espacio,
                    'archivos': basura_info['archivos']
                }
                if not CONFIG['modo_verbose']:
                    print(f"💾 Espacio liberado: {espacio:.2f} MB")
                    
            if CONFIG['pausa_entre_pasos']:
                input("\nPresiona Enter para continuar...")
        else:
            if CONFIG['modo_verbose']:
                print("✅ CARPETA 'BASURA' CONSERVADA")
            else:
                print("✅ Carpeta 'basura' conservada")
            resultados['detalles']['basura'] = {
                'eliminada': False,
                'espacio_liberado': 0,
                'archivos': basura_info['archivos']
            }
            if CONFIG['pausa_entre_pasos']:
                input("\nPresiona Enter para continuar...")
    else:
        if CONFIG['modo_verbose']:
            print("\nℹ️  CARPETA 'BASURA' NO ENCONTRADA")
        else:
            print("\nℹ️  Carpeta 'basura' no encontrada")
    
    # Preguntar por carpeta sin_edit
    if info_carpetas['sin_edit']['existe']:
        carpetas_encontradas = True
        resultados['carpetas_encontradas'] += 1
        sin_edit_info = info_carpetas['sin_edit']
        
        # Mostrar información individual de sin_edit
        mostrar_info_carpeta_individual(sin_edit_info, 'sin_edit')
        
        respuesta = input("¿Eliminar la carpeta 'sin_edit'? (s/n): ").strip().lower()
        if respuesta in ('s', 'si', 'sí', 'y', 'yes'):
            if CONFIG['modo_verbose']:
                print("\n📦 ELIMINANDO CARPETA 'SIN_EDIT'...")
            else:
                print("\n📦 Eliminando carpeta 'sin_edit'...")
                
            eliminada, espacio = eliminar_carpeta_segura(sin_edit_info['ruta'], 'sin_edit')
            if eliminada:
                espacio_liberado_total += espacio
                eliminaciones_realizadas += 1
                resultados['carpetas_eliminadas'] += 1
                resultados['espacio_liberado_mb'] += espacio
                resultados['detalles']['sin_edit'] = {
                    'eliminada': True,
                    'espacio_liberado': espacio,
                    'archivos': sin_edit_info['archivos']
                }
                if not CONFIG['modo_verbose']:
                    print(f"💾 Espacio liberado: {espacio:.2f} MB")
                    
            if CONFIG['pausa_entre_pasos']:
                input("\nPresiona Enter para continuar...")
        else:
            if CONFIG['modo_verbose']:
                print("✅ CARPETA 'SIN_EDIT' CONSERVADA")
            else:
                print("✅ Carpeta 'sin_edit' conservada")
            resultados['detalles']['sin_edit'] = {
                'eliminada': False,
                'espacio_liberado': 0,
                'archivos': sin_edit_info['archivos']
            }
            if CONFIG['pausa_entre_pasos']:
                input("\nPresiona Enter para continuar...")
    else:
        if CONFIG['modo_verbose']:
            print("\nℹ️  CARPETA 'SIN_EDIT' NO ENCONTRADA")
        else:
            print("\nℹ️  Carpeta 'sin_edit' no encontrada")
    
    # Mostrar resumen final
    if CONFIG['mostrar_banners']:
        limpiar_consola()
    
    if CONFIG['modo_verbose']:
        print("\n" + "="*50)
        print("📊 RESUMEN DETALLADO DE LIMPIEZA")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("📊 RESUMEN DE LIMPIEZA")
        print("="*50)
    
    if not carpetas_encontradas:
        print("✅ No se encontraron carpetas temporales para eliminar.")
    elif eliminaciones_realizadas > 0:
        if CONFIG['modo_verbose']:
            print(f"🗑️  CARPETAS ELIMINADAS: {eliminaciones_realizadas}")
            print(f"💾 ESPACIO LIBERADO TOTAL: {espacio_liberado_total:.2f} MB")
            print("🎉 ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
        else:
            print(f"🗑️  Carpetas eliminadas: {eliminaciones_realizadas}")
            print(f"💾 Espacio liberado total: {espacio_liberado_total:.2f} MB")
            print("🎉 ¡Limpieza completada exitosamente!")
    else:
        if CONFIG['modo_verbose']:
            print("ℹ️  NO SE ELIMINÓ NINGUNA CARPETA")
            print("💡 Las carpetas temporales se conservaron.")
        else:
            print("ℹ️  No se eliminó ninguna carpeta.")
            print("💡 Las carpetas temporales se conservaron.")
    
    print("="*50)
    
    if CONFIG['modo_verbose']:
        print("✅ PROCESO DE LIMPIEZA FINAL COMPLETADO")
    
    return resultados

def limpiar_carpetas_temporales(ruta):
    """
    Función principal para limpiar carpetas temporales.
    
    Args:
        ruta (str): Ruta de la carpeta a procesar
        
    Returns:
        dict: Resultados de la limpieza para el estado del programa
    """
    # Usar el sistema de preguntas interactivo
    resultados = preguntar_limpieza_simple(ruta)
    return resultados

# Mantener la función original por si se necesita, pero no se usará
def preguntar_limpieza_final(ruta):
    """Función original con menú (no se usará, pero se mantiene por compatibilidad)"""
    return preguntar_limpieza_simple(ruta)