import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black (Mantido e Refinado)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 13px !important; color: #ffffff !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; }
    td { background-color: #000000 !important; color: #ffffff !important; border-bottom: 1px solid #222 !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 26px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 15px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# Criando as Abas
tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Comum a ambas as abas) ---
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
    # 1. Radar
    st.subheader("🛰️ Radar de Ativos")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp.drop(columns=["Var%"]))

    # 2. Resumo IA
    st.markdown("---")
    st.subheader("🤖 Resumo da IA Rockefeller")
    if not df_radar.empty:
        df_radar['Desconto'] = (df_radar['Preço'] / df_radar['Média 30d']) - 1
        melhor = df_radar.sort_values(by='Desconto').iloc[0]
        st.info(f"**Análise Diária:** O ativo **{melhor['Ativo']}** é a melhor oportunidade hoje, com {abs(melhor['Desconto']*100):.1f}% de desconto sobre a média. A maior subida foi de **{df_radar.sort_values(by='Var%', ascending=False).iloc[0]['Ativo']}** ({df_radar['Var%'].max():.2f}%).")

    # 3. Termómetro
    st.markdown("---")
    st.subheader("🌡️ Termómetro de Ganância")
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

    # 4. Gestor XP
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
        st.metric("Património Total", f"R$ {patrimonio:.2f}", f"R$ {patrimonio - v_env:.2f}")
        if c_at > 0: st.metric("Novo Preço Médio", f"R$ {n_pm:.2f}")

    # 5. Renda e Gráfico
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
    st.header("📖 Manual do Utilizador - IA Rockefeller")
    
    st.subheader("1. 🛰️ Radar de Ativos")
    st.write("O Radar monitoriza os seus ativos em tempo real. A lógica baseia-se na **Média Móvel de 30 dias**. Se o preço atual for inferior à média, o ativo é marcado como 'Barato' (Oportunidade). Se for superior, é marcado como 'Caro' (Cautela).")

    st.subheader("2. 🌡️ Termómetro de Ganância")
    st.write("Este indicador mede a psicologia do mercado baseada na sua carteira. Se muitos ativos estiverem 'Caros', o termómetro sobe para **Euforia**, indicando risco de queda. Se estiverem 'Baratos', indica **Medo**, que é geralmente o melhor momento para comprar.")

    st.subheader("3. 🧮 Gestor XP & Preço Médio")
    st.write("Simule as suas ordens antes de ir para a corretora. O sistema calcula quantas cotas o seu dinheiro compra e quanto sobra de **Troco**. Ao inserir as suas cotas atuais, a IA prevê qual será o seu **Novo Preço Médio** após a compra.")

    st.subheader("4. 🤖 Resumo Inteligente")
    st.write("A IA analisa todos os dados e escreve um diagnóstico rápido, identificando automaticamente qual o ativo com o maior desconto matemático no dia.")

    st.info("💡 **Dica Estratégica:** Use o Radar para identificar ativos 'Baratos' e o Gestor XP para garantir que o seu Preço Médio está sempre a baixar.")
