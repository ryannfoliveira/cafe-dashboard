import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import numpy as np

# Função retirada do repositório https://github.com/ryannfoliveira/toolkit-eda
def ajuste_ordem(num: float, sep_dec: str, sep_mil: str, escala: str = 'curta'):
    '''
    Converte números brutos em formas legíveis.
    Argumentos:
      num ─ Número a ser convertido
      sep_dec ─ Separador decimal (geralmente "," ou ".")
      sep_mil ─ Separador de milhar (geralmente ".", "," ou " ")
      escala ─ 'curta' ou 'longa'
    Retorna:
      str: Número formatado com abreviação apropriada.
    '''
    def formatar_abreviado(abrev, sep_dec, sep_mil):
        str_num = abrev.replace('.', 'X').replace(',', 'Y')
        str_num = str_num.replace('X', f'{sep_dec}').replace('Y', f'{sep_mil}')
        return str_num

    if num is None or sep_dec is None or sep_mil is None or escala is None:
        raise TypeError('O valor dos argumentos não pode ser igual a None')

    if num == 0:
        raise ValueError('O número não pode ser nulo.')

    if escala != 'curta' and escala != 'longa':
        raise ValueError('Escala inválida. Use "curta" ou "longa"')

    num = abs(num)
    log_num = np.log10(num)

    if log_num < 3:
        str_num = f'{num:,.2f}'
        if str_num.endswith('.00'):
            str_num = str_num.replace('.00', '')
        str_num = str_num.replace('.', 'X').replace(',', f'{sep_mil}')
        str_num = str_num.replace('X', f'{sep_dec}')
    elif log_num < 6:
        abrev = f'{round(num/10**3, 2)} mil'
        str_num = formatar_abreviado(abrev, sep_dec, sep_mil)
    elif log_num < np.log10(2*(10**6)):
        abrev = f'{round(num/10**6, 2)} milhão'
        str_num = formatar_abreviado(abrev, sep_dec, sep_mil)
    elif log_num < 9:
        abrev = f'{round(num/10**6, 2)} milhões'
        str_num = formatar_abreviado(abrev, sep_dec, sep_mil)
    elif log_num < np.log10(2*(10**9)):
        if escala == 'curta':
            abrev = f'{round(num/10**9, 2)} bilhão'
        elif escala == 'longa':
            abrev = f'{round(num/10**6, 2)} milhões'
        str_num = formatar_abreviado(abrev, sep_dec, sep_mil)
    elif log_num < 12:
        if escala == 'curta':
            abrev = f'{round(num/10**9, 2)} bilhões'
        elif escala == 'longa':
            abrev = f'{round(num/10**6, 2)} milhões'
        str_num = formatar_abreviado(abrev, sep_dec, sep_mil)
        
    return str_num

st.title('DASHBOARD')

df = pd.read_csv('base_vendas.csv')
df['nome_cafe'] = df['nome_cafe'].apply(lambda x: x.replace('Hot Chocolate', 'Chocolate Quente').replace('Americano with Milk', 'Americano com leite').replace('Cocoa', 'Achocolatado'))
mais_vendido = pd.DataFrame(df.nome_cafe.value_counts().reset_index().iloc[0]).T.reset_index(drop=True)

cafes = df['nome_cafe'].value_counts().reset_index()
paleta = ['#FBE9D0', '#EDD0B0', '#D6A77A', '#BC8A65', '#9C6A4A', '#7B4A2F', '#5A2E1A', '#381C0B']
pio.templates.default = 'presentation'
grafico_cafes_populares = px.bar(data_frame=cafes, x=cafes['nome_cafe'],
                                 y=cafes['count'], color='count',
                                 color_continuous_scale=paleta,
                                 labels={'nome_cafe': 'Nome do café', 'count': 'Quantidade de vendas'},
                                 title='Cafés em ordem de popularidade')

formas_pagamento = df['forma_pagamento'].value_counts().reset_index()
gráfico_formas_pagamento = px.pie(data_frame=formas_pagamento, names='forma_pagamento',
                                  values='count', title='Distribuição das Formas de Pagamento',
                                  color_discrete_sequence=['#381C0B', '#5A2E1A', '#7B4A2F'])

vendas = df['valor'].sum()
vendas_legivel = f"R$ {ajuste_ordem(vendas, ',', '.')}"

aba1, aba2 = st.tabs(['Receita', 'Vendas'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', vendas_legivel)
    with coluna2:
        st.metric('O mais popular', 'Americano com leite')
    st.plotly_chart(grafico_cafes_populares, use_container_width=True)
    st.markdown('As três bebidas menos vendidas são o **espresso**, o **achocolatado** e o **chocolate quente**,' \
    ' o que à primeira vista parece evidenciar possível necessidade de alguma prática promocional ou **revisão' \
    ' da receita** utilizada pelo estabelecimento comercial. Exploraremos a questão da aparente baixa perfomance' \
    ' chocolate quente mais à frente.')
    st.plotly_chart(gráfico_formas_pagamento, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    st.dataframe(df)