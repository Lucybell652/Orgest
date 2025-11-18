import os
import shutil

def contar_archivos_a_extraer(ruta):
    """Cuenta el total de archivos que serán extraídos"""
    from main import CONFIG  # Importar configuración para modo verbose
    
    total_archivos = 0
    if CONFIG['modo_verbose']:
        print("🔍 CONTANDO ARCHIVOS A EXTRAER...")
    
    for root, dirs, files in os.walk(ruta):
        if root == ruta or "basura" in root:
            continue
        total_archivos += len(files)
        if CONFIG['modo_verbose']:
            print(f"   📁 {root}: {len(files)} archivos")
    
    if CONFIG['modo_verbose']:
        print(f"📊 TOTAL DE ARCHIVOS A EXTRAER: {total_archivos}")
    
    return total_archivos

def extraer_archivos_de_carpetas(ruta):
    """Saca todos los archivos de las subcarpetas (excepto basura) a la raíz"""
    from main import CONFIG  # Importar configuración para modo verbose
    
    if CONFIG['modo_verbose']:
        print("📤 INICIANDO EXTRACCIÓN DE ARCHIVOS...")
        print(f"📁 Ruta raíz: {ruta}")
    else:
        print("📤 Extrayendo archivos de las carpetas...")
    
    carpeta_basura = os.path.join(ruta, "basura")
    archivos_extraidos = 0
    carpetas_procesadas = 0
    
    # Primero contar el total de archivos para el progreso
    if CONFIG['modo_verbose']:
        print("📊 CONTANDO ARCHIVOS...")
    else:
        print("📊 Contando archivos a extraer...")
        
    total_archivos = contar_archivos_a_extraer(ruta)
    
    if CONFIG['modo_verbose']:
        print(f"📊 TOTAL DE ARCHIVOS A EXTRAER: {total_archivos}")
    else:
        print(f"📁 Total de archivos a extraer: {total_archivos}")
    
    print()
    
    archivos_procesados = 0
    
    for root, dirs, files in os.walk(ruta):
        # Ignorar la carpeta basura y la raíz principal
        if root == ruta or "basura" in root:
            continue
            
        carpetas_procesadas += 1
        archivos_en_carpeta = 0
        
        if CONFIG['modo_verbose']:
            print(f"📂 PROCESANDO CARPETA: {os.path.basename(root)}")
        
        for archivo in files:
            archivos_procesados += 1
            ruta_completa = os.path.join(root, archivo)
            
            # Mostrar progreso según el modo
            if CONFIG['modo_verbose']:
                print(f"   📄 Extrayendo: {archivo}")
            else:
                if archivos_procesados % 5 == 0 or archivos_procesados == total_archivos:
                    print(f"📦 Progreso: {archivos_procesados}/{total_archivos} archivos extraídos", end='\r')
            
            try:
                destino = os.path.join(ruta, archivo)
                
                # Si ya existe en destino, renombrar
                contador = 1
                nombre_base, extension = os.path.splitext(archivo)
                destino_temp = destino
                while os.path.exists(destino_temp):
                    destino_temp = os.path.join(ruta, f"{nombre_base}_{contador}{extension}")
                    contador += 1
                
                shutil.move(ruta_completa, destino_temp)
                archivos_extraidos += 1
                archivos_en_carpeta += 1
                
                if CONFIG['modo_verbose']:
                    if destino_temp != destino:
                        print(f"   ✅ Renombrado y extraído: {archivo} → {os.path.basename(destino_temp)}")
                    else:
                        print(f"   ✅ Extraído: {archivo}")
                        
            except Exception as e:
                if CONFIG['modo_verbose']:
                    print(f"   ❌ ERROR extrayendo {archivo}: {e}")
                else:
                    print(f"❌ Error al extraer archivo: {e}")
        
        if CONFIG['modo_verbose'] and archivos_en_carpeta > 0:
            print(f"   📊 Carpeta {os.path.basename(root)}: {archivos_en_carpeta} archivos extraídos")
    
    if not CONFIG['modo_verbose']:
        print()  # Nueva línea después de la barra de progreso
    
    # Eliminar carpetas vacías (excepto basura)
    if CONFIG['modo_verbose']:
        print("🗑️  BUSCANDO CARPETAS VACÍAS...")
    else:
        print("🗑️  Eliminando carpetas vacías...")
        
    carpetas_eliminadas = 0
    carpetas_vacias_encontradas = 0
    
    for root, dirs, files in os.walk(ruta, topdown=False):
        if root != ruta and root != carpeta_basura and not os.listdir(root):
            carpetas_vacias_encontradas += 1
            try:
                os.rmdir(root)
                carpetas_eliminadas += 1
                if CONFIG['modo_verbose']:
                    print(f"   🗑️  Eliminada carpeta vacía: {os.path.basename(root)}")
            except Exception as e:
                if CONFIG['modo_verbose']:
                    print(f"   ⚠️  No se pudo eliminar carpeta {os.path.basename(root)}: {e}")
                else:
                    print(f"⚠️  No se pudo eliminar carpeta {os.path.basename(root)}: {e}")
    
    if CONFIG['modo_verbose']:
        print(f"📊 CARPETAS VACÍAS ENCONTRADAS: {carpetas_vacias_encontradas}")
        print(f"🗑️  CARPETAS ELIMINADAS: {carpetas_eliminadas}")
        print("✅ EXTRACCIÓN COMPLETADA")
    else:
        print(f"📊 Carpetas vacías encontradas: {carpetas_vacias_encontradas}")
        print(f"🗑️  Carpetas eliminadas: {carpetas_eliminadas}")
    
    return {
        'archivos_extraidos': archivos_extraidos,
        'carpetas_procesadas': carpetas_procesadas,
        'carpetas_eliminadas': carpetas_eliminadas,
        'total_archivos': total_archivos
    }

