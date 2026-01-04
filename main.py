import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Harmonização Total Black e Correção de Contrastes
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .streamlit-expanderHeader { background-color: #000000 !important; border-bottom: 1px solid #333 !important; }
    .streamlit-expanderContent { background-color: #000000 !important; border: 1px solid #333 !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 26px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    table { width: 100% !important; font-size: 13px !important; }
    th, td { white-space: nowrap !important; padding: 10px !important; text-align: left !important; }
    .stTable { overflow-x: auto !important; display: block !important; }
    thead tr th { background-color: #1a1a1a !important; color: #58a6ff !important; }
    tbody td { background-color: #000000 !important; color: #ffffff !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Processamento de Dados do Radar (Criado antes para poder exportar)
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
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
            "Ativo": t, "Preço": f"R$ {preco_atual:.2f}", "Média 30d": f"R$ {media_30:.2f}",
            "Status": status, "Ação": acao, "Div. 12m": f"R$ {divs:.2f}"
        })

df_radar = pd.DataFrame(dados_finais)

# 4. Painel Lateral com Botão de Exportação CSV
st.sidebar.markdown("### ⚙️ Painel de Controle")
capital_base = st.sidebar.number_input("Capital total (R$)", value=1000.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Exportar Dados")
# Função para converter o DataFrame em CSV
csv = df_radar.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Baixar Tabela (CSV)",
    data=csv,
    file_name='radar_rockefeller.csv',
    mime='text/csv',
)
st.sidebar.info("O arquivo CSV pode ser aberto no Excel, Power BI ou Python.")

# 5. Exibição da Tabela de Radar
st.subheader("🛰️ Radar de Ativos")
st.table(df_radar)

# 6. Gestor de Patrimônio (XP)
st.markdown("---")
col_calc, col_res = st.columns([1, 1.2])

with col_calc:
    st.subheader("🧮 Gestor XP")
    with st.expander("Sua Ordem", expanded=True):
        tipo_ordem = st.selectbox("Tipo de Ordem:", ("A Mercado", "Limitada", "Stop Loss", "Stop Móvel"))
        valor_xp = st.number_input("Valor enviado para a XP (R$):", value=50.0)
        pago_xp = st.number_input("Preço pago por cota (R$):", value=31.0)
        
        cotas = int(valor_xp // pago_xp)
        troco_xp = valor_xp % pago_xp
        
        preco_petr = yf.Ticker("PETR4.SA").history(period="1d")['Close'].iloc[-1]
        patrimonio_total = (cotas * preco_petr) + troco_xp
        lucro_abs = patrimonio_total - valor_xp

with col_res:
    st.subheader("📊 Resultado")
    m1, m2 = st.columns(2)
    m1.metric("Cotas Compradas", f"{cotas} un")
    m2.metric("Troco em Conta", f"R$ {troco_xp:.2f}")
    st.metric("Patrimônio Total", f"R$ {patrimonio_total:.2f}", f"R$ {lucro_abs:.2f}")

# 7. Gráfico
st.markdown("---")
st.subheader("📈 Tendência 30d")
escolha = st.selectbox("Escolha o Ativo:", tickers)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)
