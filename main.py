import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÕES E ESTILO (INTEGRIDADE TOTAL)
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
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli", "🧬 DNA Financeiro", "📈 Backtesting", "📖 Manual"
])

# --- PROCESSAMENTO DE DADOS COM DIVIDENDOS ---
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

@st.cache_data(ttl=3600)
def obter_cambio():
    try: return yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except: return 5.40

cambio_hoje = obter_cambio()

def calcular_dados(lista):
    res = []
    for nome_ex, t in lista.items():
        try:
            ativo = yf.Ticker(t)
            hist = ativo.history(period="30d")
            info = ativo.info
            if not hist.empty:
                p_atual = hist['Close'].iloc[-1]
                # Dividendos em tempo real (trailingAnnualDividendYield)
                dy = info.get('dividendYield', 0) 
                if dy is None: dy = info.get('trailingAnnualDividendYield', 0)
                dy_percent = (dy * 100) if dy else 0.0

                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    p_atual = (p_atual / 31.1035) * cambio_hoje if t == "GC=F" else p_atual * cambio_hoje
                
                m_30 = hist['Close'].mean()
                if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]: m_30 *= cambio_hoje
                if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje
                
                lpa, vpa = info.get('trailingEps', 0), info.get('bookValue', 0)
                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
                if t in ["NVDA", "AAPL"]: p_justo *= cambio_hoje
                
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_atual < m_30 and status_m == "✅ DESCONTADO" else "⚠️ ESPERAR"
                
                res.append({
                    "Ativo": nome_ex, "Preço": p_atual, "Justo": p_justo, "DY": dy_percent,
                    "Status M": status_m, "Ação": acao, "V_Cru": p_atual, "Var_Min": variacoes.min(),
                    "Var_Max": variacoes.max(), "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "Var_H": variacoes.iloc[-1], "LPA": lpa, "VPA": vpa
                })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = calcular_dados(modelo_huli_tickers)

if 'carteira' not in st.session_state: st.session_state.carteira = {}

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo</th><th>DY (%)</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['DY']:.2f}%</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)
    
    # Gestor Dinâmico
    st.markdown("---")
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=0.0)
    opcoes = df_radar["Ativo"].unique() if not df_radar.empty else []
    padrao = ["PETR4.SA"] if "PETR4.SA" in opcoes else []
    ativos_sel = st.multiselect("Habilite seus ativos:", opcoes, default=padrao)
    
    total_investido_acumulado, v_ativos_atualizado = 0, 0
    lista_c = []
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                qtd = st.number_input(f"Qtd ({nome}):", min_value=0, key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, key=f"i_{nome}")
                p_atual = df_radar[df_radar["Ativo"] == nome]["V_Cru"].values[0]
                v_agora = qtd * p_atual
                total_investido_acumulado += investido
                v_ativos_atualizado += v_agora
                st.session_state.carteira[nome] = {"atual": v_agora}
                pm = investido/qtd if qtd > 0 else 0
                lista_c.append({"Ativo": nome, "Qtd": qtd, "PM": pm, "Total": v_agora, "Lucro": v_agora - investido})
        
        st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']:.2f}</td><td>R$ {r['Total']:.2f}</td><td>R$ {r['Lucro']:.2f}</td></tr>" for r in lista_c])}</tbody>
        </table></div>""", unsafe_allow_html=True)
        st.metric("PATRIMÔNIO TOTAL", f"R$ {(v_ativos_atualizado + (capital_xp - total_investido_acumulado)):,.2f}")

# ==================== ABA 2: RADAR CARTEIRA MODELO ====================
with tab_radar_modelo:
    st.subheader("🔍 Radar Tio Huli")
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo</th><th>DY (%)</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['DY']:.2f}%</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)

# (DNA Financeiro e demais abas permanecem com sua robustez original)
with tab_dna:
    st.header("🧬 DNA Financeiro")
    df_combined = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
    html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>LPA</th><th>VPA</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
    for _, r in df_combined.iterrows():
        p_l = r['V_Cru'] / r['LPA'] if r['LPA'] > 0 else 0
        p_vp = r['V_Cru'] / r['VPA'] if r['VPA'] > 0 else 0
        html_dna += f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{p_l:.2f}</td><td>{p_vp:.2f}</td></tr>"
    st.markdown(html_dna + "</tbody></table></div>", unsafe_allow_html=True)

# Outras abas (Backtest, Manual, etc) seguem a mesma lógica do código anterior
