# 🗂️ ORGEST - Organizador de Archivos

## 🤔 ¿Qué es ORGEST?

ORGEST es un organizador automático de archivos que te ayuda a limpiar y ordenar tus carpetas de forma inteligente. ✨ Con solo seleccionar una carpeta, ORGEST se encarga de todo el proceso de organización.

## 🚀 Características Principales

### 🗑️ Eliminación de Duplicados
- 🔍 Detecta archivos idénticos usando comparación MD5
- 📦 Mueve duplicados a carpeta "basura" para revisión
- ✅ Opción de eliminar permanentemente después de verificar

### 📂 Organización Automática
- 🖼️ Clasifica imágenes en carpeta "Imagenes"
- 🎥 Organiza videos en carpeta "Videos" 
- 📁 Mueve otros archivos a carpeta "basura"
- ⏳ Mantiene archivos WEBP y TS para conversión posterior

### 🔄 Conversión de Formatos
- 🖼️ Convierte archivos WEBP a PNG automáticamente
- 🎬 Transforma archivos TS a MP4
- 📦 Requiere FFmpeg (se instala automáticamente si es posible)

### 📤 Extracción de Archivos
- 📂 Saca todos los archivos de subcarpetas a la carpeta principal
- 🗑️ Elimina carpetas vacías automáticamente
- 🔄 Renombra archivos duplicados para evitar conflictos

### 🖼️ Pre-procesamiento de Imágenes
- 🛠️ Prepara imágenes para compatibilidad con Pillow 10.0.0
- 🔄 Convierte formatos problemáticos (RGBA, P) a RGB
- 📏 Redimensiona imágenes muy grandes automáticamente
- 💾 Guarda originales en carpeta "sin_edit"

### 🧹 Limpieza Final
- 🗑️ Opción de eliminar carpetas temporales "basura" y "sin_edit"
- 📊 Muestra estadísticas de espacio liberado
- ✅ Confirmación antes de cada eliminación

## 🎮 Cómo Usar

### 📋 Requisitos
- 🐍 Python 3.6 o superior
- ✏️ Permisos de escritura en las carpetas

### ⚡ Instalación
1. 📥 Descarga los archivos del proyecto
2. ✅ Asegúrate de tener Python instalado
3. 🚀 Ejecuta `main.py`


El programa te guiará a través de:
1. **🎛️ Selección de modo** (Automático o Personalizable)
2. **⏸️ Configuración de pausas** (Solo en modo automático)
3. **📁 Ingreso de ruta** de la carpeta a organizar
4. **⚡ Ejecución del proceso** seleccionado

### 🎯 Modos de Operación

#### 🤖 Modo Automático
Ejecuta todos los pasos en secuencia:
1. 🗑️ Eliminar duplicados
2. 📂 Organizar archivos en carpetas
3. 🔄 Convertir formatos WEBP y TS
4. 📤 Extraer archivos a la raíz
5. 🔍 Verificación final de duplicados
6. 🖼️ Pre-procesamiento de imágenes
7. 🧹 Limpieza final de carpetas temporales

#### 🔧 Modo Personalizable
Te permite elegir qué pasos ejecutar:
- 🗑️ Eliminar duplicados
- 📂 Organizar archivos
- 🔄 Convertir formatos
- 📤 Extraer archivos
- 🖼️ Pre-procesar imágenes
- 🚀 Ejecutar todos los pasos

## 📄 Formatos Soportados

### 🖼️ Imágenes
- JPG, JPEG, PNG, GIF, BMP, TIFF, ICO, WEBP

### 🎥 Videos
- MP4, AVI, MOV, MKV, WMV, FLV, MPEG, MPG, TS

## ⚙️ Características Técnicas

### 🎛️ Configuración Centralizada
- 🔍 Modo verbose para información detallada
- ⏸️ Control de pausas entre pasos
- 🧹 Limpieza automática de consola
- 📢 Sistema de banners informativos

### 🛡️ Manejo de Errores
- ❌ Captura de excepciones en todos los módulos
- 📁 Archivos problemáticos se mueven a carpeta "fallos"
- 📝 Logs de errores detallados
- ⏹️ Cancelación segura con Ctrl+C

