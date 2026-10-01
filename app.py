import streamlit as st
from streamlit_option_menu import option_menu
from datetime import date

# Configuração da página para celular
st.set_page_config(page_title="Controle Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- BARRA LATERAL (MENU BONITO E QUADRADO) ---
with st.sidebar:
    st.write("") 
    
    aba_selecionada = option_menu(
        menu_title="Meu Financeiro",
        options=["Painel", "Controle", "Lançamentos"],
        icons=["bar-chart-line-fill", "sliders", "plus-circle-fill"],
        menu_icon="wallet-fill",
        default_index=2, # Mudei para 2 para abrir direto nos Lançamentos e facilitar os seus testes
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#555", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "15px 0px",     
                "padding": "15px",        
                "border-radius": "0px",   
                "--hover-color": "#f0f2f6"
            },
            "nav-link-selected": {
                "background-color": "#28a745", 
                "color": "white", 
                "font-weight": "bold",
                "border-radius": "0px"    
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
    st.write("Registre suas movimentações financeiras.")

    # Cria duas abas separadas na tela para Entradas e Saídas
    aba_entrada, aba_saida = st.tabs(["Entradas 📈", "Saídas 📉"])

    # -- FORMULÁRIO DE ENTRADAS --
    with aba_entrada:
        with st.form("form_entrada"):
            st.subheader("Nova Receita")
            # Adicionei o campo de data para ficar completo
            data_entrada = st.date_input("Data da Entrada", date.today())
            
            # Caixa de seleção com as suas categorias
            categoria_entrada = st.selectbox("Categoria", ["Salário", "Investimento", "Outros"])
            
            # Campo de valor (permite centavos e não aceita valor negativo)
            valor_entrada = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            # Botão de salvar (use_container_width=True deixa ele largo, ótimo para celular)
            salvar_entrada = st.form_submit_button("Salvar Entrada", use_container_width=True)
            
            if salvar_entrada:
                if valor_entrada > 0:
                    st.success(f"✅ Entrada de R$ {valor_entrada:.2f} ({categoria_entrada}) registrada provisoriamente!")
                else:
                    st.error("O valor precisa ser maior que zero.")

    # -- FORMULÁRIO DE SAÍDAS (PRÓXIMO PASSO) --
    with aba_saida:
        with st.form("form_saida"):
            st.subheader("Nova Despesa")
            st.info("Configuraremos as categorias aqui baseando-se no seu arquivo Organização financeira!")
            
            data_saida = st.date_input("Data da Saída", date.today())
            categoria_saida = st.text_input("Categoria (Provisório)")
            valor_saida = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            salvar_saida = st.form_submit_button("Salvar Saída", use_container_width=True)
            
            if salvar_saida:
                st.success("Saída registrada provisoriamente!")