def extraer_archivos_raiz(ruta, modo_automatico=False):
    """
    Función principal para extraer archivos a la raíz.
    
    Args:
        ruta (str): Ruta de la carpeta a procesar
        modo_automatico (bool): Si es True, salta las confirmaciones
        
    Returns:
        dict: Resultados de la extracción para el estado del programa
    """
    from main import CONFIG  # Importar configuración
    
    # Si está en modo automático, saltar confirmación
    if not modo_automatico:
        # Mensaje según el modo
        if CONFIG['modo_verbose']:
            print("📤 PREPARANDO EXTRACCIÓN DE ARCHIVOS...")
            print(f"📁 Ruta: {ruta}")
            print("⚠️  Esta acción moverá todos los archivos de subcarpetas a la carpeta principal")
            input("Presiona Enter para continuar o Ctrl+C para cancelar...")
        else:
            print("📤 Listo para extraer archivos de subcarpetas a la carpeta principal...")
            input("Presiona Enter para continuar o Ctrl+C para cancelar...")
    else:
        # En modo automático, solo mostrar mensaje informativo
        if CONFIG['modo_verbose']:
            print("📤 EJECUTANDO EXTRACCIÓN AUTOMÁTICA...")
        else:
            print("📤 Ejecutando extracción automáticamente...")
    
    resultados_extraccion = extraer_archivos_de_carpetas(ruta)
    
    # Mostrar resumen según el modo
    if CONFIG['modo_verbose']:
        print("\n📊 RESUMEN DETALLADO DE EXTRACCIÓN:")
        print(f"   📤 Archivos extraídos a la raíz: {resultados_extraccion['archivos_extraidos']}/{resultados_extraccion['total_archivos']}")
        print(f"   📂 Carpetas procesadas: {resultados_extraccion['carpetas_procesadas']}")
        print(f"   🗑️  Carpetas vacías eliminadas: {resultados_extraccion['carpetas_eliminadas']}")
        
        if resultados_extraccion['archivos_extraidos'] < resultados_extraccion['total_archivos']:
            no_extraidos = resultados_extraccion['total_archivos'] - resultados_extraccion['archivos_extraidos']
            print(f"   ⚠️  {no_extraidos} archivos no se pudieron extraer")
    else:
        print("\n📊 RESUMEN DE EXTRACCIÓN:")
        print(f"📤 Archivos extraídos a la raíz: {resultados_extraccion['archivos_extraidos']}/{resultados_extraccion['total_archivos']}")
        print(f"📂 Carpetas procesadas: {resultados_extraccion['carpetas_procesadas']}")
        print(f"🗑️  Carpetas vacías eliminadas: {resultados_extraccion['carpetas_eliminadas']}")
        
        if resultados_extraccion['archivos_extraidos'] < resultados_extraccion['total_archivos']:
            print("💡 Algunos archivos no se pudieron extraer. Revisa los mensajes de error.")
    
    return resultados_extraccion