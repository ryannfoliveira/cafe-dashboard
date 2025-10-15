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

vendas_por_hora = df['hora'].value_counts().reset_index()
horario_pico = vendas_por_hora['hora'][0]
frequencia_pico = vendas_por_hora['count'][0]
grafico_horario_vendas = px.bar(data_frame=vendas_por_hora, x=vendas_por_hora['hora'], y=vendas_por_hora['count'],
                                color=vendas_por_hora['count'], color_continuous_scale=paleta,
                                labels={'hora': 'Horário', 'count': 'Quantidade de vendas'},
                                title='Distribuição das vendas por momento do dia')

ordem_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=ordem_dias, ordered=True)
vendas_por_dia = df['dia_semana'].value_counts().reset_index()
vendas_por_dia = vendas_por_dia.sort_values('dia_semana')
grafico_vendas_semana = px.line(data_frame=vendas_por_dia, x=vendas_por_dia['dia_semana'], y=vendas_por_dia['count'],
                                markers=True, labels={'dia_semana': 'Dia da semana', 'count': 'Quantidade de vendas'},
                                title='Distribuição das vendas ao longo dos dias da semana')

ordem_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
df['mes'] = pd.Categorical(df['mes'], categories=ordem_meses, ordered=True)
vendas_por_mes = df['mes'].value_counts().reset_index()
vendas_por_mes = vendas_por_mes.sort_values('mes')
grafico_vendas_ano = px.bar(data_frame=vendas_por_mes, x=vendas_por_mes['mes'], y=vendas_por_mes['count'],
                            color=vendas_por_mes['count'], color_continuous_scale=paleta,
                            labels={'mes': 'Mês', 'count': 'Quantidade de vendas'},
                            title='Distribuição das vendas ao longo do ano')
grafico_vendas_semana.update_traces(line={'color': '#7B4A2F'})
grafico_vendas_semana.update_yaxes(range=[349, 600])

aba1, aba2 = st.tabs(['Visão geral', 'Vendas'])

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
    st.markdown('A forma de pagamento mais frequentemente utilizada foi o **cartão**. Isso revela que mecanismos' \
    ' de incentivo financeiro ─ a exemplo de **ausência de juros** ou **oferecimento de cashback** por meio de convênio' \
    ' com outras instituições ─ podem ser empregados objetivando a diminuição do custo final da compra através dele.')

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Número de vendas', df.shape[0])
    with coluna2:
        st.metric('Horário de pico:', f'{horario_pico} horas')
    st.markdown('A hora do dia que correspondia à maior fatia da quantidade de vendas no estabelecimento eram as **10 da manhã**,' \
    f' com **{frequencia_pico} compras** feitas nesse momento do dia.')
    st.plotly_chart(grafico_horario_vendas, use_container_width=True)
    st.plotly_chart(grafico_vendas_semana, use_container_width=True)
    st.plotly_chart(grafico_vendas_ano, use_container_width=True)
    st.markdown('É nítida uma curva formando uma concavidade durante os meses correspondentes ao verão (hemisfério norte). Isso é' \
    ' explicável pelo fato de não ser atrativo ao cliente comprar bebidas e alimentos quentes durante períodos de calor constante, e é' \
    ' algo normal e esperado para cafeterias. Contudo, pode ser contornado através da introdução de um cardápio sazonal (rotativo),' \
    ' bem como de eventos e/ou descontos de tempo limitado, visando manter um fluxo constante de caixa durante qualquer época do ano.')