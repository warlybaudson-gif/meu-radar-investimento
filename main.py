import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações Visuais e Título
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="centered")
st.title("💰 IA Rockefeller: Gestão & Radar")

# 2. Menu Lateral para Configurações de Capital
st.sidebar.header("🎚️ Painel de Controle")
capital = st.sidebar.number_input("Seu Capital Disponível (R$)", min_value=0.0, value=1000.0, step=50.0)

# 3. Processamento de Dados (Radar + Dividendos + Status)
st.subheader("🛰️ Radar de Oportunidades & Dividendos")

# Lista de ativos
radar = ["VALE3.SA", "PETR4.SA", "MXRF11.SA", "BTC-USD"]
dados_final = []

with st.spinner('Atualizando dados do mercado...'):
    for ativo in radar:
        ticker = yf.Ticker(ativo)
        
        # Preço Atual
        hist = ticker.history(period="5d") # Pega os últimos dias para garantir o preço
        preco_atual = hist['Close'].iloc[-1]
        
        # Média de 30 dias para definir Caro ou Barato
        media_30 = ticker.history(period="30d")['Close'].mean()
        
        # Lógica: Caro ou Barato
        status_preco = "Barato" if preco_atual < media_30 else "Caro"
        
        # Lógica: Vender ou Comprar (Baseada no status do preço)
        acao_recomendada = "Comprar" if status_preco == "Barato" else "Vender"
        
        # Formatação de Moeda
        moeda = "$" if "USD" in ativo else "R$"
        
        # Dividendos (Yield 12 meses)
        divs = ticker.dividends
        if not divs.empty:
            yield_pct = (divs.tail(12).sum() / preco_atual) * 100
        else:
            yield_pct = 0.0

        dados_final.append({
            "Ativo": ativo,
            "Preço Atual": f"{moeda} {preco_atual:,.2f}",
            "Caro ou Barato": status_preco,
            "Recomendação": acao_recomendada,
            "Dividendos (12m)": f"{yield_pct:.2f}%"
        })

# Exibição da Tabela Atualizada
df = pd.DataFrame(dados_final)
st.table(df)

# 4. Gráfico de Análise Técnica
st.subheader("📈 Análise de Tendência (30 dias)")
escolha = st.selectbox("Selecione o ativo para ver o gráfico detalhado:", radar)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)

# 5. Calculadora de Alocação
st.subheader("🧮 Sugestão de Alocação")
if st.button("Calcular quantidade de cotas"):
    p_fii = yf.Ticker("MXRF11.SA").history(period="1d")['Close'].iloc[-1]
    quantidade = int(capital // p_fii)
    st.success(f"Com R$ {capital:,.2f}, você pode adquirir **{quantidade} cotas** de MXRF11.SA.")

