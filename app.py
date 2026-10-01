import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import date

# Configuração da página para celular
st.set_page_config(page_title="Controle Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
# Cria a tabela de memória do aplicativo caso ela não exista
if 'dados' not in st.session_state:
    st.session_state['dados'] = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor"])

# --- BARRA LATERAL (MENU BONITO E QUADRADO) ---
with st.sidebar:
    st.write("") 
    
    aba_selecionada = option_menu(
        menu_title="Meu Financeiro",
        options=["Painel", "Lançamentos", "Controles", "Banco de Dados"], # Adicionado 'Controles'
        icons=["bar-chart-line-fill", "plus-circle-fill", "sliders", "database-fill"], # Ícone de sliders para controles
        menu_icon="wallet-fill",
        default_index=2, # Abre direto na aba Controles para você ver
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
    st.info("🚧 Tela em desenvolvimento. Aqui ficarão os gráficos de resumo e os alertas de gastos.")

# --- ABA 2: LANÇAMENTOS ---
elif aba_selecionada == "Lançamentos":
    st.title("➕ Lançamentos")
    st.write("Registre suas movimentações financeiras.")

    aba_entrada, aba_saida = st.tabs(["Entradas 📈", "Saídas 📉"])

    # -- FORMULÁRIO DE ENTRADAS --
    with aba_entrada:
        with st.form("form_entrada"):
            st.subheader("Nova Receita")
            data_entrada = st.date_input("Data da Entrada", date.today())
            categoria_entrada = st.selectbox("Categoria", ["Salário", "Investimento", "Outros"])
            valor_entrada = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Entrada", use_container_width=True):
                if valor_entrada > 0:
                    nova_linha = pd.DataFrame({
                        "Data": [data_entrada.strftime("%Y-%m-%d")],
                        "Tipo": ["Receita"],
                        "Categoria": [categoria_entrada],
                        "Valor": [valor_entrada]
                    })
                    st.session_state['dados'] = pd.concat([st.session_state['dados'], nova_linha], ignore_index=True)
                    st.success(f"✅ Entrada de R$ {valor_entrada:.2f} salva com sucesso!")
                else:
                    st.error("O valor precisa ser maior que zero.")

    # -- FORMULÁRIO DE SAÍDAS --
    with aba_saida:
        with st.form("form_saida"):
            st.subheader("Nova Despesa")
            data_saida = st.date_input("Data da Saída", date.today())
            categoria_saida = st.selectbox("Categoria", ["Apartamento", "Moto ou Carro", "Estudos", "Lazer", "Cartão"])
            valor_saida = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Saída", use_container_width=True):
                if valor_saida > 0:
                    nova_linha = pd.DataFrame({
                        "Data": [data_saida.strftime("%Y-%m-%d")],
                        "Tipo": ["Despesa"],
                        "Categoria": [categoria_saida],
                        "Valor": [valor_saida]
                    })
                    st.session_state['dados'] = pd.concat([st.session_state['dados'], nova_linha], ignore_index=True)
                    st.success(f"✅ Saída de R$ {valor_saida:.2f} ({categoria_saida}) salva com sucesso!")
                else:
                    st.error("O valor precisa ser maior que zero.")

# --- ABA 3: CONTROLES ---
elif aba_selecionada == "Controles":
    st.title("⚙️ Controles")
    st.info("🚧 Tela em desenvolvimento. O que você quer colocar aqui? (Ex: Definir limites de gastos, deletar itens errados, gerenciar categorias...)")

# --- ABA 4: BANCO DE DADOS ---
elif aba_selecionada == "Banco de Dados":
    st.title("🗄️ Banco de Dados")
    st.write("Visualize, exporte e importe todos os seus registros.")

    if not st.session_state['dados'].empty:
        st.dataframe(st.session_state['dados'], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado registrado ainda. Vá até 'Lançamentos' e faça o primeiro registro!")

    st.divider()

    st.subheader("📤 Exportar Dados")
    st.write("Baixe tudo o que você cadastrou para uma planilha de Excel/CSV.")
    csv = st.session_state['dados'].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Planilha CSV",
        data=csv,
        file_name="meu_controle_financeiro.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()

    st.subheader("📥 Importar Dados")
    st.write("Envie uma planilha CSV antiga para dentro do aplicativo.")
    arquivo_upload = st.file_uploader("Escolha um arquivo .CSV", type=["csv"])
    
    if arquivo_upload is not None:
        try:
            df_importado = pd.read_csv(arquivo_upload)
            
            if st.button("Substituir dados atuais pela planilha", use_container_width=True):
                st.session_state['dados'] = df_importado
                st.success("Dados importados com sucesso!")
                st.rerun() 
        except Exception as e:
            st.error("Erro ao ler o arquivo. Certifique-se de que é um formato CSV válido.")
