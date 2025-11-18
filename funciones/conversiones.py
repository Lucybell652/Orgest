import os
import shutil
import subprocess
import sys

def verificar_ffmpeg():
    """Verifica si ffmpeg está instalado en el sistema"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def instalar_ffmpeg():
    """Intenta instalar ffmpeg de forma silenciosa o guía al usuario para hacerlo"""
    print("❌ ffmpeg no está instalado en el sistema.")
    print("🔧 Intentando instalar automáticamente (esto puede tomar unos minutos)...")
    
    try:
        # Detectar sistema operativo y intentar instalar
        if sys.platform.startswith('win'):
            # Windows - usar winget o choco
            try:
                resultado = subprocess.run(
                    ['winget', 'install', 'FFmpeg'], 
                    check=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                if resultado.returncode == 0:
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
                
            try:
                resultado = subprocess.run(
                    ['choco', 'install', 'ffmpeg', '-y'], 
                    check=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                if resultado.returncode == 0:
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
                
        elif sys.platform.startswith('linux'):
            try:
                subprocess.run(
                    ['sudo', 'apt', 'update'], 
                    check=True, 
                    capture_output=True, 
                    text=True,
                    timeout=120
                )
                resultado = subprocess.run(
                    ['sudo', 'apt', 'install', '-y', 'ffmpeg'], 
                    check=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                if resultado.returncode == 0:
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
                
        elif sys.platform.startswith('darwin'):
            try:
                resultado = subprocess.run(
                    ['brew', 'install', 'ffmpeg'], 
                    check=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                if resultado.returncode == 0:
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
                
    except Exception as e:
        pass
    
    print("❌ No se pudo instalar automáticamente.")
    print("💡 Por favor instala ffmpeg manualmente:")
    
    if sys.platform.startswith('win'):
        print("   Opción 1: Descarga desde https://ffmpeg.org/download.html")
        print("   Opción 2: Usa chocolatey: 'choco install ffmpeg'")
    elif sys.platform.startswith('linux'):
        print("   Ubuntu/Debian: 'sudo apt install ffmpeg'")
        print("   Fedora: 'sudo dnf install ffmpeg'")
        print("   Arch: 'sudo pacman -S ffmpeg'")
    elif sys.platform.startswith('darwin'):
        print("   'brew install ffmpeg'")
    
    return False

def crear_carpeta_basura(ruta):
    """Crea la carpeta basura si no existe"""
    carpeta_basura = os.path.join(ruta, "basura")
    if not os.path.exists(carpeta_basura):
        os.makedirs(carpeta_basura)
        print(f"📁 Carpeta 'basura' creada en: {carpeta_basura}")
    return carpeta_basura

def convertir_webp_a_png(ruta_webp, carpeta_basura):
    """Convierte archivos WEBP a PNG usando ffmpeg"""
    try:
        from main import CONFIG  # Importar configuración para modo verbose
        
        ruta_png = ruta_webp.replace('.webp', '.png').replace('.WEBP', '.png')
        
        if CONFIG['modo_verbose']:
            print(f"   🔄 Convirtiendo: {os.path.basename(ruta_webp)} → {os.path.basename(ruta_png)}")
        
        comando = ['ffmpeg', '-i', ruta_webp, ruta_png, '-y']
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            try:
                shutil.move(ruta_webp, os.path.join(carpeta_basura, os.path.basename(ruta_webp)))
                if CONFIG['modo_verbose']:
                    print(f"   ✅ Convertido y movido a basura: {os.path.basename(ruta_webp)}")
                return True
            except Exception as e:
                if CONFIG['modo_verbose']:
                    print(f"   ⚠️  Convertido pero no movido a basura: {os.path.basename(ruta_webp)} - {e}")
                return True
        else:
            if CONFIG['modo_verbose']:
                print(f"   ❌ Error en conversión: {os.path.basename(ruta_webp)}")
                print(f"      Error: {resultado.stderr}")
            return False
            
    except Exception as e:
        if CONFIG['modo_verbose']:
            print(f"   ❌ Excepción convirtiendo {os.path.basename(ruta_webp)}: {e}")
        return False

def convertir_ts_a_mp4(ruta_ts, carpeta_basura):
    """Convierte archivos TS a MP4 usando ffmpeg"""
    try:
        from main import CONFIG  # Importar configuración para modo verbose
        
        ruta_mp4 = ruta_ts.replace('.ts', '.mp4').replace('.TS', '.mp4')
        
        if CONFIG['modo_verbose']:
            print(f"   🔄 Convirtiendo: {os.path.basename(ruta_ts)} → {os.path.basename(ruta_mp4)}")
        
        comando = ['ffmpeg', '-i', ruta_ts, '-c', 'copy', ruta_mp4, '-y']
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            try:
                shutil.move(ruta_ts, os.path.join(carpeta_basura, os.path.basename(ruta_ts)))
                if CONFIG['modo_verbose']:
                    print(f"   ✅ Convertido y movido a basura: {os.path.basename(ruta_ts)}")
                return True
            except Exception as e:
                if CONFIG['modo_verbose']:
                    print(f"   ⚠️  Convertido pero no movido a basura: {os.path.basename(ruta_ts)} - {e}")
                return True
        else:
            if CONFIG['modo_verbose']:
                print(f"   ❌ Error en conversión: {os.path.basename(ruta_ts)}")
                print(f"      Error: {resultado.stderr}")
            return False
            
    except Exception as e:
        if CONFIG['modo_verbose']:
            print(f"   ❌ Excepción convirtiendo {os.path.basename(ruta_ts)}: {e}")
        return False

def procesar_conversiones(ruta):
    """Procesa la conversión de archivos webp y ts"""
    from main import CONFIG  # Importar configuración
    
    if CONFIG['modo_verbose']:
        print("🔄 INICIANDO PROCESO DE CONVERSIONES...")
        print(f"📁 Ruta: {ruta}")
    else:
        print("🔄 Procesando conversiones de archivos...")
    
    # Verificar e instalar ffmpeg si es necesario
    if not verificar_ffmpeg():
        print("🔧 ffmpeg no encontrado, se requiere para las conversiones.")
        if instalar_ffmpeg():
            print("✅ ffmpeg instalado correctamente")
        else:
            print("❌ No se puede continuar sin ffmpeg.")
            return {
                'webp_total': 0,
                'webp_convertidos': 0,
                'ts_total': 0,
                'ts_convertidos': 0,
                'error': 'ffmpeg_no_instalado'
            }
    
    # Crear carpeta basura
    carpeta_basura = crear_carpeta_basura(ruta)
    
    archivos_webp = []
    archivos_ts = []
    
    # Buscar archivos webp y ts en toda la ruta
    if CONFIG['modo_verbose']:
        print("🔍 Buscando archivos WEBP y TS...")
    
    for root, dirs, files in os.walk(ruta):
        if "basura" in root:
            continue
            
        for archivo in files:
            if archivo.lower().endswith('.webp'):
                archivos_webp.append(os.path.join(root, archivo))
            elif archivo.lower().endswith('.ts'):
                archivos_ts.append(os.path.join(root, archivo))
    
    total_webp = len(archivos_webp)
    total_ts = len(archivos_ts)
    convertidos_webp = 0
    convertidos_ts = 0
    
    if CONFIG['modo_verbose']:
        print(f"📊 ARCHIVOS ENCONTRADOS:")
        print(f"   WEBP: {total_webp} archivos")
        print(f"   TS: {total_ts} archivos")
    else:
        print(f"📊 Archivos WEBP encontrados: {total_webp}")
        print(f"📊 Archivos TS encontrados: {total_ts}")
    
    print()
    
    # Convertir WEBP a PNG
    if total_webp > 0:
        if CONFIG['modo_verbose']:
            print("🖼️  INICIANDO CONVERSIÓN WEBP A PNG:")
        else:
            print("🖼️  Convirtiendo WEBP a PNG:")
        
        for i, webp in enumerate(archivos_webp, 1):
            if convertir_webp_a_png(webp, carpeta_basura):
                convertidos_webp += 1
            
            if not CONFIG['modo_verbose']:
                print(f"   📊 Progreso: {i}/{total_webp} - Convertidos: {convertidos_webp}", end='\r')
        
        if not CONFIG['modo_verbose']:
            print()
    
    # Convertir TS a MP4
    if total_ts > 0:
        if CONFIG['modo_verbose']:
            print("🎥 INICIANDO CONVERSIÓN TS A MP4:")
        else:
            print("🎥 Convirtiendo TS a MP4:")
        
        for i, ts in enumerate(archivos_ts, 1):
            if convertir_ts_a_mp4(ts, carpeta_basura):
                convertidos_ts += 1
            
            if not CONFIG['modo_verbose']:
                print(f"   📊 Progreso: {i}/{total_ts} - Convertidos: {convertidos_ts}", end='\r')
        
        if not CONFIG['modo_verbose']:
            print()
    
    if CONFIG['modo_verbose']:
        print("✅ PROCESO DE CONVERSIONES COMPLETADO")
    
    return {
        'webp_total': total_webp,
        'webp_convertidos': convertidos_webp,
        'ts_total': total_ts,
        'ts_convertidos': convertidos_ts
    }

def convertir_formatos_archivos(ruta):
    """
    Función principal para convertir archivos WEBP y TS.
    
    Args:
        ruta (str): Ruta de la carpeta a procesar
    """
    resultados = procesar_conversiones(ruta)
    
    if resultados.get('error') == 'ffmpeg_no_instalado':
        print("\n❌ No se pudieron realizar las conversiones porque ffmpeg no está instalado.")
        return
    
    from main import CONFIG
    
    if CONFIG['modo_verbose']:
        print(f"\n📊 RESUMEN DETALLADO DE CONVERSIONES:")
        print(f"   🖼️  WEBP a PNG: {resultados['webp_convertidos']}/{resultados['webp_total']} convertidos")
        print(f"   🎥 TS a MP4: {resultados['ts_convertidos']}/{resultados['ts_total']} convertidos")
        
        if resultados['webp_convertidos'] < resultados['webp_total']:
            no_convertidos = resultados['webp_total'] - resultados['webp_convertidos']
            print(f"   ⚠️  {no_convertidos} archivos WEBP no se pudieron convertir")
        
        if resultados['ts_convertidos'] < resultados['ts_total']:
            no_convertidos = resultados['ts_total'] - resultados['ts_convertidos']
            print(f"   ⚠️  {no_convertidos} archivos TS no se pudieron convertir")
    else:
        print(f"\n📊 RESUMEN DE CONVERSIONES:")
        print(f"🖼️  WEBP: {resultados['webp_convertidos']}/{resultados['webp_total']} convertidos")
        print(f"🎥 TS: {resultados['ts_convertidos']}/{resultados['ts_total']} convertidos")
        
        if resultados['webp_convertidos'] < resultados['webp_total']:
            print("💡 Algunos archivos WEBP no se pudieron convertir.")
        
        if resultados['ts_convertidos'] < resultados['ts_total']:
            print("💡 Algunos archivos TS no se pudieron convertir.")
    
    return resultados