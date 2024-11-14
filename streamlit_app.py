import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title='Empenhos do Governo Federal - Dashboard',
    page_icon=':bar_chart:', 
)

@st.cache_data
def get_empenhos_data():
    """Carrega os dados de empenhos do CSV."""
    DATA_FILENAME = Path(__file__).parent/'data/202401_Empenhos.csv'
    raw_df = pd.read_csv(DATA_FILENAME)
    st.write(raw_df.head())
    return raw_df

# Carregar os dados de empenhos
df = get_empenhos_data()

# Converter a coluna de valores para float, tratando erros
df['Valor do Empenho Convertido pra R$'] = pd.to_numeric(
    df['Valor do Empenho Convertido pra R$'], errors='coerce'
)

# Filtro para o mês de janeiro de 2024
df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], errors='coerce')
filtered_df = df[df['Data Emissão'].dt.month == 1]

# Filtro de categorias econômicas
categories = filtered_df['Categoria de Despesa'].unique()
selected_categories = st.multiselect(
    'Selecione as categorias econômicas',
    categories,
    categories.tolist()
)

# Filtrar os dados com base na categoria
filtered_df = filtered_df[filtered_df['Categoria de Despesa'].isin(selected_categories)]

# Gráfico de evolução dos valores empenhados ao longo do tempo
st.header('Evolução dos valores empenhados ao longo do tempo', divider='gray')
evolution_df = filtered_df.groupby(['Data Emissão'])['Valor do Empenho Convertido pra R$'].sum().reset_index()
st.line_chart(
    evolution_df,
    x='Data Emissão',
    y='Valor do Empenho Convertido pra R$',
)

# Análise dos maiores beneficiários
st.header('Análise dos maiores beneficiários', divider='gray')
top_beneficiaries_df = filtered_df.groupby('Favorecido')['Valor do Empenho Convertido pra R$'].sum().reset_index()
top_beneficiaries_df = top_beneficiaries_df.sort_values(by='Valor do Empenho Convertido pra R$', ascending=False).head(10)
st.write(top_beneficiaries_df)

# Comparação por órgão governamental
st.header('Comparação por órgão governamental', divider='gray')
organs_df = filtered_df.groupby('Órgão')['Valor do Empenho Convertido pra R$'].sum().reset_index()
organs_df = organs_df.sort_values(by='Valor do Empenho Convertido pra R$', ascending=False)
st.bar_chart(
    organs_df.set_index('Órgão')['Valor do Empenho Convertido pra R$']
)

# Resumo dos valores empenhados
st.header('Resumo dos valores empenhados', divider='gray')
total_empenhado = filtered_df['Valor do Empenho Convertido pra R$'].sum()
st.metric(
    label="Total de valores empenhados",
    value=f"R$ {total_empenhado:,.2f}"
)
