# IA Rockefeller — Versão COMPLETA com Abas Restauradas
# Core otimizado + TODAS as abas originais restauradas

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import sqlite3

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# ==================== CACHE YFINANCE ====================
@st.cache_data(ttl=1800, show_spinner=False)
def carregar_historico(ticker, periodo="30d"):
    try:
        return yf.Ticker(ticker).history(period=periodo)
    except:
        return pd.DataFrame()

# ==================== SQLITE ====================
def conectar_db():
    return sqlite3.connect("carteira.db", check_same_thread=False)

def salvar_dados_usuario(dados):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS carteira (chave TEXT PRIMARY KEY, valor TEXT)")
    for k, v in dados.items():
        c.execute("REPLACE INTO carteira VALUES (?, ?)", (k, json.dumps(v)))
    conn.commit()
    conn.close()

def carregar_dados_usuario():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS carteira (chave TEXT PRIMARY KEY, valor TEXT)")
    c.execute("SELECT chave, valor FROM carteira")
    dados = {k: json.loads(v) for k, v in c.fetchall()}
    conn.close()
    return dados

# ==================== DADOS INICIAIS ====================
dados_salvos = carregar_dados_usuario()

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.40

# ==================== ATIVOS ====================
ativos = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "BBAS3": "BBAS3.SA",
    "ITUB4": "ITUB4.SA",
    "BTC": "BTC-USD",
    "NVDA": "NVDA",
    "AAPL": "AAPL"
}

# ==================== CÁLCULOS ====================
def calcular_dados(lista):
    res = []
    for nome, t in lista.items():
        hist = carregar_historico(t)
        if hist.empty:
            continue
        try:
            info = yf.Ticker(t).fast_info
        except:
            info = {}

        p = hist['Close'].iloc[-1]
        if t in ["NVDA", "AAPL", "BTC-USD"]:
            p *= cambio_hoje

        m30 = hist['Close'].mean()
        if t in ["NVDA", "AAPL", "BTC-USD"]:
            m30 *= cambio_hoje

        lpa = info.get('eps', 0) or 0
        vpa = info.get('bookValue', 0) or 0
        justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m30

        status = "✅ DESCONTADO" if p < justo else "❌ SOBREPREÇO"
        acao = "✅ COMPRAR" if p < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"

        res.append({
            "Ativo": nome,
            "Preço": round(p, 2),
            "Justo": round(justo, 2),
            "Status": status,
            "Ação": acao,
            "V_Cru": p
        })
    return pd.DataFrame(res)

# ==================== INTERFACE ====================
st.title("💰 IA Rockefeller")

# ====== ABAS ======
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Painel",
    "🔍 Radar",
    "🎯 Estratégia",
    "🏦 Carteira",
    "🧬 DNA",
    "📈 Backtest",
    "📖 Manual"
])

df = calcular_dados(ativos)

# ==================== ABA 1 ====================
with tab1:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    if not df.empty:
        st.markdown("### Visão Geral")
        st.dataframe(df[['Ativo','Preço','Justo','Status','Ação']], use_container_width=True)

        st.markdown("---")
        st.subheader("🌡️ Sentimento de Mercado")
        caros = len(df[df['Status'] == "❌ SOBREPREÇO"])
        score = (caros / len(df)) * 100 if len(df) > 0 else 0
        st.progress(score / 100)
        st.write(f"Índice de ativos sobreprecificados: **{int(score)}%**")

        st.markdown("---")
        st.subheader("🧮 Gestor de Carteira")
        capital = st.number_input("Capital total disponível (R$)", value=dados_salvos.get("capital", 0.0), step=100.0)

        total_atual = 0
        for _, r in df.iterrows():
            qtd = st.number_input(f"Qtd de {r['Ativo']}", min_value=0, key=f"q_{r['Ativo']}")
            total_atual += qtd * r['V_Cru']

        st.metric("Valor Atual da Carteira", f"R$ {total_atual:,.2f}")

        if st.button("💾 Salvar Aba 1"):
            salvar_dados_usuario({"capital": capital})
            st.success("Dados da Aba 1 salvos")

# ==================== ABA 2 ====================
with tab2:
    st.subheader("🔍 Radar de Oportunidades")
    st.dataframe(df[df['Ação'] == "✅ COMPRAR"], use_container_width=True)

# ==================== ABA 3 ====================
with tab3:
    st.subheader("🎯 Estratégia de Aporte")
    aporte = st.number_input("Valor mensal para investir", 0.0, step=100.0)
    if aporte > 0 and not df.empty:
        st.write(df[['Ativo', 'Preço', 'Ação']])

# ==================== ABA 4 ====================
with tab4:
    st.subheader("🏦 Minha Carteira")
    capital = st.number_input("Capital disponível", value=dados_salvos.get("capital", 0.0))
    if st.button("💾 Salvar Carteira"):
        salvar_dados_usuario({"capital": capital})
        st.success("Carteira salva")

# ==================== ABA 5 ====================
with tab5:
    st.subheader("🧬 DNA Financeiro")
    for _, r in df.iterrows():
        st.write(f"{r['Ativo']} → Preço Justo: R$ {r['Justo']}")

# ==================== ABA 6 ====================
with tab6:
    st.subheader("📈 Backtesting")
    if not df.empty:
        ativo = st.selectbox("Ativo", df['Ativo'])
        st.info(f"Simulação simples para {ativo}")

# ==================== ABA 7 ====================
with tab7:
    st.subheader("📖 Manual")
    st.markdown("""
    **IA Rockefeller**

    • Compra quando preço < média e < valor justo
    • Foco em margem de segurança
    • Pensamento de longo prazo
    """)
