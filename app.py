import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import date
import plotly.express as px

# Configuração da página para celular
st.set_page_config(page_title="Controle Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- FUNÇÃO AUXILIAR PARA FORMATAR MOEDA ---
def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
if 'dados' not in st.session_state:
    st.session_state['dados'] = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor"])

# --- BARRA LATERAL (MENU BONITO E QUADRADO) ---
with st.sidebar:
    st.write("") 
    
    aba_selecionada = option_menu(
        menu_title="Meu Financeiro",
        options=["Painel", "Lançamentos", "Controles", "Banco de Dados"],
        icons=["bar-chart-line-fill", "plus-circle-fill", "sliders", "database-fill"],
        menu_icon="wallet-fill",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#555", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", "text-align": "left", "margin": "15px 0px",     
                "padding": "15px", "border-radius": "0px", "--hover-color": "#f0f2f6"
            },
            "nav-link-selected": {
                "background-color": "#28a745", "color": "white", 
                "font-weight": "bold", "border-radius": "0px"    
            },
        }
    )

# --- ABA 1: PAINEL ---
if aba_selecionada == "Painel":
    st.title("📊 Painel")
    
    df = st.session_state['dados'].copy()
    
    if df.empty:
        st.info("Nenhum dado registrado ainda. Vá até 'Lançamentos' e faça o primeiro registro para ver os gráficos!")
    else:
        df['Data'] = pd.to_datetime(df['Data'])
        df['MesAno'] = df['Data'].dt.strftime('%m/%Y')
        
        meses_disponiveis = ["Todos os Meses"] + sorted(list(df['MesAno'].unique()), reverse=True)
        mes_selecionado = st.selectbox("📅 Filtrar por Mês/Ano", meses_disponiveis)
        
        if mes_selecionado != "Todos os Meses":
            df = df[df['MesAno'] == mes_selecionado]
            
        # Cálculos das métricas
        total_entradas = df[df['Tipo'] == 'Receita']['Valor'].sum()
        total_saidas = df[df['Tipo'] == 'Despesa']['Valor'].sum()
        liquido = total_entradas - total_saidas

        # --- DESIGN DOS 3 BALÕES (CARDS) ---
        html_cards = f"""
        <style>
        .cards-wrapper {{
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            gap: 12px;
            margin-top: 15px;
            margin-bottom: 25px;
            overflow-x: auto;
            padding-bottom: 12px; 
            padding-top: 5px;
        }}
        .cards-wrapper::-webkit-scrollbar {{ display: none; }}
        .cards-wrapper {{ -ms-overflow-style: none; scrollbar-width: none; }}
        
        .card-custom {{
            flex: 1;
            min-width: 100px; /* Ajustado para caberem os 3 perfeitamente */
            background-color: #ffffff;
            border-radius: 20px;
            padding: 20px 10px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.06);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 1px solid #f1f3f5;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .card-custom {{
                background-color: #1e1e1e;
                border: 1px solid #333;
                box-shadow: 0 6px 15px rgba(255,255,255,0.03);
            }}
        }}

        .card-icon {{ font-size: 28px; margin-bottom: 8px; }}
        .card-title {{
            font-size: 13px; color: #888; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.5px;
            margin-bottom: 5px; text-align: center;
        }}
        .card-value {{ font-size: 20px; font-weight: 800; text-align: center; }}
        
        .text-green {{ color: #20c997; }}
        .text-red {{ color: #ff6b6b; }}
        .text-blue {{ color: #339af0; }}
        </style>

        <div class="cards-wrapper">
            <div class="card-custom">
                <div class="card-icon">📈</div>
                <div class="card-title">Entradas</div>
                <div class="card-value text-green">R$ {formatar_moeda(total_entradas)}</div>
            </div>
            <div class="card-custom">
                <div class="card-icon">📉</div>
                <div class="card-title">Saídas</div>
                <div class="card-value text-red">R$ {formatar_moeda(total_saidas)}</div>
            </div>
            <div class="card-custom">
                <div class="card-icon">⚖️</div>
                <div class="card-title">Líquido</div>
                <div class="card-value text-blue">R$ {formatar_moeda(liquido)}</div>
            </div>
        </div>
        """
        st.markdown(html_cards, unsafe_allow_html=True)
        
        st.divider()

        # --- SEÇÃO DOS GRÁFICOS DE ROSCA ---
        st.subheader("Análise Visual")
        
        # Cria duas colunas para os gráficos
        col1, col2 = st.columns(2)

        # GRÁFICO 1: Despesas por Categoria
        with col1:
            st.markdown("**Despesas por Categoria**")
            df_despesas = df[df['Tipo'] == 'Despesa']
            if not df_despesas.empty and df_despesas['Valor'].sum() > 0:
                fig1 = px.pie(df_despesas, values='Valor', names='Categoria', hole=0.5)
                # Configurações para ficar bom no celular: sem legenda externa, texto dentro do gráfico
                fig1.update_traces(textposition='inside', textinfo='percent+label')
                fig1.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sem saídas registradas.")

        # GRÁFICO 2: Renda vs Gastos
        with col2:
            st.markdown("**Renda vs Gastos**")
            if total_entradas > 0 or total_saidas > 0:
                df_comparacao = pd.DataFrame({
                    "Tipo": ["Entradas", "Saídas"],
                    "Valor": [total_entradas, total_saidas]
                })
                # Filtra valores zero para o gráfico não ficar deformado
                df_comparacao = df_comparacao[df_comparacao['Valor'] > 0]
                
                # Gráfico com cores fixas (Verde para Entradas, Vermelho para Saídas)
                fig2 = px.pie(
                    df_comparacao, 
                    values='Valor', 
                    names='Tipo', 
                    hole=0.5,
                    color='Tipo',
                    color_discrete_map={"Entradas": "#20c997", "Saídas": "#ff6b6b"}
                )
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados para comparar.")