### 📊 Estadísticas y Reportes
- 🔢 Conteo de archivos procesados
- 📈 Seguimiento de archivos no procesables
- 📋 Resumen detallado al finalizar
- 💾 Espacio liberado en MB

## 🐛 Solución de Problemas

### ❌ FFmpeg no encontrado
- 🪟 Windows: Descargar desde https://ffmpeg.org/
- 🐧 Linux: `sudo apt install ffmpeg`
- 🍎 macOS: `brew install ffmpeg`

### ❌ Pillow no se instala
- 🔧 Ejecutar manualmente: `pip install pillow`
- 🌐 Verificar conexión a internet
- 🐍 Usar Python 3.6 o superior

### ❌ Archivos no se procesan
- 🔒 Verificar permisos de escritura
- 📁 Revisar carpeta "fallos" para detalles de error
- 🔄 Comprobar que los archivos no estén en uso

## 🤝 Contribuciones

Las contribuciones son bienvenidas. 🎉 Algunas áreas de mejora:
- ➕ Soporte para más formatos de archivo
- 📅 Organización por fecha o tipo
- 🖥️ Interfaz gráfica de usuario
- 📦 Procesamiento por lotes múltiples

## 📄 Licencia

Proyecto de código abierto. 📖 Úsalo y modifícalo libremente.

**¡Organiza tus archivos automáticamente con ORGEST! 🎊**

---

# 🗺️ Roadmap ORGEST

## 🟢 Mejoras Rápidas

### 1. 📊 Barra de Progreso Mejorada
- 🎯 Mostrar porcentajes exactos en lugar de conteos
- ⏱️ Agregar estimación de tiempo restante
- 📈 Progress bars visuales con ASCII
- 🔄 Actualización en tiempo real más fluida

### 2. 📋 Reportes Visuales del Espacio Liberado
- 📊 Gráficos ASCII simples para estadísticas
- 🔢 Formateo visual de números (1.5 GB vs 1500 MB)
- 🎨 Resumen con emojis y separadores
- 📁 Desglose por tipo de archivo procesado

### 3. 🎨 Temas de Colores Personalizables
- 🌓 Esquemas de color predefinidos (claro/oscuro)
- 😊 Configuración de emojis y símbolos
- 🎨 Paletas de colores para diferentes estados
- 💾 Configuración persistente entre sesiones

## 🟡 Optimizaciones

### 4. ⚡ Optimizaciones de Rendimiento
- 🔄 Procesamiento paralelo para operaciones I/O
- 💾 Cache de hashes MD5 para archivos recurrentes
- 📖 Lectura por chunks más eficiente
- 🗂️ Reducción de recorridos duplicados en directorios

### 5. 🌟 Conservar Archivo de Mejor Calidad
- 📸 Análisis de metadatos EXIF en imágenes
- 📏 Comparación de resolución y tamaño de archivo
- 🔍 Detección de compresión y artifacts
- 🧠 Lógica de selección automática del "mejor" archivo

### 6. ✅ Verificación de Integridad
- 🔒 Checksums después de operaciones de movimiento
- 🩺 Validación de archivos corruptos
- ↩️ Sistema simple de rollback para operaciones fallidas
- 📝 Logs de verificación detallados

## 🔴 Nuevas Funcionalidades

### 7. 📄 Nuevos Formatos y Procesos
- 📑 Soporte para PDF (extracción, organización)
- 📱 Conversión HEIC/HEIF (formato iPhone)
- 🗜️ Compresión optimizada con diferentes algoritmos
- 📊 Procesamiento de documentos de Office

### 8. 📦 Distribución
- 🖥️ Empacado como ejecutable (.exe, .dmg, .AppImage)
- 🔧 Instalador automático de dependencias
- 🔄 Sistema de actualizaciones
- 🏷️ Gestión de versiones y changelog

### 9. 🖥️ Interfaz Gráfica
- 🎨 GUI completa con tkinter o CustomTkinter
- 🖱️ Drag & drop de carpetas
- 👁️ Vista previa de cambios
- ⚙️ Configuración visual de opciones
