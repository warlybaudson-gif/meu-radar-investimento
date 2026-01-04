import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações Visuais Estilo Terminal
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# Estilização para Fundo Escuro
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    .stMetric { background-color: #2d2d2d; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller: Intelligence & Radar")
st.markdown("---")

# 2. Radar de Mercado em Tempo Real
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛰️ Radar de Ativos")
    tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
    dados_mercado = []

    for t in tickers:
        ativo = yf.Ticker(t)
        # Busca preço atual
        info = ativo.history(period="1d")
        if not info.empty:
            preco_atual = info['Close'].iloc[-1]
            
            # Busca média de 30 dias para o Status
            hist = ativo.history(period="30d")
            media = hist['Close'].mean()
            status = "🔥 BARATO" if preco_atual < media else "💎 FORTE"
            
            dados_mercado.append({"Ativo": t, "Preço": f"R$ {preco_atual:.2f}", "Status": status})

    df = pd.DataFrame(dados_mercado)
    st.table(df)

# 3. Calculadora de Lucro Real (Sua posição na XP)
with col2:
    st.subheader("🧮 Gestor de Patrimônio")
    with st.expander("Configurar Minha Ordem da XP", expanded=True):
        capital_investido = st.number_input("Quanto enviei para a XP (R$):", value=50.00)
        preco_pago = st.number_input("Preço que paguei por cota (R$):", value=31.00)
        
        # Cálculo de Cotas e Troco
        quantidade_cotas = int(capital_investido // preco_pago)
        sobra_caixa = capital_investido % preco_pago
        
        # Valor Atual (Baseado na PETR4)
        preco_agora = yf.Ticker("PETR4.SA").history(period="1d")['Close'].iloc[-1]
        valor_patrimonio_atual = (quantidade_cotas * preco_agora) + sobra_caixa
        lucro_prejuizo = valor_patrimonio_atual - capital_investido

    # Exibição de Resultados
    c1, c2 = st.columns(2)
    c1.metric("Cotas Adquiridas", f"{quantidade_cotas} un")
    
    cor_lucro = "normal" if lucro_prejuizo >= 0 else "inverse"
    c2.metric("Resultado Atual", f"R$ {valor_patrimonio_atual:.2f}", f"R$ {lucro_prejuizo:.2f}", delta_color=cor_lucro)

# 4. Gráfico de Tendência
st.markdown("---")
st.subheader("📈 Análise de Tendência (30 dias)")
selecionado = st.selectbox("Escolha o ativo para analisar:", tickers)
grafico_data = yf.Ticker(selecionado).history(period="30d")['Close']
st.line_chart(grafico_data)

st.sidebar.info("IA Rockefeller atualizada. Monitorando sua ordem de PETR4.")
