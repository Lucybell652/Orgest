"""
MÓDULO DE DETECCIÓN Y ELIMINACIÓN DE ARCHIVOS DUPLICADOS
Utiliza hash MD5 para identificar archivos idénticos y gestiona su eliminación.
Incluye funciones para escaneo completo y verificación rápida.
"""

import os
import shutil
import hashlib

def calcular_hash_archivo(ruta_archivo):
    """
    Calcula el hash MD5 de un archivo para comparación de contenido.
    
    Args:
        ruta_archivo (str): Ruta completa al archivo a analizar
        
    Returns:
        str or None: Hash MD5 del archivo, None si hay error o "empty_file" si está vacío
    """
    hasher = hashlib.md5()
    try:
        # Verificar que el archivo existe y es accesible
        if not os.path.exists(ruta_archivo):
            return None
            
        # Verificar tamaño del archivo - archivos vacíos se tratan diferente
        file_size = os.path.getsize(ruta_archivo)
        if file_size == 0:
            return "empty_file"  # Identificador especial para archivos vacíos
            
        # Calcular hash leyendo el archivo en bloques para eficiencia
        with open(ruta_archivo, 'rb') as archivo:
            for bloque in iter(lambda: archivo.read(8192), b""):  # Bloques de 8KB
                hasher.update(bloque)
        return hasher.hexdigest()
        
    except Exception as e:
        print(f"❌ Error al calcular hash de {os.path.basename(ruta_archivo)}: {e}")
        return None

def encontrar_duplicados(ruta):
    """
    Escanea recursivamente una carpeta buscando archivos duplicados usando MD5.
    
    Args:
        ruta (str): Ruta de la carpeta a escanear
        
    Returns:
        tuple: (lista_de_duplicados, total_archivos_escaneados)
    """
    from main import CONFIG  # Importar configuración para modo verbose
    
    if CONFIG['modo_verbose']:
        print("🔍 INICIANDO BÚSQUEDA DE DUPLICADOS CON MD5...")
        print(f"📁 Ruta: {ruta}")
    else:
        print("🔍 Buscando archivos duplicados con MD5...")
    
    hashes = {}  # Diccionario para almacenar hashes únicos
    duplicados = []  # Lista de rutas de archivos duplicados
    total_archivos = 0
    archivos_procesados = 0
    
    # Primera pasada: contar archivos totales para mostrar progreso
    if CONFIG['modo_verbose']:
        print("📊 CONTANDO ARCHIVOS...")
    else:
        print("📊 Contando archivos...")
        
    for root, dirs, files in os.walk(ruta):
        if "basura" in root:  # Ignorar carpeta de basura
            continue
        total_archivos += len(files)
    
    if CONFIG['modo_verbose']:
        print(f"📊 TOTAL DE ARCHIVOS A ESCANEAR: {total_archivos}")
    else:
        print(f"📁 Total de archivos a escanear: {total_archivos}")
    
    print()
    
    # Segunda pasada: calcular hashes y detectar duplicados
    for root, dirs, files in os.walk(ruta):
        if "basura" in root:  # Excluir carpeta de basura del análisis
            continue
            
        for archivo in files:
            archivos_procesados += 1
            ruta_completa = os.path.join(root, archivo)
            
            # Mostrar progreso según el modo
            if CONFIG['modo_verbose']:
                if archivos_procesados % 5 == 0 or archivos_procesados == total_archivos:
                    print(f"   📄 Procesando: {archivo} ({archivos_procesados}/{total_archivos})")
            else:
                if archivos_procesados % 10 == 0 or archivos_procesados == total_archivos:
                    print(f"🔍 Progreso: {archivos_procesados}/{total_archivos} - MD5: {len(duplicados)} dup", end='\r')
            
            file_hash = calcular_hash_archivo(ruta_completa)
            
            if file_hash:
                if file_hash in hashes:
                    # Hash repetido encontrado - archivo duplicado
                    if CONFIG['modo_verbose']:
                        print(f"   🔍 DUPLICADO ENCONTRADO: {archivo}")
                    duplicados.append(ruta_completa)
                else:
                    # Hash nuevo - almacenar como referencia
                    hashes[file_hash] = ruta_completa
    
    if not CONFIG['modo_verbose']:
        print()  # Nueva línea después de la barra de progreso
    
    if CONFIG['modo_verbose']:
        print(f"✅ BÚSQUEDA COMPLETADA: {len(duplicados)} duplicados encontrados")
    
    return duplicados, total_archivos

