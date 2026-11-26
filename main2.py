import streamlit as st
import pandas as pd
import plotly.express as px
import random
from pathlib import Path

# =====================================================
# 1. CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Dashboard de Estudiantes",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta institucional
ROSA = "#CB7087"
ROSA_MEDIO = "#EDBECA"
ROSA_CLARO = "#FFD6DC"
CREMA = "#FFF1E4"

PALETA = [ROSA, ROSA_MEDIO, ROSA_CLARO, CREMA]


# =====================================================
# 2. ESTILOS CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #FFF1E4;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #FFD6DC;
    border-right: 1px solid #EDBECA;
}

h1 {
    color: #CB7087 !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #CB7087 !important;
    font-weight: 700 !important;
}

[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #EDBECA;
    box-shadow: 0 3px 12px rgba(203,112,135,0.08);
}

[data-testid="stMetricLabel"] {
    color: #8B5968 !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #CB7087 !important;
    font-weight: 800;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background-color: #FFD6DC;
    padding: 10px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #FFF1E4;
    border-radius: 9px;
    color: #8B5968;
    font-weight: 600;
    padding: 10px 22px;
}

.stTabs [aria-selected="true"] {
    background-color: #CB7087 !important;
    color: white !important;
}

.texto-descriptivo {
    color: #795966;
    font-size: 15px;
    line-height: 1.7;
    background-color: #FFFFFF;
    padding: 16px 20px;
    border-left: 5px solid #CB7087;
    border-radius: 8px;
    margin-bottom: 20px;
}

hr {
    border-color: #EDBECA;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. CARGA DE DATOS
# =====================================================

@st.cache_data
def cargar_datos():

    ruta = (
        Path(__file__).resolve().parent
        / "database"
        / "Estudiantes_Matriculados_en_Programas_Académicos_-_Institución_Universitaria_Colegio_Mayor_de_Antioquia_20261126.csv"
    )

    return pd.read_csv(ruta)


df = cargar_datos()


# =====================================================
# 4. DEFINICIÓN DE VARIABLES
# =====================================================

filtros = {
    "TIPO INSCRIPCION": "Tipo de inscripción",
    "PROGRAMA": "Programa académico",
    "SEXO BIOLOGICO": "Sexo biológico"
}

columnas_faltantes = [
    col for col in filtros
    if col not in df.columns
]

if columnas_faltantes:
    st.error(f"Faltan columnas: {columnas_faltantes}")
    st.stop()


# =====================================================
# 5. FUNCIÓN DE FILTRADO
# =====================================================

def aplicar_filtros(datos, selecciones, excluir=None):

    resultado = datos

    for columna, valores in selecciones.items():

        if columna == excluir:
            continue

        if valores:
            resultado = resultado[
                resultado[columna].isin(valores)
            ]

    return resultado


# =====================================================
# 6. ENCABEZADO
# =====================================================

st.title("🎓 Dashboard de Estudiantes Matriculados")

st.markdown("""
<p style="color:#795966; font-size:16px;">
Institución Universitaria Colegio Mayor de Antioquia
<br>
Panel de análisis y caracterización de estudiantes matriculados.
</p>
""", unsafe_allow_html=True)

st.divider()


# =====================================================
# 7. FILTROS INTERCONECTADOS
# =====================================================

st.sidebar.title("⌕ Panel de filtros")

st.sidebar.caption(
    "Personaliza la información que deseas analizar."
)

selecciones = {
    columna: st.session_state.get(
        f"filtro_{columna}", []
    )
    for columna in filtros
}

for columna, etiqueta in filtros.items():

    datos_disponibles = aplicar_filtros(
        df,
        selecciones,
        excluir=columna
    )

    opciones = sorted(
        datos_disponibles[columna]
        .dropna()
        .unique()
        .tolist(),
        key=str
    )

    clave = f"filtro_{columna}"

    selecciones[columna] = [
        valor for valor in selecciones[columna]
        if valor in opciones
    ]

    st.session_state[clave] = selecciones[columna]

    seleccion = st.sidebar.multiselect(
        etiqueta,
        options=opciones,
        key=clave,
        placeholder="Todas las categorías"
    )

    selecciones[columna] = seleccion


# Aplicar todos los filtros
df_filtrado = aplicar_filtros(df, selecciones)


# =====================================================
# 8. INDICADORES KPI
# =====================================================

st.subheader("Resumen general")

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        "Total de registros",
        f"{len(df_filtrado):,}"
    )

