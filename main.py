import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuração da Página (Suas linhas 6 e 7)
st.set_page_config(page_title="IA Rockefeller", page_icon="💰")
st.title("💰 IA Rockefeller")

# 2. Menu Lateral
st.sidebar.header("Configurações")
capital = st.sidebar.number_input("Seu Capital Disponível (R$)", value=100.0)

# 3. Lógica do Radar
radar = ["VALE3.SA", "PETR4.SA", "MXRF11.SA"]
dados_radar = []

for ativo in radar:
    ticker = yf.Ticker(ativo)
    # Preço atual
    preco = ticker.history(period="1d")['Close'].iloc[-1]
    # Média dos últimos 30 dias para o cálculo de "BARATO"
    media_30 = ticker.history(period="30d")['Close'].mean()
    
    status = "BARATO" if preco < media_30 else "CARO"
    dados_radar.append({"Ativo": ativo, "Preço": f"R$ {preco:.2f}", "Status": status})

st.subheader("🛰️ Radar de Oportunidades")
st.table(pd.DataFrame(dados_radar))

# --- NOVIDADE: GRÁFICO DE TENDÊNCIA ---
st.subheader("📈 Análise de Tendência (30 dias)")
escolha = st.selectbox("Selecione o ativo para analisar:", radar)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)
# ---------------------------------------

# 4. Plano de Compra
if st.button("Calcular Melhor Alocação"):
    p_mxrf = yf.Ticker("MXRF11.SA").history(period="1d")['Close'].iloc[-1]
    cotas = int(capital // p_mxrf)
    st.success(f"Com R$ {capital:.2f}, você pode comprar {cotas} cotas de MXRF11.")
