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

# --- ESTILO GLOBAL MELHORADO ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding-top: 10px; padding-bottom: 10px; }
    [data-testid="stColumn"] {
        background: linear-gradient(145deg, #ffffff, #f0f2f6);
        border-radius: 24px; padding: 20px 10px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef; margin-bottom: 15px;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stColumn"] {
            background: linear-gradient(145deg, #1e1e1e, #121212);
            border: 1px solid #2d2d2d; box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (MENU ELEGANTE) ---
with st.sidebar:
    st.write("") 
    aba_selecionada = option_menu(
        menu_title="O Meu Financeiro",
        options=["Painel", "Lançamentos", "Controles"],
        icons=["pie-chart-fill", "plus-circle-fill", "ui-checks-grid"],
        menu_icon="wallet-fill",
        default_index=2, 
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#6c757d", "font-size": "22px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "8px 0px", "padding": "12px", "border-radius": "12px", "--hover-color": "#f0f2f6"},
            "nav-link-selected": {"background-color": "#4361ee", "color": "white", "font-weight": "bold"},
        }
    )

# --- ABA 1: PAINEL ---
if aba_selecionada == "Painel":
    st.title("✨ Visão Geral")
    df_completo = carregar_dados()
    
    if not df_completo.empty:
        df_completo['Data'] = pd.to_datetime(df_completo['Data'])
        df_completo = df_completo.sort_values('Data')
        df_completo['MesAno'] = df_completo['Data'].dt.strftime('%m/%Y')
        df_completo['Periodo'] = df_completo['Data'].dt.to_period('M')

    df_financeiro = df_completo[df_completo['Tipo'].isin(['Receita', 'Despesa', 'Despesa Fixa'])].copy()
    
    if df_financeiro.empty:
        st.info("Nenhum lançamento registado ainda. Vá a 'Lançamentos' e comece a inserir os seus dados!")
    else:
        meses_disponiveis = ["Todos os Meses"] + sorted(list(df_financeiro['MesAno'].unique()), reverse=True)
        mes_selecionado = st.selectbox("📅 Analisar Período", meses_disponiveis)
        
        if mes_selecionado != "Todos os Meses":
            df_filtrado = df_financeiro[df_financeiro['MesAno'] == mes_selecionado]
        else:
            df_filtrado = df_financeiro.copy()
            
        total_entradas = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
        total_saidas = df_filtrado[df_filtrado['Tipo'].isin(['Despesa', 'Despesa Fixa'])]['Valor'].sum()
        liquido = total_entradas - total_saidas

        # --- CARTÕES PREMIUM ---
        html_cards = f"""
        <style>
        .cards-wrapper {{ display: flex; flex-direction: row; justify-content: space-between; gap: 12px; margin-top: 5px; margin-bottom: 30px; overflow-x: auto; padding-bottom: 15px; }}
        .cards-wrapper::-webkit-scrollbar {{ display: none; }}
        .card-custom {{
            flex: 1; min-width: 100px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 20px; padding: 18px 8px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.06);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            border: 1px solid #f1f3f5; transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .card-custom:hover {{ transform: translateY(-3px); box-shadow: 0 12px 25px rgba(0,0,0,0.1); }}
        @media (prefers-color-scheme: dark) {{
            .card-custom {{ background: linear-gradient(135deg, #242424 0%, #1a1a1a 100%); border: 1px solid #333; box-shadow: 0 10px 20px rgba(0,0,0,0.4); }}
        }}
        .card-icon {{ font-size: 26px; margin-bottom: 6px; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1)); }}
        .card-title {{ font-size: 11px; color: #888; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; text-align: center; }}
        .card-value {{ font-size: 18px; font-weight: 900; text-align: center; letter-spacing: -0.5px; }}
        .text-green {{ color: #10b981; }} .text-red {{ color: #ef4444; }} .text-blue {{ color: #3b82f6; }}
        </style>
        <div class="cards-wrapper">
            <div class="card-custom"><div class="card-icon">📈</div><div class="card-title">Entradas</div><div class="card-value text-green">R$ {formatar_moeda(total_entradas)}</div></div>
            <div class="card-custom"><div class="card-icon">📉</div><div class="card-title">Saídas</div><div class="card-value text-red">R$ {formatar_moeda(total_saidas)}</div></div>
            <div class="card-custom"><div class="card-icon">💎</div><div class="card-title">Líquido</div><div class="card-value text-blue">R$ {formatar_moeda(liquido)}</div></div>
        </div>
        """
        st.markdown(html_cards, unsafe_allow_html=True)
        
        # --- GRÁFICOS DE PIZZA ---
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 5px;'>Despesas</h4>", unsafe_allow_html=True)
            df_despesas = df_filtrado[df_filtrado['Tipo'].isin(['Despesa', 'Despesa Fixa'])]
            if not df_despesas.empty and df_despesas['Valor'].sum() > 0:
                fig1 = px.pie(df_despesas, values='Valor', names='Categoria', color_discrete_sequence=px.colors.qualitative.Pastel)
                fig1.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#FFFFFF', width=2)))
                fig1.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=230, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sem saídas.")

        with col2:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 5px;'>Renda vs Gastos</h4>", unsafe_allow_html=True)
            if total_entradas > 0 or total_saidas > 0:
                df_comparacao = pd.DataFrame({"Tipo": ["Entradas", "Saídas"], "Valor": [total_entradas, total_saidas]})
                fig2 = px.pie(df_comparacao, values='Valor', names='Tipo', color='Tipo', color_discrete_map={"Entradas": "#10b981", "Saídas": "#ef4444"})
                fig2.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#FFFFFF', width=2)))
                fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=230, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados.")

        st.markdown("<h3 style='font-size: 18px; margin-top: 25px; margin-bottom: 10px; color: #555; font-weight: 800;'>Evolução Histórica</h3>", unsafe_allow_html=True)

        col3, = st.columns(1)
        with col3:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Balanço Mensal</h4>", unsafe_allow_html=True)
            df_financeiro_agrup = df_financeiro.copy()
            df_financeiro_agrup['Tipo'] = df_financeiro_agrup['Tipo'].replace({'Receita': 'Entradas', 'Despesa': 'Saídas', 'Despesa Fixa': 'Saídas'})
            df_agrupado = df_financeiro_agrup.groupby(['Periodo', 'Tipo'], as_index=False)['Valor'].sum()
            df_agrupado['MesAno'] = df_agrupado['Periodo'].dt.strftime('%b/%y') 
            
            fig3 = px.bar(df_agrupado, x='MesAno', y='Valor', color='Tipo', barmode='group', color_discrete_map={"Entradas": "#10b981", "Saídas": "#ef4444"})
            fig3.update_traces(marker_line_width=0, opacity=0.9, texttemplate='%{y:$.2s}', textposition='outside')
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=10, l=0, r=0), height=260, legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5, title=""), xaxis_title="", yaxis_title="")
            fig3.update_xaxes(showgrid=False, type='category')
            fig3.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.1)', visible=False)
            st.plotly_chart(fig3, use_container_width=True)

        col4, = st.columns(1)
        with col4:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Crescimento de Investimentos</h4>", unsafe_allow_html=True)
            df_investimentos = df_completo[df_completo['Tipo'] == 'Investimento'].copy()
            if not df_investimentos.empty:
                periodos_unicos = pd.period_range(start=df_completo['Data'].min(), end=df_completo['Data'].max(), freq='M')
                dados_evolucao = []
                for p in periodos_unicos:
                    df_ate_mes = df_investimentos[df_investimentos['Periodo'] <= p]
                    total_mes = df_ate_mes.groupby('Categoria')['Valor'].last().sum() if not df_ate_mes.empty else 0.0
                    dados_evolucao.append({'MesAno': p.strftime('%b/%y'), 'Património': total_mes})
                
                df_evo = pd.DataFrame(dados_evolucao)
                
                fig4 = px.area(df_evo, x='MesAno', y='Património')
                fig4.update_traces(line=dict(color='#8b5cf6', width=3), fillcolor='rgba(139, 92, 246, 0.3)', mode='lines+markers', marker=dict(size=6, color='#8b5cf6', symbol='circle'))
                fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=0, r=0), height=260, xaxis_title="", yaxis_title="")
                fig4.update_xaxes(showgrid=False, type='category')
                fig4.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.1)')
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("Ainda não há histórico de investimentos.")

