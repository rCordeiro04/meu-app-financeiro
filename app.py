import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import date
import plotly.express as px
import os

# Configuração da página para telemóvel
st.set_page_config(page_title="Controlo Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- SISTEMA DE ARMAZENAMENTO ÚNICO (GOOGLE PLANILHAS READY) ---
ARQUIVO_DADOS = "meu_banco_de_dados.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Detalhe", "Valor"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.write("") 
    
    aba_selecionada = option_menu(
        menu_title="O Meu Financeiro",
        options=["Painel", "Lançamentos", "Controles"],
        icons=["bar-chart-line-fill", "plus-circle-fill", "sliders"],
        menu_icon="wallet-fill",
        default_index=1, 
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#555", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "10px 0px", "padding": "12px", "border-radius": "0px", "--hover-color": "#f0f2f6"},
            "nav-link-selected": {"background-color": "#28a745", "color": "white", "font-weight": "bold", "border-radius": "0px"},
        }
    )

# --- ABA 1: PAINEL ---
if aba_selecionada == "Painel":
    st.title("📊 Painel")
    df_completo = carregar_dados()
    
    if df_completo.empty:
        st.info("Nenhum dado registado ainda. Vá até 'Lançamentos' e faça o primeiro registo!")
    else:
        df_completo['Data'] = pd.to_datetime(df_completo['Data'])
        df_completo = df_completo.sort_values('Data')
        df_completo['MesAno'] = df_completo['Data'].dt.strftime('%m/%Y')
        
        # Filtra apenas Receitas e Despesas para os gráficos financeiros do painel
        df_financeiro = df_completo[df_completo['Tipo'].isin(['Receita', 'Despesa'])]
        
        meses_disponiveis = ["Todos os Meses"] + sorted(list(df_completo['MesAno'].unique()), reverse=True)
        mes_selecionado = st.selectbox("📅 Filtrar Mês", meses_disponiveis)
        
        if mes_selecionado != "Todos os Meses":
            df_filtrado = df_financeiro[df_financeiro['MesAno'] == mes_selecionado]
        else:
            df_filtrado = df_financeiro.copy()
            
        total_entradas = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
        total_saidas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']['Valor'].sum()
        liquido = total_entradas - total_saidas

        html_cards = f"""
        <style>
        .cards-wrapper {{ display: flex; flex-direction: row; justify-content: space-between; gap: 10px; margin-top: 10px; margin-bottom: 25px; overflow-x: auto; padding-bottom: 10px; }}
        .cards-wrapper::-webkit-scrollbar {{ display: none; }}
        .cards-wrapper {{ -ms-overflow-style: none; scrollbar-width: none; }}
        .card-custom {{ flex: 1; min-width: 95px; background-color: #ffffff; border-radius: 16px; padding: 15px 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #f8f9fa; }}
        @media (prefers-color-scheme: dark) {{ .card-custom {{ background-color: #1a1a1a; border: 1px solid #2d2d2d; }} }}
        .card-icon {{ font-size: 22px; margin-bottom: 4px; }}
        .card-title {{ font-size: 11px; color: #888; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; text-align: center; }}
        .card-value {{ font-size: 16px; font-weight: 800; text-align: center; }}
        .text-green {{ color: #20c997; }} .text-red {{ color: #ff6b6b; }} .text-blue {{ color: #339af0; }}
        </style>
        <div class="cards-wrapper">
            <div class="card-custom"><div class="card-icon">📈</div><div class="card-title">Entradas</div><div class="card-value text-green">R$ {formatar_moeda(total_entradas)}</div></div>
            <div class="card-custom"><div class="card-icon">📉</div><div class="card-title">Saídas</div><div class="card-value text-red">R$ {formatar_moeda(total_saidas)}</div></div>
            <div class="card-custom"><div class="card-icon">⚖️</div><div class="card-title">Líquido</div><div class="card-value text-blue">R$ {formatar_moeda(liquido)}</div></div>
        </div>
        """
        st.markdown(html_cards, unsafe_allow_html=True)

        st.markdown("""
        <style>
        [data-testid="stColumn"] { background-color: #ffffff; border-radius: 20px; padding: 20px 10px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08); border: 1px solid #f0f2f6; margin-bottom: 15px; }
        @media (prefers-color-scheme: dark) { [data-testid="stColumn"] { background-color: #1a1a1a; border: 1px solid #2d2d2d; } }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Despesas</h4>", unsafe_allow_html=True)
            df_despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']
            if not df_despesas.empty and df_despesas['Valor'].sum() > 0:
                fig1 = px.pie(df_despesas, values='Valor', names='Categoria', hole=0.65)
                fig1.update_traces(textposition='inside', textinfo='percent', hoverinfo='label+percent+value')
                fig1.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sem saídas.")

        with col2:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Renda vs Gastos</h4>", unsafe_allow_html=True)
            if total_entradas > 0 or total_saidas > 0:
                df_comparacao = pd.DataFrame({"Tipo": ["Entradas", "Saídas"], "Valor": [total_entradas, total_saidas]})
                fig2 = px.pie(df_comparacao, values='Valor', names='Tipo', hole=0.65, color='Tipo', color_discrete_map={"Entradas": "#20c997", "Saídas": "#ff6b6b"})
                fig2.update_traces(textposition='inside', textinfo='percent', hoverinfo='label+percent+value')
                fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados.")

# --- ABA 2: LANÇAMENTOS (TUDO UNIFICADO NO ARQUIVO) ---
elif aba_selecionada == "Lançamentos":
    st.title("➕ Lançamentos e Base")
    st.write("Registe entradas, saídas e investimentos. Tudo é guardado num único ficheiro para o Google Planilhas.")

    aba_entrada, aba_saida, aba_invest, aba_banco = st.tabs(["Entradas 📈", "Saídas 📉", "Investimentos 🚀", "Base de Dados 🗄️"])

    with aba_entrada:
        with st.form("form_entrada"):
            st.subheader("Nova Receita")
            data_entrada = st.date_input("Data", date.today())
            cat_entrada = st.selectbox("Categoria", ["Salário", "Investimento", "Outros"])
            val_entrada = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Entrada", use_container_width=True):
                if val_entrada > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({
                        "Data": [data_entrada.strftime("%Y-%m-%d")],
                        "Tipo": ["Receita"],
                        "Categoria": [cat_entrada],
                        "Detalhe": [""],
                        "Valor": [val_entrada]
                    })
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success("✅ Entrada registada com sucesso!")

    with aba_saida:
        with st.form("form_saida"):
            st.subheader("Nova Despesa")
            data_saida = st.date_input("Data", date.today())
            cat_saida = st.selectbox("Categoria", ["Apartamento", "Moto ou Carro", "Estudos", "Lazer", "Cartão"])
            val_saida = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Saída", use_container_width=True):
                if val_saida > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({
                        "Data": [data_saida.strftime("%Y-%m-%d")],
                        "Tipo": ["Despesa"],
                        "Categoria": [cat_saida],
                        "Detalhe": [""],
                        "Valor": [val_saida]
                    })
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success("✅ Despesa registada com sucesso!")

    with aba_invest:
        with st.form("form_investimento"):
            st.subheader("Registar Aporte em Investimento")
            data_inv = st.date_input("Data do Aporte", date.today())
            nome_inv = st.text_input("Nome da Meta/Investimento (ex: Ações, Imóvel)")
            val_inv = st.number_input("Valor Guardado/Aporte (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Guardar Aporte", use_container_width=True):
                if val_inv > 0 and nome_inv:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({
                        "Data": [data_inv.strftime("%Y-%m-%d")],
                        "Tipo": ["Investimento"],
                        "Categoria": ["Meta de Investimento"],
                        "Detalhe": [nome_inv],
                        "Valor": [val_inv]
                    })
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success(f"✅ Aporte em '{nome_inv}' registado com sucesso!")

    with aba_banco:
        st.subheader("Base de Dados Completa")
        df_banco = carregar_dados()
        if not df_banco.empty:
            st.dataframe(df_banco, use_container_width=True, hide_index=True)
        else:
            st.info("Ainda sem registos.")

        st.divider()
        st.subheader("📤 Exportar para Google Planilhas")
        csv = df_banco.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV Consolidado", 
            data=csv, 
            file_name="meu_controle_financeiro_geral.csv", 
            mime="text/csv", 
            use_container_width=True
        )
        st.caption("Dica: Faça o download deste ficheiro e importe-o diretamente no Google Planilhas para ter todos os dados num único lugar.")

# --- ABA 3: CONTROLES ---
elif aba_selecionada == "Controles":
    st.title("⚙️ Controles")
    st.write("Acompanhe o pagamento das contas mensais.")

    df_geral = carregar_dados()
    
    mes_atual_str = date.today().strftime('%m/%Y')
    mes_input = st.text_input("Mês de Referência (MM/AAAA)", value=mes_atual_str)
    
    st.subheader(f"Contas de {mes_input}")
    
    # Lista fixa de controle de contas exigida
    contas_padrao = ["Apartamento", "Evolução de obra", "Moto/Carro", "Faculdade"]
    
    for conta in contas_padrao:
        # Verifica no banco unificado se já existe registo de pagamento para esta conta neste mês
        filtro_conta = (df_geral['Tipo'] == 'Checklist') & (df_geral['Categoria'] == mes_input) & (df_geral['Detalhe'] == conta)
        status_atual = False
        if not df_geral[filtro_conta].empty:
            status_atual = bool(df_geral[filtro_conta]['Valor'].values[0] == 1.0)
            
        novo_status = st.checkbox(conta, value=status_atual, key=f"chk_{mes_input}_{conta}")
        
        # Atualiza o estado no DataFrame consolidado
        if novo_status != status_atual:
            if not df_geral[filtro_conta].empty:
                df_geral.loc[filtro_conta, 'Valor'] = 1.0 if novo_status else 0.0
            else:
                nova_chk = pd.DataFrame({
                    "Data": [date.today().strftime("%Y-%m-%d")],
                    "Tipo": ["Checklist"],
                    "Categoria": [mes_input],
                    "Detalhe": [conta],
                    "Valor": [1.0 if novo_status else 0.0]
                })
                df_geral = pd.concat([df_geral, nova_chk], ignore_index=True)
            salvar_dados(df_geral)
