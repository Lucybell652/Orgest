import os
import shutil

def es_imagen(archivo):
    """Verifica si un archivo es una imagen (excluyendo webp)"""
    extensiones_imagen = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.ico']
    return any(archivo.lower().endswith(ext) for ext in extensiones_imagen)

def es_video(archivo):
    """Verifica si un archivo es un video (excluyendo ts)"""
    extensiones_video = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg']
    return any(archivo.lower().endswith(ext) for ext in extensiones_video)

def ordenar_archivos(ruta):
    """Ordena archivos en carpetas de imágenes y videos"""
    from main import CONFIG  # Importar configuración para modo verbose
    
    if CONFIG['modo_verbose']:
        print("📂 INICIANDO ORDENAMIENTO DE ARCHIVOS...")
        print(f"📁 Ruta: {ruta}")
    else:
        print("📂 Ordenando archivos en carpetas...")
    
    carpeta_imagenes = os.path.join(ruta, "Imagenes")
    carpeta_videos = os.path.join(ruta, "Videos")
    carpeta_basura = os.path.join(ruta, "basura")
    
    if CONFIG['modo_verbose']:
        print("📁 CREANDO CARPETAS DE DESTINO...")
    
    os.makedirs(carpeta_imagenes, exist_ok=True)
    os.makedirs(carpeta_videos, exist_ok=True)
    os.makedirs(carpeta_basura, exist_ok=True)
    
    if CONFIG['modo_verbose']:
        print(f"   ✅ Carpeta creada/mantenida: {carpeta_imagenes}")
        print(f"   ✅ Carpeta creada/mantenida: {carpeta_videos}")
        print(f"   ✅ Carpeta creada/mantenida: {carpeta_basura}")
    
    contadores = {
        'imagenes': 0,
        'videos': 0,
        'basura': 0,
        'webp': 0,
        'ts': 0
    }
    
    # Primero contar el total de archivos para el progreso
    if CONFIG['modo_verbose']:
        print("📊 CONTANDO ARCHIVOS A ORDENAR...")
    else:
        print("📊 Contando archivos a ordenar...")
        
    total_archivos = 0
    for root, dirs, files in os.walk(ruta):
        if any(x in root for x in ["Imagenes", "Videos", "basura"]):
            continue
        total_archivos += len(files)
    
    if CONFIG['modo_verbose']:
        print(f"📊 TOTAL DE ARCHIVOS A ORDENAR: {total_archivos}")
    else:
        print(f"📁 Total de archivos a ordenar: {total_archivos}")
    
    print()
    
    archivos_procesados = 0
    
    for root, dirs, files in os.walk(ruta):
        # Ignorar las carpetas de destino y basura
        if any(x in root for x in ["Imagenes", "Videos", "basura"]):
            continue
            
        if CONFIG['modo_verbose'] and files:
            print(f"📂 PROCESANDO CARPETA: {os.path.basename(root) if os.path.basename(root) else 'raíz'}")
            
        for archivo in files:
            archivos_procesados += 1
            ruta_completa = os.path.join(root, archivo)
            
            # Mostrar progreso según el modo
            if CONFIG['modo_verbose']:
                print(f"   📄 Procesando: {archivo}")
            else:
                if archivos_procesados % 10 == 0 or archivos_procesados == total_archivos:
                    print(f"📦 Progreso: {archivos_procesados}/{total_archivos} archivos ordenados", end='\r')
            
            # Contar archivos webp y ts que se dejarán para convertir después
            if archivo.lower().endswith('.webp'):
                contadores['webp'] += 1
                if CONFIG['modo_verbose']:
                    print(f"   ⏳ WEBP - Pendiente de conversión: {archivo}")
                continue
            elif archivo.lower().endswith('.ts'):
                contadores['ts'] += 1
                if CONFIG['modo_verbose']:
                    print(f"   ⏳ TS - Pendiente de conversión: {archivo}")
                continue
            
            if es_imagen(archivo):
                destino = os.path.join(carpeta_imagenes, archivo)
                contadores['imagenes'] += 1
                tipo = "🖼️  IMAGEN"
            elif es_video(archivo):
                destino = os.path.join(carpeta_videos, archivo)
                contadores['videos'] += 1
                tipo = "🎥 VIDEO"
            else:
                destino = os.path.join(carpeta_basura, archivo)
                contadores['basura'] += 1
                tipo = "🗑️  BASURA"
            
            # Mover el archivo
            try:
                # Si ya existe en destino, renombrar
                contador = 1
                nombre_base, extension = os.path.splitext(archivo)
                destino_temp = destino
                while os.path.exists(destino_temp):
                    destino_temp = os.path.join(os.path.dirname(destino), f"{nombre_base}_{contador}{extension}")
                    contador += 1
                
                shutil.move(ruta_completa, destino_temp)
                
                if CONFIG['modo_verbose']:
                    if destino_temp != destino:
                        print(f"   ✅ {tipo} (renombrado): {archivo} → {os.path.basename(destino_temp)}")
                    else:
                        print(f"   ✅ {tipo}: {archivo} → {os.path.basename(os.path.dirname(destino))}/")
                        
            except Exception as e:
                if CONFIG['modo_verbose']:
                    print(f"   ❌ ERROR moviendo {archivo}: {e}")
                else:
                    print(f"❌ Error al mover archivo: {e}")
    
    if not CONFIG['modo_verbose']:
        print()  # Nueva línea después de la barra de progreso
    
    if CONFIG['modo_verbose']:
        print("✅ ORDENAMIENTO COMPLETADO")
    
    return contadores

