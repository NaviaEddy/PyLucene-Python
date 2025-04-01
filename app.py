import os
import fitz
import pytesseract
from PIL import Image
from docx import Document as DocxDocument
import pandas as pd
import lucene
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import FSDirectory

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Reemplaza por una clave secreta adecuada
INDEX_DIR = "index_dir"
ALLOWED_EXTENSIONS = {"txt", "docx", "pdf", "png", "jpg", "jpeg",  "xls", "xlsx"}

# Inicializar la máquina virtual de Java (PyLucene)
lucene.initVM()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_txt(file):
    return file.read().decode('utf-8')

def extract_text_from_docx(file):
    doc = DocxDocument(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = "\n".join([page.get_text() for page in pdf_document])
    return text if text.strip() else None  # Si no hay texto, puede ser una imagen

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def extract_text_from_excel(file):
    try:
        excel_data = pd.read_excel(file, sheet_name=None)
        text_content = []
        for sheet_name, df in excel_data.items():
            text_content.append(f"Hoja: {sheet_name}\n{df.to_string(index=False)}")
        return "\n\n".join(text_content)
    except Exception as e:
        print(f"Error al extraer texto del Excel: {e}")
        return None

def attach_thread():
    """Adjunta el hilo actual a la JVM."""
    lucene.getVMEnv().attachCurrentThread()

def get_index_writer():
    attach_thread()  # Adjuntamos el hilo actual
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    index_path = File(INDEX_DIR).toPath()
    directory = FSDirectory.open(index_path)
    writer = IndexWriter(directory, config)
    return writer

def add_document(content, filename=None):
    writer = get_index_writer()
    doc = Document()
    doc.add(TextField("content", content, Field.Store.YES))
    if filename:
        doc.add(TextField("filename", filename, Field.Store.YES))
    writer.addDocument(doc)
    writer.commit()
    writer.close()

def search_documents(query_str):
    attach_thread()  # Adjuntamos el hilo actual
    analyzer = StandardAnalyzer()
    index_path = File(INDEX_DIR).toPath()
    directory = FSDirectory.open(index_path)
    reader = DirectoryReader.open(directory)
    searcher = IndexSearcher(reader)
    query = QueryParser("content", analyzer).parse(query_str)
    hits = searcher.search(query, 10)
    results = []
    for hit in hits.scoreDocs:
        doc = searcher.storedFields().document(hit.doc)
        results.append({
            "content": doc.get("content"),
            "filename": doc.get("filename"),
            "score": hit.score
        })
    reader.close()
    return results

# Función para indexar datos desde PostgreSQL
def index_postgres():
    # Conecta a la base de datos usando host.docker.internal si la aplicación está en Docker
    conn = psycopg2.connect(
        host="host.docker.internal",
        port=5432,
        dbname="dbpostgrado",
        user="postgres",
        password="post123post"
    )
    cur = conn.cursor()
    
    # Obtén la lista de todas las tablas del esquema "public"
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Procesando la tabla: {table_name}")
        # Selecciona todas las filas de la tabla actual
        try:
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            # Obtén la descripción de las columnas para identificar los nombres, si es necesario
            col_names = [desc[0] for desc in cur.description]
            
            for row in rows:
                # Itera por cada columna de la fila
                for idx, cell in enumerate(row):
                    # Si deseas incluir el nombre de la columna junto con el contenido
                    col_name = col_names[idx]
                    # Asegúrate de convertir el contenido a cadena si no es None
                    if cell is not None:
                        content = f"{table_name}.{col_name}: {str(cell)}"
                        add_document(content)
        except Exception as e:
            print(f"Error al procesar la tabla {table_name}: {e}")
    
    cur.close()
    conn.close()

def index_file(file_path):
    """Lee el contenido de un archivo de texto y lo indexa."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            add_document(content)
        print(f"Archivo indexado: {file_path}")
    except Exception as e:
        print(f"Error al indexar el archivo {file_path}: {e}")
        raise

def index_folder(folder_path):
    """Recorre recursivamente una carpeta e indexa todos los archivos de texto."""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Ajusta la validación de extensiones según necesites
            if file.lower().endswith(".txt"):
                file_path = os.path.join(root, file)
                index_file(file_path)

# Ruta de la interfaz principal
@app.route("/")
def home():
    return render_template("index.html")

# API para indexar la base de datos PostgreSQL
@app.route("/index_db", methods=["POST"])
def index_db():
    try:
        index_postgres()  # Función que indexa la BD
        flash("Base de datos indexada correctamente", "success")
    except Exception as e:
        flash(f"Error al indexar la base de datos: {str(e)}", "danger")
    return redirect(url_for("home"))

# API para indexar un documento individual
@app.route("/index", methods=["POST"])
def index_document():
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({
            "status": "error",
            "message": "No se proporcionó el contenido"
        }), 400
    try:
        add_document(data["content"])
        response = {
            "status": "success",
            "message": "Documento indexado correctamente",
            "document": data["content"]
        }
        return jsonify(response), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/index_path", methods=["POST"])
def index_path():
    if 'files' in request.files:
        files = request.files.getlist("files")
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    filename = file.filename.lower()
                    text_content = None

                    if filename.endswith('.txt'):
                        text_content = extract_text_from_txt(file)
                    elif filename.endswith('.docx'):
                        text_content = extract_text_from_docx(file)
                    elif filename.endswith('.pdf'):
                        text_content = extract_text_from_pdf(file)
                    elif filename.endswith(('.png', '.jpg', '.jpeg')):
                        text_content = extract_text_from_image(file)
                    elif filename.endswith(('.xls', '.xlsx')):
                        text_content = extract_text_from_excel(file)

                    if text_content:
                        add_document(text_content, filename=file.filename)
                        print(f"Archivo indexado: {file.filename}")
                    else:
                        flash(f"El archivo {file.filename} no contiene texto legible.", "warning")

                except Exception as e:
                    print(f"Error al indexar {file.filename}: {e}")
                    flash(f"Error al indexar {file.filename}: {str(e)}", "danger")
        
        flash("Archivos indexados correctamente", "success")
    else:
        flash("No se proporcionaron archivos", "danger")
    
    return redirect(url_for("home"))


# Ruta de búsqueda: ahora renderiza la respuesta en HTML siempre.
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    results = []
    if query:
        results = search_documents(query)
    return render_template("index.html", results=results, query=query)

if __name__ == "__main__":
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
    app.run(host="0.0.0.0", port=5000)