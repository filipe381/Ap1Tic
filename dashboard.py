import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página do Streamlit
st.set_page_config(layout="wide")

# --- Título do Dashboard ---
st.title("📊 Dashboard do Mercado de Combustíveis - Rio de Janeiro")
st.markdown("Análise da distribuição de postos por bandeira e volume de vendas por agente regulado.")


# --- Carregamento e Cache dos Dados ---
# Usar o cache do Streamlit acelera o app, pois os dados não são recarregados a cada interação.
@st.cache_data
def carregar_dados():
    # Carrega dados cadastrais dos postos (isso não muda)
    url_postos = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-dados-cadastrais-dos-revendedores-varejistas-de-combustiveis-automotivos/dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv"
    df_postos = pd.read_csv(url_postos, sep=";", dtype=str, encoding='latin-1')
    df_postos_rj = df_postos[df_postos["UF"] == "RJ"].copy()

    url_vendas = "https://github.com/filipe381/Ap1Tic/releases/download/dados/liquidos_Vendas_Atual.csv"

    try:
        df_vendas = pd.read_csv(url_vendas, sep=";", dtype=str, encoding='latin-1')
        # Limpeza e conversão da coluna de quantidade
        col_quantidade = 'Quantidade de Produto (mil m³)'
        if col_quantidade in df_vendas.columns:
            df_vendas[col_quantidade] = df_vendas[col_quantidade].str.replace(',', '.').astype(float)
        df_vendas_rj = df_vendas[df_vendas["UF Destino"] == "RJ"].copy()
    except Exception as e:
        # Mostra um erro mais detalhado se o download falhar
        st.error(f"Erro ao carregar os dados de vendas da URL: {e}")
        df_vendas_rj = pd.DataFrame()

    return df_postos_rj, df_vendas_rj


# Carrega os dataframes
df_postos, df_vendas = carregar_dados()

# --- Barra Lateral de Filtros (Sidebar) ---
st.sidebar.header("Filtros")
municipios = ["Todos"] + sorted(df_postos["MUNICIPIO"].unique().tolist())
municipio_selecionado = st.sidebar.selectbox("Selecione o Município:", municipios)

# Aplica o filtro de município
if municipio_selecionado != "Todos":
    df_postos_filtrado = df_postos[df_postos["MUNICIPIO"] == municipio_selecionado]
else:
    df_postos_filtrado = df_postos

# --- Análises com base nos filtros ---
# Contagem de postos por bandeira
contagem_bandeiras = df_postos_filtrado.groupby("BANDEIRA").size().sort_values(ascending=False)

# Soma de volume por agente (Este dado não é filtrado por município, pois o dataset de vendas não tem essa coluna)
if not df_vendas.empty:
    volume_por_agente = df_vendas.groupby("Agente Regulado")["Quantidade de Produto (mil m³)"].sum().sort_values(
        ascending=False)
else:
    volume_por_agente = pd.Series()

# --- Exibição dos KPIs (Key Performance Indicators) ---
st.header(f"Resumo para: {municipio_selecionado}")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Postos", f"{df_postos_filtrado.shape[0]:,}")
col2.metric("Nº de Bandeiras Diferentes", f"{len(contagem_bandeiras)}")
if not df_vendas.empty:
    col3.metric("Volume Total Vendido no RJ (mil m³)", f"{volume_por_agente.sum():,.2f}")

st.markdown("---")

# --- Layout dos Gráficos ---
st.header("Visualizações Detalhadas")
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Top 15 Bandeiras por Nº de Postos")

    # Gráfico de Barras - Bandeiras
    top_15_bandeiras = contagem_bandeiras.head(15)
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    sns.barplot(x=top_15_bandeiras.values, y=top_15_bandeiras.index, ax=ax1, palette="viridis", orient='h')
    ax1.set_xlabel("Quantidade de Postos")
    ax1.set_ylabel("Bandeira")
    plt.tight_layout()
    st.pyplot(fig1)

    with st.expander("Ver dados de Postos por Bandeira"):
        st.dataframe(contagem_bandeiras)

with col_graf2:
    if not volume_por_agente.empty:
        st.subheader("Top 15 Agentes por Volume de Vendas (RJ)")

        # Gráfico de Barras - Volume
        top_15_volume = volume_por_agente.head(15)
        fig2, ax2 = plt.subplots(figsize=(10, 8))
        sns.barplot(x=top_15_volume.values, y=top_15_volume.index, ax=ax2, palette="plasma", orient='h')
        ax2.set_xlabel("Volume Vendido (mil m³)")
        ax2.set_ylabel("Agente Regulado")
        plt.tight_layout()
        st.pyplot(fig2)

        with st.expander("Ver dados de Volume por Agente"):
            st.dataframe(volume_por_agente)
    else:
        st.warning("Dados de vendas não disponíveis para exibir o gráfico de volume.")