import streamlit as st
import pandas as pd

df = pd.read_csv('base_vendas.csv')

st.title('DADOS BRUTOS')
st.dataframe(df)