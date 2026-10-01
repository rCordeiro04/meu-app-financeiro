import streamlit as st

# Configuração da página para celular
st.set_page_config(page_title="Controle Financeiro", layout="centered")

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.title("Navegação")
    # Cria os botões de navegação
    aba_selecionada = st.radio("Ir para:", ["Painel", "Controle", "Lançamentos"])

# --- ABA 1: PAINEL ---
if aba_selecionada == "Painel":
    st.title("📊 Painel")
    st.info("🚧 Tela em desenvolvimento. Aqui ficarão os gráficos de resumo.")

# --- ABA 2: CONTROLE ---
elif aba_selecionada == "Controle":
    st.title("⚙️ Controle")
    st.info("🚧 Tela em desenvolvimento. Aqui ficará o histórico de transações e a opção de baixar os dados.")

# --- ABA 3: LANÇAMENTOS ---
elif aba_selecionada == "Lançamentos":
    st.title("➕ Lançamentos")
    st.info("🚧 Tela em desenvolvimento. Aqui ficará o formulário para adicionar novas entradas e saídas.")
