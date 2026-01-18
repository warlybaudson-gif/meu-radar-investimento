import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# Funções para Persistência de Dados
def salvar_dados_usuario(dados):
    with open("carteira_salva.json", "w") as f:
        json.dump(dados, f)

def carregar_dados_usuario():
    if os.path.exists("carteira_salva.json"):
        with open("carteira_salva.json", "r") as f:
            return json.load(f)
    return {}

dados_salvos = carregar_dados_usuario()

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; }
    .mobile-table-container { overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; }
    .rockefeller-table {
        width: 100%; border-collapse: collapse; font-family: 'Courier New', Courier, monospace;
        margin-bottom: 20px; font-size: 0.85rem;
    }
    .rockefeller-table th { background-color: #1a1a1a; color: #58a6ff !important; text-align: center; padding: 10px; border-bottom: 2px solid #333; }
    .rockefeller-table td { padding: 10px; text-align: center; border-bottom: 1px solid #222; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-radius: 8px; text-align: center; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli", "🧬 DNA Financeiro", "📈 Backtesting", "📖 Manual"
])

# --- PROCESSAMENTO DE DADOS ---
modelo_huli_tickers = {
    "TAESA": "TAEE11.SA", "ENGIE": "EGIE3.SA", "ALUPAR": "ALUP11.SA",
    "SANEPAR": "SAPR11.SA", "SABESP": "SBSP3.SA", "BANCO DO BRASIL": "BBAS3.SA",
    "ITAÚ": "ITUB4.SA", "BB SEGURIDADE": "BBSE3.SA", "HGLG11": "HGLG11.SA",
    "XPML11": "XPML11.SA", "IVVB11": "IVVB11.SA", "APPLE": "AAPL",
    "RENNER": "LREN3.SA", "GRENDENE": "GRND3.SA", "MATEUS": "GMAT3.SA", 
    "VISC11": "VISC11.SA", "MAGALU": "MGLU3.SA", "XPLG11": "XPLG11.SA",
    "MXRF11": "MXRF11.SA", "CPTS11": "CPTS11.SA", "VGHF11": "VGHF11.SA",
    "VIVA11": "VIVA11.SA", "KLBN4": "KLBN4.SA", "SAPR4": "SAPR4.SA", "GARE11": "GARE11.SA"
}

ativos_estrategicos = {
    "PETR4.SA": "PETR4.SA", "VALE3.SA": "VALE3.SA", "BTC-USD": "BTC-USD", 
    "Nvidia": "NVDA", "Jóias (Ouro)": "GC=F", "Câmbio USD/BRL": "USDBRL=X"
}

tickers_map = {**ativos_estrategicos, **modelo_huli_tickers}

def calcular_dados(lista):
    res = []
    try: cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except: cambio = 5.40
    
    for nome_ex, t in lista.items():
        try:
            ativo = yf.Ticker(t); hist = ativo.history(period="30d"); info = ativo.info
            if hist.empty: continue
            p_at = hist['Close'].iloc[-1]
            if t in ["NVDA", "AAPL", "BTC-USD"]: p_at *= cambio
            if t == "GC=F": p_at = (p_at / 31.1035) * cambio
            
            m_30 = hist['Close'].mean()
            if t in ["NVDA", "AAPL", "BTC-USD"]: m_30 *= cambio
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio
            
            lpa, vpa = info.get('trailingEps', 0), info.get('bookValue', 1)
            p_jus = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
            if t in ["NVDA", "AAPL"]: p_jus *= cambio
            
            dy = info.get('dividendYield', 0)
            status = "✅ DESCONTADO" if p_at < p_jus else "❌ SOBREPREÇO"
            acao = "✅ COMPRAR" if p_at < m_30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"
            
            var = hist['Close'].pct_change() * 100
            res.append({
                "Ativo": nome_ex, "Empresa": info.get('longName', nome_ex), "Preço": f"{p_at:.2f}",
                "Justo": f"{p_jus:.2f}", "DY": f"{(dy*100):.1f}%".replace('.',','), "Status M": status,
                "Ação": acao, "V_Cru": p_at, "Var_Min": var.min(), "Var_Max": var.max(),
                "Dias_A": (var > 0).sum(), "Dias_B": (var < 0).sum(), "Var_H": var.iloc[-1],
                "LPA": lpa, "VPA": vpa, "Ticker_Raw": t
            })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = df_radar[df_radar['Ativo'].isin(modelo_huli_tickers.keys())]

