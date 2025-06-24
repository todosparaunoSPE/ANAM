# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 18:26:59 2025

@author: jahop
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración general
st.set_page_config(page_title="ANAM - Evaluación de Riesgos Aduanales", layout="wide")
st.title("🛂 ANÁLISIS TÉCNICO Y LEGAL DE OPERACIONES ADUANALES")
st.markdown("Simulación de panel para el **puesto de Analista en ANAM - El Marqués, Qro.**")

# Generar datos simulados
@st.cache_data
def cargar_datos():
    data = {
        "Fecha": pd.date_range(start="2024-06-01", periods=20, freq='D'),
        "Aduana": ["Nuevo Laredo", "Manzanillo", "Veracruz", "CDMX"] * 5,
        "País Origen": ["China", "EE.UU.", "Venezuela", "Alemania", "Irán"] * 4,
        "Producto": ["Celulares", "Reactivos químicos", "Refacciones", "Ropa", "Computadoras"] * 4,
        "Valor USD": [25000, 120000, 15000, 8000, 90000] * 4,
        "Empresa": ["TecnoSA", "Químicos MX", "MotorMex", "Textiles SA", "InnovaTech"] * 4,
        "Tipo": ["Importación", "Importación", "Exportación", "Importación", "Exportación"] * 4,
        "Código Arancelario": ["8517.12.99", "3822.00.01", "8708.99.99", "6201.11.00", "8471.30.01"] * 4
    }
    df = pd.DataFrame(data)

    # Asignar riesgo legal simulado
    condiciones_alto = (df["Valor USD"] > 100000) | (df["País Origen"].isin(["Venezuela", "Irán"])) | (df["Código Arancelario"].isin(["3822.00.01"]))
    condiciones_medio = (df["Valor USD"].between(80000, 100000)) & ~condiciones_alto
    df["Riesgo Legal"] = "Bajo"
    df.loc[condiciones_medio, "Riesgo Legal"] = "Medio"
    df.loc[condiciones_alto, "Riesgo Legal"] = "Alto"
    return df

df = cargar_datos()

# Sidebar - Filtros
st.sidebar.header("🔎 Filtros")
aduanas = st.sidebar.multiselect("Aduana", options=df["Aduana"].unique(), default=df["Aduana"].unique())
riesgos = st.sidebar.multiselect("Riesgo Legal", options=df["Riesgo Legal"].unique(), default=df["Riesgo Legal"].unique())

# Filtro por fecha
fechas = st.sidebar.date_input("Filtrar por rango de fechas", [df["Fecha"].min(), df["Fecha"].max()])
if len(fechas) == 2:
    df = df[(df["Fecha"] >= pd.to_datetime(fechas[0])) & (df["Fecha"] <= pd.to_datetime(fechas[1]))]

# Filtro por empresa y producto
empresa_buscada = st.sidebar.text_input("Buscar empresa")
producto_buscado = st.sidebar.text_input("Buscar producto")

df_filtro = df[(df["Aduana"].isin(aduanas)) & (df["Riesgo Legal"].isin(riesgos))]

if empresa_buscada:
    df_filtro = df_filtro[df_filtro["Empresa"].str.contains(empresa_buscada, case=False)]

if producto_buscado:
    df_filtro = df_filtro[df_filtro["Producto"].str.contains(producto_buscado, case=False)]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("🚢 Operaciones Totales", len(df_filtro))
col2.metric("💲 Valor Total (USD)", f"${df_filtro['Valor USD'].sum():,.0f}")
col3.metric("⚖️ Riesgo Alto", df_filtro[df_filtro["Riesgo Legal"] == "Alto"].shape[0])

# Cumplimiento normativo
df_filtro["Cumplimiento"] = df_filtro["Riesgo Legal"].apply(lambda x: "No cumple" if x == "Alto" else "Cumple")

# Tabla
st.subheader("📋 Detalle de operaciones filtradas")
st.dataframe(df_filtro, use_container_width=True)

# Gráfico 1 - Valor por Aduana
fig1 = px.bar(df_filtro.groupby("Aduana")["Valor USD"].sum().reset_index(),
              x="Aduana", y="Valor USD", title="Valor Total por Aduana")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2 - Distribución por Riesgo
fig2 = px.pie(df_filtro, values="Valor USD", names="Riesgo Legal", title="Distribución de Riesgo Legal")
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3 - Evolución temporal
fig_line = px.line(df_filtro, x="Fecha", y="Valor USD", color="Aduana", title="Evolución de valor aduanal por día")
st.plotly_chart(fig_line, use_container_width=True)

# Mapa de operaciones por aduana
st.subheader("🗺️ Mapa de Operaciones por Aduana")
coordenadas = {
    "Nuevo Laredo": (27.5, -99.5),
    "Manzanillo": (19.05, -104.3),
    "Veracruz": (19.2, -96.1),
    "CDMX": (19.43, -99.13)
}
df_mapa = df_filtro.groupby("Aduana")["Valor USD"].sum().reset_index()
df_mapa["Lat"] = df_mapa["Aduana"].map(lambda x: coordenadas[x][0])
df_mapa["Lon"] = df_mapa["Aduana"].map(lambda x: coordenadas[x][1])
st.map(df_mapa.rename(columns={"Lat": "latitude", "Lon": "longitude"}))

# Descarga CSV
st.download_button(
    label="📥 Descargar resultados filtrados (CSV)",
    data=df_filtro.to_csv(index=False).encode('utf-8'),
    file_name="reporte_aduanal.csv",
    mime="text/csv"
)

# Explicación de criterios de riesgo
with st.expander("📚 Criterios de clasificación de riesgo legal"):
    st.markdown("""
    **Riesgo Alto:**
    - Valor mayor a $100,000 USD
    - Países con alertas: Venezuela, Irán
    - Productos químicos o estratégicos

    **Riesgo Medio:**
    - Valor entre $80,000 y $100,000 USD

    **Riesgo Bajo:**
    - Operaciones comunes y/o con valores menores a $80,000 USD
    """)

# Resumen automático
st.markdown("### 🧠 Resumen del análisis:")
st.markdown(f"""
- Se analizaron **{len(df_filtro)} operaciones**.
- El valor total fue de **${df_filtro['Valor USD'].sum():,.0f} USD**.
- Se detectaron **{(df_filtro['Riesgo Legal'] == 'Alto').sum()} operaciones con riesgo legal alto**.
- Las aduanas con mayor valor fueron: **{', '.join(df_filtro.groupby('Aduana')['Valor USD'].sum().nlargest(2).index)}**.
""")

# Footer
st.markdown("---")
st.markdown("🧑‍⚖️ **Simulación técnica y legal para postulación a Analista ANAM** | Elaborado por: Javier Horacio Pérez Ricárdez")
