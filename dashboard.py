import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import io

# Configuração da página do Streamlit
st.set_page_config(layout="wide")

# --- Título do Dashboard ---
st.title("Dashboard do Mercado de Combustíveis - Rio de Janeiro")
st.markdown("Análise da distribuição de postos por bandeira, volume de vendas e tendências temporais.")


# --- Carregamento e Cache dos Dados ---
@st.cache_data
def carregar_dados():
    # Cabeçalho para simular um navegador e evitar erro 404
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Carrega dados cadastrais dos postos
    try:
        url_postos = ("https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-dados-cadastrais-dos-revendedores-varejistas-de-combustiveis-automotivos/dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv")
        response_postos = requests.get(url_postos, headers=headers)
        response_postos.raise_for_status()
        df_postos = pd.read_csv(io.StringIO(response_postos.text), sep=";", dtype=str, encoding='latin-1', on_bad_lines='skip')
        df_postos_rj = df_postos[df_postos["UF"] == "RJ"].copy()
    except Exception as e:
        st.error(f"Erro ao carregar os dados de cadastro da ANP: {e}")
        df_postos_rj = pd.DataFrame()

    # Carrega dados de vendas
    try:
        url_vendas = "https://github.com/filipe381/Ap1Tic/releases/download/dados/liquidos_Vendas_Atual.csv"
        response_vendas = requests.get(url_vendas, headers=headers)
        response_vendas.raise_for_status()
        df_vendas = pd.read_csv(io.StringIO(response_vendas.text), sep=";", dtype=str, encoding='latin-1', on_bad_lines='skip')
        col_quantidade = 'Quantidade de Produto (mil m³)'
        df_vendas[col_quantidade] = df_vendas[col_quantidade].str.replace(',', '.').astype(float)
        df_vendas_rj = df_vendas[df_vendas["UF Destino"] == "RJ"].copy()
    except Exception as e:
        st.error(f"Erro ao carregar os dados de vendas do GitHub: {e}")
        df_vendas_rj = pd.DataFrame()

    # --- NOVA ANÁLISE TEMPORAL ---
    # Prepara os dados para o gráfico de crescimento de postos
    if not df_postos_rj.empty:
        df_postos_rj['Data de Vinculação'] = pd.to_datetime(df_postos_rj['DATAVINCULACAO'], errors='coerce', format='%d/%m/%Y')
        df_postos_rj.dropna(subset=['Data de Vinculação'], inplace=True)
        df_postos_rj['Ano de Vinculação'] = df_postos_rj['Data de Vinculação'].dt.year
        df_postos_recentes = df_postos_rj[df_postos_rj['Ano de Vinculação'] >= 2000]
        postos_por_ano = df_postos_recentes.groupby(['Ano de Vinculação', 'BANDEIRA']).size().reset_index(name='Novos Postos')
        postos_por_ano['Total Acumulado'] = postos_por_ano.groupby('BANDEIRA')['Novos Postos'].cumsum()
        top_bandeiras = df_postos_recentes['BANDEIRA'].value_counts().nlargest(4).index
        df_crescimento_postos = postos_por_ano[postos_por_ano['BANDEIRA'].isin(top_bandeiras)]
    else:
        df_crescimento_postos = pd.DataFrame()

    return df_postos_rj, df_vendas_rj, df_crescimento_postos


# Carrega os dataframes
df_postos, df_vendas, df_crescimento_postos = carregar_dados()

# --- Barra Lateral de Filtros (Sidebar) ---
st.sidebar.header("Filtros")
if not df_postos.empty:
    municipios = ["Todos"] + sorted(df_postos["MUNICIPIO"].unique().tolist())
    municipio_selecionado = st.sidebar.selectbox("Selecione o Município:", municipios)

    # Aplica o filtro de município
    if municipio_selecionado != "Todos":
        df_postos_filtrado = df_postos[df_postos["MUNICIPIO"] == municipio_selecionado]
    else:
        df_postos_filtrado = df_postos
else:
    df_postos_filtrado = pd.DataFrame()
    st.sidebar.warning("Dados de postos não disponíveis para filtro.")


# --- Análises com base nos filtros ---
if not df_postos_filtrado.empty:
    contagem_bandeiras = df_postos_filtrado.groupby("BANDEIRA").size().sort_values(ascending=False)
else:
    contagem_bandeiras = pd.Series()

if not df_vendas.empty:
    volume_por_agemte = df_vendas.groupby("Agente Regulado")["Quantidade de Produto (mil m³)"].sum().sort_values(ascending=False)
else:
    volume_por_agemte = pd.Series()


# --- Exibição dos KPIs (Key Performance Indicators) ---
st.header(f"Resumo para: {municipio_selecionado if 'municipio_selecionado' in locals() else 'Todos'}")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Postos", f"{df_postos_filtrado.shape[0]:,}")
col2.metric("Nº de Bandeiras Diferentes", f"{len(contagem_bandeiras)}")
if not volume_por_agemte.empty:
    col3.metric("Volume Total Vendido no RJ (mil m³)", f"{volume_por_agemte.sum():,.2f}")

st.markdown("---")

# --- Layout dos Gráficos ---
st.header("Análise de Market Share (Cenário Atual)")
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not contagem_bandeiras.empty:
        st.subheader("Top 15 Bandeiras por Nº de Postos")
        top_15_bandeiras = contagem_bandeiras.head(15)
        fig1, ax1 = plt.subplots(figsize=(10, 8))
        sns.barplot(x=top_15_bandeiras.values, y=top_15_bandeiras.index, ax=ax1, palette="viridis", orient='h')
        ax1.set_xlabel("Quantidade de Postos")
        ax1.set_ylabel("Bandeira")
        plt.tight_layout()
        st.pyplot(fig1)
        with st.expander("Ver todos os dados"):
            st.dataframe(contagem_bandeiras)

with col_graf2:
    if not volume_por_agemte.empty:
        st.subheader("Top 15 Agentes por Volume de Vendas")
        top_15_volume = volume_por_agemte.head(15)
        fig2, ax2 = plt.subplots(figsize=(10, 8))
        sns.barplot(x=top_15_volume.values, y=top_15_volume.index, ax=ax2, palette="plasma", orient='h')
        ax2.set_xlabel("Volume Vendido (mil m³)")
        ax2.set_ylabel("Agente Regulado")
        plt.tight_layout()
        st.pyplot(fig2)
        with st.expander("Ver todos os dados"):
            st.dataframe(volume_por_agemte)

st.markdown("---")

# --- NOVA SEÇÃO: ANÁLISE TEMPORAL ---
st.header("Análise Temporal de Crescimento (Estado do RJ)")

if not df_crescimento_postos.empty:
    st.subheader("Crescimento Acumulado do Nº de Postos das Maiores Bandeiras (a partir de 2000)")

    fig3, ax3 = plt.subplots(figsize=(12, 7))
    sns.lineplot(data=df_crescimento_postos, x='Ano de Vinculação', y='Total Acumulado', hue='BANDEIRA', marker='o', palette='plasma', ax=ax3)
    ax3.set_title('Crescimento Acumulado do Número de Postos das Maiores Bandeiras', fontsize=16)
    ax3.set_ylabel('Número Total de Postos (Acumulado)')
    ax3.set_xlabel('Ano')
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.legend(title='Bandeira')
    plt.tight_layout()
    st.pyplot(fig3)

    with st.expander("Ver dados da análise de crescimento"):
        st.dataframe(df_crescimento_postos)
else:
    st.warning("Dados para a análise de crescimento não puderam ser calculados.")