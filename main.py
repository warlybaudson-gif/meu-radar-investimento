import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Tenta carregar o gráfico. Se não tiver a biblioteca, o app continua funcionando!
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

# --- CONFIGURAÇÃO E ESTILO (PRESERVADOS) ---
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; }
    .mobile-table-container { overflow-x: auto; width: 100%; }
    .rockefeller-table {
        width: 100%; border-collapse: collapse; font-family: 'Courier New', Courier, monospace;
        margin-bottom: 20px; font-size: 0.85rem;
    }
    .rockefeller-table th { background-color: #1a1a1a; color: #58a6ff !important; padding: 10px; border-bottom: 2px solid #333; }
    .rockefeller-table td { padding: 10px; text-align: center !important; border-bottom: 1px solid #222; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-radius: 8px; padding: 10px; }
    .manual-section { border-left: 3px solid #58a6ff; padding: 15px; margin-bottom: 25px; background-color: #0a0a0a; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# --- MAPEAMENTO DE ATIVOS (VARREDURA COMPLETA) ---
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

# --- MOTOR DE CÁLCULO ---
@st.cache_data(ttl=3600)
def carregar_dados_globais():
    try:
        cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except:
        cambio = 5.50
    return cambio

cambio_atual = carregar_dados_globais()

def processar_ativos(lista):
    dados_lista = []
    for nome, t in lista.items():
        try:
            ativo = yf.Ticker(t)
            hist = ativo.history(period="30d")
            info = ativo.info
            if not hist.empty:
                p_raw = hist['Close'].iloc[-1]
                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    fator = (cambio_atual / 31.1035) if t == "GC=F" else cambio_atual
                    p_real = p_raw * fator
                else: p_real = p_raw
                
                m30 = hist['Close'].mean() * (cambio_atual if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"] else 1)
                lpa = info.get('trailingEps', 1)
                vpa = info.get('bookValue', 1)
                lpa_r = lpa * cambio_atual if t in ["NVDA", "AAPL"] else lpa
                vpa_r = vpa * cambio_atual if t in ["NVDA", "AAPL"] else vpa
                
                pj = np.sqrt(22.5 * lpa_r * vpa_r) if (lpa_r * vpa_r) > 0 else m30
                status = "✅ DESCONTADO" if p_real < pj else "❌ SOBREPREÇO"
                var = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_real < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"
                
                dados_lista.append({
                    "Ativo": nome, "Preço": p_real, "Justo": pj, "LPA": lpa_r, "VPA": vpa_r,
                    "Status": status, "Ação": acao, "Var_Min": var.min(), "Var_Max": var.max(),
                    "Dias_A": (var > 0).sum(), "Dias_B": (var < 0).sum(), "Var_H": var.iloc[-1]
                })
        except: continue
    return pd.DataFrame(dados_lista)

df_p = processar_ativos(tickers_map)
df_m = processar_ativos(modelo_huli_tickers)
if 'carteira' not in st.session_state: st.session_state.carteira = {}

# --- ABAS ---
tab_painel, tab_radar_modelo, tab_dna, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🧬 DNA (LPA/VPA)", "🎯 Estratégia Huli", "🏦 Carteira Modelo Huli", "📖 Manual de Instruções"
])

with tab_painel:
    st.subheader("🛰️ Radar Estratégico")
    if not df_p.empty:
        st.dataframe(df_p[["Ativo", "Preço", "Justo", "Status", "Ação"]], use_container_width=True)
        
        if HAS_PLOTLY:
            fig = go.Figure(data=[
                go.Bar(name='Preço', x=df_p['Ativo'], y=df_p['Preço'], marker_color='#58a6ff'),
                go.Bar(name='Justo', x=df_p['Ativo'], y=df_p['Justo'], marker_color='#238636')
            ])
            st.plotly_chart(fig, use_container_width=True)
    
    st.sidebar.header("⚙️ Gestão Patrimonial")
    g_ouro = st.sidebar.number_input("Ouro Físico (g):", 0.0)
    v_bens = st.sidebar.number_input("Imóveis/Bens (R$):", 0.0)
    cap_total = st.sidebar.number_input("Capital na XP (R$):", 0.0)

with tab_dna:
    st.subheader("🧬 DNA Financeiro")
    df_dna_all = pd.concat([df_p, df_m]).drop_duplicates(subset="Ativo")
    st.table(df_dna_all[["Ativo", "LPA", "VPA", "Status"]])

with tab_huli:
    st.subheader("🎯 Rebalanceamento e Backtesting")
    if not df_p.empty:
        at_bt = st.selectbox("Simular Ativo:", df_p["Ativo"].unique())
        d_bt = df_p[df_p["Ativo"] == at_bt].iloc[0]
        st.success(f"Eficácia: {at_bt} | Atual: R$ {d_bt['Preço']:.2f} | Oscilação Mensal: {d_bt['Var_Min']:.2f}%")

with tab_modelo:
    st.header("🏦 Carteira Modelo Huli")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("TAEE11, EGIE3, ALUP11, SAPR11, SBSP3, BBAS3, ITUB4, BBSE3, CXSE3")
    with col2:
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("Bitcoin (BTC), Ethereum (ETH), Nvidia (NVDA), Apple (AAPL)")

with tab_manual:
    st.header("📖 Manual de Instruções")
    st.markdown('<div class="manual-section"><b>LPA/VPA:</b> Indicadores de saúde real. <br> <b>Margem de Segurança:</b> Diferença entre preço e valor justo.</div>', unsafe_allow_html=True)
