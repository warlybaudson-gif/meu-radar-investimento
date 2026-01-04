import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Harmonização Total Black e Ajuste para Celular (Responsivo)
st.markdown("""
    <style>
    /* Fundo Total Escuro */
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Ajuste da Tabela para não quebrar texto no Celular */
    table { width: 100% !important; font-size: 12px !important; }
    thead tr th { 
        background-color: #1a1a1a !important; 
        color: #58a6ff !important; 
        white-space: nowrap !important; /* Impede a quebra de linha no cabeçalho */
        padding: 5px !important;
    }
    tbody td { background-color: #000000 !important; color: #ffffff !important; }
    
    /* Estilo das Métricas (Calculadora) */
    div[data-testid="stMetric"] { 
        background-color: #111111; 
        border: 1px solid #333333; 
        padding: 10px; 
        border-radius: 8px; 
    }
    
    /* Esconder menus desnecessários para limpar o visual */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Painel Lateral
st.sidebar.markdown("### ⚙️ Configurações")
capital_base = st.sidebar.number_input("Capital total (R$)", value=1000.0)

# 4. Tabela de Radar Harmonizada
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
        
        # Lógica de Ontem
        status = "🔥 BARATO" if preco_atual < media_30 else "💎 CARO"
        acao = "✅ COMPRAR" if preco_atual < media_30 else "⚠️ ESPERAR"
        
        # Dividendos 12 meses (12m)
        divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
        
        dados_finais.append({
            "Ativo": t, 
            "Preço": f"R$ {preco_atual:.2f}", 
            "Média 30d": f"R$ {media_30:.2f}",
            "Status": status,
            "Ação": acao,
            "Div. 12m": f"R$ {divs:.2f}" # Nome da coluna encurtado para ajudar no celular
        })

df = pd.DataFrame(dados_finais)
st.table(df)

# 5. Gestor de Patrimônio (Ajustado para PETR4)
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧮 Gestor XP")
    with st.expander("Sua Ordem", expanded=True):
        valor_xp = st.number_input("Valor enviado (R$):", value=50.0)
        pago_xp = st.number_input("Preço pago (R$):", value=31.0)
        
        cotas = int(valor_xp // pago_xp)
        sobra = valor_xp % pago_xp
        
        preco_petr = yf.Ticker("PETR4.SA").history(period="1d")['Close'].iloc[-1]
        patrimonio = (cotas * preco_petr) + sobra
        resultado = patrimonio - valor_xp

with col2:
    st.subheader("📊 Resultado")
    st.metric("Cotas", f"{cotas} un")
    st.metric("Patrimônio", f"R$ {patrimonio:.2f}", f"R$ {resultado:.2f}")

# 6. Gráfico Harmonizado
st.markdown("---")
st.subheader("📈 Tendência 30d")
escolha = st.selectbox("Ativo:", tickers)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)
