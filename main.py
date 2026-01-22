import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

# ===================== PERSISTÊNCIA =====================
def salvar_dados_usuario(dados):
    with open("carteira_salva.json", "w") as f:
        json.dump(dados, f)

def carregar_dados_usuario():
    if os.path.exists("carteira_salva.json"):
        with open("carteira_salva.json", "r") as f:
            return json.load(f)
    return {}

dados_salvos = carregar_dados_usuario()

# ===================== CONFIG STREAMLIT =====================
st.set_page_config(
    page_title="IA Rockefeller",
    page_icon="💰",
    layout="wide"
)

# ===================== ESTILO =====================
st.markdown("""
<style>
.stApp { background-color: #000; color: #fff; }
.stMarkdown, td, th, p, label { color: #fff !important; white-space: nowrap !important; }
.rockefeller-table { width:100%; border-collapse: collapse; font-family: Courier New; font-size: 0.85rem;}
.rockefeller-table th { background:#1a1a1a; color:#58a6ff; padding:8px; border-bottom:2px solid #333;}
.rockefeller-table td { padding:8px; border-bottom:1px solid #222; text-align:center;}
.mobile-table-container { overflow-x:auto; }
</style>
""", unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# ===================== TICKERS =====================
modelo_huli_tickers = {
    "TAESA": "TAEE11.SA", "ENGIE": "EGIE3.SA", "ALUPAR": "ALUP11.SA",
    "SANEPAR": "SAPR11.SA", "SABESP": "SBSP3.SA",
    "BANCO DO BRASIL": "BBAS3.SA", "ITAÚ": "ITUB4.SA",
    "BB SEGURIDADE": "BBSE3.SA", "IVVB11": "IVVB11.SA",
    "RENNER": "LREN3.SA", "GRENDENE": "GRND3.SA",
    "MATEUS": "GMAT3.SA", "MAGALU": "MGLU3.SA"
}

ativos_estrategicos = {
    "PETROBRAS": "PETR4.SA", "VALE": "VALE3.SA",
    "BITCOIN": "BTC-USD", "NVIDIA": "NVDA",
    "OURO": "GC=F", "DÓLAR": "USDBRL=X"
}

tickers_map = {**ativos_estrategicos, **modelo_huli_tickers}

# ===================== FUNÇÃO DE DADOS =====================
def calcular_dados(lista):
    res = []
    fim = datetime.today()
    inicio = fim - timedelta(days=90)

    for nome, ticker in lista.items():
        try:
            ativo = yf.Ticker(ticker)
            hist = ativo.history(start=inicio, end=fim)

            if hist.empty:
                continue

            close = hist["Close"]
            p_atual = float(close.iloc[-1])
            m_30 = float(close.tail(30).mean())
            variacoes = close.pct_change() * 100

            info = ativo.info
            lpa = info.get("trailingEps", 0) or 0
            vpa = info.get("bookValue", 0) or 0
            dy = info.get("dividendYield", 0) or 0

            if lpa > 0 and vpa > 0 and ".SA" in ticker:
                p_justo = np.sqrt(22.5 * lpa * vpa)
            else:
                p_justo = m_30

            status = "DESCONTADO" if p_atual < p_justo else "SOBREPRECO"
            acao = (
                "COMPRAR" if p_atual < m_30 and status == "DESCONTADO"
                else "VENDER" if p_atual > p_justo * 1.2
                else "ESPERAR"
            )

            res.append({
                "Ativo": nome,
                "Preço": p_atual,
                "Justo": p_justo,
                "DY": f"{dy*100:.1f}%".replace(".", ","),
                "Status": status,
                "Ação": acao,
                "Var_Min": variacoes.min(),
                "Var_Max": variacoes.max(),
                "Dias_A": (variacoes > 0).sum(),
                "Dias_B": (variacoes < 0).sum(),
                "LPA": lpa,
                "VPA": vpa
            })

        except Exception as e:
            st.warning(f"Erro em {nome}: {e}")

    return pd.DataFrame(res)

@st.cache_data(ttl=3600)
def carregar_dados(lista):
    return calcular_dados(lista)

df_radar = carregar_dados(tickers_map)
df_modelo = carregar_dados(modelo_huli_tickers)

if df_radar.empty:
    st.error("Erro ao carregar dados do mercado.")
    st.stop()

# ===================== ABAS =====================
tab1, tab2, tab3 = st.tabs([
    "📊 Painel",
    "🎯 Estratégia Huli",
    "📖 Manual"
])

# ===================== ABA 1 =====================
with tab1:
    st.subheader("🛰️ Radar de Ativos")

    html = f"""
    <div class="mobile-table-container">
    <table class="rockefeller-table">
    <tr><th>Ativo</th><th>Preço</th><th>Justo</th><th>DY</th><th>Status</th><th>Ação</th></tr>
    {''.join([
        f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['DY']}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>"
        for _, r in df_radar.iterrows()
    ])}
    </table></div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ===================== ABA 2 =====================
with tab2:
    st.subheader("🎯 Oportunidades de Compra")
    compras = df_modelo[df_modelo["Ação"] == "COMPRAR"]

    if compras.empty:
        st.info("Nenhum ativo em ponto ideal de compra.")
    else:
        st.dataframe(compras, use_container_width=True)

# ===================== ABA 3 =====================
with tab3:
    st.markdown("""
    **Preço Justo (Graham):**  
    √(22,5 × LPA × VPA)

    **COMPRAR:** abaixo do preço justo e da média de 30 dias  
    **VENDER:** muito acima do preço justo  
    **ESPERAR:** neutro
    """)
