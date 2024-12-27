import streamlit as st
import pandas as pd
import os

# Función para cargar o inicializar el CSV
def load_csv(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path, index_col=0)
    else:
        return pd.DataFrame(columns=["Identificación", "Número de muestra"])

# Función para guardar el dataframe al CSV
def save_csv(df, file_path):
    df.to_csv(file_path)

# Seleccionar o gestionar archivos CSV existentes
st.title("Gestión de Archivos CSV")

# Mostrar lista de archivos CSV en el directorio actual
csv_files = [f for f in os.listdir() if f.endswith('.csv')]
selected_csv = st.selectbox("Seleccionar archivo CSV:", options=["Crear nuevo"] + csv_files)

CSV_FILE = None

if selected_csv == "Crear nuevo":
    new_csv_name = st.text_input("Nombre del nuevo archivo CSV (incluya .csv):")
    if st.button("Crear archivo CSV"):
        if new_csv_name and not os.path.exists(new_csv_name):
            pd.DataFrame(columns=["Identificación", "Número de muestra"]).to_csv(new_csv_name)
            st.success(f"Archivo '{new_csv_name}' creado exitosamente.")
            CSV_FILE = new_csv_name
        elif os.path.exists(new_csv_name):
            st.error("El archivo ya existe.")
else:
    CSV_FILE = selected_csv
    # Permitir eliminar el archivo seleccionado
    if st.button("Eliminar archivo seleccionado"):
        os.remove(CSV_FILE)
        st.success(f"Archivo '{CSV_FILE}' eliminado exitosamente.")
        st.stop()

if not CSV_FILE:
    st.warning("Por favor, seleccione o cree un archivo CSV antes de continuar.")
    st.stop()

# Cargar o inicializar el CSV
responses = load_csv(CSV_FILE)

# Crear el formulario en Streamlit
st.title("Formulario de Evaluación de Muestras")

# Input para identificación del usuario
user_id = st.text_input("Identificación del usuario:")
if user_id in responses.get("Identificación", []):
    st.warning("Ya has realizado esta encuesta. Gracias por participar.")
    st.stop()

# Input para el número de muestra
sample_number = st.text_input("Número de la muestra:")

# Selector para el tipo de separación de respuestas
separator_type = st.radio("Seleccione el tipo de separación de palabras:", ("Fila", "Coma"))
separator = "\n" if separator_type == "Fila" else ","

# Inputs para las descripciones
less_than_reference = st.text_area("La muestra es menos que la referencia (describa):")
more_than_reference = st.text_area("La muestra es más que la referencia (describa):")

# Botón para enviar el formulario
if st.button("Enviar respuesta"):
    # Tokenizar palabras ingresadas por el usuario
    less_words = set(filter(None, less_than_reference.split(separator)))
    more_words = set(filter(None, more_than_reference.split(separator)))

    # Unir las palabras únicas
    all_words = less_words.union(more_words)

    if not all_words and not sample_number.strip() and not user_id.strip():
        st.warning("No se permite guardar respuestas vacías. Por favor, complete al menos un campo.")
        st.stop()

    # Asegurar que las columnas Identificación y Número de muestra estén al inicio
    for word in all_words:
        if word not in responses.columns:
            responses[word] = 0

    # Crear una nueva fila con los valores ingresados
    new_row = {word: 0 for word in responses.columns}
    new_row.update({word: 1 for word in less_words.union(more_words)})
    new_row["Número de muestra"] = sample_number
    new_row["Identificación"] = user_id

    # Reordenar las columnas para que Identificación y Número de muestra estén al inicio
    responses = pd.concat([responses, pd.DataFrame([new_row])], ignore_index=True)
    responses = responses[["Identificación", "Número de muestra"] + [col for col in responses.columns if col not in ["Identificación", "Número de muestra"]]]

    # Guardar los cambios en el CSV
    save_csv(responses, CSV_FILE)

    st.success("Respuesta guardada exitosamente.")

# Mostrar el contenido actual del CSV
st.header("Respuestas guardadas")
st.dataframe(responses)
