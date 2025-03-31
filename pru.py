from docx import Document

def test_docx_extraction(file_path):
    doc = Document(file_path)
    for para in doc.paragraphs:
        print(para.text)

test_docx_extraction(r"D:\USFX\8vo Semestre - CICO\SIS325\GeoAR.docx")