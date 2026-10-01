import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import date
import plotly.express as px
import os

# Configuração da página para telemóvel
st.set_page_config(page_title="Controlo Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- SISTEMA DE ARMAZENAMENTO ÚNICO E BLINDADO ---
ARQUIVO_DADOS = "meu_banco_de_dados.csv"

def carregar_dados():
    colunas_padrao = ["Data", "Tipo", "Categoria", "Detalhe", "Valor"]
    if os.path.exists(ARQUIVO_DADOS):
        try:
            df = pd.read_csv(ARQUIVO_DADOS)
            for col in colunas_padrao:
                if col not in df.columns:
                    df[col] = "" if col != "Valor" else 0.0
            return df[colunas_padrao] 
        except Exception:
            return pd.DataFrame(columns=colunas_padrao)
    return pd.DataFrame(columns=colunas_padrao)

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
        default_index=2, 
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
    
    if not df_completo.empty:
        df_completo['Data'] = pd.to_datetime(df_completo['Data'])
        df_completo = df_completo.sort_values('Data')
        df_completo['MesAno'] = df_completo['Data'].dt.strftime('%m/%Y')
        df_completo['Periodo'] = df_completo['Data'].dt.to_period('M')

    # Integra as Despesas Normais e as Despesas Fixas (Contas do Mês) nos cálculos
    df_financeiro = df_completo[df_completo['Tipo'].isin(['Receita', 'Despesa', 'Despesa Fixa'])].copy()
    
    if df_financeiro.empty:
        st.info("Nenhum lançamento registado ainda. Vá a 'Lançamentos' e comece a inserir os seus dados!")
    else:
        meses_disponiveis = ["Todos os Meses"] + sorted(list(df_financeiro['MesAno'].unique()), reverse=True)
        mes_selecionado = st.selectbox("📅 Filtrar Mês (Balões e Gráficos)", meses_disponiveis)
        
        if mes_selecionado != "Todos os Meses":
            df_filtrado = df_financeiro[df_financeiro['MesAno'] == mes_selecionado]
        else:
            df_filtrado = df_financeiro.copy()
            
        total_entradas = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
        total_saidas = df_filtrado[df_filtrado['Tipo'].isin(['Despesa', 'Despesa Fixa'])]['Valor'].sum()
        liquido = total_entradas - total_saidas

        # --- BALÕES FLUTUANTES ---
        html_cards = f"""
        <style>
        .cards-wrapper {{ display: flex; flex-direction: row; justify-content: space-between; gap: 10px; margin-top: 10px; margin-bottom: 25px; overflow-x: auto; padding-bottom: 10px; }}
        .cards-wrapper::-webkit-scrollbar {{ display: none; }}
        .card-custom {{ flex: 1; min-width: 95px; background-color: #ffffff; border-radius: 16px; padding: 15px 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #f8f9fa; }}
        @media (prefers-color-scheme: dark) {{ .card-custom {{ background-color: #1a1a1a; border: 1px solid #2d2d2d; }} }}
        .card-icon {{ font-size: 22px; margin-bottom: 4px; }}
        .card-title {{ font-size: 11px; color: #888; font-weight: 700; text-transform: uppercase; text-align: center; }}
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

        st.markdown("<style>[data-testid='stColumn'] { background-color: #ffffff; border-radius: 20px; padding: 20px 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #f0f2f6; margin-bottom: 15px; } @media (prefers-color-scheme: dark) { [data-testid='stColumn'] { background-color: #1a1a1a; border: 1px solid #2d2d2d; } }</style>", unsafe_allow_html=True)
        
        # --- LINHA 1: GRÁFICOS DE ROSCA ---
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Despesas</h4>", unsafe_allow_html=True)
            df_despesas = df_filtrado[df_filtrado['Tipo'].isin(['Despesa', 'Despesa Fixa'])]
            if not df_despesas.empty and df_despesas['Valor'].sum() > 0:
                fig1 = px.pie(df_despesas, values='Valor', names='Categoria', hole=0.65)
                fig1.update_traces(textposition='inside', textinfo='percent')
                fig1.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sem saídas.")

        with col2:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Renda vs Gastos</h4>", unsafe_allow_html=True)
            if total_entradas > 0 or total_saidas > 0:
                df_comparacao = pd.DataFrame({"Tipo": ["Entradas", "Saídas"], "Valor": [total_entradas, total_saidas]})
                fig2 = px.pie(df_comparacao, values='Valor', names='Tipo', hole=0.65, color='Tipo', color_discrete_map={"Entradas": "#20c997", "Saídas": "#ff6b6b"})
                fig2.update_traces(textposition='inside', textinfo='percent')
                fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados.")

        st.markdown("<h3 style='font-size: 18px; margin-top: 20px; margin-bottom: 5px; color: #555;'>Evolução Histórica Anual</h3>", unsafe_allow_html=True)

        # --- LINHA 2: GRÁFICO DE BARRAS (Entradas vs Saídas) ---
        col3, = st.columns(1)
        with col3:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Entradas vs Saídas</h4>", unsafe_allow_html=True)
            df_financeiro_agrup = df_financeiro.copy()
            # Unifica as Despesas Fixas na mesma coluna de Saídas
            df_financeiro_agrup['Tipo'] = df_financeiro_agrup['Tipo'].replace({'Receita': 'Entradas', 'Despesa': 'Saídas', 'Despesa Fixa': 'Saídas'})
            df_agrupado = df_financeiro_agrup.groupby(['Periodo', 'Tipo'], as_index=False)['Valor'].sum()
            df_agrupado['MesAno'] = df_agrupado['Periodo'].dt.strftime('%m/%Y')
            
            fig3 = px.bar(df_agrupado, x='MesAno', y='Valor', color='Tipo', barmode='group', color_discrete_map={"Entradas": "#20c997", "Saídas": "#ff6b6b"})
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=0, r=0), height=240, legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, title=""), xaxis_title="", yaxis_title="")
            fig3.update_xaxes(showgrid=False, type='category')
            fig3.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.1)')
            st.plotly_chart(fig3, use_container_width=True)

        # --- LINHA 3: GRÁFICO DE ÁREA (Evolução Total Investido) ---
        col4, = st.columns(1)
        with col4:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Evolução Total Investido</h4>", unsafe_allow_html=True)
            df_investimentos = df_completo[df_completo['Tipo'] == 'Investimento'].copy()
            if not df_investimentos.empty:
                periodos_unicos = pd.period_range(start=df_completo['Data'].min(), end=df_completo['Data'].max(), freq='M')
                dados_evolucao = []
                for p in periodos_unicos:
                    df_ate_mes = df_investimentos[df_investimentos['Periodo'] <= p]
                    total_mes = df_ate_mes.groupby('Categoria')['Valor'].last().sum() if not df_ate_mes.empty else 0.0
                    dados_evolucao.append({'MesAno': p.strftime('%m/%Y'), 'Total Investido': total_mes})
                
                df_evo = pd.DataFrame(dados_evolucao)
                
                fig4 = px.area(df_evo, x='MesAno', y='Total Investido')
                fig4.update_traces(line_color='#b197fc', fillcolor='rgba(177, 151, 252, 0.25)')
                fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=0, r=0), height=240, xaxis_title="", yaxis_title="")
                fig4.update_xaxes(showgrid=False, type='category')
                fig4.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.1)')
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("Ainda não há histórico de investimentos.")

# --- ABA 2: LANÇAMENTOS E BASE DE DADOS ---
elif aba_selecionada == "Lançamentos":
    st.title("➕ Lançamentos e Base")
    st.write("Registe as suas entradas e saídas diárias variadas.")

    aba_entrada, aba_saida, aba_banco = st.tabs(["Entradas 📈", "Saídas 📉", "Base de Dados 🗄️"])

    with aba_entrada:
        with st.form("form_entrada"):
            st.subheader("Nova Receita")
            data_entrada = st.date_input("Data", date.today())
            cat_entrada = st.selectbox("Categoria", ["Salário", "Investimento", "Outros"])
            val_entrada = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Entrada", use_container_width=True):
                if val_entrada > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({"Data": [data_entrada.strftime("%Y-%m-%d")], "Tipo": ["Receita"], "Categoria": [cat_entrada], "Detalhe": [""], "Valor": [val_entrada]})
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success("✅ Entrada registada no Banco de Dados!")

    with aba_saida:
        with st.form("form_saida"):
            st.subheader("Nova Despesa Variável")
            data_saida = st.date_input("Data", date.today())
            cat_saida = st.selectbox("Categoria", ["Lazer", "Cartão de Crédito", "Alimentação", "Compras", "Outros"])
            val_saida = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Saída", use_container_width=True):
                if val_saida > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({"Data": [data_saida.strftime("%Y-%m-%d")], "Tipo": ["Despesa"], "Categoria": [cat_saida], "Detalhe": [""], "Valor": [val_saida]})
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success("✅ Despesa registada no Banco de Dados!")

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
        st.download_button(label="📥 Baixar Ficheiro Consolidado (CSV)", data=csv, file_name="meu_controle_financeiro_geral.csv", mime="text/csv", use_container_width=True)

# --- ABA 3: CONTROLES (INVESTIMENTOS E CONTAS DO MÊS) ---
elif aba_selecionada == "Controles":
    st.title("⚙️ Controles")
    df_geral = carregar_dados()

    aba_invest, aba_contas = st.tabs(["Meus Investimentos 🚀", "Contas do Mês ✅"])

    with aba_invest:
        st.subheader("Gestão de Investimentos")
        st.write("Acompanhe e atualize os seus investimentos ao longo do tempo.")

        inv_names = df_geral[df_geral['Tipo'].isin(['Meta', 'Investimento'])]['Categoria'].unique()

        if len(inv_names) > 0:
            for inv_nome in inv_names:
                df_meta = df_geral[(df_geral['Tipo'] == 'Meta') & (df_geral['Categoria'] == inv_nome)]
                meta_val = float(df_meta['Valor'].iloc[-1]) if not df_meta.empty else 1.0
                prazo_val = str(df_meta['Detalhe'].iloc[-1]) if not df_meta.empty else "Não definido"
                
                df_inv = df_geral[(df_geral['Tipo'] == 'Investimento') & (df_geral['Categoria'] == inv_nome)]
                atual_val = float(df_inv['Valor'].iloc[-1]) if not df_inv.empty else 0.0
                
                progresso = min(atual_val / meta_val, 1.0) if meta_val > 0 else 0.0
                
                st.markdown(f"**{inv_nome}** (Prazo: *{prazo_val}*)")
                st.progress(progresso, text=f"Guardado: R$ {formatar_moeda(atual_val)} / Meta: R$ {formatar_moeda(meta_val)}")
            st.divider()
        else:
            st.info("Crie o seu primeiro investimento abaixo.")

        with st.expander("➕ Criar Novo Investimento / Meta", expanded=(len(inv_names)==0)):
            with st.form("form_cria_meta"):
                novo_nome = st.text_input("Nome do Investimento (ex: Tesouro Direto)")
                nova_meta = st.number_input("Objetivo Financeiro (R$)", min_value=0.0, step=100.0, format="%.2f")
                novo_prazo = st.text_input("Prazo (ex: 2 anos, Dez/2026)")
                
                if st.form_submit_button("Guardar Novo Investimento", use_container_width=True):
                    if novo_nome:
                        df_novo1 = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Meta"], "Categoria": [novo_nome], "Detalhe": [novo_prazo], "Valor": [nova_meta]})
                        df_novo2 = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Investimento"], "Categoria": [novo_nome], "Detalhe": ["Saldo Inicial"], "Valor": [0.0]})
                        df_geral = pd.concat([df_geral, df_novo1, df_novo2], ignore_index=True)
                        salvar_dados(df_geral)
                        st.success("✅ Investimento criado com sucesso!")
                        st.rerun()

        if len(inv_names) > 0:
            with st.expander("🔄 Atualizar Saldo Atual", expanded=True):
                with st.form("form_atualiza_saldo"):
                    inv_escolhido = st.selectbox("Qual investimento deseja atualizar?", inv_names)
                    novo_saldo = st.number_input("Qual é o saldo total HOJE? (R$)", min_value=0.0, step=50.0, format="%.2f")
                    
                    if st.form_submit_button("Atualizar Saldo", use_container_width=True):
                        df_novo = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Investimento"], "Categoria": [inv_escolhido], "Detalhe": ["Atualização de Saldo"], "Valor": [novo_saldo]})
                        df_geral = pd.concat([df_geral, df_novo], ignore_index=True)
                        salvar_dados(df_geral)
                        st.success(f"✅ Saldo de '{inv_escolhido}' atualizado para R$ {formatar_moeda(novo_saldo)}!")
                        st.rerun()

    with aba_contas:
        mes_atual_str = date.today().strftime('%m/%Y')
        mes_input = st.text_input("Mês de Referência (MM/AAAA)", value=mes_atual_str)
        st.subheader(f"Contas Pagas em {mes_input}")
        
        # Filtra e soma as contas registadas no mês consultado
        df_contas_mes = df_geral[(df_geral['Tipo'] == 'Despesa Fixa') & (df_geral['Detalhe'] == mes_input)]
        
        if not df_contas_mes.empty:
            total_contas = df_contas_mes['Valor'].sum()
            for index, row in df_contas_mes.iterrows():
                st.markdown(f"✅ **{row['Categoria']}**: R$ {formatar_moeda(row['Valor'])}")
            st.info(f"💰 **Total de contas fixas pagas:** R$ {formatar_moeda(total_contas)}")
        else:
            st.info("Nenhuma conta registada para este mês.")

        st.divider()
        st.subheader("Registar Nova Conta do Mês")
        with st.form("form_nova_conta"):
            col1, col2 = st.columns(2)
            with col1:
                conta_sugestao = st.selectbox("Selecione a Conta", ["Apartamento", "Evolução de obra", "Moto/Carro", "Faculdade", "Outra..."])
            with col2:
                conta_personalizada = st.text_input("Se escolheu 'Outra...', digite o nome:")
                
            valor_conta = st.number_input("Valor Pago (R$)", min_value=0.0, step=10.0, format="%.2f")
            
            if st.form_submit_button("Salvar Pagamento", use_container_width=True):
                nome_final = conta_personalizada if conta_sugestao == "Outra..." else conta_sugestao
                if nome_final and valor_conta > 0:
                    # Grava a conta como 'Despesa Fixa' vinculada ao Mês (Detalhe)
                    nova_conta = pd.DataFrame({
                        "Data": [date.today().strftime("%Y-%m-%d")],
                        "Tipo": ["Despesa Fixa"],
                        "Categoria": [nome_final],
                        "Detalhe": [mes_input],
                        "Valor": [valor_conta]
                    })
                    df_geral = pd.concat([df_geral, nova_conta], ignore_index=True)
                    salvar_dados(df_geral)
                    st.success(f"✅ Conta '{nome_final}' de R$ {formatar_moeda(valor_conta)} registada com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, informe o nome da conta e um valor maior que zero.")