def mover_duplicados_a_basura(ruta, duplicados):
    """
    Mueve archivos duplicados a la carpeta 'basura' de forma segura.
    
    Args:
        ruta (str): Ruta base donde crear la carpeta basura
        duplicados (list): Lista de rutas de archivos duplicados a mover
        
    Returns:
        int: Número de archivos movidos exitosamente
    """
    from main import CONFIG  # Importar configuración para modo verbose
    
    carpeta_basura = os.path.join(ruta, "basura")
    os.makedirs(carpeta_basura, exist_ok=True)  # Crear carpeta si no existe
    
    movidos_exitosos = 0
    total_duplicados = len(duplicados)
    
    if total_duplicados > 0:
        if CONFIG['modo_verbose']:
            print(f"🗑️  MOVIENDO {total_duplicados} ARCHIVOS DUPLICADOS A LA CARPETA BASURA...")
        else:
            print(f"🗑️  Moviendo {total_duplicados} archivos duplicados a la carpeta basura...")
    
    for i, duplicado in enumerate(duplicados, 1):
        try:
            nombre_archivo = os.path.basename(duplicado)
            destino = os.path.join(carpeta_basura, nombre_archivo)
            
            # Si ya existe un archivo con ese nombre en basura, renombrar
            contador = 1
            while os.path.exists(destino):
                nombre, extension = os.path.splitext(nombre_archivo)
                destino = os.path.join(carpeta_basura, f"{nombre}_{contador}{extension}")
                contador += 1
            
            shutil.move(duplicado, destino)
            movidos_exitosos += 1
            
            # Mostrar progreso del movimiento según el modo
            if CONFIG['modo_verbose']:
                print(f"   📦 Movido: {nombre_archivo} → basura/")
            else:
                if i % 5 == 0 or i == total_duplicados:
                    print(f"📦 Progreso: {i}/{total_duplicados} archivos movidos", end='\r')
                
        except Exception as e:
            if CONFIG['modo_verbose']:
                print(f"   ❌ ERROR moviendo {nombre_archivo}: {e}")
            else:
                print(f"❌ Error al mover archivo duplicado: {e}")
    
    if total_duplicados > 0 and not CONFIG['modo_verbose']:
        print()  # Nueva línea después de la barra de progreso
    
    if CONFIG['modo_verbose']:
        print(f"✅ MOVIMIENTO COMPLETADO: {movidos_exitosos}/{total_duplicados} archivos movidos")
    
    return movidos_exitosos

def eliminar_duplicados(ruta, modo_automatico=False):
    """
    Función principal para eliminar duplicados con opción de limpieza inmediata.
    
    Args:
        ruta (str): Ruta de la carpeta a procesar
        modo_automatico (bool): Si es True, no pregunta por eliminar carpeta basura
        
    Returns:
        dict: Resultados del proceso para el estado del programa
    """
    from main import CONFIG  # Importar configuración para modo verbose
    
    if CONFIG['modo_verbose']:
        print("🚀 INICIANDO ELIMINACIÓN DE DUPLICADOS...")
    
    duplicados, total_archivos = encontrar_duplicados(ruta)
    
    if CONFIG['modo_verbose']:
        print(f"📊 RESULTADOS DEL ESCANEO:")
        print(f"   Total de archivos escaneados: {total_archivos}")
        print(f"   Archivos duplicados encontrados: {len(duplicados)}")
    else:
        print(f"📊 Total de archivos escaneados: {total_archivos}")
        print(f"🔍 Archivos duplicados encontrados: {len(duplicados)}")
    
    resultados = {
        'total_archivos': total_archivos,
        'duplicados_encontrados': len(duplicados),
        'duplicados_eliminados': 0,
        'carpeta_basura_eliminada': False
    }
    
    if duplicados:
        movidos = mover_duplicados_a_basura(ruta, duplicados)
        resultados['duplicados_eliminados'] = movidos
        
        if CONFIG['modo_verbose']:
            print(f"🗑️  ARCHIVOS MOVIDOS A BASURA: {movidos}")
        else:
            print(f"🗑️  Archivos movidos a basura: {movidos}")
        
        # Solo preguntar si eliminar la carpeta basura en modo personalizado
        if not modo_automatico:
            carpeta_basura = os.path.join(ruta, "basura")
            if os.path.exists(carpeta_basura):
                print(f"\n📦 Carpeta 'basura' creada con {movidos} archivos duplicados")
                print("Se recomienda que se revise antes de borrarlo.")
                respuesta = input("¿Deseas eliminar la carpeta 'basura' ahora? (s/n): ").strip().lower()
                if respuesta in ('s', 'si', 'sí', 'y', 'yes'):
                    try:
                        shutil.rmtree(carpeta_basura)
                        print("✅ Carpeta 'basura' eliminada exitosamente")
                        resultados['carpeta_basura_eliminada'] = True
                    except Exception as e:
                        print(f"❌ Error al eliminar carpeta 'basura': {e}")
                else:
                    print("✅ Carpeta 'basura' conservada")
    else:
        if CONFIG['modo_verbose']:
            print("✅ NO SE ENCONTRARON ARCHIVOS DUPLICADOS")
        else:
            print("✅ No se encontraron archivos duplicados.")
    
    if CONFIG['modo_verbose']:
        print("✅ PROCESO DE ELIMINACIÓN DE DUPLICADOS COMPLETADO")
    
    return resultados

