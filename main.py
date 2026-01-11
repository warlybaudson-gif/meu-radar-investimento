import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# 1. TRATAMENTO DE ERRO PARA BIBLIOTECAS VISUAIS
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except:
    HAS_PLOTLY = False

# 2. CONFIGURAÇÃO DE INTERFACE
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .stMarkdown, p, label, .stTable td { color: #ffffff !important; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    .manual-section { border-left: 3px solid #58a6ff; padding: 15px; background-color: #0a0a0a; margin-bottom: 20px; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. MAPEAMENTO (VARREDURA TOTAL)
tickers_map = {
    "PETR4.SA": "PETR4.SA", "VALE3.SA": "VALE3.SA", "MXRF11.SA": "MXRF11.SA", 
    "BTC-USD": "BTC-USD", "Nvidia": "NVDA", "Jóias (Ouro)": "GC=F", 
    "Nióbio": "NGLOY", "Grafeno": "FGPHF"
}

# 4. MOTOR DE DADOS ULTRA-RESISTENTE
@st.cache_data(ttl=300)
def motor_de_dados():
    try:
        # Tenta pegar o câmbio, se falhar usa padrão
        try: cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
        except: cambio = 5.60
        
        colecao = []
        for nome, t in tickers_map.items():
            try:
                # Busca simplificada para evitar timeout
                ativo = yf.Ticker(t)
                h = ativo.history(period="30d")
                if h.empty: continue
                
                p_raw = h['Close'].iloc[-1]
                # Lógica de Câmbio/Ouro
                f = (cambio / 31.1035) if t == "GC=F" else (cambio if t in ["NVDA", "NGLOY", "FGPHF", "BTC-USD"] else 1)
                p_brl = p_raw * f
                
                # Dados DNA (LPA/VPA)
                inf = ativo.info
                lpa = inf.get('trailingEps', 1.0)
                vpa = inf.get('bookValue', 1.0)
                
                # Graham
                pj = np.sqrt(22.5 * lpa * vpa * (cambio if t == "NVDA" else 1))
                var = h['Close'].pct_change() * 100
                
                colecao.append({
                    "Ativo": nome, "Preço": p_brl, "Justo": pj, "LPA": lpa, "VPA": vpa,
                    "Min": var.min(), "Status": "✅ DESCONTADO" if p_brl < pj else "❌ CARO"
                })
            except: continue
        return pd.DataFrame(colecao), cambio
    except Exception as e:
        return pd.DataFrame(), 5.60

df_p, v_cambio = motor_de_dados()

# 5. ESTRUTURA DE NAVEGAÇÃO
tabs = st.tabs(["📊 Radar", "🧬 DNA Financeiro", "🎯 Estratégia", "🏦 Carteira Modelo", "📖 Manual"])

with tabs[0]: # RADAR
    if not df_p.empty:
        st.subheader("🛰️ Monitoramento de Ativos")
        st.dataframe(df_p[["Ativo", "Preço", "Justo", "Status"]], use_container_width=True)
        
        if HAS_PLOTLY:
            fig = go.Figure(data=[
                go.Bar(name='Preço Atual', x=df_p['Ativo'], y=df_p['Preço'], marker_color='#58a6ff'),
                go.Bar(name='Valor de Graham', x=df_p['Ativo'], y=df_p['Justo'], marker_color='#238636')
            ])
            fig.update_layout(barmode='group', paper_bgcolor='black', plot_bgcolor='black', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("⚠️ Erro de Conexão com a API de Dados. Exibindo apenas seções estáticas.")

with tabs[1]: # DNA
    st.subheader("🧬 Indicadores LPA e VPA")
    if not df_p.empty:
        st.table(df_p[["Ativo", "LPA", "VPA"]])
    else:
        st.write("Dados indisponíveis no momento.")

with tabs[2]: # ESTRATÉGIA
    st.subheader("📈 Backtesting de Pânico")
    if not df_p.empty:
        sel = st.selectbox("Ativo para Simulação:", df_p["Ativo"].unique())
        d = df_p[df_p["Ativo"] == sel].iloc[0]
        st.info(f"Se você tivesse comprado {sel} no fundo do mês (R$ {d['Preço']*(1+d['Min']/100):.2f}), seu ganho seria de {abs(d['Min']):.2f}%.")

with tabs[3]: # CARTEIRA (CONTEÚDO PRESERVADO)
    st.header("🏦 Carteira Modelo Huli")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("TAESA (TAEE11), ENGIE (EGIE3), BANCO DO BRASIL (BBAS3), SAPR11")
    with col2:
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("Bitcoin, Nvidia, Apple, Grafeno (FGPHF), Nióbio (NGLOY)")

with tabs[4]: # MANUAL (CONTEÚDO PRESERVADO)
    st.header("📖 Manual Rockefeller")
    st.markdown('<div class="manual-section"><b>Fórmula de Graham:</b> Raiz Quadrada de (22,5 * LPA * VPA). Se o preço atual for menor que isso, há margem de segurança.</div>', unsafe_allow_html=True)

# PATRIMÔNIO GLOBAL NA LATERAL
with st.sidebar:
    st.header("⚙️ Meu Patrimônio")
    st.number_input("Ouro (g):", 0.0)
    st.number_input("XP/Bolsa (R$):", 0.0)
    st.number_input("Imóveis/Bens (R$):", 0.0)
