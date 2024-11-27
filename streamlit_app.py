import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Configurações da página no Streamlit
st.set_page_config(
    page_title='Empenhos do Governo Federal - Dashboard',  # Título da página
    page_icon=':bar_chart:',  # Ícone exibido no navegador
    layout="wide"  # Layout largo
)

# Função para carregar os dados com caching para melhorar desempenho
@st.cache_data
def get_empenhos_data():
    """Carrega os dados de empenhos do arquivo Excel (.xlsx)."""
    DATA_FILENAME = Path(__file__).parent / 'data/202401_Empenhos.xlsx'  # Caminho relativo do arquivo
    raw_df = pd.read_excel(DATA_FILENAME)  # Lê o arquivo Excel
    return raw_df

# Função para formatar valores em reais
def formatar_real(valor):
    """Formata valores para o formato monetário brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # Troca . e , conforme o padrão brasileiro

# Função para adicionar unidades aos valores
def adicionar_unidade(valor):
    """Adiciona a unidade 'milhões' ou 'bilhões' ao final do valor sem abreviá-lo."""
    if valor >= 1e9:
        return f"{formatar_real(valor)} (bilhões)"  # Adiciona "(bilhões)" para valores acima de 1 bilhão
    elif valor >= 1e6:
        return f"{formatar_real(valor)} (milhões)"  # Adiciona "(milhões)" para valores acima de 1 milhão
    else:
        return formatar_real(valor)  # Formata valores menores normalmente

# Adiciona estilo customizado para tooltips dos gráficos Altair
tooltip_css = """
<style>
    .vega-tooltip {
        font-size: 14px !important;
        max-width: 400px !important;
        white-space: normal !important;
    }
