import pandas as pd
import streamlit as st
import plotly.io as pio
import json
import time
from prophet import Prophet
from prophet.serialize import model_from_json
from prophet.plot import plot_plotly
from pages.Dados_Brutos import converter_csv, mensagem_sucesso

if 'previsto' not in st.session_state:
    st.session_state['previsto'] = None
if 'plotado' not in st.session_state:
    st.session_state['plotado'] = None

# Função para as coisas não ficarem presas na tela
def resetar_previsao():
    st.session_state['previsto'] = None
    st.session_state['plotado'] = None

# Desserializando o modelo. Treinei noutro ambiente
# RMSE de 4.01 no teste. Como é menor que o desvio-padrão, sinal de que o modelo
# aprendeu de verdade. Mas como os dados são sintéticos, isso já cheira a conquista para mim.
with open('prophet.json', 'r') as f:
    m = model_from_json(f.read())

pio.templates.default = 'presentation'

st.title('Fazer previsões')

st.markdown('''
Nesta seção, aplicamos o modelo Prophet para analisar o histórico de vendas e identificar os padrões que regem a rotina do café.
O objetivo é transformar dados brutos em uma visão antecipada, oferecendo uma base estatística sólida para o planejamento de estoque, escalas de equipe e gestão de recursos para as próximas semanas.
Para usar, preencha o número de dias que deseja prever no campo abaixo e, em seguida, clique em "Prever".
'''
)
st.divider()

st.markdown('#### Quantos dias você quer prever?')
dias = st.number_input('', min_value=1, value=1, step=1)


if st.button('Prever'):
    resetar_previsao()
    st.session_state['previsto'] = True

if st.session_state['previsto'] == True:
    if st.session_state['plotado'] is None:
        # Colocando um spinner para evitar aquela coisa feia enquanto o gráfico é feito
        with st.spinner('Processando...'):
            placeholder = st.empty()
            futuro = m.make_future_dataframe(periods=dias)
            previsao = m.predict(futuro)
        
            fig = plot_plotly(fcst=previsao, m=m)
            # Fazendo o gráfico condizer com o resto da identidade visual do dashboard
            fig.update_traces(
            line_color='#4dcc04',
            marker_color='rgba(255, 255, 255, 0.3)',
            fillcolor='rgba(77, 204, 4, 0.15)',
            selector=dict(type='scatter'),
            )

            fig.update_xaxes(title_text="Data")
            fig.update_yaxes(title_text="Vendas")

            fig.update_layout(
                width=850,           # Valor base (o use_container_width vai sobrescrever, mas evita o pulo)
                height=600,          # Altura fixa para o container não "quicar"
                plot_bgcolor='#0b1216',
                paper_bgcolor='#0b1216',
                font_color='#f0f2f6',
                hovermode="x unified",
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#141b21',
                    linecolor='#1e293b'
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#141b21', 
                    linecolor='#1e293b'
                )
            )

            st.session_state['imagem'] = fig
            st.session_state['dados_previstos'] = previsao
            st.session_state['plotado'] = True
            # Colocando isso só para ser a pá de cal no desconforto gráfico
            time.sleep(1)
            
    fig = st.session_state['imagem']
    st.plotly_chart(
    fig, use_container_width=True, config={'responsive': False}
    )
    

    # Pegando só a parte dos dados correspondente às previsões
    previsao = st.session_state['dados_previstos']
    dados_previstos = previsao.tail(dias).reset_index(drop=True)

    st.markdown('---')
    st.markdown('#### Dados previstos')
    st.dataframe(dados_previstos)
    st.markdown(f'Há :green[{dados_previstos.shape[0]}] linhas e :green[{dados_previstos.shape[1]}] colunas.')

    st.markdown('##### Salvar arquivo como:')
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        nome_arquivo = st.text_input('', label_visibility='collapsed', placeholder='Nome do arquivo', max_chars=100)
        nome_arquivo += '.csv'
    with coluna2:
        st.download_button('Download (.csv)', data = converter_csv(dados_previstos), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)
    if nome_arquivo != '.csv':
        st.markdown(f'O arquivo será salvo como "{nome_arquivo}"')