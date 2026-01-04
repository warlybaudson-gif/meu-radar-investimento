import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Harmonização Total Black e Visibilidade Máxima (Células Brancas)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Fontes Brancas Puras nas Células */
    table { width: 100% !important; font-size: 13px !important; color: #ffffff !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; white-space: nowrap !important; }
    td { background-color: #000000 !important; color: #ffffff !important; white-space: nowrap !important; border-bottom: 1px solid #222 !important; }
    
    /* Visibilidade de Rótulos e Expander */
    label { color: #ffffff !important; font-weight: bold !important; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    .streamlit-expanderContent { background-color: #000000 !important; border: 1px solid #333 !important; }
    
    /* Métricas e Blocos */
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 26px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 15px; border-radius: 10px; }
    
    /* Rolagem Lateral para Celular */
    .stTable { overflow-x: auto !important; display: block !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Processamento de Dados (Garantindo PETR4)
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
    try:
        # Busca dados do ativo
        ativo = yf.Ticker(t)
        hist_1d = ativo.history(period="1d")
        
        # Se os dados existirem, processa
        if not hist_1d.empty:
            preco_atual = hist_1d['Close'].iloc[-1]
            hist_30d = ativo.history(period="30d")
            media_30 = hist_30d['Close'].mean()
            
            status = "🔥 BARATO" if preco_atual < media_30 else "💎 CARO"
            acao = "✅ COMPRAR" if preco_atual < media_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            
            dados_finais.append({
                "Ativo": t, 
                "Preço": f"R$ {preco_atual:.2f}", 
                "Média 30d": f"R$ {media_30:.2f}",
                "Status": status, 
                "Ação": acao, 
                "Div. 12m": f"R$ {divs:.2f}"
            })
    except Exception as e:
        st.error(f"Erro ao carregar {t}: {e}")

df_radar = pd.DataFrame(dados_finais)

# 4. Exibição e Exportação
st.subheader("🛰️ Radar de Ativos")
if not df_radar.empty:
    st.table(df_radar)
    
    csv = df_radar.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Baixar Dados (Excel/BI)", data=csv, file_name='radar_rockefeller.csv', mime='text/csv')
else:
    st.warning("Aguardando resposta do mercado para carregar PETR4 e outros ativos...")

st.markdown("---")

# 5. Gestor de Patrimônio (XP)
col_calc, col_res = st.columns([1, 1.2])

with col_calc:
    st.subheader("🧮 Gestor XP")
    with st.expander("Sua Ordem", expanded=True):
        tipo_ordem = st.selectbox("Tipo de Ordem:", ("A Mercado", "Limitada", "Stop Loss", "Stop Móvel"))
        valor_xp = st.number_input("Valor enviado (R$):", value=50.0)
        pago_xp = st.number_input("Preço pago (R$):", value=31.0)
        
        # Lógica de Troco
        cotas = int(valor_xp // pago_xp)
        troco_xp = valor_xp % pago_xp
        
        # Tenta pegar preço da PETR4 para lucro real
        try:
            preco_petr = yf.Ticker("PETR4.SA").history(period="1d")['Close'].iloc[-1]
        except:
            preco_petr = pago_xp
            
        patrimonio_total = (cotas * preco_petr) + troco_xp
        lucro_abs = patrimonio_total - valor_xp

with col_res:
    st.subheader("📊 Resultado")
    m1, m2 = st.columns(2)
    m1.metric("Cotas Compradas", f"{cotas} un")
    m2.metric("Troco em Conta", f"R$ {troco_xp:.2f}")
    st.metric("Patrimônio Total", f"R$ {patrimonio_total:.2f}", f"R$ {lucro_abs:.2f}")

# 6. Gráfico
st.markdown("---")
st.subheader("📈 Tendência 30d")
escolha = st.selectbox("Escolha o Ativo:", tickers)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)
