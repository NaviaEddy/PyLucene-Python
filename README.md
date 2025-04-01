# Motor de Busqueda con PyLucene

Aplicación web para indexar y buscar contenido de documentos y bases de datos mediante PyLucene.

## 📋 Resumen del Proyecto

Este proyecto es una aplicación web desarrollada en Python usando el framework Flask. La aplicación ofrece una interfaz HTML para:

- Indexar documentos (archivos de texto, DOCX, PDF, imágenes) y datos de una base de datos PostgreSQL.
- Realizar búsquedas de texto utilizando PyLucene, una integración de la biblioteca Java Lucene para indexado y búsqueda.

El sistema permite agregar contenido de diversas fuentes a un índice de búsqueda, facilitando la recuperación de información a partir de consultas de texto.

## ✨ Características Principales

- **Indexación de Archivos**: Soporta archivos en formato .txt, .docx, .pdf y archivos de imagen (.png, .jpg, .jpeg).
  - Para archivos PDF, se utiliza la biblioteca [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) para extraer texto.
  - Para imágenes, se utiliza [pytesseract](https://pypi.org/project/pytesseract/) para reconocimiento óptico de caracteres (OCR).

- **Indexación de Base de Datos PostgreSQL**: Se conecta a una base de datos PostgreSQL, recorre las tablas del esquema public y extrae el contenido de cada celda para indexarlo.

- **Búsqueda de Documentos**: Implementa búsqueda de contenido indexado utilizando PyLucene, con un límite de resultados y puntajes asociados.

- **Interfaz Web**: La aplicación utiliza plantillas HTML para renderizar formularios de búsqueda e indexación, y para mostrar resultados.

- **Contenerización con Docker**: Se incluye un Dockerfile para construir una imagen de Docker, lo que facilita el despliegue de la aplicación en contenedores.

## 📁 Estructura del Proyecto
```plaintext
├── app.py            # Código principal de la aplicación Flask
├── Dockerfile        # Instrucciones para construir la imagen Docker
├── requirements.txt  # Lista de dependencias de Python
└── templates
└── index.html    # Plantilla HTML para la interfaz de usuario
```
## 🔧 Requisitos y Dependencias

### Requisitos de Software

- **Python 3**
- **Java**: Necesario para ejecutar PyLucene (asegúrese de tener una versión compatible instalada)
- **PostgreSQL**: Base de datos utilizada para indexar datos
- **Tesseract OCR**: Utilizado para extraer texto de imágenes

### Dependencias de Python

El archivo requirements.txt incluye las siguientes librerías:

- Flask
- Pytesseract
- Pillow
- PyMuPDF (fitz)
- python-docx
- psycopg2
- pylucene (a través de la imagen de Docker coady/pylucene o configuración personalizada)

> [!NOTE]
> La instalación y configuración de PyLucene puede requerir pasos adicionales, ya que implica la integración de código Java con Python.

## 🚀 Instalación y Configuración

### Instalación Local

1. **Instalar dependencias del sistema**:
   Asegúrese de contar con Java, Tesseract OCR y PostgreSQL instalados.

2. **Clonar el repositorio y configurar entorno virtual**:
   ```bash
   git clone https://github.com/NaviaEddy/PyLucene-Python.git
3. **Instalar dependencias de Python**:
   ```bash
   pip install -r requirements.txt
4. **Importar la imagen de Docker coady/pylucene**
   ```bash
   docker pull coady/pylucene
5. **Configurar conexion a PostgreSQL**: Actualice las credenciales y parámetros de conexión en la función index_postgres() del archivo app.py si es necesario.
   
### Instalación con Docker

1. **Construir la imagen de Docjer**
    ```bash
    docker build -t buscador-pylucene .
3. **Ejecuta el contenedor**
    ```bash
    docker run -p 5000:5000 buscador-pylucene

> [!NOTE]
> Si la base de datos PostgreSQL se ejecuta en otro contenedor o en el host, asegúrese de que la conexión (host, puerto, etc.) esté correctamente configurada (por ejemplo, usando host.docker.internal).

## 💻 Descripción del Código
### app.py
- **Imports y Configuración Inicial**: Importa librerías necesarias e inicializa la aplicación Flask.
- **Funciones de Extracción de Texto**:
    - **extract_text_from_txt()**: Extrae texto de archivos de texto.
    - **extract_text_from_docx()**: Procesa documentos DOCX.
    - **extract_text_from_pdf()**: Extrae texto de archivos PDF.
    - **extract_text_from_image()**: Utiliza Tesseract OCR para extraer texto de imágenes.
- **Funciones de Indexado con PyLucene**:
    - **attach_thread()**: Adjunta el hilo actual a la JVM.
    - **get_index_writer()**: Configura y retorna un IndexWriter.
    - **add_document(content)**: Crea un documento Lucene con el contenido.
    - **search_documents(query_str)**: Realiza búsquedas en el índice.
- **Indexación de la Base de Datos PostgreSQL**:
    - **index_postgres()**: Conecta a la base de datos y añade el contenido al índice.
- **Indexación de Archivos**:
    - **index_file(file_path)**: Indexa archivos individuales.
    - **index_folder(folder_path)**: Recorre e indexa carpetas.
- **Rutas y Endpoints de Flask**:
    - **/**: Ruta principal que renderiza la plantilla index.html.
    - **/index_db**: Endpoint para indexar la base de datos PostgreSQL.
    - **/index**: API para indexar documentos mediante solicitudes JSON.
    - **/index_path**: Endpoint para indexar archivos mediante formularios.
    - **/search**: Endpoint para realizar búsquedas en el índice.
      
### Dockerfile
El Dockerfile utiliza la imagen base coady/pylucene y:
  - Establece el directorio de trabajo
  - Copia los archivos del proyecto
  - Instala las dependencias de Python
  - Expone el puerto 5000
  - Define el comando para ejecutar la aplicación
    
### Plantilla HTML (templates/index.html)
La plantilla HTML ofrece:
  - Un formulario de búsqueda
  - Sección para indexar la base de datos PostgreSQL
  - Sección para indexar archivos o carpetas
  - Renderización de resultados de búsqueda y mensajes flash
    
## 📝 Uso de la Aplicación
### Inicio y Búsqueda
  - Al acceder a la raíz (/), se muestra la interfaz principal con un formulario de búsqueda.
  - Ingrese una consulta en el campo de búsqueda y presione el botón "Buscar" para ver los resultados indexados.
    
### Indexación de la Base de Datos
  - Utilice el formulario "Indexar Base de Datos PostgreSQL" para extraer e indexar los datos de la base de datos.
  - Se mostrará un mensaje flash indicando el éxito o error del proceso.
    
### Indexación de Archivos
  - En la sección "Indexar Archivo o Carpeta", seleccione uno o varios archivos (o carpetas en navegadores compatibles) y haga clic en "Indexar Selección".
  - Los archivos seleccionados se procesan y el texto extraído se añade al índice para futuras búsquedas.

## ⚙️ Configuraciones y Personalizaciones
  - **Clave Secreta de Flask**: La variable app.secret_key en app.py debe modificarse por una clave secreta segura para producción.
  - **Directorio del Índice**: La constante INDEX_DIR define dónde se almacena el índice de Lucene. Asegúrese de que el directorio tenga permisos de escritura.
  - **Parámetros de Conexión a PostgreSQL**: Verifique y ajuste los parámetros de conexión en la función index_postgres() según la configuración de su servidor de base de datos.

## ⚠️ Consideraciones Finales
  - **Integración PyLucene y JVM**: Es importante que la máquina virtual de Java esté correctamente inicializada y configurada para que PyLucene funcione sin problemas. La función lucene.initVM() se utiliza al     inicio del script.
  - **Manejo de Errores**: La aplicación cuenta con manejo básico de errores para operaciones de indexación. Se recomienda mejorar los mensajes y agregar registros (logs) para un entorno de producción.
  - **Contenerización y Despliegue**: El Dockerfile facilita el despliegue en ambientes con Docker. Asegúrese de que los servicios externos (como PostgreSQL) sean accesibles desde el contenedor, ajustando las   configuraciones de red y host según sea necesario.

## 👥 Contribuciones
Siéntase libre de contribuir a este proyecto. Puede abrir un issue o enviar un pull request con sus mejoras.

## 📄 Licencia
Este proyecto está bajo la licencia MIT.
