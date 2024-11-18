import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Configurações da página no Streamlit
st.set_page_config(
    page_title='Empenhos do Governo Federal - Dashboard',
    page_icon=':bar_chart:',
)

@st.cache_data
def get_empenhos_data():
    """Carrega os dados de empenhos do arquivo Excel (.xlsx)."""
    DATA_FILENAME = Path(__file__).parent / 'data/202401_Empenhos.xlsx'
    raw_df = pd.read_excel(DATA_FILENAME)
    return raw_df

# Função para formatar valores monetários
def formatar_real(valor):
    """Formata valores para o formato monetário brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para adicionar a unidade (milhões ou bilhões) ao final
def adicionar_unidade(valor):
    """Adiciona a unidade 'milhões' ou 'bilhões' ao final do valor."""
    if valor >= 1e9:
        return f"{formatar_real(valor)} (bilhões)"
    elif valor >= 1e6:
        return f"{formatar_real(valor)} (milhões)"
    else:
        return formatar_real(valor)

# Carregar os dados de empenhos
df = get_empenhos_data()

# Converter a coluna de valores para float e a coluna de datas
df['Valor do Empenho Convertido pra R$'] = pd.to_numeric(
    df['Valor do Empenho Convertido pra R$'], errors='coerce'
)
df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], errors='coerce')

# Filtro de período de dias
st.header('Filtro por Período de Dias')
start_date, end_date = st.date_input(
    'Selecione o período',
    value=(df['Data Emissão'].min(), df['Data Emissão'].max())
)

# Aplicar o filtro de período de dias
filtered_df = df[(df['Data Emissão'] >= pd.to_datetime(start_date)) & (df['Data Emissão'] <= pd.to_datetime(end_date))]

# Filtro de categorias econômicas
categories = filtered_df['Categoria de Despesa'].unique()
selected_categories = st.multiselect(
    'Selecione as categorias econômicas',
    categories,
    categories.tolist()
)

# Filtrar os dados com base na categoria
filtered_df = filtered_df[filtered_df['Categoria de Despesa'].isin(selected_categories)]

# Mostrar todos os valores considerados para os cálculos
st.header('Valores Considerados para os Cálculos', divider='gray')
filtered_df_display = filtered_df.copy()
filtered_df_display['Valor do Empenho Convertido pra R$'] = filtered_df_display[
    'Valor do Empenho Convertido pra R$'
].apply(adicionar_unidade)
st.write(filtered_df_display[['Id Empenho', 'Data Emissão', 'Categoria de Despesa', 'Valor do Empenho Convertido pra R$']])

# Gráfico de evolução dos valores empenhados ao longo do tempo
st.header('Evolução dos valores empenhados ao longo do tempo', divider='gray')
evolution_df = filtered_df.groupby(['Data Emissão'])['Valor do Empenho Convertido pra R$'].sum().reset_index()
evolution_df['Valor Formatado'] = evolution_df['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)
evolution_chart = (
    alt.Chart(evolution_df)
    .mark_line(point=True)
    .encode(
        x=alt.X('Data Emissão:T', title='Data'),
        y=alt.Y('Valor do Empenho Convertido pra R$:Q', title='Valor (R$)'),
        tooltip=[
            alt.Tooltip('Data Emissão:T', title='Data'),
            alt.Tooltip('Valor Formatado:N', title='Valor')
        ]
    )
    .properties(width=800, height=400)
)
st.altair_chart(evolution_chart, use_container_width=True)

# Análise dos maiores beneficiários
st.header('Análise dos maiores beneficiários', divider='gray')
top_beneficiaries_df = filtered_df.groupby('Favorecido')['Valor do Empenho Convertido pra R$'].sum().reset_index()
top_beneficiaries_df = top_beneficiaries_df.sort_values(by='Valor do Empenho Convertido pra R$', ascending=False).head(10)
top_beneficiaries_df['Valor Formatado'] = top_beneficiaries_df['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)
top_beneficiaries_chart = (
    alt.Chart(top_beneficiaries_df)
    .mark_bar()
    .encode(
        x=alt.X('Valor do Empenho Convertido pra R$:Q', title='Valor (R$)'),
        y=alt.Y('Favorecido:N', sort='-x', title='Favorecido'),
        tooltip=[
            alt.Tooltip('Favorecido:N', title='Favorecido'),
            alt.Tooltip('Valor Formatado:N', title='Valor')
        ]
    )
    .properties(width=800, height=400)
)
st.altair_chart(top_beneficiaries_chart, use_container_width=True)

# Comparação por órgão governamental
st.header('Comparação por órgão governamental', divider='gray')
organs_df = filtered_df.groupby('Órgão')['Valor do Empenho Convertido pra R$'].sum().reset_index()
organs_df = organs_df.sort_values(by='Valor do Empenho Convertido pra R$', ascending=False).head(10)
organs_df['Valor Formatado'] = organs_df['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)
organs_chart = (
    alt.Chart(organs_df)
    .mark_bar()
    .encode(
        x=alt.X('Órgão:N', sort='-y', title='Órgão'),
        y=alt.Y('Valor do Empenho Convertido pra R$:Q', title='Valor (R$)'),
        tooltip=[
            alt.Tooltip('Órgão:N', title='Órgão'),
            alt.Tooltip('Valor Formatado:N', title='Valor')
        ]
    )
    .properties(width=800, height=400)
)
st.altair_chart(organs_chart, use_container_width=True)

# Distribuição por Categoria Econômica
st.header('Distribuição por Categoria Econômica', divider='gray')

category_distribution = (
    filtered_df.groupby('Categoria de Despesa')['Valor do Empenho Convertido pra R$']
    .sum()
    .reset_index()
)
category_distribution['Valor Formatado'] = category_distribution['Valor do Empenho Convertido pra R$'].apply(adicionar_unidade)

# Gráfico de pizza com Altair
category_chart = (
    alt.Chart(category_distribution)
    .mark_arc()
    .encode(
        theta=alt.Theta('Valor do Empenho Convertido pra R$:Q', title='Valor (R$)'),
        color=alt.Color('Categoria de Despesa:N', legend=None),
        tooltip=[
            alt.Tooltip('Categoria de Despesa:N', title='Categoria'),
            alt.Tooltip('Valor Formatado:N', title='Valor')
        ]
    )
    .properties(width=800, height=400)
)
st.altair_chart(category_chart, use_container_width=True)

# Mostrar a tabela com valores
st.write(category_distribution)


# Resumo dos valores empenhados considerando o filtro
st.header('Resumo dos valores empenhados', divider='gray')
total_empenhado = filtered_df['Valor do Empenho Convertido pra R$'].sum()
st.metric(
    label="Total de valores empenhados (filtro aplicado)",
    value=adicionar_unidade(total_empenhado)
)
