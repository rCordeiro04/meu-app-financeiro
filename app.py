import streamlit as st
from streamlit_option_menu import option_menu

# Configuração da página para celular
st.set_page_config(page_title="Controle Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- BARRA LATERAL (MENU BONITO E QUADRADO) ---
with st.sidebar:
    st.write("") # Espaço em branco no topo para dar um respiro
    
    aba_selecionada = option_menu(
        menu_title="Meu Financeiro",
        options=["Painel", "Controle", "Lançamentos"],
        icons=["bar-chart-line-fill", "sliders", "plus-circle-fill"],
        menu_icon="wallet-fill",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#555", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "15px 0px",     # Aumenta a distância vertical entre os botões
                "padding": "15px",        # Deixa o botão mais alto e preenchido
                "border-radius": "0px",   # Remove as bordas arredondadas (quadrado perfeito)
                "--hover-color": "#f0f2f6"
            },
            "nav-link-selected": {
                "background-color": "#28a745", 
                "color": "white", 
                "font-weight": "bold",
                "border-radius": "0px"    # Mantém o formato quadrado quando selecionado
            },
        }
    )

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
