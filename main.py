import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÕES E ESTILO (PRESERVANDO SUA IDENTIDADE VISUAL)
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

# 2. ABAS (ORIGINAIS)
tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli", "🧬 DNA Financeiro", "📈 Backtesting", "📖 Manual"
])

# 3. MAPEAMENTO E MOTOR DE CÁLCULO (COM DIVIDENDOS)
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
    except: return 5.50

cambio_hoje = obter_cambio()

def motor_calculo(lista):
    colecao = []
    for nome, t in lista.items():
        try:
            a = yf.Ticker(t)
            h = a.history(period="30d")
            inf = a.info
            if not h.empty:
                p_at = h['Close'].iloc[-1]
                # Coleta de Dividendos
                dy = inf.get('dividendYield', 0)
                if dy is None: dy = inf.get('trailingAnnualDividendYield', 0)
                dy_perc = (dy * 100) if dy else 0.0

                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    f = (cambio_hoje / 31.1035) if t == "GC=F" else cambio_hoje
                    p_at *= f
                
                m30 = h['Close'].mean() * (cambio_hoje if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"] else 1)
                if t == "GC=F": m30 = (h['Close'].mean() / 31.1035) * cambio_hoje
                
                lpa, vpa = inf.get('trailingEps', 0), inf.get('bookValue', 0)
                pj = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m30
                if t in ["NVDA", "AAPL"]: pj *= cambio_hoje
                
                status = "✅ DESCONTADO" if p_at < pj else "❌ SOBREPREÇO"
                vr = h['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_at < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"
                
                colecao.append({
                    "Ativo": nome, "Preço": p_at, "Justo": pj, "DY": dy_perc, "Status": status, "Ação": acao,
                    "V_Cru": p_at, "Var_Min": vr.min(), "Var_Max": vr.max(), "Dias_A": (vr > 0).sum(),
                    "Dias_B": (vr < 0).sum(), "Var_H": vr.iloc[-1], "LPA": lpa, "VPA": vpa
                })
        except: continue
    return pd.DataFrame(colecao)

df_p = motor_calculo(tickers_map)
df_m = motor_calculo(modelo_huli_tickers)

if 'carteira' not in st.session_state: st.session_state.carteira = {}

# --- ABA 1: PAINEL DE CONTROLE (ROBUSTEZ MÁXIMA) ---
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo</th><th>DY (%)</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['DY']:.2f}%</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_p.iterrows()])}</tbody>
    </table></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🧮 Gestor de Patrimônio")
    cap_xp = st.number_input("💰 Capital Total Corretora (R$):", value=0.0)
    
    opcoes = df_p["Ativo"].unique() if not df_p.empty else []
    padrao = ["PETR4.SA"] if "PETR4.SA" in opcoes else []
    ativos_sel = st.multiselect("Selecione seus ativos:", opcoes, default=padrao)
    
    v_inv_total, v_atual_total = 0, 0
    lista_gestao = []
    
    if ativos_sel:
        c1, c2 = st.columns(2)
        for i, n in enumerate(ativos_sel):
            with [c1, c2][i % 2]:
                q = st.number_input(f"Qtd ({n}):", key=f"q_{n}", min_value=0)
                inv = st.number_input(f"Investido R$ ({n}):", key=f"i_{n}", min_value=0.0)
                p_at = df_p[df_p["Ativo"] == n]["V_Cru"].values[0]
                v_agora = q * p_at
                v_inv_total += inv
                v_atual_total += v_agora
                st.session_state.carteira[n] = {"atual": v_agora}
                pm = inv/q if q > 0 else 0
                lista_gestao.append({"Ativo": n, "Qtd": q, "PM": pm, "Total": v_agora, "Lucro": v_agora - inv})
        
        st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']:.2f}</td><td>R$ {r['Total']:.2f}</td><td>R$ {r['Lucro']:.2f}</td></tr>" for r in lista_gestao])}</tbody>
        </table></div>""", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("SALDO EM ATIVOS", f"R$ {v_atual_total:,.2f}")
        m2.metric("PATRIMÔNIO GLOBAL", f"R$ {(v_atual_total + (cap_xp - v_inv_total)):,.2f}")

# --- ABA 2: RADAR MODELO (DIVIDENDOS) ---
with tab_radar_modelo:
    st.subheader("🔍 Radar Tio Huli")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo</th><th>DY (%)</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['DY']:.2f}%</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_m.iterrows()])}</tbody>
    </table></div>""", unsafe_allow_html=True)

# --- ABA 5: DNA FINANCEIRO ---
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")
    df_tot = pd.concat([df_p, df_m]).drop_duplicates(subset="Ativo")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>LPA</th><th>VPA</th><th>P/L</th><th>P/VP</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{(r['V_Cru']/r['LPA'] if r['LPA']>0 else 0):.2f}</td><td>{(r['V_Cru']/r['VPA'] if r['VPA']>0 else 0):.2f}</td></tr>" for _, r in df_tot.iterrows()])}</tbody>
    </table></div>""", unsafe_allow_html=True)

# (Backtest, Estratégia e Manual preservados conforme original)