with kpi2:
    st.metric(
        "Programas académicos",
        f"{df_filtrado['PROGRAMA'].nunique():,}"
    )

with kpi3:
    st.metric(
        "Tipos de inscripción",
        f"{df_filtrado['TIPO INSCRIPCION'].nunique():,}"
    )

st.divider()


# =====================================================
# 9. PREPARAR DATOS PARA GRÁFICOS
# =====================================================

def preparar_conteo(datos, columna):

    conteo = (
        datos[columna]
        .fillna("Sin información")
        .astype(str)
        .value_counts()
        .rename_axis("Categoría")
        .reset_index(name="Estudiantes")
    )

    return conteo


# =====================================================
# 10. CONFIGURACIÓN VISUAL DE GRÁFICOS
# =====================================================

def configurar_grafico(fig, titulo):

    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(size=19, color=ROSA)
        ),

        font=dict(
            family="Arial",
            size=12,
            color="#795966"
        ),

        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",

        margin=dict(
            l=25,
            r=25,
            t=65,
            b=35
        ),

        height=450
    )

    return fig


# =====================================================
# 11. DESCRIPCIONES ALEATORIAS
# =====================================================

descripciones = {

    "TIPO INSCRIPCION": [
        "Conoce cómo se distribuyen los estudiantes según su modalidad de inscripción.",
        "Explora las diferentes formas de ingreso y participación académica.",
        "Identifica los tipos de inscripción con mayor representación.",
        "Analiza el comportamiento de las modalidades de inscripción."
    ],

    "PROGRAMA": [
        "Descubre cuáles son los programas académicos con mayor participación estudiantil.",
        "Explora la distribución de estudiantes entre la oferta académica institucional.",
        "Identifica los programas que concentran una mayor cantidad de estudiantes.",
        "Conoce cómo se distribuye la matrícula entre los programas académicos."
    ],

    "SEXO BIOLOGICO": [
        "Observa la composición de la población estudiantil según el sexo biológico registrado.",
        "Explora la distribución de estudiantes por sexo biológico.",
        "Conoce la participación de cada categoría en la población matriculada.",
        "Analiza la composición de la matrícula según esta característica."
    ]
}


# =====================================================
# 12. CREACIÓN DE PESTAÑAS
# =====================================================

tab1, tab2, tab3 = st.tabs([
    "Tipo de inscripción",
    "Programa académico",
    "Sexo biológico"
])


# =====================================================
# 13. PESTAÑA TIPO DE INSCRIPCIÓN
# =====================================================

