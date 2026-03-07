import streamlit as st
import pandas as pd
import time

@st.cache_data
def converter_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso', icon = '✅')
    time.sleep(5)
    sucesso.empty()

def main():
    df = pd.read_csv('base_vendas.csv')

    st.title('DADOS BRUTOS')
    st.markdown('Abaixo, a base de dados completa que registra todas as vendas.')

    st.sidebar.title('Filtros')

    with st.sidebar.expander('Produtos'):
        produtos = st.multiselect('Selecione os produtos a serem exibidos', df['nome_cafe'].unique(), df['nome_cafe'].unique())

    with st.sidebar.expander('Momento do dia'):
        momento_dia = st.multiselect('Filtre as vendas por parte do dia', df['momento_do_dia'].unique(), df['momento_do_dia'].unique())

    with st.sidebar.expander('Dia da semana'):
        dia_semana = st.multiselect('Filtre as vendas por dia da semana', df['dia_semana'].unique(), df['dia_semana'].unique())

    with st.sidebar.expander('Forma de pagamento'):
        forma_pagamento = st.multiselect('Filtre as vendas por forma de pagamento', df['forma_pagamento'].unique(), df['forma_pagamento'].unique())

    dados_filtrados = df[
        df['nome_cafe'].isin(produtos) &
        df['momento_do_dia'].isin(momento_dia) &
        df['dia_semana'].isin(dia_semana) &
        df['forma_pagamento'].isin(forma_pagamento)
    ]

    st.dataframe(dados_filtrados)
    st.markdown(f'Há :green[{dados_filtrados.shape[0]}] linhas e :green[{dados_filtrados.shape[1]}] colunas.')

    st.markdown('' \
    '---' \
    '')

    st.markdown('##### Salvar arquivo como:')
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        nome_arquivo = st.text_input('', label_visibility='collapsed', placeholder='Nome do arquivo', max_chars=100)
        nome_arquivo += '.csv'
    with coluna2:
        st.download_button('Download (.csv)', data = converter_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)
    if nome_arquivo != '.csv':
        st.markdown(f'O arquivo será salvo como "{nome_arquivo}"')

if __name__ == "__main__":
    main()