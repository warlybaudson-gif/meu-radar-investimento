import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black (Mantido)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 12px !important; color: #ffffff !important; border-collapse: collapse !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; white-space: nowrap !important; padding: 8px 4px !important; }
    td { background-color: #000000 !important; color: #ffffff !important; white-space: nowrap !important; border-bottom: 1px solid #222 !important; padding: 8px 4px !important; }
    .stTable { overflow-x: auto !important; display: block !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Radar + Histórico de Volatilidade) ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_radar = []
dados_volatilidade = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        
        if not hist_30d.empty:
            # Dados para o Radar
            p_atual = hist_30d['Close'].iloc[-1]
            m_30 = hist_30d['Close'].mean()
            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            
            dados_radar.append({
                "Ativo": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": status, "Ação": acao, "Div. 12m": divs
            })
            
            # Dados para o Raio-X de Volatilidade (NOVO)
            variacoes = hist_30d['Close'].pct_change() * 100
            subidas = (variacoes > 0).sum()
            descidas = (variacoes < 0).sum()
            maior_alta = variacoes.max()
            maior_queda = variacoes.min()
            
            dados_volatilidade.append({
                "Ativo": t,
                "Dias de Alta": f"🟢 {subidas}",
                "Dias de Baixa": f"🔴 {descidas}",
                "Maior Subida": f"{maior_alta:.2f}%",
                "Maior Queda": f"{maior_queda:.2f}%"
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

with tab_painel:
    # 1. Radar Principal (Mantido)
    st.subheader("🛰️ Radar de Ativos")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp)

    # 2. NOVO BLOCO: RAIO-X DE VOLATILIDADE
    st.markdown("---")
    st.subheader("📊 Raio-X de Volatilidade (30 Dias)")
    st.caption("Frequência de oscilação e picos de preço.")
    st.table(df_vol)

    # 3. Resumo IA (Mantido)
    st.markdown("---")
    st.subheader("🤖 Resumo da IA Rockefeller")
    if not df_radar.empty:
        df_radar['Desconto'] = (df_radar['Preço'] / df_radar['Média 30d']) - 1
        melhor = df_radar.sort_values(by='Desconto').iloc[0]
        st.info(f"**Análise:** O ativo **{melhor['Ativo']}** é a melhor oportunidade hoje. Nos últimos 30 dias, ele teve {df_vol[df_vol['Ativo']==melhor['Ativo']]['Dias de Baixa'].values[0]} quedas, criando este ponto de entrada.")

    # 4. Termômetro, Gestor XP e Restante (Mantidos Sem Alteração)
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
    with t2: st.progress(score / 100)

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

# --- ABA MANUAL (Mantida) ---
with tab_manual:
    st.header("📖 Manual do Utilizador")
    st.write("Novo item: **Raio-X de Volatilidade** - Exibe a força do ativo. Se um ativo tem muitas baixas mas a 'Maior Subida' é alta, ele tem potencial de recuperação.")
