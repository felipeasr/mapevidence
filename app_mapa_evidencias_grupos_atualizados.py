import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mapa de Evidências", layout="wide")

# === 1) Carrega dados ===
df = pd.read_excel("mapa_de_evidencias_com_paises_e_bases.xlsx")
df["Tamanho"] = 1

# === 2) Limpeza dos níveis de confiança ===
# Remove espaços em branco e padroniza a caixa (title case)
df["Nível de Confiança"] = (
    df["Nível de Confiança"]
    .astype(str)
    .str.strip()
    .str.title()
)

# (Opcional: para ver se sobrou alguma categoria estranha)
st.sidebar.write("Categorias encontradas:", df["Nível de Confiança"].unique())

# === 3) Filtros na sidebar ===
with st.sidebar:
    st.header("🔍 Filtros")
    pais = st.selectbox("🌍 País", ["Todos"] + sorted(df["País"].dropna().unique()))
    populacao = st.selectbox("👥 População", ["Todos"] + sorted(df["População"].dropna().unique()))
    efeito = st.selectbox("⚠️ Efeito Adverso", ["Todos"] + sorted(df["Efeito Adverso"].dropna().unique()))
    grupo_interv = st.selectbox("🧩 Grupo de Intervenção", ["Todos"] + sorted(df["Grupo de Intervenção"].dropna().unique()))

# Aplica os filtros
df_filtrado = df.copy()
if pais != "Todos":
    df_filtrado = df_filtrado[df_filtrado["País"] == pais]
if populacao != "Todos":
    df_filtrado = df_filtrado[df_filtrado["População"] == populacao]
if efeito != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Efeito Adverso"] == efeito]
if grupo_interv != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Grupo de Intervenção"] == grupo_interv]

# === 4) Cabeçalho e contagem ===
st.title("📊 Mapa de Evidências em Oncologia")
st.markdown(f"**Total de estudos únicos:** {df_filtrado['Título'].nunique()}")

# === 5) Ordenação dos eixos ===
ordem_y = (
    df_filtrado[["Grupo de Intervenção", "Intervenção Ordenada"]]
    .drop_duplicates()
    .assign(GrupoRank=lambda d: d["Grupo de Intervenção"].rank(method="dense").astype(int))
    .sort_values(["GrupoRank", "Intervenção Ordenada"])
)
ordem_y_list = ordem_y["Intervenção Ordenada"].tolist()
ordem_x = df_filtrado.sort_values(by=["Grupo de Desfecho", "Desfecho"])["Desfecho"].unique()

# === 6) Criação do gráfico com cores fixas ===
fig = px.scatter(
    df_filtrado,
    x="Desfecho",
    y="Intervenção Ordenada",
    size="Tamanho",
    color="Nível de Confiança",
    hover_data=["Grupo de Intervenção", "Grupo de Desfecho", "Título", "Ano", "Resultado (Efeito)"],
    category_orders={
        "Desfecho": ordem_x,
        "Intervenção Ordenada": ordem_y_list
    },
    size_max=20,
    height=900,
    color_discrete_map={
        "Muito Baixo": "#FF4D4D",
        "Baixo":       "#FF9999",
        "Moderado":    "#4D79FF",
        "Alto":        "#3366FF",
        "Muito Alto":  "#0033CC",
    }
)

# Adiciona linhas horizontais para separar grupos
y_positions = []
prev = None
for _, row in ordem_y.iterrows():
    if prev and row["Grupo de Intervenção"] != prev:
        y_positions.append(row["Intervenção Ordenada"])
    prev = row["Grupo de Intervenção"]

for y in y_positions:
    fig.add_shape(
        type="line",
        x0=-0.5, x1=len(ordem_x) - 0.5,
        y0=y, y1=y,
        line=dict(color="gray", width=1, dash="dot"),
        xref="x", yref="y",
    )

fig.update_layout(
    xaxis_title="Desfechos (agrupados)",
    yaxis_title="Grupos de Intervenção | Intervenções",
    margin=dict(l=40, r=40, t=40, b=40),
)

# === 7) Exibe o gráfico e a tabela ===
st.plotly_chart(fig, use_container_width=True)

with st.expander("📋 Ver tabela de dados"):
    st.dataframe(df_filtrado)
