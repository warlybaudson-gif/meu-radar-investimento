# IA Rockefeller - Versão Corrigida e Otimizada
# Inclui: Cache yfinance, Persistência SQLite, Proteções de erro

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import sqlite3
import os

# ==================== CONFIG STREAMLIT ====================
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# ==================== CACHE YFINANCE ====================
@st.cache_data(ttl=1800, show_spinner=False)
def carregar_historico(ticker, periodo="30d"):
    try:
        return yf.Ticker(ticker).history(period=periodo)
    except:
        return pd.DataFrame()

# ==================== BANCO SQLITE ====================
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

# ==================== FUNÇÃO PRINCIPAL ====================
def calcular_dados(lista):
    res = []
    for nome_ex, t in lista.items():
        try:
            hist = carregar_historico(t)
            if hist.empty:
                continue

            ativo = yf.Ticker(t)
            try:
                info = ativo.fast_info
            except:
                info = {}

            p_atual = hist['Close'].iloc[-1]
            dy = info.get('dividendYield', 0) or 0
            dy_fmt = f"{dy*100:.1f}%".replace('.', ',')

            if t in ["NVDA", "AAPL", "BTC-USD"]:
                p_atual *= cambio_hoje

            m30 = hist['Close'].mean()
            if t in ["NVDA", "AAPL", "BTC-USD"]:
                m30 *= cambio_hoje

            lpa = info.get('eps', 0) or 0
            vpa = info.get('bookValue', 0) or 0
            p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m30

            status = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
            variacoes = hist['Close'].pct_change() * 100
            acao = "✅ COMPRAR" if p_atual < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"

            res.append({
                "Ativo": nome_ex,
                "Preço": round(p_atual, 2),
                "Justo": round(p_justo, 2),
                "DY": dy_fmt,
                "Status": status,
                "Ação": acao,
                "V_Cru": p_atual,
                "Var_Min": variacoes.min(),
                "Var_Max": variacoes.max()
            })
        except:
            continue
    return pd.DataFrame(res)

# ==================== INTERFACE ====================
st.title("💰 IA Rockefeller")

st.info("Versão corrigida, rápida e estável (cache + SQLite)")

# Exemplo simples de uso
ativos_demo = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "BITCOIN": "BTC-USD",
    "NVIDIA": "NVDA"
}

df = calcular_dados(ativos_demo)

st.dataframe(df, use_container_width=True)

st.markdown("---")
st.subheader("💾 Persistência de Teste")
capital = st.number_input("Capital XP", value=dados_salvos.get("capital", 0.0))

if st.button("Salvar"):
    salvar_dados_usuario({"capital": capital})
    st.success("Salvo com sucesso")
