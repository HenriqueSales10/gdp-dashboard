import streamlit as st
import pandas as pd
from pathlib import Path

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
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Carregar os dados de empenhos
df = get_empenhos_data()

# Exibir o número total de registros lidos da base
total_registros = len(df)
st.write(f"Total de registros lidos da base: {total_registros}")

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
].apply(formatar_real)
st.write(filtered_df_display[['Id Empenho', 'Data Emissão', 'Categoria de Despesa', 'Valor do Empenho Convertido pra R$']])

# Gráfico de evolução dos valores empenhados ao longo do tempo
st.header('Evolução dos valores empenhados ao longo do tempo', divider='gray')
evolution_df = filtered_df.groupby(['Data Emissão'])['Valor do Empenho Convertido pra R$'].sum().reset_index()
evolution_df['Valor do Empenho Convertido pra R$'] = evolution_df['Valor do Empenho Convertido pra R$'].apply(formatar_real)
st.line_chart(
    filtered_df.groupby(['Data Emissão'])['Valor do Empenho Convertido pra R$'].sum()
)

# Análise dos maiores beneficiários
st.header('Análise dos maiores beneficiários', divider='gray')
top_beneficiaries_df = filtered_df.groupby('Favorecido')['Valor do Empenho Convertido pra R$'].sum().reset_index()
top_beneficiaries_df = top_beneficiaries_df.sort_values(by='Valor do Empenho Convertido pra R$', ascending=False).head(10)
top_beneficiaries_df['Valor do Empenho Convertido pra R$'] = top_beneficiaries_df[
    'Valor do Empenho Convertido pra R$'
].apply(formatar_real)
st.write(top_beneficiaries_df)

# Comparação por órgão governamental
st.header('Comparação por órgão governamental', divider='gray')
organs_df = filtered_df.groupby('Órgão')['Valor do Empenho Convertido pra R$'].sum().reset_index()
organs_df = organs_df.sort_values(by='Valor do Empenho Convertido pra R$', ascending=False)
st.bar_chart(
    organs_df.set_index('Órgão')['Valor do Empenho Convertido pra R$']
)

# Resumo dos valores empenhados considerando o filtro
st.header('Resumo dos valores empenhados', divider='gray')
total_empenhado = filtered_df['Valor do Empenho Convertido pra R$'].sum()
st.metric(
    label="Total de valores empenhados (filtro aplicado)",
    value=formatar_real(total_empenhado)
)

# Botão para download dos valores com Id Empenho
st.header('Download dos Valores com Id Empenho', divider='gray')
filtered_df_csv = filtered_df.copy()
filtered_df_csv['Valor do Empenho Convertido pra R$'] = filtered_df_csv[
    'Valor do Empenho Convertido pra R$'
].apply(formatar_real)
csv_data = filtered_df_csv[['Id Empenho', 'Valor do Empenho Convertido pra R$']].to_csv(index=False)
st.download_button(
    label="Baixar Valores com Id Empenho",
    data=csv_data,
    file_name='id_empenho_valores.csv',
    mime='text/csv'
)

# Exibir os valores na tela para conferência
st.write(filtered_df_display[['Id Empenho', 'Valor do Empenho Convertido pra R$']])
