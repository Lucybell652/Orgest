import os
import shutil
import subprocess
import sys
from pathlib import Path

def install_package(package):
    """Instala un paquete pip si no está disponible de forma silenciosa"""
    try:
        __import__("PIL" if package == "Pillow" else package)
        return True
    except ImportError:
        print(f"📦 Instalando {package}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                try:
                    __import__("PIL" if package == "Pillow" else package)
                    return True
                except ImportError:
                    return False
            else:
                return False
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

def check_dependencies():
    """Verifica e instala dependencias necesarias para el pre-procesador de forma silenciosa"""
    # Pillow es el nombre del paquete, pero se importa como PIL
    if not install_package("Pillow"):
        print("❌ No se pudo instalar Pillow. Instálalo manualmente:")
        print("   pip install pillow>=10.0.0")
        return False
    
    return True

# 🔥 CORRECCIÓN: Definir ANTIALIAS para compatibilidad
def setup_pillow_compatibility():
    """Configura compatibilidad para versiones antiguas y nuevas de Pillow"""
    from PIL import Image
    try:
        # Para Pillow >= 10.0.0
        if not hasattr(Image, 'ANTIALIAS'):
            Image.ANTIALIAS = Image.LANCZOS
        if not hasattr(Image, 'Resampling'):
            Image.Resampling = type('Resampling', (), {'LANCZOS': Image.LANCZOS})
    except AttributeError:
        pass
    return Image

class ImagePreprocessor:
    """Pre-procesa imágenes para compatibilidad con Pillow 10.0.0"""
    
    def __init__(self, ruta_base):
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        self.processed_count = 0
        self.failed_count = 0
        self.moved_count = 0
        self.ruta_base = ruta_base
        self.carpeta_fallos = os.path.join(ruta_base, "fallos")
        
        # 🔥 CORRECCIÓN: Configurar compatibilidad al inicializar
        self.Image = setup_pillow_compatibility()
    
    def limpiar_consola(self):
        """Limpia la consola según el sistema operativo"""
        from main import CONFIG
        if CONFIG['limpiar_consola']:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def create_sin_edit_folder(self, folder_path):
        """Crea la carpeta 'sin_edit' si no existe"""
        from main import CONFIG
        
        sin_edit_folder = os.path.join(folder_path, "sin_edit")
        if not os.path.exists(sin_edit_folder):
            os.makedirs(sin_edit_folder)
            if CONFIG['modo_verbose']:
                print(f"   📁 Carpeta 'sin_edit' creada: {sin_edit_folder}")
        return sin_edit_folder
    
    def create_fallos_folder(self):
        """Crea la carpeta 'fallos' si no existe"""
        from main import CONFIG
        
        if not os.path.exists(self.carpeta_fallos):
            os.makedirs(self.carpeta_fallos)
            if CONFIG['modo_verbose']:
                print(f"   📁 Carpeta 'fallos' creada: {self.carpeta_fallos}")
        return self.carpeta_fallos
    
    def move_original_to_backup(self, original_path, sin_edit_folder):
        """Mueve el archivo original a la carpeta sin_edit de forma segura"""
        from main import CONFIG
        
        try:
            if not os.path.exists(original_path):
                return False
            
            filename = os.path.basename(original_path)
            destination = os.path.join(sin_edit_folder, filename)
            
            # Si el archivo ya existe en el destino, agregar un sufijo numérico
            counter = 1
            base_destination = destination
            name, ext = os.path.splitext(filename)
            
            while os.path.exists(destination):
                destination = os.path.join(sin_edit_folder, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.move(original_path, destination)
            self.moved_count += 1
            
            if CONFIG['modo_verbose']:
                if destination != base_destination:
                    print(f"   📦 Original renombrado y movido a sin_edit: {filename} → {os.path.basename(destination)}")
                else:
                    print(f"   📦 Original movido a sin_edit: {filename}")
                    
            return True
            
        except Exception as e:
            if CONFIG['modo_verbose']:
                print(f"   ❌ ERROR moviendo original {os.path.basename(original_path)}: {e}")
            return False
    
    def move_to_fallos(self, image_path, error_message):
        """Mueve una imagen fallida a la carpeta de fallos"""
        from main import CONFIG
        
        try:
            if not os.path.exists(image_path):
                return False
            
            # Crear carpeta fallos si no existe
            self.create_fallos_folder()
            
            filename = os.path.basename(image_path)
            destination = os.path.join(self.carpeta_fallos, filename)
            
            # Si ya existe en fallos, renombrar
            counter = 1
            name, ext = os.path.splitext(filename)
            while os.path.exists(destination):
                destination = os.path.join(self.carpeta_fallos, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.move(image_path, destination)
            
            # Crear archivo de log con el error
            log_file = os.path.join(self.carpeta_fallos, f"{os.path.splitext(filename)[0]}_error.txt")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Error al procesar: {filename}\n")
                f.write(f"Error: {error_message}\n")
                f.write(f"Fecha: {subprocess.getoutput('date /t' if os.name == 'nt' else 'date')}\n")
            
            if CONFIG['modo_verbose']:
                print(f"   🚨 Imagen fallida movida a 'fallos': {filename}")
                
            return True
            
        except Exception as e:
            if CONFIG['modo_verbose']:
                print(f"   ❌ ERROR moviendo a fallos {os.path.basename(image_path)}: {e}")
            else:
                print(f"❌ Error al mover a fallos: {e}")
            return False
    
    def find_images_needing_processing(self, folder_path):
        """Encuentra imágenes que podrían necesitar pre-procesamiento"""
        from main import CONFIG
        
        images = []
        
        try:
            for root, dirs, files in os.walk(folder_path):
                # Excluir carpetas de respaldo del procesamiento, pero permitir que existan
                # No excluir "fallos" aquí para que la carpeta pueda ser creada
                if "sin_edit" in root or "YaRespaldo" in root or "basura" in root:
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = Path(file).suffix.lower()
                    
                    # Excluir archivos que estén en la carpeta "fallos"
                    if "fallos" in file_path:
                        continue
                        
                    if ext in self.supported_extensions:
                        images.append(file_path)
            
            if CONFIG['modo_verbose']:
                print(f"   🔍 Imágenes encontradas para procesar: {len(images)}")
                
            return images
            
        except Exception as e:
            if CONFIG['modo_verbose']:
                print(f"   ❌ ERROR buscando imágenes: {e}")
            return []
    
    def needs_resize_processing(self, img, max_dimension=5000):
        """Verifica si la imagen necesita redimensionamiento"""
        width, height = img.size
        
        # Si la imagen es muy grande, podría necesitar redimensionamiento
        if width > max_dimension or height > max_dimension:
            return True
        
        # Verificar modo de color (convertir RGBA to RGB si es necesario)
        if img.mode in ('RGBA', 'LA', 'P'):
            return True
            
        return False
    
    def process_image(self, image_path, sin_edit_folder, output_quality=85, max_dimension=5000):
        """Procesa una imagen y mueve el original a sin_edit"""
        from main import CONFIG
        
        try:
            # Primero mover el original a sin_edit
            original_moved = self.move_original_to_backup(image_path, sin_edit_folder)
            if not original_moved:
                return False
            
            # Ahora procesar la imagen (que ahora está en sin_edit, trabajar con copia)
            original_in_backup = os.path.join(sin_edit_folder, os.path.basename(image_path))
            
            # 🔥 CORRECCIÓN: Usar self.Image que ya tiene la compatibilidad configurada
            with self.Image.open(original_in_backup) as img:
                original_mode = img.mode
                original_size = img.size
                
                if CONFIG['modo_verbose']:
                    print(f"   🖼️  Procesando: {os.path.basename(image_path)}")
                    print(f"      Modo original: {original_mode}, Tamaño: {original_size}")
                
                # Convertir modos problemáticos a RGB
                if img.mode in ('RGBA', 'LA'):
                    # Crear fondo blanco para imágenes con transparencia
                    background = self.Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img, mask=img)
                    img = background
                    if CONFIG['modo_verbose']:
                        print(f"      Convertido de {original_mode} a RGB")
                
                elif img.mode == 'P':
                    # Convertir imágenes paletizadas
                    img = img.convert('RGB')
                    if CONFIG['modo_verbose']:
                        print(f"      Convertido de {original_mode} a RGB")
                
                # 🔥 CORRECCIÓN: Usar LANCZOS en lugar de ANTIALIAS
                needs_resize = self.needs_resize_processing(img, max_dimension)
                if needs_resize:
                    width, height = img.size
                    
                    if width > max_dimension or height > max_dimension:
                        # Calcular nuevo tamaño manteniendo aspect ratio
                        ratio = min(max_dimension/width, max_dimension/height)
                        new_size = (int(width * ratio), int(height * ratio))
                        
                        # 🔥 CORRECCIÓN: Usar LANCZOS (reemplazo de ANTIALIAS)
                        img = img.resize(new_size, self.Image.LANCZOS)
                        if CONFIG['modo_verbose']:
                            print(f"      Redimensionado: {original_size} → {new_size}")
                
                # Guardar la versión procesada en la ubicación original
                save_kwargs = {}
                if image_path.lower().endswith(('.jpg', '.jpeg')):
                    save_kwargs = {'quality': output_quality, 'optimize': True}
                    if CONFIG['modo_verbose']:
                        print(f"      Guardado como JPEG con calidad: {output_quality}%")
                elif image_path.lower().endswith('.png'):
                    save_kwargs = {'optimize': True}
                    if CONFIG['modo_verbose']:
                        print("      Guardado como PNG optimizado")
                elif image_path.lower().endswith('.webp'):
                    save_kwargs = {'quality': output_quality}
                    if CONFIG['modo_verbose']:
                        print(f"      Guardado como WEBP con calidad: {output_quality}%")
                
                img.save(image_path, **save_kwargs)
                self.processed_count += 1
                
                if CONFIG['modo_verbose']:
                    print(f"      ✅ Procesamiento completado")
                    
                return True
                    
        except Exception as e:
            self.failed_count += 1
            error_msg = str(e)
            
            # Mover el archivo fallido a la carpeta de fallos
            if CONFIG['modo_verbose']:
                print(f"   ❌ ERROR procesando {os.path.basename(image_path)}: {error_msg}")
                print(f"      📁 Moviendo a carpeta 'fallos'...")
            else:
                print(f"❌ Error procesando {os.path.basename(image_path)}: {error_msg}")
                print(f"   📁 Moviendo a carpeta 'fallos'...")
                
            self.move_to_fallos(image_path, error_msg)
            
            return False
    
    def process_folder(self, folder_path, output_quality=85, max_dimension=5000):
        """Procesa todas las imágenes en una carpeta"""
        from main import CONFIG
        
        if CONFIG['modo_verbose']:
            print("🖼️  INICIANDO PROCESAMIENTO DE IMÁGENES...")
            print(f"📁 Ruta: {folder_path}")
        
        # Crear carpetas necesarias al inicio
        sin_edit_folder = self.create_sin_edit_folder(folder_path)
        self.create_fallos_folder()  # Asegurar que la carpeta fallos existe
        
        images = self.find_images_needing_processing(folder_path)
        
        if not images:
            print("✅ No se encontraron imágenes para procesar")
            return {
                'total_imagenes': 0,
                'procesadas': 0,
                'fallos': 0,
                'movidas_sin_edit': 0
            }
        
        total_images = len(images)
        
        if CONFIG['modo_verbose']:
            print(f"📊 TOTAL DE IMÁGENES A PROCESAR: {total_images}")
        else:
            print(f"🖼️  Procesando {total_images} imágenes...")
        
        for i, image_path in enumerate(images, 1):
            # Limpiar consola para cada archivo si está configurado
            if CONFIG['limpiar_consola'] and not CONFIG['modo_verbose']:
                self.limpiar_consola()
                print("=== PRE-PROCESAMIENTO DE IMÁGENES ===")
                print(f"📊 Progreso general: {i}/{total_images}")
                print(f"✅ Procesadas: {self.processed_count}")
                print(f"📦 Movidas a sin_edit: {self.moved_count}")
                print(f"❌ Errores: {self.failed_count}")
                print("-" * 40)
            
            self.process_image(image_path, sin_edit_folder, output_quality, max_dimension)
        
        # Mostrar resumen final
        return self._print_summary()
    
    def _print_summary(self):
        """Muestra resumen del procesamiento"""
        from main import CONFIG
        
        # Limpiar consola antes de mostrar el resumen final si está configurado
        if CONFIG['limpiar_consola']:
            self.limpiar_consola()
            
        if CONFIG['modo_verbose']:
            print("\n" + "=" * 50)
            print("📊 RESUMEN DETALLADO DE PRE-PROCESAMIENTO")
            print("=" * 50)
            print(f"   ✅ Imágenes procesadas exitosamente: {self.processed_count}")
            print(f"   📦 Originales movidos a 'sin_edit': {self.moved_count}")
            print(f"   ❌ Imágenes con errores: {self.failed_count}")
            
            if self.failed_count > 0:
                print(f"\n   ⚠️  {self.failed_count} imágenes fallaron en el procesamiento.")
                print(f"   📁 Se movieron a la carpeta 'fallos' para revisión manual.")
                print(f"   📍 Ruta: {self.carpeta_fallos}")
                print("   💡 Cada archivo fallido tiene un archivo .txt con detalles del error.")
            else:
                # Si no hay errores, eliminar la carpeta fallos si existe y está vacía
                if os.path.exists(self.carpeta_fallos):
                    try:
                        # Verificar si la carpeta está vacía
                        if not any(os.scandir(self.carpeta_fallos)):
                            shutil.rmtree(self.carpeta_fallos)
                            print(f"\n   🗑️  Carpeta 'fallos' eliminada (estaba vacía)")
                        else:
                            print(f"\n   📁 Carpeta 'fallos' conservada (contiene archivos)")
                    except Exception as e:
                        print(f"\n   ⚠️  No se pudo verificar/eliminar carpeta 'fallos': {e}")
            
            print("   🎉 ¡PRE-PROCESAMIENTO COMPLETADO!")
        else:
            print("\n" + "=" * 50)
            print("📊 RESUMEN DE PRE-PROCESAMIENTO")
            print("=" * 50)
            print(f"✅ Imágenes procesadas: {self.processed_count}")
            print(f"📦 Originales movidos a 'sin_edit': {self.moved_count}")
            print(f"❌ Errores: {self.failed_count}")
            
            if self.failed_count > 0:
                print(f"\n⚠️  {self.failed_count} imágenes fallaron en el procesamiento.")
                print(f"📁 Se movieron a la carpeta 'fallos' para revisión manual.")
                print(f"📍 Ruta: {self.carpeta_fallos}")
                print("💡 Cada archivo fallido tiene un archivo .txt con detalles del error.")
            else:
                # Si no hay errores, eliminar la carpeta fallos si existe y está vacía
                if os.path.exists(self.carpeta_fallos):
                    try:
                        # Verificar si la carpeta está vacía
                        if not any(os.scandir(self.carpeta_fallos)):
                            shutil.rmtree(self.carpeta_fallos)
                            print(f"\n🗑️  Carpeta 'fallos' eliminada (estaba vacía)")
                    except Exception as e:
                        pass  # En modo normal, no mostrar errores de limpieza
        
        print("🎉 ¡Pre-procesamiento completado!")
        
        # Retornar resultados para el estado del programa
        return {
            'total_imagenes': self.processed_count + self.failed_count,
            'procesadas': self.processed_count,
            'fallos': self.failed_count,
            'movidas_sin_edit': self.moved_count
        }

def preprocesar_imagenes(ruta, modo_automatico=False):
    """
    Función principal para el pre-procesamiento de imágenes.
    
    Args:
        ruta (str): Ruta de la carpeta a procesar
        modo_automatico (bool): Si es True, salta las confirmaciones
        
    Returns:
        dict: Resultados del preprocesamiento para el estado del programa
    """
    from main import CONFIG
    
    # 🔥 CORRECCIÓN: Configurar compatibilidad globalmente
    setup_pillow_compatibility()
    
    # Mostrar siempre el banner del punto 5
    print("\n" + "="*50)
    print("PUNTO 5: PRE-PROCESAMIENTO DE IMÁGENES")
    print("="*50)
    print("🖼️  PRE-PROCESADOR DE IMÁGENES PARA PILLOW 10.0.0")
    print("📦 Los originales se moverán a carpeta 'sin_edit'")
    print("🔄 Las versiones procesadas quedarán en su ubicación original")
    print("❌ Los archivos fallidos irán a carpeta 'fallos'")
    print("="*50)
    
    # Verificar dependencias silenciosamente
    if not check_dependencies():
        print("❌ No se pudieron instalar las dependencias necesarias.")
        print("   El pre-procesamiento de imágenes se omitirá.")
        if CONFIG['pausa_entre_pasos'] and not modo_automatico:
            input("\nPresiona Enter para continuar...")
        return {
            'total_imagenes': 0,
            'procesadas': 0,
            'fallos': 0,
            'movidas_sin_edit': 0,
            'error': 'dependencias_faltantes'
        }
    
    # Verificar que Pillow funciona sin mostrar mensajes si todo está bien
    try:
        from PIL import Image
        # Si llegamos aquí, todo está correcto - no mostrar mensaje
    except ImportError as e:
        print(f"❌ Error importando Pillow: {e}")
        print("   El pre-procesamiento de imágenes se omitirá.")
        if CONFIG['pausa_entre_pasos'] and not modo_automatico:
            input("\nPresiona Enter para continuar...")
        return {
            'total_imagenes': 0,
            'procesadas': 0,
            'fallos': 0,
            'movidas_sin_edit': 0,
            'error': 'pillow_no_importa'
        }
    
    # Si está en modo automático, saltar confirmación y ejecutar directamente
    if modo_automatico:
        print("🖼️  Ejecutando pre-procesamiento automáticamente...\n")
        
        # Procesar imágenes
        preprocessor = ImagePreprocessor(ruta)
        resultados = preprocessor.process_folder(
            ruta, 
            output_quality=85,
            max_dimension=5000
        )
        
        return resultados
    
    # Bucle de confirmación solo para modo NO automático
    while True:
        confirm = input("\n¿Iniciar el pre-procesamiento de imágenes? (s/n): ").strip().lower()
        
        if confirm == '':
            # Si presiona Enter sin escribir, mostrar mensaje en la misma línea
            print("\033[F\033[K", end='')  # Retrocede a la línea anterior y la limpia
            continue
        elif confirm in ('s', 'si', 'sí', 'y', 'yes'):
            print("🚀 Iniciando pre-procesamiento de imágenes...\n")
            
            # Procesar imágenes
            preprocessor = ImagePreprocessor(ruta)
            resultados = preprocessor.process_folder(
                ruta, 
                output_quality=85,
                max_dimension=5000
            )
            
            # El resumen final ya se muestra limpio desde _print_summary
            if CONFIG['pausa_entre_pasos']:
                input("\nPresiona Enter para continuar...")
            return resultados
            
        elif confirm in ('n', 'no', 'not', 'q'):
            print("❌ Pre-procesamiento de imágenes cancelado.")
            if CONFIG['pausa_entre_pasos']:
                input("\nPresiona Enter para continuar...")
            return {
                'total_imagenes': 0,
                'procesadas': 0,
                'fallos': 0,
                'movidas_sin_edit': 0,
                'error': 'cancelado_por_usuario'
            }
        else:
            # Respuesta no válida, volver a preguntar en la misma línea
            print("\033[F\033[K", end='')  # Retrocede a la línea anterior y la limpia