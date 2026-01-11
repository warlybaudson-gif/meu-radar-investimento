import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Tenta importar o Plotly, se não conseguir, o app não quebra
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. ESTILO E IDENTIDADE VISUAL (PRESERVADOS)
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; white-space: nowrap !important; }
    .mobile-table-container { overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; }
    .rockefeller-table {
        width: 100%; border-collapse: collapse; font-family: 'Courier New', Courier, monospace;
        margin-bottom: 20px; font-size: 0.85rem;
    }
    .rockefeller-table th { background-color: #1a1a1a; color: #58a6ff !important; text-align: center !important; padding: 10px; border-bottom: 2px solid #333; }
    .rockefeller-table td { padding: 10px; text-align: center !important; border-bottom: 1px solid #222; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-radius: 8px; text-align: center; }
    .manual-section { border-left: 3px solid #58a6ff; padding: 15px; margin-bottom: 25px; background-color: #0a0a0a; border-radius: 0 5px 5px 0; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 2. ABAS
tab_painel, tab_radar_modelo, tab_dna, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🧬 DNA (LPA/VPA)", "🎯 Estratégia Huli", "🏦 Carteira Modelo Huli", "📖 Manual de Instruções"
])

# 3. MAPEAMENTO (VARREDURA TOTAL)
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

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.50

def motor_calculo(lista):
    colecao = []
    for nome, t in lista.items():
        try:
            a = yf.Ticker(t)
            h = a.history(period="30d")
            inf = a.info
            if not h.empty:
                p_r = h['Close'].iloc[-1]
                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    f = (cambio_hoje / 31.1035) if t == "GC=F" else cambio_hoje
                    p_at = p_r * f
                else: p_at = p_r
                
                m30 = h['Close'].mean() * (cambio_hoje if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"] else 1)
                if t == "GC=F": m30 = (h['Close'].mean() / 31.1035) * cambio_hoje
                
                lpa, vpa = inf.get('trailingEps', 0), inf.get('bookValue', 0)
                lpa_f = lpa * (cambio_hoje if t in ["NVDA", "AAPL", "NGLOY", "FGPHF"] else 1)
                vpa_f = vpa * (cambio_hoje if t in ["NVDA", "AAPL", "NGLOY", "FGPHF"] else 1)
                
                pj = np.sqrt(22.5 * lpa_f * vpa_f) if lpa_f > 0 and vpa_f > 0 else m30
                status = "✅ DESCONTADO" if p_at < pj else "❌ SOBREPREÇO"
                vr = h['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_at < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"
                
                colecao.append({
                    "Ativo": nome, "Preço": p_at, "Justo": pj, "LPA": lpa_f, "VPA": vpa_f,
                    "Status": status, "Ação": acao, "Var_Min": vr.min(), "Var_Max": vr.max(),
                    "Dias_A": (vr > 0).sum(), "Dias_B": (vr < 0).sum(), "Var_H": vr.iloc[-1]
                })
        except: continue
    return pd.DataFrame(colecao)

df_p = motor_calculo(tickers_map)
df_m = motor_calculo(modelo_huli_tickers)
if 'carteira' not in st.session_state: st.session_state.carteira = {}

# --- ABA 1: PAINEL DE CONTROLE ---
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo</th><th>Status</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_p.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)
    
    st.subheader("📊 Raio-X de Volatilidade")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_p.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

    if HAS_PLOTLY:
        st.subheader("📉 Margem de Segurança: Preço vs Valor de Graham")
        fig = go.Figure(data=[
            go.Bar(name='Preço Atual', x=df_p['Ativo'], y=df_p['Preço'], marker_color='#58a6ff'),
            go.Bar(name='Preço Justo', x=df_p['Ativo'], y=df_p['Justo'], marker_color='#238636')
        ])
        fig.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with st.sidebar:
        st.header("⚙️ Patrimônio Global")
        g_ouro = st.number_input("Ouro Físico (g):", value=0.0)
        v_bens_imoveis = st.number_input("Imóveis/Outros Bens (R$):", value=0.0)

    st.subheader("🧮 Gestor de Carteira")
    cap_xp_total = st.number_input("💰 Capital Total na XP (R$):", value=0.0)
    ativos_ativos = st.multiselect("Habilite ativos:", df_p["Ativo"].unique(), default=["PETR4.SA"])
    
    v_total_inv_h, v_bolsa_agora_h = 0, 0
    if ativos_ativos:
        c1, c2 = st.columns(2)
        for i, n_h in enumerate(ativos_ativos):
            with [c1, c2][i % 2]:
                qh = st.number_input(f"Qtd ({n_h}):", key=f"qh_{n_h}")
                ih = st.number_input(f"Investido R$ ({n_h}):", key=f"ih_{n_h}")
                pm_h = df_p[df_p["Ativo"] == n_h]["Preço"].values[0]
                va_h = qh * pm_h
                v_bolsa_agora_h += va_h
                v_total_inv_h += ih
                st.session_state.carteira[n_h] = {"atual": va_h}
        
        tr_xp = cap_xp_total - v_total_inv_h
        po_h = df_p[df_p["Ativo"] == "Jóias (Ouro)"]["Preço"].values[0]
        patri_glob = v_bolsa_agora_h + tr_xp + (g_ouro * po_h) + v_bens_imoveis
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa & Cripto", f"R$ {v_bolsa_agora_h:,.2f}")
        m2.metric("Saldo, Ouro & Bens", f"R$ {(tr_xp + (g_ouro * po_h) + v_bens_imoveis):,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_glob:,.2f}")

# --- ABA 3: DNA (LPA/VPA) ---
with tab_dna:
    st.subheader("🧬 DNA Financeiro: LPA e VPA em Tempo Real")
    df_tot = pd.concat([df_p, df_m]).drop_duplicates(subset="Ativo")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>LPA</th><th>VPA</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{(r['Preço']/r['LPA'] if r['LPA']>0 else 0):.2f}</td><td>{(r['Preço']/r['VPA'] if r['VPA']>0 else 0):.2f}</td></tr>" for _, r in df_tot.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# --- ABA 4: ESTRATÉGIA + BACKTESTING ---
with tab_huli:
    st.subheader("📈 Backtesting: Eficácia do Sinal Rockefeller")
    at_f = st.selectbox("Simular Ativo:", df_p["Ativo"].unique())
    d_f = df_p[df_p["Ativo"] == at_f].iloc[0]
    p_fundo = d_f['Preço'] * (1 - (abs(d_f['Var_Min'])/100))
    st.success(f"""**Análise de Eficácia {at_f}:**
    - Valor Atual: R$ {d_f['Preço']:.2f}
    - Valor no Fundo (Recorde): R$ {p_fundo:.2f}
    - Ganho em comprar no pânico: {abs(d_f['Var_Min']):.2f}%""")

# --- ABA 5: CARTEIRA MODELO ---
with tab_modelo:
    st.header("🏦 Carteira Modelo Huli")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11, EGIE3, ALUP11\n\n**• Saneamento:** SAPR11, SBSP3\n\n**• Bancos:** BBAS3, ITUB4")
    with col_b:
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("**• Cripto:** Bitcoin, Ethereum\n\n**• Tech:** Nvidia, Apple")

# --- ABA 6: MANUAL ---
with tab_manual:
    st.header("📖 Manual Rockefeller")
    st.write("Guia completo sobre Graham, LPA/VPA e estratégias de rebalanceamento.")
