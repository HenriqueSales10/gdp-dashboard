import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Função para carregar os dados
@st.cache_data
def get_empenhos_data(file):
    """Carregar os dados dos empenhos do governo federal a partir do arquivo enviado."""
    
    # Carregar o arquivo Excel
    raw_empenhos_df = pd.read_excel(file)
    
    # Converter a coluna 'Data Emissão' para o formato de data
    raw_empenhos_df['Data Emissão'] = pd.to_datetime(raw_empenhos_df['Data Emissão'], format='%d/%m/%Y')
    
    # Filtrar apenas os dados de janeiro de 2024
    raw_empenhos_df = raw_empenhos_df[raw_empenhos_df['Data Emissão'].dt.month == 1]
    raw_empenhos_df['Ano'] = raw_empenhos_df['Data Emissão'].dt.year

    return raw_empenhos_df

# Interface para upload do arquivo Excel
st.title('Análise dos Empenhos do Governo Federal - Janeiro de 2024')

uploaded_file = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Carregar os dados do arquivo
    empenhos_df = get_empenhos_data(uploaded_file)

    # Filtros de Ano
    min_value = empenhos_df['Ano'].min()
    max_value = empenhos_df['Ano'].max()

    from_year, to_year = st.slider(
        'Selecione o período de interesse:',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value]
    )

    # Filtro para Órgãos Governamentais
    orgaos = empenhos_df['Órgão'].unique()
    selected_orgaos = st.multiselect(
        'Selecione os órgãos governamentais:',
        orgaos,
        orgaos.tolist()
    )

    # Filtrando os dados conforme as seleções
    filtered_empenhos_df = empenhos_df[
        (empenhos_df['Órgão'].isin(selected_orgaos)) &
        (empenhos_df['Ano'] >= from_year) & (empenhos_df['Ano'] <= to_year)
    ]

    # Gráfico 1: Distribuição por Categoria de Despesa
    st.header('Distribuição por Categoria de Despesa')
    categoria_economica = filtered_empenhos_df['Categoria de Despesa'].value_counts()
    fig1 = px.pie(categoria_economica, values=categoria_economica.values, names=categoria_economica.index, title='Distribuição por Categoria de Despesa')
    st.plotly_chart(fig1)

    # Gráfico 2: Maiores Beneficiários
    st.header('Maiores Beneficiários dos Empenhos')
    maiores_beneficiarios = filtered_empenhos_df.groupby('Favorecido')['Valor do Empenho Convertido pra R$'].sum().sort_values(ascending=False).head(10)
    fig2 = px.bar(maiores_beneficiarios, x=maiores_beneficiarios.index, y=maiores_beneficiarios.values, title='Top 10 Maiores Beneficiários')
    st.plotly_chart(fig2)

    # Gráfico 3: Comparação por Órgão Governamental
    st.header('Comparação por Órgão Governamental')
    comparacao_orgaos = filtered_empenhos_df.groupby('Órgão')['Valor do Empenho Convertido pra R$'].sum().sort_values(ascending=False).head(10)
    fig3 = px.bar(comparacao_orgaos, x=comparacao_orgaos.index, y=comparacao_orgaos.values, title='Top 10 Órgãos com Maior Valor Empenhado')
    st.plotly_chart(fig3)

    # Gráfico 4: Evolução dos Valores Empenhados ao Longo do Mês
    st.header('Evolução dos Valores Empenhados')
    evolucao_mensal = filtered_empenhos_df.groupby(['Ano', 'Mês'])['Valor do Empenho Convertido pra R$'].sum()
    fig4 = px.line(evolucao_mensal, x=evolucao_mensal.index, y=evolucao_mensal.values, title='Evolução dos Valores Empenhados')
    st.plotly_chart(fig4)

else:
    st.warning("Por favor, faça o upload de um arquivo Excel para visualizar os dados.")
