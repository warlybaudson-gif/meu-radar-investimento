import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÕES DE IDENTIDADE E LAYOUT
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. ESTILO TOTAL BLACK (IDENTIDADE VISUAL)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 12px !important; color: #ffffff !important; border-collapse: collapse !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; white-space: nowrap !important; padding: 8px 4px !important; }
    td { background-color: #000000 !important; color: #ffffff !important; white-space: nowrap !important; border-bottom: 1px solid #222 !important; padding: 8px 4px !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel & Carteira", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Consolidação Yahoo Finance) ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "NGLOY", "FGPHF", "USDBRL=X"]
dados_radar = []

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.30 

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            # Conversão para BRL
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio_hoje
                else: p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            nomes_dict = {"GC=F": "Jóias (Ouro)", "NVDA": "Nvidia (IA)", "NGLOY": "Nióbio", "FGPHF": "Grafeno"}
            nome_display = nomes_dict.get(t, t)
            
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100

            dados_radar.append({
                "Ativo": nome_display, "Ticker_Raw": t, "Preço": p_atual, "Média 30d": m_30, 
                "Div_Ano": divs, "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO",
                "Var_Hoje": variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0,
                "Pico": variacoes.max(), "Fundo": variacoes.min()
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)

# ==================== ABA 1: PAINEL & CARTEIRA ====================
with tab_painel:
    # 1. RADAR RESUMIDO
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    df_resumo = df_radar.copy()
    df_resumo["Preço"] = df_resumo["Preço"].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_resumo[["Ativo", "Preço", "Status"]])

    st.markdown("---")

    # 2. GESTOR DE CARTEIRA DINÂMICA (A Nova Funcionalidade)
    st.subheader("🧮 Minha Carteira Multiativos")
    
    # Chave Seletora para Habilitar Ativos
    ativos_escolhidos = st.multiselect(
        "Habilite os ativos que você possui na carteira:",
        options=df_radar["Ativo"].unique(),
        default=["PETR4.SA"]
    )

    if ativos_escolhidos:
        lista_carteira = []
        renda_total_mes = 0
        valor_total_investido = 0

        st.write("📝 **Preencha suas quantidades e custos médios:**")
        # Layout de colunas para os inputs
        cols = st.columns(len(ativos_escolhidos) if len(ativos_escolhidos) <= 4 else 4)
        
        for i, nome_ativo in enumerate(ativos_escolhidos):
            col_idx = i % 4
            with cols[col_idx]:
                st.markdown(f"**{nome_ativo}**")
                qtd = st.number_input(f"Quantidade:", min_value=0, value=1, key=f"q_{nome_ativo}")
                pm = st.number_input(f"Preço Médio (R$):", min_value=0.0, value=0.0, key=f"p_{nome_ativo}")
                
                # Dados do Radar
                preco_agora = df_radar[df_radar["Ativo"] == nome_ativo]["Preço"].values[0]
                div_ano = df_radar[df_radar["Ativo"] == nome_ativo]["Div_Ano"].values[0]
                
                # Cálculos
                posicao = qtd * preco_agora
                lucro = (preco_agora - pm) * qtd if pm > 0 else 0
                renda_mes = (div_ano * qtd) / 12
                
                lista_carteira.append({
                    "Ativo": nome_ativo, "Qtd": qtd, "PM": f"R$ {pm:.2f}",
                    "Valor Atual": f"R$ {posicao:.2f}", "Lucro/Prej": f"R$ {lucro:.2f}",
                    "Renda/Mês": f"R$ {renda_mes:.2f}"
                })
                valor_total_investido += posicao
                renda_total_mes += renda_mes

        st.markdown("### 📊 Consolidação da Carteira")
        st.table(pd.DataFrame(lista_carteira))

        # Totais e Extras
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        
        # Inputs laterais para bens físicos e saldo
        st.sidebar.subheader("💰 Patrimônio Extra")
        saldo_xp = st.sidebar.number_input("Saldo em Dinheiro na XP (R$):", value=0.0)
        v_minerais = st.sidebar.number_input("Valor Minerais Raros (R$):", value=0.0)
        
        total_geral = valor_total_investido + saldo_xp + v_minerais
        
        m1.metric("Total em Ativos", f"R$ {valor_total_investido:.2f}")
        m2.metric("Renda Passiva Mensal", f"R$ {renda_total_mes:.2f}")
        m3.metric("PATRIMÔNIO GLOBAL", f"R$ {total_geral:.2f}")

# ==================== ABA 2: MANUAL DIDÁTICO ====================
with tab_manual:
    st.header("📖 Manual de Instruções - IA Rockefeller V4")
    
    with st.expander("🛰️ 1. Radar e Novos Ativos (Ouro, Nióbio, Grafeno)", expanded=True):
        st.markdown("""
        * **Nióbio & Grafeno:** Como não são negociados diretamente, rastreamos as mineradoras **Anglo American** e **First Graphene**. O preço é convertido de Dólar para Real automaticamente.
        * **Jóias:** O valor reflete 1 grama de ouro puro convertido para Real.
        * **Status 🔥 BARATO:** Significa que o preço hoje está abaixo da média dos últimos 30 dias.
        """)

    with st.expander("🧮 2. Gestor Multiativos (Tabela Dinâmica)"):
        st.markdown("""
        * **Habilitar Ativos:** Use a 'Chave Seletora' para adicionar apenas os ativos que você comprou.
        * **Quantidade e PM:** Insira o quanto você tem e quanto pagou. O sistema mostrará seu lucro real na tabela.
        * **Renda Passiva:** A métrica 'Renda Passiva Mensal' no topo é a soma de todos os dividendos da sua carteira selecionada.
        """)

    with st.expander("📊 3. Patrimônio Global"):
        st.markdown("""
        * **Consolidação:** O sistema soma seus Ativos + Saldo XP + Minerais Raros para te dar sua riqueza real.
        * **Dica:** Mantenha seus preços médios atualizados para que o cálculo de Lucro/Prejuízo seja preciso.
        """)
