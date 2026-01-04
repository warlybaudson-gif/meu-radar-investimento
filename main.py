import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 13px !important; color: #ffffff !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; }
    td { background-color: #000000 !important; color: #ffffff !important; border-bottom: 1px solid #222 !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 26px !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 15px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Processamento de Dados (Radar)
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_1d = ativo.history(period="1d")
        if not hist_1d.empty:
            preco_atual = hist_1d['Close'].iloc[-1]
            hist_30d = ativo.history(period="30d")
            media_30 = hist_30d['Close'].mean()
            status = "🔥 BARATO" if preco_atual < media_30 else "💎 CARO"
            acao = "✅ COMPRAR" if preco_atual < media_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            dados_finais.append({
                "Ativo": t, "Preço": preco_atual, "Média 30d": media_30,
                "Status": status, "Ação": acao, "Div. 12m": divs
            })
    except: continue

df_radar = pd.DataFrame(dados_finais)

# --- RADAR ---
st.subheader("🛰️ Radar de Ativos")
df_display = df_radar.copy()
for col in ["Preço", "Média 30d", "Div. 12m"]:
    df_display[col] = df_display[col].apply(lambda x: f"R$ {x:.2f}")
st.table(df_display)

# --- NOVO BLOCO: PSICOLOGIA DO MERCADO (TERMÔMETRO) ---
st.markdown("---")
st.subheader("🌡️ Termômetro de Ganância (Market Sentiment)")
# Lógica do Termômetro: Quantos ativos estão "CAROS" vs "BARATOS"
caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
total = len(df_radar)
sentimento_score = (caros / total) * 100

col_term1, col_term2 = st.columns([1, 2])
with col_term1:
    if sentimento_score <= 25:
        st.error("😨 MEDO EXTREMO")
        st.caption("Oportunidade de ouro. Quase tudo está abaixo da média.")
    elif sentimento_score <= 50:
        st.warning("⚖️ NEUTRO / CAUTELA")
        st.caption("Mercado equilibrado. Seja seletivo.")
    elif sentimento_score <= 75:
        st.info("🤑 GANÂNCIA")
        st.caption("Muitos ativos subindo. Cuidado com o topo.")
    else:
        st.success("🚀 EUFORIA TOTAL")
        st.caption("Risco alto de correção. Todos os ativos estão caros.")

with col_term2:
    st.progress(sentimento_score / 100)
    st.write(f"Índice de Ganância do seu Radar: **{sentimento_score:.0f}%**")

# --- ALERTAS ---
st.markdown("---")
st.subheader("🎯 Alertas de Preço Alvo")
col_a1, col_a2 = st.columns(2)
with col_a1:
    alvo_ativo = st.selectbox("Ativo alvo:", tickers)
    preco_alvo = st.number_input(f"Alvo para {alvo_ativo}:", value=0.0)
with col_a2:
    if preco_alvo > 0:
        p_agora = df_radar[df_radar['Ativo'] == alvo_ativo]['Preço'].values[0]
        if p_agora <= preco_alvo: st.success("🚀 OPORTUNIDADE ATINGIDA!")
        else: st.write(f"Preço atual: R$ {p_agora:.2f}")

# --- GESTOR XP & PREÇO MÉDIO ---
st.markdown("---")
col_calc, col_res = st.columns([1, 1.2])
with col_calc:
    st.subheader("🧮 Gestor XP")
    with st.expander("Sua Ordem", expanded=True):
        valor_xp = st.number_input("Valor enviado (R$):", value=50.0)
        pago_xp = st.number_input("Preço pago (R$):", value=31.0)
        c_atuais = st.number_input("Cotas atuais:", value=0)
        pm_atual = st.number_input("PM atual:", value=0.0)
        
        c_novas = int(valor_xp // pago_xp)
        troco_xp = valor_xp % pago_xp
        novo_pm = ((c_atuais * pm_atual) + (c_novas * pago_xp)) / (c_atuais + c_novas) if c_atuais > 0 else pago_xp

with col_res:
    st.subheader("📊 Resultado")
    m1, m2 = st.columns(2)
    m1.metric("Cotas Novas", f"{c_novas} un")
    m2.metric("Troco", f"R$ {troco_xp:.2f}")
    if c_atuais > 0: st.metric("Novo Preço Médio", f"R$ {novo_pm:.2f}")

# --- PROJEÇÃO DE RENDA ---
st.markdown("---")
st.subheader("💰 Projeção de Renda")
ativo_div = st.selectbox("Simular renda de:", tickers)
qtd_sim = st.number_input("Quantidade de cotas:", value=100)
div_v = df_radar[df_radar['Ativo'] == ativo_div]['Div. 12m'].values[0] if not df_radar[df_radar['Ativo'] == ativo_div].empty else 0
st.metric("Renda Mensal Estimada", f"R$ {(div_v * qtd_sim / 12):.2f}")

# --- GRÁFICO ---
st.markdown("---")
st.subheader("📈 Tendência 30d")
escolha = st.selectbox("Ver gráfico de:", tickers)
st.line_chart(yf.Ticker(escolha).history(period="30d")['Close'])