</style>
"""
st.markdown(tooltip_css, unsafe_allow_html=True)

# Carrega os dados usando a função com cache
df = get_empenhos_data()

# Pré-processamento dos dados
df['Valor do Empenho Convertido pra R$'] = pd.to_numeric(
    df['Valor do Empenho Convertido pra R$'], errors='coerce'  # Converte para numérico, tratando erros
)
df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], errors='coerce')  # Converte para formato de data

# Criação da seção de filtros na barra lateral
st.sidebar.header("Filtros")  # Título na barra lateral
# Filtro por período
start_date, end_date = st.sidebar.date_input(
    'Selecione o período',
    value=(df['Data Emissão'].min(), df['Data Emissão'].max())  # Valores padrão baseados nos dados
)
# Filtra os dados com base no período selecionado
filtered_df = df[(df['Data Emissão'] >= pd.to_datetime(start_date)) & (df['Data Emissão'] <= pd.to_datetime(end_date))]

# Filtro por categorias econômicas
categories = filtered_df['Categoria de Despesa'].unique()  # Obtém categorias únicas
selected_categories = st.sidebar.multiselect(
    'Selecione as categorias econômicas',
    categories,  # Opções disponíveis
    categories.tolist()  # Seleciona todas por padrão
)
filtered_df = filtered_df[filtered_df['Categoria de Despesa'].isin(selected_categories)]  # Filtra os dados

# Título e resumo do dashboard
st.title("Dashboard de Análise de Empenhos")  # Título principal do app
st.metric(
    label="Total de valores empenhados (filtro aplicado)",  # Rótulo do indicador
    value=adicionar_unidade(filtered_df['Valor do Empenho Convertido pra R$'].sum())  # Soma dos valores filtrados
)

# Divisão da página em colunas para organização dos gráficos
col1, col2 = st.columns(2)

# Gráfico de evolução dos valores empenhados
with col1:
    st.subheader("Evolução dos Valores Empenhados")  # Subtítulo
    evolution_df = filtered_df.groupby(['Data Emissão'])['Valor do Empenho Convertido pra R$'].sum().reset_index()
    evolution_df['Valor Formatado'] = evolution_df['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)
    evolution_chart = (
        alt.Chart(evolution_df)
        .mark_line(point=True)  # Gráfico de linha com pontos
        .encode(
            x=alt.X('Data Emissão:T', title='Data'),  # Eixo X com formato de data
            y=alt.Y('Valor do Empenho Convertido pra R$:Q', title='Valor Empenhado (R$)'),  # Eixo Y com valores
            tooltip=[  # Tooltip com informações detalhadas
                alt.Tooltip('Data Emissão:T', title='Data'),
                alt.Tooltip('Valor Formatado:N', title='Valor')
            ]
        )
        .properties(width=700, height=400)  # Tamanho do gráfico
    )
    st.altair_chart(evolution_chart, use_container_width=True)  # Exibe o gráfico no Streamlit

# Gráfico dos maiores beneficiários
with col2:
    st.subheader("Maiores Beneficiários")  # Subtítulo
    top_beneficiaries = (
        filtered_df.groupby('Favorecido')['Valor do Empenho Convertido pra R$']
        .sum()
        .reset_index()
        .sort_values(by='Valor do Empenho Convertido pra R$', ascending=False)
        .head(10)  # Seleciona os 10 maiores beneficiários
    )
    top_beneficiaries['Valor Formatado'] = top_beneficiaries['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)
    beneficiaries_chart = (
        alt.Chart(top_beneficiaries)
        .mark_bar()  # Gráfico de barras
        .encode(
            x=alt.X('Valor do Empenho Convertido pra R$:Q', title='Valor (R$)'),  # Eixo X
            y=alt.Y('Favorecido:N', sort='-x', title='Favorecido'),  # Eixo Y
            tooltip=[alt.Tooltip('Favorecido:N'), alt.Tooltip('Valor Formatado:N')]  # Tooltip
        )
        .properties(width=700, height=400)
    )
    st.altair_chart(beneficiaries_chart, use_container_width=True)

# Seção para outros gráficos
col1, col2 = st.columns(2)

# Gráfico de comparação por órgão governamental
with col1:
    st.subheader("Comparação por Órgão Governamental")
    organs_df = (
        filtered_df.groupby('Órgão')['Valor do Empenho Convertido pra R$']
        .sum()
        .reset_index()
        .sort_values(by='Valor do Empenho Convertido pra R$', ascending=False)
        .head(10)  # Seleciona os 10 maiores órgãos
    )
    organs_df['Valor Formatado'] = organs_df['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)
    organs_chart = (
        alt.Chart(organs_df)
        .mark_bar()
        .encode(
            x=alt.X('Órgão:N', sort='-y', title='Órgão'),  # Eixo X
            y=alt.Y('Valor do Empenho Convertido pra R$:Q', title='Valor (R$)'),  # Eixo Y
            tooltip=[alt.Tooltip('Órgão:N'), alt.Tooltip('Valor Formatado:N')]
        )
        .properties(width=700, height=400)
    )
    st.altair_chart(organs_chart, use_container_width=True)

# Gráfico de distribuição por categoria econômica
with col2:
    st.subheader("Distribuição por Categoria Econômica")
    category_distribution = (
        filtered_df.groupby('Categoria de Despesa')['Valor do Empenho Convertido pra R$']
        .sum()
        .reset_index()
    )
    category_distribution['Valor Formatado'] = category_distribution['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)
    category_chart = (
        alt.Chart(category_distribution)
        .mark_arc()  # Gráfico de pizza
        .encode(
            theta=alt.Theta('Valor do Empenho Convertido pra R$:Q', title='Valor (R$)'),  # Ângulo proporcional ao valor
            color=alt.Color('Categoria de Despesa:N', legend=None),  # Cor por categoria
            tooltip=[
                alt.Tooltip('Categoria de Despesa:N', title='Categoria'),
                alt.Tooltip('Valor Formatado:N', title='Valor')
            ]
        )
        .properties(width=700, height=400)
    )
    st.altair_chart(category_chart, use_container_width=True)
