import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black e Visibilidade
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
    .streamlit-expanderContent { background-color: #000000 !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Processamento de Dados (Radar)
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist = ativo.history(period="1d")
        if not hist.empty:
            p_atual = hist['Close'].iloc[-1]
            m_30 = ativo.history(period="30d")['Close'].mean()
            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            dados_finais.append({"Ativo": t, "Preço": p_atual, "Média 30d": m_30, "Status": status, "Ação": acao, "Div. 12m": divs})
    except: continue

df_radar = pd.DataFrame(dados_finais)

# --- RADAR ---
st.subheader("🛰️ Radar de Ativos")
df_display = df_radar.copy()
for col in ["Preço", "Média 30d", "Div. 12m"]:
    df_display[col] = df_display[col].apply(lambda x: f"R$ {x:.2f}")
st.table(df_display)

# --- TERMÔMETRO ---
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
    st.write(f"Índice: **{score:.0f}%**")

# --- GESTOR XP COM CAMPO DE PATRIMÔNIO RESTAURADO ---
st.markdown("---")
c_calc, c_res = st.columns([1, 1.2])
with c_calc:
    st.subheader("🧮 Gestor XP")
    with st.expander("Sua Ordem", expanded=True):
        tipo_ordem = st.selectbox("Estratégia da Ordem:", ("A Mercado", "Limitada", "Stop Loss", "Stop Móvel"))
        v_envio = st.number_input("Valor enviado (R$):", value=50.0)
        p_pago = st.number_input("Preço da cota (R$):", value=31.0)
        c_at = st.number_input("Cotas que já possui:", value=0)
        pm_at = st.number_input("Preço Médio atual:", value=0.0)
        
        n_cotas = int(v_envio // p_pago)
        troco = v_envio % p_pago
        
        # Lógica de Patrimônio e Lucro (Usando PETR4 como base de simulação)
        try:
            p_mercado = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0]
        except:
            p_mercado = p_pago
            
        patrimonio_simulado = (n_cotas * p_mercado) + troco
        lucro_simulado = patrimonio_simulado - v_envio
        
        n_pm = ((c_at * pm_at) + (n_cotas * p_pago)) / (c_at + n_cotas) if c_at > 0 else p_pago

with c_res:
    st.subheader("📊 Resultado")
    st.caption(f"Execução: **{tipo_ordem}**")
    
    # Linha 1: Cotas e Troco
    r1, r2 = st.columns(2)
    r1.metric("Cotas Novas", f"{n_cotas} un")
    r2.metric("Troco", f"R$ {troco:.2f}")
    
    # Linha 2: Patrimônio Total (RESTABELECIDO)
    st.metric("Patrimônio Total (Nesta Ordem)", f"R$ {patrimonio_simulado:.2f}", f"R$ {lucro_simulado:.2f}")
    
    # Linha 3: Novo PM
    if c_at > 0:
        st.metric("Seu Novo Preço Médio", f"R$ {n_pm:.2f}")

# --- PROJEÇÃO DE RENDA ---
st.markdown("---")
st.subheader("💰 Projeção de Renda")
a_div = st.selectbox("Simular ativo:", tickers)
q_sim = st.number_input("Qtd. de cotas:", value=100)
dv = df_radar[df_radar['Ativo'] == a_div]['Div. 12m'].values[0] if not df_radar[df_radar['Ativo'] == a_div].empty else 0
st.metric(f"Renda Mensal Est. ({a_div})", f"R$ {(dv * q_sim / 12):.2f}")

# --- GRÁFICO ---
st.markdown("---")
st.subheader("📈 Tendência 30d")
sel_graf = st.selectbox("Ver histórico de:", tickers)
st.line_chart(yf.Ticker(sel_graf).history(period="30d")['Close'])