# --- ABA 2: LANÇAMENTOS ---
elif aba_selecionada == "Lançamentos":
    st.title("➕ Lançamentos")
    st.write("Registre suas movimentações financeiras.")

    aba_entrada, aba_saida = st.tabs(["Entradas 📈", "Saídas 📉"])

    with aba_entrada:
        with st.form("form_entrada"):
            st.subheader("Nova Receita")
            data_entrada = st.date_input("Data da Entrada", date.today())
            categoria_entrada = st.selectbox("Categoria", ["Salário", "Investimento", "Outros"])
            valor_entrada = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Entrada", use_container_width=True):
                if valor_entrada > 0:
                    nova_linha = pd.DataFrame({"Data": [data_entrada.strftime("%Y-%m-%d")], "Tipo": ["Receita"], "Categoria": [categoria_entrada], "Valor": [valor_entrada]})
                    st.session_state['dados'] = pd.concat([st.session_state['dados'], nova_linha], ignore_index=True)
                    st.success(f"✅ Entrada de R$ {valor_entrada:.2f} salva com sucesso!")

    with aba_saida:
        with st.form("form_saida"):
            st.subheader("Nova Despesa")
            data_saida = st.date_input("Data da Saída", date.today())
            categoria_saida = st.selectbox("Categoria", ["Apartamento", "Moto ou Carro", "Estudos", "Lazer", "Cartão"])
            valor_saida = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Saída", use_container_width=True):
                if valor_saida > 0:
                    nova_linha = pd.DataFrame({"Data": [data_saida.strftime("%Y-%m-%d")], "Tipo": ["Despesa"], "Categoria": [categoria_saida], "Valor": [valor_saida]})
                    st.session_state['dados'] = pd.concat([st.session_state['dados'], nova_linha], ignore_index=True)
                    st.success(f"✅ Saída de R$ {valor_saida:.2f} ({categoria_saida}) salva com sucesso!")

# --- ABA 3: CONTROLES ---
elif aba_selecionada == "Controles":
    st.title("⚙️ Controles")
    st.info("🚧 Tela em desenvolvimento.")

# --- ABA 4: BANCO DE DADOS ---
elif aba_selecionada == "Banco de Dados":
    st.title("🗄️ Banco de Dados")
    if not st.session_state['dados'].empty:
        st.dataframe(st.session_state['dados'], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado registrado ainda.")

    st.divider()
    st.subheader("📤 Exportar")
    csv = st.session_state['dados'].to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Baixar Planilha CSV", data=csv, file_name="meu_controle_financeiro.csv", mime="text/csv", use_container_width=True)

    st.divider()
    st.subheader("📥 Importar")
    arquivo_upload = st.file_uploader("Escolha um arquivo .CSV", type=["csv"])
    if arquivo_upload is not None:
        df_importado = pd.read_csv(arquivo_upload)
        if st.button("Substituir dados atuais", use_container_width=True):
            st.session_state['dados'] = df_importado
            st.success("Dados importados!")
            st.rerun()
