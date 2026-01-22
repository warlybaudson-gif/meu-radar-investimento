import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ===============================
# CONFIGURAÇÃO GERAL
# ===============================
st.set_page_config(
    page_title="IA Rockefeller",
    page_icon="💰",
    layout="wide"
)

st.title("💰 IA Rockefeller — Painel Inteligente de Investimentos")

# ===============================
# DICIONÁRIO ÚNICO DE ATIVOS
# ===============================
TICKERS_UNIFICADOS = {
    # Ações BR
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "BBAS3": "BBAS3.SA",
    "ITUB4": "ITUB4.SA",
    "LREN3": "LREN3.SA",
    "GRND3": "GRND3.SA",
    "MGLU3": "MGLU3.SA",

    # Elétricas / Saneamento
    "TAEE11": "TAEE11.SA",
    "EGIE3": "EGIE3.SA",
    "ALUP11": "ALUP11.SA",
    "SAPR11": "SAPR11.SA",

    # FIIs
    "MXRF11": "MXRF11.SA",
    "HGLG11": "HGLG11.SA",
    "XPML11": "XPML11.SA",
    "VISC11": "VISC11.SA",
    "VIVA11": "VIVA11.SA",
    "GARE11": "GARE11.SA",

    # ETFs / Exterior
    "IVVB11": "IVVB11.SA",
    "AAPL": "AAPL",
    "NVDA": "NVDA",

    # Cripto / Commodities / Câmbio
    "BTC": "BTC-USD",
    "OURO": "GC=F",
    "USD": "USDBRL=X"
}

# ===============================
# FUNÇÃO DE DECISÃO (REGRA MÃE)
# ===============================
def decidir_acao(preco, justo, media, tipo):
    if preco <= 0:
        return "⚠️ ESPERAR"

    if tipo == "cripto":
        return "🟢 ACUMULAR" if preco < media else "⚠️ ESPERAR"

    if tipo == "fii":
        if preco < justo:
            return "✅ COMPRAR"
        elif preco > justo * 1.25:
            return "🟠 REDUZIR"
        else:
            return "⚠️ ESPERAR"

    # ações
    if preco < justo and preco < media:
        return "✅ COMPRAR"
    elif preco > justo * 1.20:
        return "🛑 VENDER"
    else:
        return "⚠️ ESPERAR"

# ===============================
# MOTOR CENTRAL — ABA 1
# ===============================
@st.cache_data(ttl=3600)
def montar_df_base():
    dados = []

    cambio = yf.Ticker("USDBRL=X").history(period="1d")["Close"].iloc[-1]

    for nome, ticker in TICKERS_UNIFICADOS.items():
        try:
            ativo = yf.Ticker(ticker)
            hist = ativo.history(period="30d")
            info = ativo.info

            if hist.empty:
                continue

            preco = hist["Close"].iloc[-1]
            media = hist["Close"].mean()

            lpa = info.get("trailingEps", 0)
            vpa = info.get("bookValue", 0)
            justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else media

            # Conversões
            if ticker in ["AAPL", "NVDA", "BTC-USD"]:
                preco *= cambio
                media *= cambio
                justo *= cambio

            if ticker == "GC=F":  # ouro
                preco = (preco / 31.1035) * cambio
                media = (media / 31.1035) * cambio
                justo = media

            tipo = (
                "cripto" if nome == "BTC"
                else "fii" if nome.endswith("11")
                else "acao"
            )

            decisao = decidir_acao(preco, justo, media, tipo)
            margem = ((justo - preco) / justo) * 100 if justo > 0 else 0
            prioridade = margem + (10 if preco < media else 0)

            dados.append({
                "Ativo": nome,
                "Preço (R$)": round(preco, 2),
                "Valor Justo (R$)": round(justo, 2),
                "Margem (%)": round(margem, 1),
                "Prioridade": round(prioridade, 1),
                "Decisão": decisao
            })

        except:
            pass

    return pd.DataFrame(dados)

# ===============================
# CRIAÇÃO DAS ABAS
# ===============================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Aba 1 — Painel Geral",
    "🛰️ Aba 2 — Carteira Modelo",
    "🎯 Aba 3 — Estratégia de Aporte",
    "📖 Aba 4 — Manual"
])

df_base = montar_df_base()

# ===============================
# ABA 1 — PAINEL GERAL
# ===============================
with tab1:
    st.subheader("📊 Painel Geral de Decisão")

    def cor_decisao(valor):
        if "COMPRAR" in valor or "ACUMULAR" in valor:
            return "background-color:#14532d;color:#dcfce7"
        if "VENDER" in valor or "REDUZIR" in valor:
            return "background-color:#7f1d1d;color:#fee2e2"
        return "background-color:#78350f;color:#fef3c7"

    st.dataframe(
        df_base
        .sort_values("Prioridade", ascending=False)
        .style.applymap(cor_decisao, subset=["Decisão"]),
        use_container_width=True,
        hide_index=True
    )

# ===============================
# ABA 2 — CARTEIRA MODELO
# ===============================
with tab2:
    st.subheader("🛰️ Carteira Modelo")

    CARTEIRA_MODELO = [
        "TAEE11","EGIE3","ALUP11","SAPR11",
        "BBAS3","ITUB4",
        "MXRF11","HGLG11","XPML11",
        "VISC11","VIVA11","GARE11",
        "IVVB11"
    ]

    df_modelo = df_base[df_base["Ativo"].isin(CARTEIRA_MODELO)]

    st.dataframe(
        df_modelo.sort_values("Prioridade", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ===============================
# ABA 3 — ESTRATÉGIA DE APORTE
# ===============================
with tab3:
    st.subheader("🎯 Estratégia Inteligente de Aporte")

    aporte = st.number_input(
        "💰 Quanto deseja investir agora? (R$)",
        min_value=0.0,
        step=100.0
    )

    df_compra = df_base[
        df_base["Decisão"].str.contains("COMPRAR|ACUMULAR")
    ].sort_values("Prioridade", ascending=False)

    if aporte > 0 and not df_compra.empty:
        aporte_por_ativo = aporte / len(df_compra)
        plano = []

        for _, r in df_compra.iterrows():
            cotas = int(aporte_por_ativo // r["Preço (R$)"])
            plano.append({
                "Ativo": r["Ativo"],
                "Preço (R$)": r["Preço (R$)"],
                "Cotas": cotas,
                "Capital Usado (R$)": round(cotas * r["Preço (R$)"], 2)
            })

        st.dataframe(
            pd.DataFrame(plano),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum ativo em ponto de compra ou aporte zerado.")

# ===============================
# ABA 4 — MANUAL
# ===============================
with tab4:
    st.markdown("""
### 📖 Manual Rápido

**Aba 1**  
- Fonte única da verdade  
- Verde = oportunidade  
- Amarelo = esperar  
- Vermelho = vender/reduzir  

**Aba 2**  
- Apenas filtra a carteira modelo  

**Aba 3**  
- Executa aportes automaticamente  
- Respeita prioridade e decisão  

Sistema pronto para uso contínuo.
""")
