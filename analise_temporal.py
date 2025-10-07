import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def analisar_dados():
    # --- Análise 1: Volume de Vendas por Ano ---
    print("--- Iniciando Análise 1: Market Share de Volume de Vendas por Ano ---")
    try:
        # URL do seu GitHub Release
        url_vendas = "https://github.com/filipe381/Ap1Tic/releases/download/dados/liquidos_Vendas_Atual.csv"
        df_vendas = pd.read_csv(url_vendas, sep=";", dtype=str, encoding='latin-1', on_bad_lines='skip')

        col_quantidade = 'Quantidade de Produto (mil m³)'
        df_vendas[col_quantidade] = df_vendas[col_quantidade].str.replace(',', '.').astype(float)
        df_vendas['Ano'] = pd.to_numeric(df_vendas['Ano'], errors='coerce')
        df_vendas.dropna(subset=['Ano'], inplace=True)
        df_vendas['Ano'] = df_vendas['Ano'].astype(int)

        if df_vendas['Ano'].nunique() > 1:
            print(
                "\n[CONCLUSÃO ANÁLISE 1]: Boa notícia! Seu arquivo de vendas contém dados de múltiplos anos e É SUFICIENTE para uma análise temporal de market share.\n")
            # Restante do código para gerar o gráfico...
            vendas_por_ano_agente = df_vendas.groupby(['Ano', 'Agente Regulado'])[col_quantidade].sum().reset_index()
            total_vendas_ano = df_vendas.groupby('Ano')[col_quantidade].sum().reset_index().rename(
                columns={col_quantidade: 'Total Ano'})
            df_market_share = pd.merge(vendas_por_ano_agente, total_vendas_ano, on='Ano')
            df_market_share['Market Share (%)'] = (df_market_share[col_quantidade] / df_market_share['Total Ano']) * 100
            top_agentes = df_market_share.groupby('Agente Regulado')['Market Share (%)'].mean().nlargest(4).index
            df_plot = df_market_share[df_market_share['Agente Regulado'].isin(top_agentes)]

            plt.figure(figsize=(12, 7))
            sns.lineplot(data=df_plot, x='Ano', y='Market Share (%)', hue='Agente Regulado', marker='o',
                         palette='viridis')
            plt.title('Evolução do Market Share (Volume de Vendas) dos Maiores Agentes', fontsize=16)
            plt.ylabel('Participação de Mercado (%)')
            plt.xlabel('Ano')
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(title='Agente Regulado')
            plt.tight_layout()
            plt.savefig('market_share_vendas_por_ano.png')
            print("Gráfico 'market_share_vendas_por_ano.png' foi gerado.")
        else:
            print(
                "\n[CONCLUSÃO ANÁLISE 1]: Atenção! Seu arquivo de vendas contém dados de apenas um ano. Ele NÃO É SUFICIENTE para uma análise de evolução ao longo do tempo.\n")
    except Exception as e:
        print(f"\n[ERRO ANÁLISE 1]: Não foi possível processar o arquivo de vendas. Erro: {e}\n")

    # --- Análise 2: Número de Postos por Ano ---
    print("\n--- Iniciando Análise 2: Evolução da Quantidade de Postos por Bandeira ---")
    try:
        # ...

        url_postos = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-dados-cadastrais-dos-revendedores-varejistas-de-combustiveis-automotivos/dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv"
        df_postos = pd.read_csv(url_postos, sep=";" , dtype=str)
    # ...
        df_postos['Data de Vinculação'] = pd.to_datetime(df_postos['DATAVINCULACAO'], errors='coerce',
                                                         format='%d/%m/%Y')
        df_postos.dropna(subset=['Data de Vinculação'], inplace=True)
        df_postos['Ano de Vinculação'] = df_postos['Data de Vinculação'].dt.year
        df_postos_recentes = df_postos[df_postos['Ano de Vinculação'] >= 2000]

        postos_por_ano = df_postos_recentes.groupby(['Ano de Vinculação', 'BANDEIRA']).size().reset_index(
            name='Novos Postos')
        postos_por_ano['Total Acumulado'] = postos_por_ano.groupby('BANDEIRA')['Novos Postos'].cumsum()

        top_bandeiras = df_postos_recentes['BANDEIRA'].value_counts().nlargest(4).index
        df_plot_postos = postos_por_ano[postos_por_ano['BANDEIRA'].isin(top_bandeiras)]

        plt.figure(figsize=(12, 7))
        sns.lineplot(data=df_plot_postos, x='Ano de Vinculação', y='Total Acumulado', hue='BANDEIRA', marker='o',
                     palette='plasma')
        plt.title('Crescimento Acumulado do Número de Postos das Maiores Bandeiras (a partir de 2000)', fontsize=16)
        plt.ylabel('Número Total de Postos (Acumulado)')
        plt.xlabel('Ano')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(title='Bandeira')
        plt.tight_layout()
        plt.savefig('crescimento_postos_por_ano.png')
        print("Gráfico 'crescimento_postos_por_ano.png' foi gerado.")
        print("\n[CONCLUSÃO ANÁLISE 2]: Os dados cadastrais de postos SÃO SUFICIENTES para a análise temporal.\n")
    except Exception as e:
        print(f"\n[ERRO ANÁLISE 2]: Não foi possível processar o arquivo de cadastro de postos. Erro: {e}\n")


# Executa a função de análise
if __name__ == "__main__":
    analisar_dados()