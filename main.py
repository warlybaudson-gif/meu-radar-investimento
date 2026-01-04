import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black e Correção de Tabela Mobile
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* CORREÇÃO PARA CELULAR: Evitar quebra de texto nas tabelas */
    table { 
        width: 100% !important; 
        font-size: 12px !important; /* Fonte levemente menor para mobile */
        color: #ffffff !important; 
        border-collapse: collapse !important;
    }
    th { 
        background-color: #1a1a1a !important; 
        color: #58a6ff !important; 
        white-space: nowrap !important; /* Impede quebra no cabeçalho */
        padding: 8px 4px !important;
    }
    td { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        white-space: nowrap !important; /* Impede quebra nas células */
        border-bottom: 1px solid #222 !important; 
        padding: 8px 4px !important;
    }
    
    /* Container com rolagem lateral para evitar quebra do layout */
    .stTable { 
        overflow-x: auto !important; 
        display: block !important; 
    }

    /* Estilização Geral */
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist = ativo.history(period="2d")
        if not hist.empty:
            p_atual = hist['Close'].iloc[-1]
            p_ant = hist['Close'].iloc[0]
            var = ((p_atual / p_ant) - 1) * 100
            m_30 = ativo.history(period="30d")['Close'].mean()
            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            dados_finais.append({"Ativo": t, "Preço": p_atual, "Média 30d": m_30, "Status": status, "Ação": acao, "Div. 12m": divs, "Var%": var})
    except: continue
df_radar = pd.DataFrame(dados_finais)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: 
        df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    
    # Exibe a tabela (o CSS cuidará da não-quebra)
    st.table(df_disp.drop(columns=["Var%"]))

    st.markdown("---")
    st.subheader("🤖 Resumo da IA Rockefeller")
    if not df_radar.empty:
        df_radar['Desconto'] = (df_radar['Preço'] / df_radar['Média 30d']) - 1
        melhor = df_radar.sort_values(by='Desconto').iloc[0]
        st.info(f"**Análise Diária:** O ativo **{melhor['Ativo']}** é a melhor oportunidade hoje. A maior subida foi de **{df_radar.sort_values(by='Var%', ascending=False).iloc[0]['Ativo']}** ({df_radar['Var%'].max():.2f}%).")

    st.markdown("---")
    st.subheader("🌡️ Termômetro de Ganância")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    t1, t2 = st.columns([1, 2])
    with t1:
        if score <= 25: st.error("😨 MEDO EXTREMO")
        elif score <= 50: st.warning("⚖️ NEUTRO")
        elif score <= 75: st.info("🤑 GANÂNCIA")
        else: st.success("🚀 EUFORIA TOTAL")
    with t2:
        st.progress(score / 100)

    st.markdown("---")
    c_calc, c_res = st.columns([1, 1.2])
    with c_calc:
        st.subheader("🧮 Gestor XP")
        with st.expander("Sua Ordem", expanded=True):
            tipo = st.selectbox("Estratégia:", ("A Mercado", "Limitada", "Stop Loss"))
            v_env = st.number_input("Valor (R$):", value=50.0)
            p_pg = st.number_input("Preço Cota (R$):", value=31.0)
            c_at = st.number_input("Cotas atuais:", value=0)
            pm_at = st.number_input("PM atual:", value=0.0)
            n_cotas = int(v_env // p_pg)
            troco = v_env % p_pg
            try: p_mkt = df_radar[df_radar['Ativo']=="PETR4.SA"]['Preço'].values[0]
            except: p_mkt = p_pg
            patrimonio = (n_cotas * p_mkt) + troco
            n_pm = ((c_at * pm_at) + (n_cotas * p_pg)) / (c_at + n_cotas) if c_at > 0 else p_pg
    with c_res:
        st.subheader("📊 Resultado")
        st.metric("Cotas Novas", f"{n_cotas} un")
        st.metric("Troco", f"R$ {troco:.2f}")
        st.metric("Patrimônio Total", f"R$ {patrimonio:.2f}", f"R$ {patrimonio - v_env:.2f}")
        if c_at > 0: st.metric("Novo Preço Médio", f"R$ {n_pm:.2f}")

    st.markdown("---")
    st.subheader("💰 Projeção de Renda")
    a_div = st.selectbox("Ativo:", tickers)
    q_s = st.number_input("Qtd:", value=100)
    dv = df_radar[df_radar['Ativo']==a_div]['Div. 12m'].values[0] if not df_radar[df_radar['Ativo']==a_div].empty else 0
    st.metric("Renda Mensal", f"R$ {(dv * q_s / 12):.2f}")

    st.markdown("---")
    st.subheader("📈 Tendência 30d")
    sel = st.selectbox("Histórico:", tickers)
    st.line_chart(yf.Ticker(sel).history(period="30d")['Close'])

# ==================== ABA 2: MANUAL DE INSTRUÇÕES ====================
with tab_manual:
    st.header("📖 Manual do Utilizador")
    st.write("Aqui você encontra as instruções para cada módulo do sistema.")
    st.markdown("""
    * **Radar de Ativos:** Monitoramento baseado em médias de 30 dias.
    * **Termômetro:** Analisa o sentimento do mercado (Medo x Euforia).
    * **Gestor XP:** Simula ordens, calcula troco e novo preço médio.
    """)
