import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# --- PERSISTÊNCIA DE DADOS ---
def salvar_dados_usuario(dados):
    with open("carteira_salva.json", "w") as f:
        json.dump(dados, f)

def carregar_dados_usuario():
    if os.path.exists("carteira_salva.json"):
        with open("carteira_salva.json", "r") as f:
            return json.load(f)
    return {}

dados_salvos = carregar_dados_usuario()

# --- CONFIGURAÇÕES E ESTILO ---
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

tab_painel, tab_radar_m, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli", "🧬 DNA Financeiro", "📈 Backtesting", "📖 Manual"
])

# --- TICKERS ---
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

# --- CÁLCULO ---
def calcular_dados(lista):
    res = []
    try: cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except: cambio = 5.40
    for nome_ex, t in lista.items():
        try:
            ativo = yf.Ticker(t); hist = ativo.history(period="30d"); info = ativo.info
            if hist.empty: continue
            p_atual = hist['Close'].iloc[-1]
            if t in ["NVDA", "AAPL", "BTC-USD"]: p_atual *= cambio
            if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio
            m_30 = hist['Close'].mean()
            if t in ["NVDA", "AAPL", "BTC-USD"]: m_30 *= cambio
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio
            lpa, vpa = info.get('trailingEps', 0), info.get('bookValue', 0)
            p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
            if t in ["NVDA", "AAPL"]: p_justo *= cambio
            dy = info.get('dividendYield', 0)
            status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
            variacoes = hist['Close'].pct_change() * 100
            acao = "✅ COMPRAR" if p_atual < p_justo and p_atual < m_30 else "⚠️ ESPERAR"
            res.append({
                "Ativo": nome_ex, "Empresa": info.get('longName', nome_ex), "Preço": f"{p_atual:.2f}",
                "Justo": f"{p_justo:.2f}", "DY": f"{(dy*100):.1f}%".replace('.',','), "Status M": status_m, "Ação": acao,
                "V_Cru": p_atual, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(), 
                "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                "Var_H": variacoes.iloc[-1], "LPA": lpa, "VPA": vpa, "Ticker_Raw": t
            })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = df_radar[df_radar['Ativo'].isin(modelo_huli_tickers.keys())]

# --- ABA 1 ---
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Empresa</th><th>Ativo</th><th>Preço</th><th>Justo</th><th>DY</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Empresa']}</td><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['DY']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)

    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    st.subheader("🧮 Gestor de Carteira Dinâmica")
    capital_xp = st.number_input("💰 Capital na XP (R$):", min_value=0.0, value=dados_salvos.get("capital_xp", 0.0))
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=[])
    
    v_ativos_atualizado = 0
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                q_salva = dados_salvos.get(f"q_{nome}", 0)
                i_salva = dados_salvos.get(f"i_{nome}", 0.0)
                qtd = st.number_input(f"Qtd ({nome}):", min_value=0, value=q_salva, key=f"q_{nome}")
                inv = st.number_input(f"Investido ({nome}):", min_value=0.0, value=i_salva, key=f"i_{nome}")
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                v_ativos_atualizado += (qtd * info["V_Cru"])
                if qtd > 0 and info["V_Cru"] < (inv/qtd):
                    st.warning(f"📉 Oportunidade em {nome}: Abaixo do seu PM!")

    if st.button("💾 Salvar Carteira"):
        d_salvar = {"capital_xp": capital_xp}
        for n in ativos_sel:
            d_salvar[f"q_{n}"] = st.session_state[f"q_{n}"]
            d_salvar[f"i_{n}"] = st.session_state[f"i_{n}"]
        salvar_dados_usuario(d_salvar)
        st.success("✅ Salvo!")

# --- ABA 3 ---
with tab_huli:
    st.header("🎯 Estratégia Huli")
    v_aporte = st.number_input("Aporte (R$):", min_value=0.0, step=100.0, key="ap_huli")
    df_prio = df_radar_modelo[df_radar_modelo['Ação'] == "✅ COMPRAR"].copy()
    if not df_prio.empty:
        total_renda = 0
        for _, r in df_prio.iterrows():
            p = r['V_Cru']
            ct = int((v_aporte / len(df_prio)) // p) if p > 0 else 0
            dy = float(r['DY'].replace('%','').replace(',','.'))/100
            total_renda += (ct * p * (dy/12))
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1: st.metric("Investimento", f"R$ {v_aporte:,.2f}")
        with c2: st.metric("Renda Mensal Est.", f"R$ {total_renda:.2f}")
        if st.button("💾 Salvar Plano"): st.success("✅ Plano salvo!")

# --- ABA 4 ---
with tab_modelo:
    st.header("🏦 Onde o Tio Huli Investe")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11, EGIE3, ALUP11 | **• Bancos:** BBAS3, ITUB4")
        st.markdown('<div class="huli-category"><b>🏢 Fundos Imobiliários</b></div>', unsafe_allow_html=True)
        st.write("**• Logística:** HGLG11, XPLG11 | **• Shoppings:** XPML11, VISC11")
    with c2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda</b></div>', unsafe_allow_html=True)
        st.write("**• Ouro:** GC=F | **• Dólar:** IVVB11 (S&P 500)")
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("**• Tech:** NVDA, AAPL | **• Cripto:** Bitcoin (BTC)")

# --- ABA 5/6/7 ---
with tab_dna:
    st.header("🧬 DNA Financeiro")
    st.dataframe(df_radar[['Ativo', 'Empresa', 'LPA', 'VPA']], use_container_width=True)

with tab_backtest:
    st.header("📈 Backtesting")
    st.write("Simulação de rendimento baseada no fundo mensal.")

with tab_manual:
    st.header("📖 Manual")
    st.markdown("* **Justo:** Preço de Graham. * **Ação:** Baseada em preço < justo e média.")
