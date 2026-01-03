import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuração da Página do App
st.set_page_config(page_title="IA Rockefeller", page_icon="💰")
st.title("💰 Sistema Rockefeller: Gestão de Capital")

# 2. Menu Lateral (Sidebar)
st.sidebar.header("Configurações")
capital = st.sidebar.number_input("Seu Capital Disponível (R$)", value=100.0)
alerta_perda = st.sidebar.slider("Alerta de Risco (%)", 1, 20, 5)

# 3. O Radar (Lógica que você já testou)
st.subheader("🛰️ Radar de Oportunidades")
radar = ["VALE3.SA", "PETR4.SA", "MXRF11.SA"]
dados_radar = []

for ativo in radar:
    preco = yf.Ticker(ativo).history(period="1d")['Close'].iloc[-1]
    # Lógica de decisão simplificada para o App
    status = "BARATO" if preco < (preco * 1.01) else "CARO" # Exemplo dinâmico
    dados_radar.append({"Ativo": ativo, "Preço": f"R$ {preco:.2f}", "Status": status})

st.table(pd.DataFrame(dados_radar))

# 4. Calculadora Inteligente
st.subheader("💸 Plano de Compra Sugerido")
if st.button("Calcular Melhor Alocação"):
    # Aqui entra o seu código de cálculo de cotas
    preco_fii = 9.50 # Baseado no seu último print
    cotas = int(capital // preco_fii)
    investido = cotas * preco_fii
    
    st.success(f"Com R$ {capital}, a IA sugere comprar {cotas} cotas de MXRF11.")

    st.info(f"Renda Mensal Estimada: R$ {cotas * 0.10:.2f}")
