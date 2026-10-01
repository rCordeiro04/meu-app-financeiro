import streamlit as st
from streamlit_option_menu import option_menu

# Configuração da página para telemóvel
st.set_page_config(page_title="Controlo Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- BARRA LATERAL (MENU BONITO) ---
with st.sidebar:
    st.write("") # Espaço em branco para dar um respiro no topo
    
    aba_selecionada = option_menu(
        menu_title="O Meu Financeiro",  # Título do menu
        options=["Painel", "Controlo", "Lançamentos"], # Os nomes dos seus botões
        icons=["bar-chart-line-fill", "sliders", "plus-circle-fill"], # Ícones modernos para cada aba
        menu_icon="wallet-fill", # Ícone que fica ao lado do Título
        default_index=0, # Aba que abre por defeito (0 = Painel)
        styles={
            "container": {"padding": "5!important", "background-color": "transparent"},
            "icon": {"color": "#555", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px", "--hover-color": "#f0f2f6"},
            "nav-link-selected": {"background-color": "#28a745", "color": "white", "font-weight": "bold"},
        }
    )

# --- ABA 1: PAINEL ---
if aba_selecionada == "Painel":
    st.title("📊 Painel")
    st.info("🚧 Ecrã em desenvolvimento. Aqui ficarão os gráficos de resumo.")

# --- ABA 2: CONTROLO ---
elif aba_selecionada == "Controlo":
    st.title("⚙️ Controlo")
    st.info("🚧 Ecrã em desenvolvimento. Aqui ficará o histórico de transações e a opção de exportar os dados.")

# --- ABA 3: LANÇAMENTOS ---
elif aba_selecionada == "Lançamentos":
    st.title("➕ Lançamentos")
    st.info("🚧 Ecrã em desenvolvimento. Aqui ficará o formulário para adicionar novas despesas e receitas.")
