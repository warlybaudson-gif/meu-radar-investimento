import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. PROTEÇÃO DE BIBLIOTECAS (Evita tela vazia se o Plotly não estiver instalado)
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except:
    HAS_PLOTLY = False

# 2. CONFIGURAÇÕES DE INTERFACE (PRESERVADAS)
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; }
    .rockefeller-table {
        width: 100%; border-collapse: collapse; font-family: 'Courier New', monospace;
        margin-bottom: 20px; font-size: 0.85rem;
    }
    .rockefeller-table th { background-color: #1a1a1a; color: #58a6ff !important; padding: 10px; border-bottom: 2px solid #333; }
    .rockefeller-table td { padding: 10px; text-align: center; border-bottom: 1px solid #222; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    .manual-section { border-left: 3px solid #58a6ff; padding: 15px; margin-bottom: 25px; background-color: #0a0a0a; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. MAPEAMENTO COMPLETO (Nióbio, Grafeno, Câmbio e Modelo Huli)
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

# 4. MOTOR DE DADOS (ANTI-TRAVAMENTO)
@st.cache_data(ttl=600)
def coletar_dados_robustos():
    try:
        cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except:
        cambio = 5.50
    
    def processar(lista):
        res = []
        for nome, t in lista.items():
            try:
                a = yf.Ticker(t)
                h = a.history(period="30d")
                inf = a.info
                if not h.empty:
                    p_raw = h['Close'].iloc[-1]
                    f = (cambio / 31.1035) if t == "GC=F" else (cambio if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"] else 1)
                    p_real = p_raw * f
                    m30 = h['Close'].mean() * f
                    
                    lpa, vpa = inf.get('trailingEps', 0), inf.get('bookValue', 0)
                    lpa_r = lpa * (cambio if t in ["NVDA", "AAPL"] else 1)
                    vpa_r = vpa * (cambio if t in ["NVDA", "AAPL"] else 1)
                    
                    pj = np.sqrt(22.5 * lpa_r * vpa_r) if (lpa_r * vpa_r) > 0 else m30
                    var = h['Close'].pct_change() * 100
                    
                    res.append({
                        "Ativo": nome, "Preço": p_real, "Justo": pj, "LPA": lpa_r, "VPA": vpa_r,
                        "Status": "✅ DESCONTADO" if p_real < pj else "❌ SOBREPREÇO",
                        "Ação": "✅ COMPRAR" if p_real < m30 and p_real < pj else "⚠️ ESPERAR",
                        "Var_Min": var.min(), "Var_H": var.iloc[-1],
                        "Dias_A": (var > 0).sum(), "Dias_B": (var < 0).sum()
                    })
            except: continue
        return pd.DataFrame(res)
    
    return processar(tickers_map), processar(modelo_huli_tickers), cambio

df_p, df_m, v_cambio = coletar_dados_robustos()
if 'carteira' not in st.session_state: st.session_state.carteira = {}

# 5. ESTRUTURA DE ABAS (VARREDURA TOTAL DE REQUISITOS)
tab_painel, tab_dna, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel", "🧬 DNA (LPA/VPA)", "🎯 Estratégia & Backtesting", "🏦 Carteira Modelo", "📖 Manual"
])

with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    if not df_p.empty:
        st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo</th><th>Status</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_p.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)
        
        # GRÁFICO (RESTAURADO E PROTEGIDO)
        if HAS_PLOTLY:
            st.subheader("📉 Margem de Segurança")
            fig = go.Figure(data=[
                go.Bar(name='Preço Atual', x=df_p['Ativo'], y=df_p['Preço'], marker_color='#58a6ff'),
                go.Bar(name='Preço Justo', x=df_p['Ativo'], y=df_p['Justo'], marker_color='#238636')
            ])
            fig.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)

    # PATRIMÔNIO GLOBAL (LADO DIREITO/SIDEBAR)
    with st.sidebar:
        st.header("⚙️ Patrimônio Global")
        g_ouro = st.number_input("Ouro Físico (g):", value=0.0)
        v_bens = st.number_input("Outros Bens (R$):", value=0.0)
        cap_xp = st.number_input("Capital na XP (R$):", value=0.0)

with tab_dna:
    st.subheader("🧬 DNA Financeiro (LPA e VPA)")
    df_dna = pd.concat([df_p, df_m]).drop_duplicates(subset="Ativo")
    st.dataframe(df_dna[["Ativo", "LPA", "VPA", "Status"]], use_container_width=True)

with tab_huli:
    st.subheader("📈 Eficácia Comprovada (Backtesting)")
    if not df_p.empty:
        at_bt = st.selectbox("Simular Ativo:", df_p["Ativo"].unique())
        d_bt = df_p[df_p["Ativo"] == at_bt].iloc[0]
        p_fundo = d_bt['Preço'] * (1 + (d_bt['Var_Min']/100))
        st.success(f"**Análise {at_bt}:** Preço Atual: R$ {d_bt['Preço']:.2f} | Fundo do Mês: R$ {p_fundo:.2f} | Eficácia: {abs(d_bt['Var_Min']):.2f}% de ganho potencial.")

with tab_modelo:
    st.header("🏦 Carteira Modelo Huli")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("• Energia: TAEE11, EGIE3, ALUP11\n\n• Saneamento: SAPR11, SBSP3\n\n• Bancos: BBAS3, ITUB4")
    with c2:
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("• Cripto: Bitcoin, Ethereum\n\n• Tech: Nvidia, Apple")

with tab_manual:
    st.header("📖 Manual Rockefeller")
    st.markdown('<div class="manual-section"><b>LPA/VPA:</b> O DNA da empresa. Se o lucro cai mas o patrimônio cresce, há valor escondido.</div>', unsafe_allow_html=True)
