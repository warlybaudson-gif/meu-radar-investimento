import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Harmonização Total Black e Correção de Contrastes
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* CORREÇÃO: Fundo da caixa 'Sua Ordem' (Expander) para Preto */
    .streamlit-expanderHeader { background-color: #000000 !important; border-bottom: 1px solid #333 !important; }
    .streamlit-expanderContent { background-color: #000000 !important; border: 1px solid #333 !important; }
    
    /* CORREÇÃO: Deixar os números do Resultado bem claros e visíveis */
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }

    /* Labels dos campos de entrada em Branco */
    label { color: #ffffff !important; font-weight: bold !important; }
    
    /* Tabela Responsiva e Dark */
    table { width: 100% !important; font-size: 13px !important; }
    th, td { white-space: nowrap !important; padding: 10px !important; text-align: left !important; }
    .stTable { overflow-x: auto !important; display: block !important; }
    thead tr th { background-color: #1a1a1a !important; color: #58a6ff !important; }
    tbody td { background-color: #000000 !important; color: #ffffff !important; }
    
    /* Estilo dos blocos de métricas */
    div[data-testid="stMetric"] { 
        background-color: #111111; 
        border: 1px solid #333333; 
        padding: 15px; 
        border-radius: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Painel Lateral
st.sidebar.markdown("### ⚙️ Configurações")
capital_base = st.sidebar.number_input("Capital total (R$)", value=1000.0)

# 4. Tabela de Radar
st.subheader("🛰️ Radar de Ativos")
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

df = pd.DataFrame(dados_finais)
st.table(df)

# 5. Gestor de Patrimônio (XP) Corrigido
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧮 Gestor XP")
    # A caixa abaixo agora terá o fundo totalmente preto
    with st.expander("Sua Ordem", expanded=True):
        tipo_ordem = st.selectbox("Tipo de Ordem:", ("A Mercado", "Limitada", "Stop Loss", "Stop Móvel"))
        valor_xp = st.number_input("Valor enviado para a XP (R$):", value=50.0)
        pago_xp = st.number_input("Preço pago por cota (R$):", value=31.0)
        
        cotas = int(valor_xp // pago_xp)
        sobra = valor_xp % pago_xp
        
        preco_petr = yf.Ticker("PETR4.SA").history(period="1d")['Close'].iloc[-1]
        patrimonio = (cotas * preco_petr) + sobra
        resultado = patrimonio - valor_xp

with col2:
    st.subheader("📊 Resultado")
    st.write(f"Ordem Selecionada: **{tipo_ordem}**")
    # Os valores abaixo agora estarão em branco brilhante e fáceis de ler
    st.metric("Cotas Adquiridas", f"{cotas} un")
    st.metric("Patrimônio Total", f"R$ {patrimonio:.2f}", f"R$ {resultado:.2f}")

# 6. Gráfico Harmonizado
st.markdown("---")
st.subheader("📈 Tendência 30d")
escolha = st.selectbox("Escolha o Ativo:", tickers)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)