def verificar_duplicados(ruta, modo_automatico=False):
    """
    Verificación rápida de duplicados, ideal para usar antes del preprocesamiento.
    
    Args:
        ruta (str): Ruta de la carpeta a verificar
        modo_automatico (bool): Si es True, no pregunta por eliminar carpeta basura
        
    Returns:
        dict: Resultados de la verificación para el estado del programa
    """
    from main import CONFIG  # Importar configuración para modo verbose
    
    if CONFIG['modo_verbose']:
        print("🔍 INICIANDO VERIFICACIÓN RÁPIDA DE DUPLICADOS...")
    else:
        print("🔍 Verificación rápida de duplicados...")
        
    duplicados, total_archivos = encontrar_duplicados(ruta)
    
    if CONFIG['modo_verbose']:
        print(f"📊 RESULTADOS DE LA VERIFICACIÓN:")
        print(f"   Total de archivos escaneados: {total_archivos}")
        print(f"   Archivos duplicados encontrados: {len(duplicados)}")
    else:
        print(f"📊 Total de archivos escaneados: {total_archivos}")
        print(f"🔍 Archivos duplicados encontrados: {len(duplicados)}")
    
    resultados = {
        'total_archivos': total_archivos,
        'duplicados_encontrados': len(duplicados),
        'duplicados_eliminados': 0,
        'carpeta_basura_eliminada': False
    }
    
    if duplicados:
        movidos = mover_duplicados_a_basura(ruta, duplicados)
        resultados['duplicados_eliminados'] = movidos
        
        if CONFIG['modo_verbose']:
            print(f"🗑️  ARCHIVOS MOVIDOS A BASURA: {movidos}")
        else:
            print(f"🗑️  Archivos movidos a basura: {movidos}")
        
        # Solo preguntar si eliminar la carpeta basura en modo personalizado
        if not modo_automatico:
            carpeta_basura = os.path.join(ruta, "basura")
            if os.path.exists(carpeta_basura):
                print(f"\n📦 Carpeta 'basura' creada con {movidos} archivos duplicados")
                respuesta = input("¿Deseas eliminar la carpeta 'basura' ahora? (s/n): ").strip().lower()
                if respuesta in ('s', 'si', 'sí', 'y', 'yes'):
                    try:
                        shutil.rmtree(carpeta_basura)
                        print("✅ Carpeta 'basura' eliminada exitosamente")
                        resultados['carpeta_basura_eliminada'] = True
                    except Exception as e:
                        print(f"❌ Error al eliminar carpeta 'basura': {e}")
                else:
                    print("✅ Carpeta 'basura' conservada")
    else:
        if CONFIG['modo_verbose']:
            print("✅ NO SE ENCONTRARON ARCHIVOS DUPLICADOS")
        else:
            print("✅ No se encontraron archivos duplicados.")
    
    if CONFIG['modo_verbose']:
        print("✅ VERIFICACIÓN DE DUPLICADOS COMPLETADA")
    
    return resultados