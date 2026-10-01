import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("💸 O Meu Controle Financeiro")

# Tabela de dados de exemplo
dados = pd.DataFrame({
    "Categoria": ["Alimentação", "Transporte", "Lazer", "Moradia"],
    "Valor": [350.0, 150.0, 200.0, 1200.0]
})

col1, col2 = st.columns(2)

with col1:
    st.subheader("Despesas por Categoria")
    # Gráfico de rosca
    fig = px.pie(dados, values='Valor', names='Categoria', hole=0.5)
    st.plotly_chart(fig)

with col2:
    st.subheader("Resumo dos Lançamentos")
    st.dataframe(dados, use_container_width=True)
    
    # Botão para baixar os dados em CSV/Excel
    csv = dados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar em Excel/CSV",
        data=csv,
        file_name='meu_financeiro.csv',
        mime='text/csv'
    )
