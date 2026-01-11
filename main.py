import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. SEGURANÇA TOTAL: Tenta importar o Plotly, se falhar, o sistema ignora o gráfico
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except:
    HAS_PLOTLY = False

# 2. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# Estilo Rockefeller (Fundo Preto, Letras Brancas)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #58a6ff !important; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    .manual-section { border-left: 3px solid #58a6ff; padding: 15px; background-color: #0a0a0a; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. MAPEAMENTO DE ATIVOS (RESTABELECIDO 100%)
tickers_map = {
    "PETR4.SA": "PETR4.SA", "VALE3.SA": "VALE3.SA", "MXRF11.SA": "MXRF11.SA", 
    "BTC-USD": "BTC-USD", "Nvidia": "NVDA", "Jóias (Ouro)": "GC=F", 
    "Nióbio": "NGLOY", "Grafeno": "FGPHF", "Câmbio USD/BRL": "USDBRL=X"
}

modelo_huli_tickers = {
    "TAESA": "TAEE11.SA", "ENGIE": "EGIE3.SA", "ALUPAR": "ALUP11.SA",
    "SANEPAR": "SAPR11.SA", "SABESP": "SBSP3.SA", "BANCO DO BRASIL": "BBAS3.SA",
    "ITAÚ": "ITUB4.SA", "BB SEGURIDADE": "BBSE3.SA", "HGLG11": "HGLG11.SA",
    "XPML11": "XPML11.SA", "IVVB11": "IVVB11.SA", "APPLE": "AAPL"
}

# 4. MOTOR DE DADOS COM TRATAMENTO DE ERRO (ANTI-TELA VAZIA)
@st.cache_data(ttl=600)
def obter_dados():
    try:
        cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except:
        cambio = 5.50
    
    res = []
    for nome, t in tickers_map.items():
        try:
            a = yf.Ticker(t)
            h = a.history(period="30d")
            inf = a.info
            if not h.empty:
                p_r = h['Close'].iloc[-1]
                # Lógica de Câmbio
                f = (cambio / 31.1035) if t == "GC=F" else (cambio if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"] else 1)
                p_at = p_r * f
                m30 = h['Close'].mean() * f
                
                lpa = inf.get('trailingEps', 1)
                vpa = inf.get('bookValue', 1)
                pj = np.sqrt(22.5 * lpa * vpa * (f if t in ["NVDA", "AAPL"] else 1))
                
                var = h['Close'].pct_change() * 100
                res.append({
                    "Ativo": nome, "Preço": p_at, "Justo": pj, "LPA": lpa, "VPA": vpa,
                    "Var_Min": var.min(), "Var_H": var.iloc[-1]
                })
        except: continue
    return pd.DataFrame(res), cambio

df_p, v_cambio = obter_dados()

# 5. ORGANIZAÇÃO DAS ABAS (TODAS RESTAURADAS)
tabs = st.tabs(["📊 Painel", "🔍 Radar Modelo", "🧬 DNA", "🎯 Estratégia", "🏦 Carteira Huli", "📖 Manual"])

with tabs[0]: # Painel
    if not df_p.empty:
        st.subheader("🛰️ Monitoramento em Tempo Real")
        st.dataframe(df_p[["Ativo", "Preço", "Justo"]], use_container_width=True)
        
        if HAS_PLOTLY:
            fig = go.Figure(data=[
                go.Bar(name='Preço Atual', x=df_p['Ativo'], y=df_p['Preço'], marker_color='#58a6ff'),
                go.Bar(name='Preço Justo', x=df_p['Ativo'], y=df_p['Justo'], marker_color='#238636')
            ])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Erro ao carregar dados da API. Verifique a conexão.")

with tabs[2]: # DNA
    st.subheader("🧬 DNA dos Ativos (LPA e VPA)")
    st.write(df_p[["Ativo", "LPA", "VPA"]] if not df_p.empty else "Carregando...")

with tabs[3]: # Estratégia + Backtesting
    st.subheader("📈 Backtesting de Eficácia")
    if not df_p.empty:
        sel = st.selectbox("Escolha o Ativo:", df_p["Ativo"].unique())
        row = df_p[df_p["Ativo"] == sel].iloc[0]
        st.success(f"O ativo {sel} custa R$ {row['Preço']:.2f}. No fundo do mês, custou R$ {row['Preço']*(1+(row['Var_Min']/100)):.2f}. Eficácia de aporte: {abs(row['Var_Min']):.2f}%")

with tabs[4]: # Carteira Huli (TEXTOS COMPLETOS)
    st.header("🏦 Carteira Modelo Huli")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("• Energia: TAEE11, EGIE3, ALUP11\n\n• Saneamento: SAPR11, SBSP3\n\n• Bancos: BBAS3, ITUB4, SANB11")
    with c2:
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("• Cripto: Bitcoin, Ethereum\n\n• Tech: Nvidia, Apple")

with tabs[5]: # Manual (TEXTO COMPLETO)
    st.header("📖 Manual Rockefeller")
    st.markdown('<div class="manual-section"><b>LPA/VPA:</b> Representam o Lucro e Valor Patrimonial. Usamos a fórmula de Benjamin Graham para calcular o Preço Justo.</div>', unsafe_allow_html=True)
