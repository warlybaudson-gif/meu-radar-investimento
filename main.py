import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade (Ontem)
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# Estilização para o visual Preto e Cinza
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    div[data-testid="stMetricValue"] { color: #ffffff; }
    thead tr th { background-color: #2d2d2d !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller: Inteligência e Radar")

# 2. Painel Lateral (Ontem)
st.sidebar.markdown("### ⚙️ Painel de Controle")
capital_disponivel = st.sidebar.number_input("Seu Capital Disponível (R$)", value=1000.0)

# 3. A Tabela com as colunas: Preço, Média, Caro/Barato, Comprar/Vender e Dividendos
st.subheader("🛰️ Radar de Ativos Estratégicos")
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
    ativo = yf.Ticker(t)
    hist_1d = ativo.history(period="1d")
    
    if not hist_1d.empty:
        preco_atual = hist_1d['Close'].iloc[-1]
        
        # Média de 30 dias
        hist_30d = ativo.history(period="30d")
        media_30 = hist_30d['Close'].mean()
        
        # Lógica: Caro ou Barato
        status = "🔥 BARATO" if preco_atual < media_30 else "💎 CARO"
        
        # Lógica: Comprar ou Vender
        decisao = "✅ COMPRAR" if preco_atual < media_30 else "⚠️ AGUARDAR / VENDER"
        
        # Busca Dividendos (Soma dos últimos 12 meses)
        # Para BTC-USD o dividendo será 0.00
        dividendos = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
        
        dados_finais.append({
            "Ativo": t, 
            "Preço": f"R$ {preco_atual:.2f}", 
            "Média (30d)": f"R$ {media_30:.2f}",
            "Status": status,
            "Ação": decisao,
            "Dividendos (12m)": f"R$ {dividendos:.2f}"
        })

df = pd.DataFrame(dados_finais)
st.table(df)

# 4. Integração da Calculadora de Hoje (Sua Ordem XP)
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧮 Gestor de Patrimônio")
    with st.expander("Minha Ordem da XP", expanded=True):
        valor_enviado = st.number_input("Valor enviado para a XP (R$):", value=50.0)
        preco_executado = st.number_input("Preço pago por cota (R$):", value=31.0)
        
        qtd_cotas = int(valor_enviado // preco_executado)
        sobra = valor_enviado % preco_executado
        
        # Cálculo baseado no preço real da Petrobras agora
        preco_petr = yf.Ticker("PETR4.SA").history(period="1d")['Close'].iloc[-1]
        patrimonio_hj = (qtd_cotas * preco_petr) + sobra
        lucro_abs = patrimonio_hj - valor_enviado

with col2:
    st.subheader("📊 Resultado em Tempo Real")
    st.metric("Cotas Adquiridas (PETR4)", f"{qtd_cotas} un")
    st.metric("Patrimônio Atual", f"R$ {patrimonio_hj:.2f}", f"R$ {lucro_abs:.2f}")

# 5. Gráfico de Tendência
st.markdown("---")
st.subheader("📈 Histórico de Preços (30 dias)")
escolha = st.selectbox("Selecione o ativo para o gráfico:", tickers)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)

st.sidebar.info(f"Monitorando {len(tickers)} ativos com inteligência Rockefeller.")
