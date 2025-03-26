# archivo: extractor_impi_app.py
import streamlit as st
import re
import pandas as pd
from PyPDF2 import PdfReader

st.set_page_config(page_title="Extractor de Estado de la Técnica", layout="wide")
st.title("📄 Extractor de datos de reportes del IMPI")

# Función para extraer datos
def extraer_info(texto):
    records = re.split(r"Record \d+/\d+", texto)

    # Paso 3: Definir patrones de búsqueda
    pub_pat = re.compile(r"Publication Number:\s*(\S+)")
    title_pat = re.compile(r"Title:\s*(.+)")
    adv_pat = re.compile(r"Abstract - DWPI Advantage:\s*(.+?)(?=\nAbstract|\n|$)", re.DOTALL)
    nov_pat = re.compile(r"Abstract - DWPI Novelty:\s*(.+?)(?=\nAbstract|\n|$)", re.DOTALL)

    # Paso 4: Extraer información de cada registro
    data = []
    for i, record in enumerate(records[1:], start=1):
        pub = pub_pat.search(record)
        title = title_pat.search(record)
        adv = adv_pat.search(record)
        nov = nov_pat.search(record)

        if pub and title and adv and nov:
            data.append({
                "Record": i,
                "Publication Number": pub.group(1).strip(),
                "Title": title.group(1).strip(),
                "Abstract - DWPI Advantage": adv.group(1).strip(),
                "Abstract - DWPI Novelty": nov.group(1).strip()
            })

    return data

# Subida de archivo
archivo = st.file_uploader("📤 Sube tu archivo PDF", type="pdf")

if archivo:
    reader = PdfReader(archivo)
    texto = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    
    resultados = extraer_info(texto)

    if resultados:
        df = pd.DataFrame(resultados)
        st.success(f"✅ Se extrajeron {len(df)} registros.")
        st.dataframe(df)

        # Descargar como TXT
        txt_content = "\n\n".join(
            f"Registro {i+1}\n" + "\n".join(f"{k}: {v}" for k, v in row.items())
            for i, row in df.iterrows()
        )
        st.download_button("📄 Descargar como .txt", txt_content, file_name="documentos_relevantes.txt")

        # Descargar como CSV
        csv_content = df.to_csv(index=False)
        st.download_button("📊 Descargar como .csv", csv_content, file_name="documentos_relevantes.csv")

    else:
        st.warning("⚠️ No se encontraron datos con el formato esperado.")