import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black e Mobile (Ajustado)
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

# --- PROCESSAMENTO DE DADOS (PETR4 INCLUÍDA) ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_radar = []
dados_volatilidade = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            m_30 = hist_30d['Close'].mean()
            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            
            variacoes = hist_30d['Close'].pct_change() * 100
            subidas = (variacoes > 0).sum()
            descidas = (variacoes < 0).sum()
            maior_alta = variacoes.max()
            maior_queda = variacoes.min()
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0
            
            is_recorde_queda = "🚨 RECORDE" if var_hoje <= maior_queda and var_hoje < 0 else ""
            
            dados_radar.append({
                "Ativo": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": status, "Ação": acao, "Div. 12m": divs, "Var_Hoje": var_hoje
            })
            
            dados_volatilidade.append({
                "Ativo": t,
                "Dias Alta/Baixa": f"🟢{subidas} / 🔴{descidas}",
                "Pico Mensal": f"+{maior_alta:.2f}%",
                "Fundo Mensal": f"{maior_queda:.2f}%",
                "Alerta": is_recorde_queda
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

with tab_painel:
    # 1. Radar Principal
    st.subheader("🛰️ Radar de Ativos")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp.drop(columns=["Var_Hoje"]))

    # 2. Resumo da IA
    st.markdown("---")
    st.subheader("🤖 Resumo da IA Rockefeller")
    if not df_radar.empty:
        recorde_ativo = df_vol[df_vol['Alerta'] == "🚨 RECORDE"]
        if not recorde_ativo.empty:
            st.error(f"⚠️ **ALERTA DE FUNDO:** O ativo **{recorde_ativo.iloc[0]['Ativo']}** atingiu hoje sua maior queda do mês!")
        else:
            df_radar['Desconto'] = (df_radar['Preço'] / df_radar['Média 30d']) - 1
            melhor = df_radar.sort_values(by='Desconto').iloc[0]
            st.info(f"**Análise:** O foco hoje é **{melhor['Ativo']}**, com o melhor desconto técnico sobre a média.")

    # 3. Raio-X de Volatilidade
    st.markdown("---")
    st.subheader("📊 Raio-X de Volatilidade (30 Dias)")
    st.table(df_vol)

    # 4. Termómetro
    st.markdown("---")
    st.subheader("🌡️ Termómetro de Ganância")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    t1, t2 = st.columns([1, 2])
    with t1:
        if score <= 25: st.error("😨 MEDO EXTREMO")
        elif score <= 50: st.warning("⚖️ NEUTRO")
        else: st.success("🚀 EUFORIA")
    with t2: st.progress(score / 100)

    # 5. Gestor XP (PETR4 DEFINIDA COMO PADRÃO)
    st.markdown("---")
    c_calc, c_res = st.columns([1, 1.2])
    with c_calc:
        st.subheader("🧮 Gestor XP")
        with st.expander("Sua Ordem", expanded=True):
            v_env = st.number_input("Valor (R$):", value=50.0)
            # Busca o preço real da PETR4 para sugerir no campo
            p_petr_sugerido = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0] if not df_radar.empty else 31.0
            p_pg = st.number_input("Preço da Cota (R$):", value=float(p_petr_sugerido))
            c_at = st.number_input("Cotas atuais:", value=0)
            pm_at = st.number_input("PM atual:", value=0.0)
            
            n_cotas = int(v_env // p_pg)
            troco = v_env % p_pg
            n_pm = ((c_at * pm_at) + (n_cotas * p_pg)) / (c_at + n_cotas) if c_at > 0 else p_pg
    with c_res:
        st.subheader("📊 Resultado")
        st.metric("Cotas Novas", f"{n_cotas} un")
        st.metric("Troco", f"R$ {troco:.2f}")
        # Patrimônio baseado no preço real da PETR4 agora
        p_mkt = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0] if not df_radar.empty else p_pg
        patri = (n_cotas * p_mkt) + troco
        st.metric("Patrimônio Total", f"R$ {patri:.2f}", f"R$ {patri - v_env:.2f}")
        if c_at > 0: st.metric("Novo PM", f"R$ {n_pm:.2f}")

    # 6. Gráfico
    st.markdown("---")
    st.subheader("📈 Tendência 30d")
    sel = st.selectbox("Histórico:", tickers)
    st.line_chart(yf.Ticker(sel).history(period="30d")['Close'])

# --- ABA MANUAL ---
with tab_manual:
    st.header("📖 Manual do Utilizador")
    st.write("O sistema processa PETR4.SA, VALE3.SA, MXRF11.SA e BTC-USD. O Gestor XP usa a PETR4 como ativo padrão de referência.")
