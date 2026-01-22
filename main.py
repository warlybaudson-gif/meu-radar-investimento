import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(
    page_title="IA Rockefeller",
    page_icon="💰",
    layout="wide"
)

st.title("💰 IA Rockefeller")

# =========================
# LISTA ÚNICA DE ATIVOS
# =========================
ATIVOS = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "BBAS3": "BBAS3.SA",
    "ITUB4": "ITUB4.SA",
    "BBSE3": "BBSE3.SA",
    "TAEE11": "TAEE11.SA",
    "EGIE3": "EGIE3.SA",
    "ALUP11": "ALUP11.SA",
    "SAPR11": "SAPR11.SA",
    "MXRF11": "MXRF11.SA",
    "HGLG11": "HGLG11.SA",
    "XPML11": "XPML11.SA",
    "VISC11": "VISC11.SA",
    "VIVA11": "VIVA11.SA",
    "GARE11": "GARE11.SA",
    "IVVB11": "IVVB11.SA",
    "AAPL": "AAPL",
    "NVDA": "NVDA",
    "BTC": "BTC-USD",
    "OURO": "GC=F",
    "USD": "USDBRL=X"
}

# =========================
# FUNÇÃO CENTRAL (ESTRUTURA PRESERVADA)
# =========================
@st.cache_data(ttl=3600)
def calcular_dados(lista):
    res = []

    # câmbio carregado uma única vez
    cambio = yf.Ticker("USDBRL=X").history(period="1d")["Close"].iloc[-1]

    for nome, ticker in lista.items():
        try:
            ativo = yf.Ticker(ticker)
            hist = ativo.history(period="60d")
            info = ativo.info

            if hist.empty:
                continue

            preco = hist["Close"].iloc[-1]
            media = hist["Close"].mean()

            # Conversões
            if ticker in ["AAPL", "NVDA", "BTC-USD"]:
                preco *= cambio
                media *= cambio

            if ticker == "GC=F":  # ouro
                preco = (preco / 31.1035) * cambio
                media = (media / 31.1035) * cambio

            # Preço justo (Graham com fallback seguro)
            lpa = info.get("trailingEps", 0)
            vpa = info.get("bookValue", 0)

            if lpa > 0 and vpa > 0:
                justo = np.sqrt(22.5 * lpa * vpa)
                if ticker in ["AAPL", "NVDA"]:
                    justo *= cambio
            else:
                justo = media

            # Margem de segurança
            margem = ((justo - preco) / justo) * 100 if justo > 0 else 0

            # Classificação de tipo
            if nome == "BTC":
                tipo = "cripto"
            elif nome.endswith("11"):
                tipo = "fii"
            else:
                tipo = "acao"

            # Decisão FINAL
            if tipo == "cripto":
                acao = "🟢 ACUMULAR" if preco < media else "⚠️ ESPERAR"
            elif tipo == "fii":
                if preco < justo:
                    acao = "✅ COMPRAR"
                elif preco > justo * 1.25:
                    acao = "🟠 REDUZIR"
                else:
                    acao = "⚠️ ESPERAR"
            else:
                if preco < justo and preco < media:
                    acao = "✅ COMPRAR"
                elif preco > justo * 1.20:
                    acao = "🛑 VENDER"
                else:
                    acao = "⚠️ ESPERAR"

            prioridade = margem + (10 if preco < media else 0)

            res.append({
                "Ativo": nome,
                "Preço (R$)": round(preco, 2),
                "Valor Justo (R$)": round(justo, 2),
                "Margem (%)": round(margem, 1),
                "Prioridade": round(prioridade, 1),
                "Decisão": acao
            })

        except:
            continue

    return pd.DataFrame(res)

# =========================
# CRIAÇÃO DAS ABAS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Aba 1 — Geral",
    "🛰️ Aba 2 — Carteira",
    "🎯 Aba 3 — Aporte",
    "📖 Aba 4 — Manual"
])

df = calcular_dados(ATIVOS)

# =========================
# ABA 1 — FONTE DA VERDADE
# =========================
with tab1:
    st.subheader("📊 Painel Geral")

    def cor_decisao(v):
        if "COMPRAR" in v or "ACUMULAR" in v:
            return "background-color:#14532d;color:#dcfce7"
        if "VENDER" in v or "REDUZIR" in v:
            return "background-color:#7f1d1d;color:#fee2e2"
        return "background-color:#78350f;color:#fef3c7"

    st.dataframe(
        df.sort_values("Prioridade", ascending=False)
          .style.applymap(cor_decisao, subset=["Decisão"]),
        use_container_width=True,
        hide_index=True
    )

# =========================
# ABA 2 — CARTEIRA
# =========================
with tab2:
    st.subheader("🛰️ Carteira Modelo")

    carteira = [
        "TAEE11","EGIE3","ALUP11","SAPR11",
        "BBAS3","ITUB4",
        "MXRF11","HGLG11","XPML11",
        "VISC11","VIVA11","GARE11",
        "IVVB11"
    ]

    st.dataframe(
        df[df["Ativo"].isin(carteira)]
          .sort_values("Prioridade", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# =========================
# ABA 3 — APORTE
# =========================
with tab3:
    st.subheader("🎯 Estratégia de Aporte")

    aporte = st.number_input("Valor do aporte (R$)", min_value=0.0, step=100.0)

    df_compra = df[df["Decisão"].str.contains("COMPRAR|ACUMULAR")]

    if aporte > 0 and not df_compra.empty:
        valor_por_ativo = aporte / len(df_compra)
        plano = []

        for _, r in df_compra.iterrows():
            cotas = int(valor_por_ativo // r["Preço (R$)"])
            plano.append({
