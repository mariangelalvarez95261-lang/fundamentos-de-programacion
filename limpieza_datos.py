import pandas as pd
import streamlit as st
from io import BytesIO
from urllib.request import urlopen

st.title("Limpieza de Datos")
ruta = "https://raw.githubusercontent.com/VMjavier/claseAnalisisDatos/refs/heads/main/veterinaria_colombia.csv"

@st.cache_data
def cargar_datos():
    with urlopen(ruta, timeout=15) as respuesta:
        datos = respuesta.read()
    return pd.read_csv(BytesIO(datos))

try:
    df = cargar_datos()
    st.dataframe(df, use_container_width=True)
except Exception as error:
    st.error(f"No se pudo cargar el archivo CSV: {error}")

df = pd.read_csv(ruta)
st.write(df)

st.subheader("1. columnas del dataset")
st.write(df.columns)
st.subheader("Columnas del dataset")
st.write(df.columns)

st.subheader("2. Valores nulos por columna")
nulos = df.isnull().sum().reset_index()
nulos.columns = ["Columna", "Valores nulos"]
st.write(nulos)

st.subheader("3. Dimensiones del dataset")
filas, columnas = df.shape
c1, c2 = st.columns(2)
c1.metric("Filas", filas)
c2.metric("Columnas", columnas)

df.columns = df.columns.str.strip().str.lower().str.replace(' ','_')

#si quiero cambiar el color de la columna particular, puedo usar el siguiente código:
df.columns = df.columns.str.strip().str.lower().str.replace(' ','_').str.replace('á','a').str.replace('é','e').str.replace('í','i').str.replace('ó','o').str.replace('ú','u')

#cambiar el nombre de una columna en particular, puedo usar el siguiente código:
df.rename(columns = {"nombre": "nombre_mascota"}, inplace = True)

st.subheader("4. columnas del dataset despues de la limpieza")
st.write(df.columns)

df.drop(columns = ["nombre_mascota"], inplace = True)

st.subheader("6. Dataset limpieza parcial")
st.write(df)