# --- ABA 2: LANÇAMENTOS, INVESTIMENTOS E BASE DE DADOS ---
elif aba_selecionada == "Lançamentos":
    st.title("💸 Operações")
    st.write("Gira os seus fluxos de caixa e investimentos.")

    aba_entrada, aba_saida, aba_invest, aba_banco = st.tabs(["Receitas 📈", "Despesas 📉", "Investir 🚀", "Dados 🗄️"])

    with aba_entrada:
        with st.form("form_entrada"):
            st.subheader("Nova Receita")
            data_entrada = st.date_input("Data", date.today())
            cat_entrada = st.selectbox("Categoria", ["Salário", "Rendimentos", "Vendas", "Outros"])
            val_entrada = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Guardar Receita", use_container_width=True, type="primary"):
                if val_entrada > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({"Data": [data_entrada.strftime("%Y-%m-%d")], "Tipo": ["Receita"], "Categoria": [cat_entrada], "Detalhe": [""], "Valor": [val_entrada]})
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success("✅ Guardado com sucesso!")

    with aba_saida:
        with st.form("form_saida"):
            st.subheader("Nova Despesa Variável")
            data_saida = st.date_input("Data", date.today())
            cat_saida = st.selectbox("Categoria", ["Lazer", "Cartão de Crédito", "Alimentação", "Compras", "Transporte", "Outros"])
            val_saida = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Guardar Despesa", use_container_width=True, type="primary"):
                if val_saida > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({"Data": [data_saida.strftime("%Y-%m-%d")], "Tipo": ["Despesa"], "Categoria": [cat_saida], "Detalhe": [""], "Valor": [val_saida]})
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success("✅ Guardado com sucesso!")

    with aba_invest:
        st.subheader("O Meu Portfólio")
        df_geral = carregar_dados()
        inv_names = df_geral[df_geral['Tipo'].isin(['Meta', 'Investimento'])]['Categoria'].unique()

        if len(inv_names) > 0:
            for inv_nome in inv_names:
                df_meta = df_geral[(df_geral['Tipo'] == 'Meta') & (df_geral['Categoria'] == inv_nome)]
                meta_val = float(df_meta['Valor'].iloc[-1]) if not df_meta.empty else 1.0
                prazo_val = str(df_meta['Detalhe'].iloc[-1]) if not df_meta.empty else "Não definido"
                
                df_inv = df_geral[(df_geral['Tipo'] == 'Investimento') & (df_geral['Categoria'] == inv_nome)]
                atual_val = float(df_inv['Valor'].iloc[-1]) if not df_inv.empty else 0.0
                
                progresso = min(atual_val / meta_val, 1.0) if meta_val > 0 else 0.0
                
                st.markdown(f"<div style='font-size: 15px; font-weight: 700; color: #4361ee;'>{inv_nome} <span style='font-size: 12px; color: #888; font-weight: 400;'>({prazo_val})</span></div>", unsafe_allow_html=True)
                st.progress(progresso, text=f"R$ {formatar_moeda(atual_val)} de R$ {formatar_moeda(meta_val)}")
                st.write("")
            st.divider()
        else:
            st.info("Crie o seu primeiro objetivo financeiro.")

        with st.expander("➕ Novo Objetivo", expanded=(len(inv_names)==0)):
            with st.form("form_cria_meta"):
                novo_nome = st.text_input("Nome (ex: Tesouro Selic, Fundo Imobiliário)")
                nova_meta = st.number_input("Meta Alvo (R$)", min_value=0.0, step=100.0, format="%.2f")
                novo_prazo = st.text_input("Prazo / Horizonte")
                
                if st.form_submit_button("Criar Objetivo", use_container_width=True, type="primary"):
                    if novo_nome:
                        df_novo1 = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Meta"], "Categoria": [novo_nome], "Detalhe": [novo_prazo], "Valor": [nova_meta]})
                        df_novo2 = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Investimento"], "Categoria": [novo_nome], "Detalhe": ["Saldo Inicial"], "Valor": [0.0]})
                        df_geral = pd.concat([df_geral, df_novo1, df_novo2], ignore_index=True)
                        salvar_dados(df_geral)
                        st.success("✅ Objetivo criado!")
                        st.rerun()

        if len(inv_names) > 0:
            with st.expander("🔄 Atualizar Saldo", expanded=True):
                with st.form("form_atualiza_saldo"):
                    inv_escolhido = st.selectbox("Investimento", inv_names)
                    novo_saldo = st.number_input("Saldo Total Atualizado (R$)", min_value=0.0, step=50.0, format="%.2f")
                    
                    if st.form_submit_button("Registar Saldo", use_container_width=True, type="primary"):
                        df_novo = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Investimento"], "Categoria": [inv_escolhido], "Detalhe": ["Atualização de Saldo"], "Valor": [novo_saldo]})
                        df_geral = pd.concat([df_geral, df_novo], ignore_index=True)
                        salvar_dados(df_geral)
                        st.success(f"✅ Atualizado!")
                        st.rerun()

    with aba_banco:
        st.subheader("Gestão da Base de Dados")
        df_banco = carregar_dados()
        
        if not df_banco.empty:
            st.dataframe(df_banco, use_container_width=True, hide_index=True)
        else:
            st.info("A base de dados está vazia.")

        st.divider()
        st.subheader("Ferramentas")
        col1, col2 = st.columns(2)
        with col1:
            csv = df_banco.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Exportar (.CSV)", data=csv, file_name="financas_consolidadas.csv", mime="text/csv", use_container_width=True, type="primary")
        with col2:
            if st.button("🗑️ Apagar Tudo", use_container_width=True):
                df_vazio = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Detalhe", "Valor"])
                salvar_dados(df_vazio)
                st.success("✅ Base de dados limpa com sucesso!")
                st.rerun()

        st.divider()
        st.subheader("Restaurar Base de Dados")
        st.write("Faça o upload do ficheiro CSV que exportou anteriormente para restaurar os seus dados.")
        arquivo_upload = st.file_uploader("Escolher ficheiro .CSV", type=["csv"])
        
        if arquivo_upload is not None:
            if st.button("Restaurar Dados", use_container_width=True, type="primary"):
                try:
                    df_importado = pd.read_csv(arquivo_upload)
                    colunas_padrao = ["Data", "Tipo", "Categoria", "Detalhe", "Valor"]
                    for col in colunas_padrao:
                        if col not in df_importado.columns:
                            df_importado[col] = "" if col != "Valor" else 0.0
                    df_importado = df_importado[colunas_padrao]
                    salvar_dados(df_importado)
                    st.success("✅ Base de dados restaurada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error("Erro ao ler o ficheiro. Verifique se é o CSV correto.")

# --- ABA 3: CONTROLES DE CONTAS MENSAIS ---
elif aba_selecionada == "Controles":
    st.title("⚙ Contas Fixas")
    st.write("Gestão inteligente dos seus compromissos recorrentes.")
    df_geral = carregar_dados()

    # Variáveis de sessão para o Mês e Ano
    if 'mes_controle' not in st.session_state:
        st.session_state['mes_controle'] = date.today().strftime('%m')
    if 'ano_controle' not in st.session_state:
        st.session_state['ano_controle'] = str(date.today().year)

    # --- FILTRO DE MÊS E ANO (CAIXAS DE SELEÇÃO) ---
    meses_dict = {"01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril", "05": "Maio", "06": "Junho", 
                  "07": "Julho", "08": "Agosto", "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"}
    nomes_meses = list(meses_dict.values())
    mes_atual_nome = meses_dict[st.session_state['mes_controle']]

    ano_atual = date.today().year
    lista_anos = [str(a) for a in range(ano_atual - 2, ano_atual + 4)]
    
    col1, col2 = st.columns(2)
    with col1:
        mes_selecionado = st.selectbox("📅 Selecione o Mês:", nomes_meses, index=nomes_meses.index(mes_atual_nome))
    with col2:
        ano_selecionado = st.selectbox("📅 Selecione o Ano:", lista_anos, index=lista_anos.index(st.session_state['ano_controle']))

    # Recupera o número do mês com base no nome selecionado
    mes_num_selecionado = [k for k, v in meses_dict.items() if v == mes_selecionado][0]

    # Atualiza a sessão e recarrega a página se os filtros mudarem
    if mes_num_selecionado != st.session_state['mes_controle'] or ano_selecionado != st.session_state['ano_controle']:
        st.session_state['mes_controle'] = mes_num_selecionado
        st.session_state['ano_controle'] = ano_selecionado
        st.rerun()

    mes_input = f"{st.session_state['mes_controle']}/{st.session_state['ano_controle']}"
    mes_selecionado_dt = pd.to_datetime(mes_input, format='%m/%Y')

    st.divider()

    df_setups = df_geral[df_geral['Tipo'] == 'Conta Fixa Setup']
    df_pagas = df_geral[(df_geral['Tipo'] == 'Despesa Fixa') & (df_geral['Detalhe'] == mes_input)]
    nomes_pagas = df_pagas['Categoria'].tolist()

    contas_ativas_mes = []
    
    for _, row in df_setups.iterrows():
        setup_dt = pd.to_datetime(row['Data'])
        setup_mes_dt = pd.to_datetime(setup_dt.strftime('%m/%Y'), format='%m/%Y')
        
        diff_meses = (mes_selecionado_dt.year - setup_mes_dt.year) * 12 + (mes_selecionado_dt.month - setup_mes_dt.month)
        
        if diff_meses >= 0: 
            if row['Detalhe'] == 'Indefinido':
                contas_ativas_mes.append(row)
            else:
                try:
                    duracao = int(row['Detalhe'])
                    if diff_meses < duracao: 
                        contas_ativas_mes.append(row)
                except:
                    pass

    # --- CONTAS PAGAS (CARTÃO LUXO) ---
    st.subheader(f"✅ Pagas em {mes_selecionado} de {st.session_state['ano_controle']}")
    if not df_pagas.empty:
        total_contas = df_pagas['Valor'].sum()
        
        html_contas = f"""
        <style>
        .bill-card {{ background: linear-gradient(135deg, #ffffff 0%, #f1f8ff 100%); border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; margin-bottom: 25px; }}
        @media (prefers-color-scheme: dark) {{ .bill-card {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }} }}
        .bill-total {{ font-size: 20px; font-weight: 900; color: #2563eb; text-align: center; margin-bottom: 25px; letter-spacing: -0.5px; }}
        @media (prefers-color-scheme: dark) {{ .bill-total {{ color: #3b82f6; }} }}
        .bill-item {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px dashed #cbd5e1; font-size: 16px; align-items: center; }}
        @media (prefers-color-scheme: dark) {{ .bill-item {{ border-bottom: 1px dashed #475569; }} }}
        .bill-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
        .bill-name {{ font-weight: 600; color: #334155; display: flex; align-items: center; gap: 8px; }}
        @media (prefers-color-scheme: dark) {{ .bill-name {{ color: #f8fafc; }} }}
        .bill-value {{ font-weight: 800; color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 4px 10px; border-radius: 8px; }}
        </style>
        <div class="bill-card"><div class="bill-total">Total Cumprido: R$ {formatar_moeda(total_contas)}</div>
        """
        for index, row in df_pagas.iterrows():
            html_contas += f'<div class="bill-item"><span class="bill-name"><span style="color:#10b981;">✔</span> {row["Categoria"]}</span><span class="bill-value">R$ {formatar_moeda(row["Valor"])}</span></div>'
        html_contas += "</div>"
        st.markdown(html_contas, unsafe_allow_html=True)
    else:
        st.info("Ainda não liquidou nenhuma conta neste mês.")

    # --- CONTAS PENDENTES ---
    contas_unicas = {}
    for c in contas_ativas_mes:
        if c['Categoria'] not in nomes_pagas and c['Categoria'] not in contas_unicas:
            contas_unicas[c['Categoria']] = c

    contas_pendentes = list(contas_unicas.values())
    
    st.subheader(f"⏳ A Pagar")
    if contas_pendentes:
        for idx, p in enumerate(contas_pendentes):
            with st.form(f"pagar_{idx}_{p['Categoria']}"):
                colA, colB, colC = st.columns([2, 1, 1])
                with colA:
                    st.markdown(f"<div style='margin-top: 5px; font-weight: 700; font-size: 15px;'>{p['Categoria']}</div>", unsafe_allow_html=True)
                    st.caption(f"Previsto: R$ {formatar_moeda(p['Valor'])}")
                with colB:
                    valor_pago = st.number_input("Valor", value=float(p['Valor']), min_value=0.0, step=10.0, key=f"val_{idx}_{p['Categoria']}", label_visibility="collapsed")
                with colC:
                    if st.form_submit_button("Pagar", use_container_width=True, type="primary"):
                        nova_conta = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Despesa Fixa"], "Categoria": [p['Categoria']], "Detalhe": [mes_input], "Valor": [valor_pago]})
                        df_geral = pd.concat([df_geral, nova_conta], ignore_index=True)
                        salvar_dados(df_geral)
                        st.rerun()
    else:
        if contas_ativas_mes:
            st.success("🎉 Tudo pago! Não tem mais pendências este mês.")
        else:
            st.info("Não tem compromissos configurados.")

    st.divider()

    # --- CONFIGURAR NOVA CONTA ---
    with st.expander("⚙ Adicionar Nova Conta Recorrente"):
        st.write("Automatize as suas contas (ex: renda, mensalidades).")
        with st.form("form_setup_conta"):
            nome_conta = st.text_input("Nome da Conta")
            valor_estimado = st.number_input("Valor Médio Previsto (R$)", min_value=0.0, step=10.0, format="%.2f")
            
            indefinido = st.checkbox("Recorrente (Para Sempre)", value=True)
            duracao = st.number_input("Ou defina a Duração (meses)", min_value=1, value=12, step=1, disabled=indefinido)
            
            if st.form_submit_button("Configurar Conta", use_container_width=True, type="primary"):
                if nome_conta and valor_estimado > 0:
                    detalhe_duracao = "Indefinido" if indefinido else str(duracao)
                    novo_setup = pd.DataFrame({"Data": [date.today().strftime("%Y-%m-%d")], "Tipo": ["Conta Fixa Setup"], "Categoria": [nome_conta], "Detalhe": [detalhe_duracao], "Valor": [valor_estimado]})
                    df_geral = pd.concat([df_geral, novo_setup], ignore_index=True)
                    salvar_dados(df_geral)
                    st.success(f"✅ Conta ativada com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos obrigatórios.")