def organizar_archivos_carpetas(ruta):
    """
    Función principal para organizar archivos en carpetas.
    
    Args:
        ruta (str): Ruta de la carpeta a procesar
        
    Returns:
        dict: Resultados del ordenamiento para el estado del programa
    """
    from main import CONFIG  # ✅ CORRECCIÓN: Importar CONFIG aquí también
    
    contadores = ordenar_archivos(ruta)
    
    # Mostrar resumen según el modo
    if CONFIG['modo_verbose']:
        print("\n📊 RESUMEN DETALLADO DE ORDENAMIENTO:")
        print(f"   🖼️  Archivos movidos a 'Imagenes': {contadores['imagenes']}")
        print(f"   🎥 Archivos movidos a 'Videos': {contadores['videos']}")
        print(f"   🗑️  Archivos movidos a 'basura': {contadores['basura']}")
        print(f"   ⏳ Archivos WEBP pendientes de conversión: {contadores['webp']}")
        print(f"   ⏳ Archivos TS pendientes de conversión: {contadores['ts']}")
        
        if contadores['webp'] > 0 or contadores['ts'] > 0:
            print("\n   💡 Los archivos WEBP y TS se procesarán en el siguiente paso de conversiones.")
    else:
        print("\n📊 RESUMEN DE ORDENAMIENTO:")
        print(f"🖼️  Archivos movidos a 'Imagenes': {contadores['imagenes']}")
        print(f"🎥 Archivos movidos a 'Videos': {contadores['videos']}")
        print(f"🗑️  Archivos movidos a 'basura': {contadores['basura']}")
        print(f"⏳ Archivos WEBP pendientes de conversión: {contadores['webp']}")
        print(f"⏳ Archivos TS pendientes de conversión: {contadores['ts']}")
        
        if contadores['webp'] > 0 or contadores['ts'] > 0:
            print("\n💡 Los archivos WEBP y TS se procesarán en el siguiente paso de conversiones.")
    
    # Retornar resultados para el estado del programa
    resultados = {
        'total_archivos_procesados': contadores['imagenes'] + contadores['videos'] + contadores['basura'] + contadores['webp'] + contadores['ts'],
        'imagenes_movidas': contadores['imagenes'],
        'videos_movidos': contadores['videos'],
        'basura_movida': contadores['basura'],
        'webp_pendientes': contadores['webp'],
        'ts_pendientes': contadores['ts']
    }
    
    return resultados