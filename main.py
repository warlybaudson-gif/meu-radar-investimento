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
dados_volatilidade = []

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.25 

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            # Conversão para BRL (Ativos Internacionais)
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": 
                    p_atual = (p_atual / 31.1035) * cambio_hoje
                else: 
                    p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            nomes_dict = {
                "GC=F": "Jóias (Ouro)", "NVDA": "Nvidia (IA)", 
                "NGLOY": "Nióbio (Proxy)", "FGPHF": "Grafeno (Proxy)"
            }
            nome_display = nomes_dict.get(t, t)

            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0
            
            dados_radar.append({
                "Ativo": nome_display, "Ticker_Raw": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO",
                "Ação": "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR",
                "Div_Ano": divs, "Var_Hoje": var_hoje
            })
            dados_volatilidade.append({
                "Ativo": nome_display, "Dias A/B": f"🟢{(variacoes > 0).sum()}/🔴{(variacoes < 0).sum()}", 
                "Pico": f"+{variacoes.max():.2f}%", "Fundo": f"{variacoes.min():.2f}%", 
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else ""
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL & CARTEIRA ====================
with tab_painel:
    # 1. RADAR DE ATIVOS
    st.subheader("🛰️ Radar de Ativos Consolidados")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div_Ano"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp[["Ativo", "Preço", "Média 30d", "Status", "Ação"]])

    # 2. TERMÔMETRO E VOLATILIDADE
    st.markdown("---")
    col_term, col_vol = st.columns([1, 1.5])
    with col_term:
        st.subheader("🌡️ Sentimento")
        caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
        score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
        st.progress(score / 100)
        st.write(f"Índice de Ganância: **{score:.0f}%**")
    with col_vol:
        st.subheader("📊 Volatilidade 30d")
        st.table(df_vol.head(5))

    # 3. GESTOR DE CARTEIRA DINÂMICA (A MUDANÇA SOLICITADA)
    st.markdown("---")
    st.subheader("🧮 Minha Carteira Multiativos")
    
    ativos_selecionados = st.multiselect(
        "Selecione os ativos que você possui para habilitar a gestão:",
        options=df_radar["Ativo"].unique(),
        default=["PETR4.SA"]
    )

    if ativos_selecionados:
        lista_carteira = []
        renda_total_mes = 0
        valor_total_investido = 0

        st.write("📝 **Ajuste Quantidades e Preços Médios:**")
        cols_input = st.columns(len(ativos_selecionados) if len(ativos_selecionados) <= 4 else 4)
        
        for idx, nome_ativo in enumerate(ativos_selecionados):
            with cols_input[idx % 4]:
                st.markdown(f"**{nome_ativo}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=0, key=f"q_{nome_ativo}")
                pm = st.number_input(f"PM (R$):", min_value=0.0, value=0.0, key=f"p_{nome_ativo}")
                
                # Dados para cálculo
                p_agora = df_radar[df_radar["Ativo"] == nome_ativo]["Preço"].values[0]
                d_ano = df_radar[df_radar["Ativo"] == nome_ativo]["Div_Ano"].values[0]
                
                v_posicao = qtd * p_agora
                lucro = (p_agora - pm) * qtd if pm > 0 else 0
                r_mes = (d_ano * qtd) / 12
                
                lista_carteira.append({
                    "Ativo": nome_ativo, "Qtd": qtd, "PM": f"R$ {pm:.2f}",
                    "Valor Atual": f"R$ {v_posicao:.2f}", "L/P Real": f"R$ {lucro:.2f}",
                    "Renda/Mês": f"R$ {r_mes:.2f}"
                })
                valor_total_investido += v_posicao
                renda_total_mes += r_mes

        st.markdown("### 📊 Tabela Consolidada")
        st.table(pd.DataFrame(lista_carteira))

        # 4. PATRIMÔNIO GLOBAL
        st.markdown("---")
        st.subheader("💰 Patrimônio Consolidado")
        c1, c2, c3 = st.columns(3)
        
        with st.sidebar:
            st.header("⚙️ Ajustes Físicos")
            saldo_xp = st.number_input("Saldo em Conta XP (R$):", value=0.0)
            g_ouro = st.number_input("Peso Ouro Físico (g):", value=0.0)
            v_extra = st.number_input("Outros Minerais (R$):", value=0.0)
            
        p_ouro = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0]
        total_ouro = g_ouro * p_ouro
        patri_total = valor_total_investido + saldo_xp + total_ouro + v_extra

        c1.metric("Ativos em Bolsa", f"R$ {valor_total_investido:.2f}")
        c2.metric("Renda Passiva Est.", f"R$ {renda_total_mes:.2f}/mês")
        c3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_total:.2f}")

# ==================== ABA 2: MANUAL DIDÁTICO ====================
with tab_manual:
    st.header("📖 Guia Estratégico IA Rockefeller")
    
    with st.expander("🛰️ 1. Radar e Ativos Estratégicos", expanded=True):
        st.markdown("""
        * **Nióbio & Grafeno:** Rastreia mineradoras líderes (Anglo American e First Graphene) como termômetro do setor.
        * **Ouro e Nvidia:** Conversão automática de câmbio para valores reais em BRL.
        """)

    with st.expander("🧮 2. Carteira Dinâmica (Como usar)"):
        st.markdown("""
        * **Chave Seletora:** No campo 'Selecione os ativos', você habilita apenas o que tem na carteira.
        * **Tabela:** O sistema gera automaticamente os cálculos de Lucro/Prejuízo e Renda baseados na sua quantidade e preço médio.
        * **Renda Passiva:** É a soma de todos os proventos dos ativos selecionados.
        """)
