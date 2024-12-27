import streamlit as st
import pandas as pd
import os

# Ruta del archivo CSV donde se guardarán las respuestas
CSV_FILE = "respuestas.csv"

# Función para cargar o inicializar el CSV
def load_csv():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, index_col=0)
    else:
        return pd.DataFrame()

# Función para guardar el dataframe al CSV
def save_csv(df):
    df.to_csv(CSV_FILE)

# Cargar o inicializar el CSV
responses = load_csv()

# Crear el formulario en Streamlit
st.title("Formulario de Evaluación de Muestras")

# Input para identificación del usuario
user_id = st.text_input("Identificación del usuario:")
if user_id in responses.get("Identificación", []):
    st.warning("Ya has realizado esta encuesta. Gracias por participar.")
    st.stop()

# Input para el número de muestra
sample_number = st.text_input("Número de la muestra:")

# Inputs para las descripciones
less_than_reference = st.text_area("La muestra es menos que la referencia (describa):")
more_than_reference = st.text_area("La muestra es más que la referencia (describa):")

# Botón para enviar el formulario
if st.button("Enviar respuesta"):
    # Tokenizar palabras ingresadas por el usuario
    less_words = set(less_than_reference.split())
    more_words = set(more_than_reference.split())

    # Unir las palabras únicas
    all_words = less_words.union(more_words)

    # Actualizar el DataFrame de respuestas
    for word in all_words:
        if word not in responses.columns:
            responses[word] = 0

    # Crear una nueva fila con los valores ingresados
    new_row = {word: 0 for word in responses.columns}
    new_row.update({word: 1 for word in less_words.union(more_words)})
    new_row["Número de muestra"] = sample_number
    new_row["Identificación"] = user_id

    # Agregar la nueva fila al DataFrame
    responses = responses.append(new_row, ignore_index=True)

    # Guardar los cambios en el CSV
    save_csv(responses)

    st.success("Respuesta guardada exitosamente.")

# Mostrar el contenido actual del CSV
st.header("Respuestas guardadas")
st.dataframe(responses)
