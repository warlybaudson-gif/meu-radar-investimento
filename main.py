import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black, Mobile e Tabelas
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 12px !important; color: #ffffff !important; border-collapse: collapse !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; white-space: nowrap !important; padding: 8px 4px !important; }
    td { background-color: #000000 !important; color: #ffffff !important; white-space: nowrap !important; border-bottom: 1px solid #222 !important; padding: 8px 4px !important; }
    .stTable { overflow-x: auto !important; display: block !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Incluso novos ativos) ---
# Tickers: Ouro (GC=F), Nvidia (NVDA), Dólar (USDBRL=X) + Originais
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "USDBRL=X"]
dados_radar = []
dados_volatilidade = []

# Busca câmbio primeiro para converter ativos estrangeiros
try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.0 # Fallback caso falhe

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            # Ajuste de conversão para Ouro e Nvidia
            if t in ["NVDA", "GC=F"]:
                if t == "GC=F": # Ouro é por Onça, convertemos para Grama
                    p_atual = (p_atual / 31.1035) * cambio_hoje
                else: # Nvidia apenas dólar para real
                    p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            # Se for dólar puro, a média também precisa ser ajustada
            if t in ["NVDA", "GC=F"]: m_30 = m_30 * (cambio_hoje if t != "GC=F" else cambio_hoje/31.1035)

            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X"] else 0.0
            
            variacoes = hist_30d['Close'].pct_change() * 100
            subidas = (variacoes > 0).sum()
            descidas = (variacoes < 0).sum()
            maior_alta = variacoes.max()
            maior_queda = variacoes.min()
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0
            
            is_recorde = "🚨 RECORDE" if var_hoje <= (maior_queda * 0.98) and var_hoje < 0 else ""
            
            nome_amigavel = "Jóias (Ouro)" if t == "GC=F" else ("Nvidia" if t == "NVDA" else t)

            dados_radar.append({
                "Ativo": nome_amigavel, "Preço": p_atual, "Média 30d": m_30, 
                "Status": status, "Ação": acao, "Div. 12m": divs, "Var_Hoje": var_hoje
            })
            dados_volatilidade.append({
                "Ativo": nome_amigavel, "Dias A/B": f"🟢{subidas}/🔴{descidas}", 
                "Pico": f"+{maior_alta:.2f}%", "Fundo": f"{maior_queda:.2f}%", "Alerta": is_recorde
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    # 1. RADAR
    st.subheader("🛰️ Radar de Ativos Consolidado")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp.drop(columns=["Var_Hoje"]))

    # 2. TERMÔMETRO DE GANÂNCIA
    st.markdown("---")
    st.subheader("🌡️ Termômetro de Ganância")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    t1, t2 = st.columns([1, 2])
    with t1:
        if score <= 25: st.error("😨 MEDO EXTREMO")
        elif score <= 50: st.warning("⚖️ NEUTRO / CAUTELA")
        elif score <= 75: st.info("🤑 GANÂNCIA")
        else: st.success("🚀 EUFORIA TOTAL")
    with t2:
        st.progress(score / 100)
        st.write(f"Índice de Ganância: **{score:.0f}%**")

    # 3. RAIO-X DE VOLATILIDADE
    st.markdown("---")
    st.subheader("📊 Raio-X de Volatilidade (Ativos + Novos)")
    st.table(df_vol)

    # 4. GESTOR DE PATRIMÔNIO (XP + ATIVOS FÍSICOS)
    st.markdown("---")
    st.subheader("🧮 Gestor de Patrimônio Real")
    c_in, c_out = st.columns([1, 1.2])
    with c_in:
        with st.expander("💼 Ativos Externos", expanded=True):
            v_minerais = st.number_input("Minerais Raros (R$):", value=0.0)
            g_joias = st.number_input("Jóias (Gramas de Ouro):", value=0.0)
            v_env = st.number_input("Saldo na XP (R$):", value=50.0)
            
    with c_out:
        # Preço do ouro hoje calculado no Radar
        p_ouro_grama = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0] if not df_radar.empty else 777.0
        val_joias_total = g_joias * p_ouro_grama
        
        # Patrimônio Consolidado
        patri_total = v_env + v_minerais + val_joias_total
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Jóias", f"R$ {val_joias_total:.2f}")
        m2.metric("Minerais", f"R$ {v_minerais:.2f}")
        m3.metric("Saldo XP", f"R$ {v_env:.2f}")
        
        st.metric("PATRIMÔNIO CONSOLIDADO", f"R$ {patri_total:.2f}", delta="Atualizado via Yahoo Finance")

    # 5. TENDÊNCIA
    st.markdown("---")
    st.subheader("📈 Tendência")
    sel = st.selectbox("Escolha o Ativo para análise gráfica:", df_radar['Ativo'].unique())
    # Mapeia de volta para o ticker original para o gráfico
    map_tickers = {"Jóias (Ouro)": "GC=F", "Nvidia": "NVDA"}
    ticker_graf = map_tickers.get(sel, sel)
    st.line_chart(yf.Ticker(ticker_graf).history(period="30d")['Close'])

# (O manual permanece igual, cobrindo as explicações anteriores)
with tab_manual:
    st.header("📖 Manual de Instruções - IA Rockefeller")
    # ... (restante do seu manual original)
