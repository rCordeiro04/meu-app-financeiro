import streamlit as st
import pandas as pd
import plotly.express as px

# layout="centered" força a estrutura vertical, ideal para telemóveis
st.set_page_config(page_title="Controlo Financeiro", layout="centered")

st.title("💸 O Meu Controlo Financeiro")

# Tabela de dados de exemplo
dados = pd.DataFrame({
    "Categoria": ["Alimentação", "Transporte", "Lazer", "Moradia"],
    "Valor": [350.0, 150.0, 200.0, 1200.0]
})

# Tudo organizado de cima para baixo (vertical) em vez de lado a lado
st.subheader("Despesas por Categoria")
# Gráfico de rosca adaptado à largura do ecrã
fig = px.pie(dados, values='Valor', names='Categoria', hole=0.5)
st.plotly_chart(fig, use_container_width=True)

st.divider() # Linha separadora

st.subheader("Resumo dos Lançamentos")
# Tabela com mapa de calor (verde para vermelho consoante o valor)
st.dataframe(
    dados.style.background_gradient(cmap='RdYlGn_r', subset=['Valor']), 
    use_container_width=True
)
    
# Ferramenta para exportar e baixar para Excel/CSV
csv = dados.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar em Excel/CSV",
    data=csv,
    file_name='meu_financeiro.csv',
    mime='text/csv',
    use_container_width=True # Botão largo, fácil de tocar no ecrã do telemóvel
)
