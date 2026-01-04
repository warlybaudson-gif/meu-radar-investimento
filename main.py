import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade e Performance
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Varredura de CSS: Garantindo Contraste e Responsividade Total
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Correção de Expander e Inputs */
    .streamlit-expanderHeader { background-color: #000000 !important; border: 1px solid #333 !important; border-radius: 8px !important; }
    .streamlit-expanderContent { background-color: #000000 !important; border: 1px solid #333 !important; border-radius: 0 0 8px 8px !important; }
    
    /* Labels e Métricas com Visibilidade Máxima */
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 24px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    
    /* Tabela Anti-Quebra para Celular */
    table { width: 100% !important; font-size: 13px !important; }
    th, td { white-space: nowrap !important; padding: 12px 8px !important; text-align: left !important; border-bottom: 1px solid #222 !important; }
    .stTable { overflow-x: auto !important; display: block !important; border-radius: 10px !important; }
    thead tr th { background-color: #1a1a1a !important; color: #58a6ff !important; }
    
    /* Blocos de Resultado */
    div[data-testid="stMetric"] { 
        background-color: #0c0e11; 
        border: 1px solid #30363d; 
        padding: 15px; 
        border-radius: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Varredura de Dados: Radar de Ativos
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_1d = ativo.history(period="1d")
        if not hist_1d.empty:
            preco_atual = hist_1d['Close'].iloc[-1]
            hist_30d = ativo.history(period="30d")
            media_30 = hist_30d['Close'].mean()
            
            status = "🔥 BARATO" if preco_atual < media_30 else "💎 CARO"
            acao = "✅ COMPRAR" if preco_atual < media_30 else "⚠️ ESPERAR"
            
            # Varredura de Dividendos: Evita erro se o dado estiver vazio
            divs_yield = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            
            dados_finais.append({
                "Ativo": t, 
                "Preço": f"R$ {preco_atual:.2f}", 
                "Média 30d": f"R$ {media_30:.2f}",
                "Status": status, 
                "Ação": acao, 
                "Div. 12m": f"R$ {divs_yield:.2f}"
            })
    except Exception:
        continue # Pula se houver falha na API para não travar o app

df_radar = pd.DataFrame(dados_finais)

# 4. Exibição e Exportação
st.subheader("🛰️ Radar de Ativos")
st.table(df_radar)

csv = df_radar.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar Dados (Excel/BI)",
    data=csv,
    file_name='radar_rockefeller.csv',
    mime='text/csv',
)

st.markdown("---")

# 5. Varredura do Gestor XP: Lógica de Cálculo
col_calc, col_res = st.columns([1, 1.2])

with col_calc:
    st.subheader("🧮 Gestor XP")
    with st.expander("Sua Ordem", expanded=True):
        tipo_ordem = st.selectbox("Tipo de Ordem:", ("A Mercado", "Limitada", "Stop Loss", "Stop Móvel"))
        valor_xp = st.number_input("Valor enviado (R$):", min_value=0.0, value=50.0, step=10.0)
        pago_xp = st.number_input("Preço pago (R$):", min_value=0.01, value=31.0, step=0.5)
        
        # Lógica de Troco e Cotas
        cotas = int(valor_xp // pago_xp)
        troco_xp = valor_xp % pago_xp
        
        # Busca PETR4 em tempo real para o patrimônio
        try:
            preco_petr = yf.Ticker("PETR4.SA").history(period="1d")['Close'].iloc[-1]
        except:
            preco_petr = pago_xp # Fallback caso a API falhe
            
        patrimonio_total = (cotas * preco_petr) + troco_xp
        lucro_abs = patrimonio_total - valor_xp

with col_res:
    st.subheader("📊 Resultado")
    st.caption(f"Estratégia: {tipo_ordem}")
    r1, r2 = st.columns(2)
    r1.metric("Cotas", f"{cotas} un")
    r2.metric("Troco em Conta", f"R$ {troco_xp:.2f}")
    st.metric("Patrimônio Total", f"R$ {patrimonio_total:.2f}", f"R$ {lucro_abs:.2f}")

# 6. Gráfico de Tendência
st.markdown("---")
st.subheader("📈 Tendência (30 dias)")
escolha = st.selectbox("Analisar Histórico:", tickers)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)