with tab1:

    columna = "TIPO INSCRIPCION"

    conteo = preparar_conteo(df_filtrado, columna)

    st.subheader("Análisis por tipo de inscripción")

    st.markdown(
        f'<div class="texto-descriptivo">'
        f'{random.choice(descripciones[columna])}'
        f'</div>',
        unsafe_allow_html=True
    )

    if not conteo.empty:

        izquierda, derecha = st.columns([1.5, 1])

        with izquierda:

            fig = px.bar(
                conteo.sort_values(
                    "Estudiantes",
                    ascending=True
                ),
                x="Estudiantes",
                y="Categoría",
                orientation="h",
                text="Estudiantes",
                color="Categoría",
                color_discrete_sequence=PALETA
            )

            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
                cliponaxis=False
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Número de estudiantes",
                yaxis_title="",
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#F3E2E5"
                )
            )

            configurar_grafico(
                fig,
                "Distribución de inscripciones"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with derecha:

            fig = px.pie(
                conteo,
                names="Categoría",
                values="Estudiantes",
                hole=0.65,
                color_discrete_sequence=PALETA
            )

            fig.update_traces(
                textinfo="percent",
                textposition="inside",
                marker=dict(
                    line=dict(color="white", width=3)
                )
            )

            configurar_grafico(
                fig,
                "Participación porcentual"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.info("No hay registros disponibles con estos filtros.")


# =====================================================
# 14. PESTAÑA PROGRAMA ACADÉMICO
# =====================================================

with tab2:

    columna = "PROGRAMA"

    conteo = preparar_conteo(df_filtrado, columna)

    st.subheader("Análisis por programa académico")

    st.markdown(
        f'<div class="texto-descriptivo">'
        f'{random.choice(descripciones[columna])}'
        f'</div>',
        unsafe_allow_html=True
    )

    if not conteo.empty:

        top_programas = (
            conteo
            .sort_values(
                "Estudiantes",
                ascending=False
            )
            .head(15)
            .sort_values(
                "Estudiantes",
                ascending=True
            )
        )

        fig = px.bar(
            top_programas,
            x="Estudiantes",
            y="Categoría",
            orientation="h",
            text="Estudiantes",
            color="Estudiantes",
            color_continuous_scale=[
                CREMA,
                ROSA_CLARO,
                ROSA_MEDIO,
                ROSA
            ]
        )

        fig.update_traces(
            textposition="outside",
            marker_line_width=0,
            cliponaxis=False
        )

        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Número de estudiantes",
            yaxis_title="",
            xaxis=dict(
                showgrid=True,
                gridcolor="#F3E2E5"
            ),
            height=600
        )

        configurar_grafico(
            fig,
            "Distribución de estudiantes por programa"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            f"Se muestran los 15 programas principales "
            f"de {len(conteo)} categorías disponibles."
        )

    else:
        st.info("No hay registros disponibles con estos filtros.")


# =====================================================
# 15. PESTAÑA SEXO BIOLÓGICO
# =====================================================

with tab3:

    columna = "SEXO BIOLOGICO"

    conteo = preparar_conteo(df_filtrado, columna)

    st.subheader("Análisis por sexo biológico")

    st.markdown(
        f'<div class="texto-descriptivo">'
        f'{random.choice(descripciones[columna])}'
        f'</div>',
        unsafe_allow_html=True
    )

    if not conteo.empty:

        izquierda, derecha = st.columns([1.3, 1])

        with izquierda:

            fig = px.bar(
                conteo.sort_values(
                    "Estudiantes",
                    ascending=True
                ),
                x="Estudiantes",
                y="Categoría",
                orientation="h",
                text="Estudiantes",
                color="Categoría",
                color_discrete_sequence=PALETA
            )

            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
                cliponaxis=False
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Número de estudiantes",
                yaxis_title="",
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#F3E2E5"
                )
            )

            configurar_grafico(
                fig,
                "Distribución de estudiantes"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with derecha:

            fig = px.pie(
                conteo,
                names="Categoría",
                values="Estudiantes",
                hole=0.65,
                color_discrete_sequence=PALETA
            )

            fig.update_traces(
                textinfo="percent",
                textposition="inside",
                marker=dict(
                    line=dict(color="white", width=3)
                )
            )

            configurar_grafico(
                fig,
                "Composición porcentual"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.info("No hay registros disponibles con estos filtros.")


# =====================================================
# 16. TABLA GENERAL OCULTA
# =====================================================

st.divider()

with st.expander(
    "📋 Consultar base de datos filtrada",
    expanded=False
):

    st.caption(
        "Consulta los registros que corresponden "
        "a los filtros seleccionados."
    )

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )

    st.write(
        f"Total de registros: {len(df_filtrado):,}"
    )


# =====================================================
# 17. PIE DE PÁGINA
# =====================================================

st.sidebar.divider()

st.sidebar.caption("Dashboard institucional")
st.sidebar.caption("Análisis de estudiantes matriculados")