# --- ABA 1 ---
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_r = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Empresa</th><th>Ativo</th><th>Preço</th><th>Justo</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Empresa']}</td><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_r, unsafe_allow_html=True)

    st.subheader("🧮 Gestor de Carteira")
    cap_xp = st.number_input("Capital XP (R$):", value=dados_salvos.get("capital_xp", 0.0))
    sel = st.multiselect("Ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])
    
    v_total_at = 0
    df_graf = pd.DataFrame()
    if sel:
        c = st.columns(2)
        for i, n in enumerate(sel):
            with c[i % 2]:
                q = st.number_input(f"Qtd ({n}):", value=dados_salvos.get(f"q_{n}", 0), key=f"q_{n}")
                inv = st.number_input(f"Inv ({n}):", value=dados_salvos.get(f"i_{n}", 0.0), key=f"i_{n}")
                row = df_radar[df_radar["Ativo"] == n].iloc[0]
                v_total_at += (q * row["V_Cru"])
                if q > 0 and row["V_Cru"] < (inv/q):
                    st.warning(f"📉 Oportunidade em {n}!")
                df_graf[n] = yf.Ticker(row["Ticker_Raw"]).history(period="30d")['Close']
        
        st.line_chart(df_graf)
        if st.button("💾 Salvar"):
            d = {"capital_xp": cap_xp}
            for n in sel:
                d[f"q_{n}"] = st.session_state[f"q_{n}"]
                d[f"i_{n}"] = st.session_state[f"i_{n}"]
            salvar_dados_usuario(d); st.success("Salvo!")

# --- ABA 2 ---
with tab_radar_modelo:
    st.subheader("🔍 Radar Carteira Modelo")
    html_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço</th><th>Justo</th><th>DY</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['DY']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_m, unsafe_allow_html=True)

# --- ABA 3 ---
with tab_huli:
    st.header("🎯 Estratégia Huli")
    aporte = st.number_input("Aporte (R$):", value=500.0, key="ap_huli")
    df_compra = df_radar_modelo[df_radar_modelo['Ação'] == "✅ COMPRAR"].copy()
    if not df_compra.empty:
        renda_t = 0
        for _, r in df_compra.iterrows():
            pv = r['V_Cru']
            ct = int((aporte / len(df_compra)) // pv) if pv > 0 else 0
            renda_t += (ct * pv * (float(r['DY'].replace('%','').replace(',','.'))/1200))
        st.metric("Renda Mensal Est.", f"R$ {renda_t:.2f}")

# --- ABA 4 ---
with tab_modelo:
    st.header("🏦 Carteira Modelo")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("TAEE11, EGIE3, ALUP11, BBAS3, ITUB4")
    with c2:
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("BTC, NVDA, AAPL, MGLU3")

# --- ABA 5 ---
with tab_dna:
    st.header("🧬 DNA Financeiro")
    st.dataframe(df_radar[['Ativo', 'LPA', 'VPA']], use_container_width=True)

# --- ABA 6 ---
with tab_backtest:
    st.header("📈 Backtesting")
    if not df_radar.empty:
        at = st.selectbox("Ativo:", df_radar["Ativo"].unique(), key="bt_sel")
        d = df_radar[df_radar["Ativo"] == at].iloc[0]
        st.success(f"Lucro potencial no mês: {abs(d['Var_Min']):.2f}%")

# --- ABA 7 ---
with tab_manual:
    st.header("📖 Manual")
    st.write("Cálculos baseados em Graham e Médias de 30 dias.")
