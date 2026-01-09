import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÕES
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. ESTILO TOTAL BLACK
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
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")
tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Incluindo Grafeno e Nióbio) ---
# NGLOY = Anglo American (Nióbio) | FGPHF = First Graphene (Grafeno)
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "NGLOY", "FGPHF", "USDBRL=X"]
dados_radar = []
dados_volatilidade = []

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.20 

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            # Conversão para BRL (Ativos Internacionais)
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio_hoje
                else: p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            # Nomes Amigáveis
            nomes = {
                "GC=F": "Jóias (Ouro)", "NVDA": "Nvidia (IA)", 
                "NGLOY": "Nióbio (Proxy)", "FGPHF": "Grafeno (Proxy)",
                "USDBRL=X": "Dólar Comercial"
            }
            nome_exibicao = nomes.get(t, t)

            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0
            
            dados_radar.append({
                "Ativo": nome_exibicao, "Ticker_Raw": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": status, "Ação": acao, "Div. 12m": divs, "Var_Hoje": var_hoje
            })
            dados_volatilidade.append({
                "Ativo": nome_exibicao, "Dias A/B": f"🟢{(variacoes > 0).sum()}/🔴{(variacoes < 0).sum()}", 
                "Pico": f"+{variacoes.max():.2f}%", "Fundo": f"{variacoes.min():.2f}%", 
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else ""
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp[["Ativo", "Preço", "Média 30d", "Status", "Ação"]])

    st.markdown("---")
    st.subheader("🧮 Gestor de Patrimônio Real")
    c_in, c_out = st.columns([1, 1.2])
    with c_in:
        with st.expander("Configurar Carteira", expanded=True):
            v_env = st.number_input("Saldo na XP (R$):", value=50.0)
            g_joias = st.number_input("Gramas de Ouro:", value=0.0)
            v_minerais = st.number_input("Minerais Raros/Nióbio Físico (R$):", value=0.0)
    
    with c_out:
        p_ouro = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0]
        patri_total = v_env + (g_joias * p_ouro) + v_minerais
        st.metric("PATRIMÔNIO CONSOLIDADO", f"R$ {patri_total:.2f}")
        st.info("Inclui Ativos Digitais, Metais e Minerais de Alta Tecnologia.")

    st.markdown("---")
    st.subheader("📊 Raio-X de Volatilidade (Grafeno & Nióbio inclusos)")
    st.table(df_vol)

# ==================== ABA 2: MANUAL ====================
with tab_manual:
    st.header("📖 Guia Estratégico IA Rockefeller")
    with st.expander("🔬 Monitoramento de Minerais de Tecnologia (Nióbio/Grafeno)"):
        st.markdown("""
        Como o Nióbio e o Grafeno não são ações comuns, a IA Rockefeller monitora as **empresas líderes** desses setores:
        * **Nióbio (Anglo American):** Uma das poucas mineradoras globais que extraem Nióbio de forma comercial. O status 'Barato' indica que o setor de mineração estratégica está em queda.
        * **Grafeno (First Graphene):** Empresa focada na aplicação industrial do grafeno. É um ativo de **Altíssima Volatilidade** (veja o Raio-X).
        * **Nióbio Físico:** Se você possui amostras ou minerais físicos, insira o valor estimado no campo **Minerais Raros** do Gestor.
        """)
    with st.expander("🧮 Gestor e Preço Médio"):
        st.markdown("Use esta aba para simular suas compras na XP e entender o impacto no seu patrimônio total.")
