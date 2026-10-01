import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import date
import plotly.express as px
import os
import json

# Configuração da página para celular
st.set_page_config(page_title="Controle Financeiro", layout="centered", initial_sidebar_state="expanded")

# --- SISTEMAS DE ARMAZENAMENTO FÍSICO ---
ARQUIVO_DADOS = "meu_banco_de_dados.csv"
ARQUIVO_CONTROLES = "meus_controles.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

def carregar_controles():
    if os.path.exists(ARQUIVO_CONTROLES):
        with open(ARQUIVO_CONTROLES, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "contas_pagas": {},
        "metas_investimento": {"Reserva de Emergência": 0.0, "CDB / Tesouro Direto": 0.0, "Ações / FIIs": 0.0}
    }

def salvar_controles(dados):
    with open(ARQUIVO_CONTROLES, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- BARRA LATERAL (MENU BONITO E QUADRADO) ---
with st.sidebar:
    st.write("") 
    
    aba_selecionada = option_menu(
        menu_title="Meu Financeiro",
        options=["Painel", "Lançamentos", "Controles"],
        icons=["bar-chart-line-fill", "plus-circle-fill", "sliders"],
        menu_icon="wallet-fill",
        default_index=2, # Abre direto nos Controles para você testar
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
        st.info("Nenhum dado registrado ainda. Vá até 'Lançamentos' e faça o primeiro registro para ver os gráficos!")
    else:
        df_completo['Data'] = pd.to_datetime(df_completo['Data'])
        df_completo = df_completo.sort_values('Data')
        df_completo['MesAno'] = df_completo['Data'].dt.strftime('%m/%Y')
        
        meses_disponiveis = ["Todos os Meses"] + sorted(list(df_completo['MesAno'].unique()), reverse=True)
        mes_selecionado = st.selectbox("📅 Filtrar Mês (Balões e Gráficos de Rosca)", meses_disponiveis)
        
        if mes_selecionado != "Todos os Meses":
            df_filtrado = df_completo[df_completo['MesAno'] == mes_selecionado]
        else:
            df_filtrado = df_completo.copy()
            
        total_entradas = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
        total_saidas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']['Valor'].sum()
        liquido = total_entradas - total_saidas

        html_cards = f"""
        <style>
        .cards-wrapper {{ display: flex; flex-direction: row; justify-content: space-between; gap: 10px; margin-top: 10px; margin-bottom: 25px; overflow-x: auto; padding-bottom: 10px; }}
        .cards-wrapper::-webkit-scrollbar {{ display: none; }}
        .cards-wrapper {{ -ms-overflow-style: none; scrollbar-width: none; }}
        .card-custom {{ flex: 1; min-width: 95px; background-color: #ffffff; border-radius: 16px; padding: 15px 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #f8f9fa; transition: transform 0.2s ease; }}
        @media (prefers-color-scheme: dark) {{ .card-custom {{ background-color: #1a1a1a; border: 1px solid #2d2d2d; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }} }}
        .card-icon {{ font-size: 22px; margin-bottom: 4px; }}
        .card-title {{ font-size: 11px; color: #888; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; text-align: center; }}
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
        @media (prefers-color-scheme: dark) { [data-testid="stColumn"] { background-color: #1a1a1a; border: 1px solid #2d2d2d; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); } }
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
                st.info("Sem saídas no período.")

        with col2:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Renda vs Gastos</h4>", unsafe_allow_html=True)
            if total_entradas > 0 or total_saidas > 0:
                df_comparacao = pd.DataFrame({"Tipo": ["Entradas", "Saídas"], "Valor": [total_entradas, total_saidas]})
                df_comparacao = df_comparacao[df_comparacao['Valor'] > 0]
                fig2 = px.pie(df_comparacao, values='Valor', names='Tipo', hole=0.65, color='Tipo', color_discrete_map={"Entradas": "#20c997", "Saídas": "#ff6b6b"})
                fig2.update_traces(textposition='inside', textinfo='percent', hoverinfo='label+percent+value')
                fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados no período.")

        st.markdown("<h3 style='font-size: 18px; margin-top: 20px; margin-bottom: 5px; color: #555;'>Evolução Histórica</h3>", unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Comparativo Anual</h4>", unsafe_allow_html=True)
            df_agrupado = df_completo.groupby(['MesAno', 'Tipo'], as_index=False)['Valor'].sum()
            df_agrupado['Tipo'] = df_agrupado['Tipo'].replace({'Receita': 'Entradas', 'Despesa': 'Saídas'})
            fig3 = px.bar(df_agrupado, x='MesAno', y='Valor', color='Tipo', barmode='group', color_discrete_map={"Entradas": "#20c997", "Saídas": "#ff6b6b"})
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=0, r=0), height=240, legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, title=""), xaxis_title="", yaxis_title="")
            fig3.update_xaxes(showgrid=False)
            fig3.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.1)')
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown("<h4 style='text-align: center; color: #666; font-size: 15px; font-weight: 700; margin-bottom: 10px;'>Evolução do Guardado</h4>", unsafe_allow_html=True)
            df_pivot = df_completo.pivot_table(index='MesAno', columns='Tipo', values='Valor', aggfunc='sum', fill_value=0).reset_index()
            if 'Receita' not in df_pivot.columns: df_pivot['Receita'] = 0
            if 'Despesa' not in df_pivot.columns: df_pivot['Despesa'] = 0
            df_pivot['Guardado'] = df_pivot['Receita'] - df_pivot['Despesa']
            fig4 = px.bar(df_pivot, x='MesAno', y='Guardado')
            fig4.update_traces(marker_color='#b197fc')
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=0, r=0), height=240, xaxis_title="", yaxis_title="")
            fig4.update_xaxes(showgrid=False)
            fig4.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.1)')
            st.plotly_chart(fig4, use_container_width=True)

# --- ABA 2: LANÇAMENTOS ---
elif aba_selecionada == "Lançamentos":
    st.title("➕ Lançamentos")
    st.write("Registre e consulte suas movimentações financeiras.")

    aba_entrada, aba_saida, aba_banco = st.tabs(["Entradas 📈", "Saídas 📉", "Banco de Dados 🗄️"])

    with aba_entrada:
        with st.form("form_entrada"):
            st.subheader("Nova Receita")
            data_entrada = st.date_input("Data da Entrada", date.today())
            categoria_entrada = st.selectbox("Categoria", ["Salário", "Investimento", "Outros"])
            valor_entrada = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Entrada", use_container_width=True):
                if valor_entrada > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({"Data": [data_entrada.strftime("%Y-%m-%d")], "Tipo": ["Receita"], "Categoria": [categoria_entrada], "Valor": [valor_entrada]})
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success(f"✅ Entrada salva fisicamente!")

    with aba_saida:
        with st.form("form_saida"):
            st.subheader("Nova Despesa")
            data_saida = st.date_input("Data da Saída", date.today())
            categoria_saida = st.selectbox("Categoria", ["Apartamento", "Moto ou Carro", "Estudos", "Lazer", "Cartão"])
            valor_saida = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Salvar Saída", use_container_width=True):
                if valor_saida > 0:
                    df = carregar_dados()
                    nova_linha = pd.DataFrame({"Data": [data_saida.strftime("%Y-%m-%d")], "Tipo": ["Despesa"], "Categoria": [categoria_saida], "Valor": [valor_saida]})
                    df = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df)
                    st.success(f"✅ Saída salva fisicamente!")

    with aba_banco:
        st.subheader("Consultar Registos")
        df_banco = carregar_dados()
        if not df_banco.empty:
            st.dataframe(df_banco, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado registrado ainda.")

        st.divider()
        st.subheader("📤 Exportar Dados")
        csv = df_banco.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar Planilha CSV", data=csv, file_name="meu_controle_financeiro.csv", mime="text/csv", use_container_width=True)

        st.divider()
        st.subheader("📥 Importar Dados")
        arquivo_upload = st.file_uploader("Escolha um arquivo .CSV", type=["csv"])
        if arquivo_upload is not None:
            df_importado = pd.read_csv(arquivo_upload)
            if st.button("Substituir dados atuais pela planilha", use_container_width=True):
                salvar_dados(df_importado)
                st.success("Dados importados e salvos com sucesso!")
                st.rerun()

# --- ABA 3: CONTROLES ---
elif aba_selecionada == "Controles":
    st.title("⚙️ Controles")
    st.write("Acompanhe o pagamento das contas e planeie os investimentos por mês.")

    controles = carregar_controles()

    aba_contas, aba_invest = st.tabs(["Contas do Mês ✅", "Investimentos Planejados 🚀"])

    with aba_contas:
        st.subheader("Checklist de Pagamentos")
        
        # Filtro de Mês para os Controles
        mes_atual_str = date.today().strftime('%m/%Y')
        mes_input = st.text_input("Mês de Referência (MM/AAAA)", value=mes_atual_str)
        
        if mes_input not in controles["contas_pagas"]:
            # Inicializa as contas específicas solicitadas para o novo mês
            controles["contas_pagas"][mes_input] = {
                "Apartamento": False, 
                "Evolução de obra": False, 
                "Moto/Carro": False, 
                "Faculdade": False
            }
            salvar_controles(controles)

        st.info(f"Marque as contas pagas referentes a **{mes_input}**. Salvo automaticamente.")
        
        # Exibe as caixas de seleção para o mês escolhido
        contas_do_mes = controles["contas_pagas"][mes_input]
        for conta, status in list(contas_do_mes.items()):
            novo_status = st.checkbox(conta, value=status, key=f"chk_{mes_input}_{conta}")
            controles["contas_pagas"][mes_input][conta] = novo_status
            
        salvar_controles(controles)

        # Barra de Progresso Visual do Mês
        total_contas = len(contas_do_mes)
        contas_pagas = sum(contas_do_mes.values())
        
        if total_contas > 0:
            percentual = contas_pagas / total_contas
            st.progress(percentual, text=f"Progresso de {mes_input}: {contas_pagas} de {total_contas} contas pagas")
            
            if percentual == 1.0:
                st.success(f"🎉 Parabéns! Todas as contas de {mes_input} foram quitadas.")

        # Opção de adicionar nova conta personalizada se necessário
        st.divider()
        nova_conta = st.text_input("Adicionar outra conta a este mês:")
        if st.button("Adicionar Conta", use_container_width=True):
            if nova_conta and nova_conta not in controles["contas_pagas"][mes_input]:
                controles["contas_pagas"][mes_input][nova_conta] = False
                salvar_controles(controles)
                st.rerun()

    with aba_invest:
        st.subheader("Metas de Investimento")
        st.write("Defina o valor que pretende guardar para cada objetivo financeiro.")
        
        for invest, valor in controles["metas_investimento"].items():
            novo_valor = st.number_input(f"Meta para {invest} (R$)", value=float(valor), min_value=0.0, step=50.0, format="%.2f", key=f"inv_{invest}")
            controles["metas_investimento"][invest] = novo_valor
            
        salvar_controles(controles)

        total_investimentos = sum(controles["metas_investimento"].values())
        st.info(f"🎯 O seu objetivo total de investimentos é: **R$ {formatar_moeda(total_investimentos)}**")

        st.divider()
        novo_invest = st.text_input("Adicionar nova categoria de investimento:")
        if st.button("Adicionar Categoria", use_container_width=True):
            if novo_invest and novo_invest not in controles["metas_investimento"]:
                controles["metas_investimento"][novo_invest] = 0.0
                salvar_controles(controles)
                st.rerun()
