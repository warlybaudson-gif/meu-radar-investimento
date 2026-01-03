import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações Visuais e Título
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="centered")
st.title("💰 IA Rockefeller: Gestão & Radar")

# 2. Menu Lateral para Configurações de Capital
st.sidebar.header("🎚️ Painel de Controle")
capital = st.sidebar.number_input("Seu Capital Disponível (R$)", min_value=0.0, value=1000.0, step=50.0)
st.sidebar.info("Este capital será usado para sugerir a compra de cotas.")

# 3. Processamento de Dados (Radar + Dividendos)
st.subheader("🛰️ Radar de Oportunidades & Dividendos")

# Lista de ativos: Ações, FII e Cripto
radar = ["VALE3.SA", "PETR4.SA", "MXRF11.SA", "BTC-USD"]
dados_final = []

with st.spinner('Atualizando dados do mercado...'):
    for ativo in radar:
        ticker = yf.Ticker(ativo)
        
        # Preço e Moeda
        hist = ticker.history(period="1d")
        preco_atual = hist['Close'].iloc[-1]
        moeda = "$" if "USD" in ativo else "R$"
        
        # Cálculo de Dividendos (Yield)
        # Pegamos os dividendos dos últimos 12 meses e dividimos pelo preço
        divs = ticker.dividends
        if not divs.empty:
            ultimos_12m = divs.tail(12).sum()
            yield_pct = (ultimos_12m / preco_atual) * 100
        else:
            yield_pct = 0.0

        dados_final.append({
            "Ativo": ativo,
            "Preço Atual": f"{moeda} {preco_atual:,.2f}",
            "Dividendos (12m)": f"{yield_pct:.2f}%",
            "Sugerido": "SIM" if yield_pct > 0 or "USD" in ativo else "OBSERVAR"
        })

# Exibição da Tabela
df = pd.DataFrame(dados_final)
st.table(df)

# 4. Gráfico de Análise Técnica (Tendência)
st.subheader("📈 Análise de Tendência (Últimos 30 Dias)")
escolha = st.selectbox("Selecione o ativo para ver o gráfico detalhado:", radar)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)

# 5. Calculadora de Alocação Inteligente
st.subheader("🧮 Sugestão de Alocação")
if st.button("Calcular quantidade de cotas"):
    # Exemplo com MXRF11 que é acessível
    p_fii = yf.Ticker("MXRF11.SA").history(period="1d")['Close'].iloc[-1]
    quantidade = int(capital // p_fii)
    sobra = capital % p_fii
    
    st.success(f"Com R$ {capital:,.2f}, você pode adquirir **{quantidade} cotas** de MXRF11.SA.")
    st.warning(f"Ainda restariam R$ {sobra:.2f} no seu saldo.")
