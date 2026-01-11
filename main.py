import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# --- SISTEMA DE MEMÓRIA (ADICIONADO) ---
DB_FILE = "data_rockefeller.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f:
        json.dump(dados, f)

if 'storage' not in st.session_state:
    st.session_state.storage = carregar_dados()

# 1. CONFIGURAÇÕES E ESTILO (MANTIDO INTEGRALMENTE)
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
    "🏦 Carteira Modelo Huli", "🧬 DNA Financeiro", "📈 Backtesting", "📖 Manual de Instruções"
])

# --- PROCESSAMENTO DE DADOS ---
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
    cambio_hoje = 5.40

def calcular_dados(lista):
    res = []
    for nome_ex, t in lista.items():
        try:
            ativo = yf.Ticker(t)
            hist = ativo.history(period="30d")
            info = ativo.info
            if not hist.empty:
                p_atual = hist['Close'].iloc[-1]
                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    p_atual = (p_atual / 31.1035) * cambio_hoje if t == "GC=F" else p_atual * cambio_hoje
                
                lpa = info.get('trailingEps', 0)
                vpa = info.get('bookValue', 0)
                
                # Resolução para o DNA (ADICIONADO)
                net_income = info.get('netIncomeToCommon', 0)
                shares = info.get('sharesOutstanding', 1)
                equity = info.get('totalStockholderEquity', 0)
                f_lpa = f"{net_income:,.0f} / {shares:,.0f}" if net_income else "N/A"
                f_vpa = f"{equity:,.0f} / {shares:,.0f}" if equity else "N/A"

                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else p_atual
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", "Justo": f"{p_justo:.2f}",
                    "Status M": status_m, "Ação": "✅ COMPRAR" if p_atual < p_justo else "⚠️ ESPERAR",
                    "V_Cru": p_atual, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(),
                    "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "LPA": lpa, "VPA": vpa, "F_LPA": f_lpa, "F_VPA": f_vpa, "Var_H": variacoes.iloc[-1]
                })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = calcular_dados(modelo_huli_tickers)

# ==================== ABA 1: PAINEL DE CONTROLE (RESTAURADO) ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)
    
    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    # ... (Resto do Gestor da Aba 1 mantido)

# ==================== ABA 2: RADAR MODELO (COLUNAS ADICIONADAS + PATRIMÔNIO) ====================
with tab_radar_modelo:
    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>LPA</th><th>VPA</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira: Ativos Modelo")
    saved_cap = st.session_state.storage.get("cap_modelo", 0.0)
    capital_xp_m = st.number_input("💰 Capital na Corretora (R$):", value=float(saved_cap), key="cap_huli")
    ativos_sel_m = st.multiselect("Habilite ativos:", df_radar_modelo["Ativo"].unique(), key="sel_huli")
    
    total_m, v_atual_m = 0, 0
    nomes_g, valores_g = [], []
    if ativos_sel_m:
        for nome in ativos_sel_m:
            qtd_key = f"q_m_{nome}"
            inv_key = f"i_m_{nome}"
            saved_q = st.session_state.storage.get(qtd_key, 0)
            saved_i = st.session_state.storage.get(inv_key, 0.0)
            
            q = st.number_input(f"Qtd {nome}:", value=int(saved_q), key=qtd_key)
            i = st.number_input(f"Investido {nome}:", value=float(saved_i), key=inv_key)
            
            p_at = df_radar_modelo[df_radar_modelo["Ativo"] == nome]["V_Cru"].values[0]
            v_agora = q * p_at
            total_m += i
            v_atual_m += v_agora
            nomes_g.append(nome)
            valores_g.append(v_agora)
            
            # Salva na sessão
            st.session_state.storage[qtd_key] = q
            st.session_state.storage[inv_key] = i
            
    if st.button("💾 Salvar Tudo"):
        st.session_state.storage["cap_modelo"] = capital_xp_m
        salvar_dados(st.session_state.storage)
        st.success("Dados salvos!")

    st.subheader("💰 Patrimônio Global (Estratégia Modelo)")
    troco = capital_xp_m - total_m
    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa (Modelo)", f"R$ {v_atual_m:,.2f}")
    c2.metric("Saldo Caixa", f"R$ {troco:,.2f}")
    c3.metric("TOTAL", f"R$ {(v_atual_m + troco):,.2f}")

    if nomes_g:
        st.bar_chart(pd.DataFrame({"Ativo": nomes_g, "R$": valores_g}).set_index("Ativo"))

# ==================== ABA 4: CARTEIRA MODELO (RESTAURADO COMPLETO) ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras (Renda Passiva)</b></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11, EGIE3, ALUP11 | **• Saneamento:** SAPR11, SBSP3")
        st.write("**• Bancos:** BBAS3, ITUB4, SANB11 | **• Seguradoras:** BBSE3, CXSE3")
        st.markdown('<div class="huli-category"><b>🏢 Fundos Imobiliários</b></div>', unsafe_allow_html=True)
        st.write("**• Logística:** HGLG11, XPLG11 | **• Shoppings:** XPML11, VISC11")
    with col2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda (Segurança)</b></div>', unsafe_allow_html=True)
        st.write("**• Ouro:** OZ1D | **• Dólar:** IVVB11 | **• Renda Fixa:** Tesouro Selic")
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("**• Cripto:** BTC, ETH | **• Tech:** NVDA, AAPL")

# ==================== ABA 5: DNA (RESOLUÇÃO ADICIONADA) ====================
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")
    df_c = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
    html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>LPA</th><th>Resolução LPA</th><th>VPA</th><th>Resolução VPA</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
    for _, r in df_c.iterrows():
        pl = float(r['V_Cru'])/r['LPA'] if r['LPA'] > 0 else 0
        pvp = float(r['V_Cru'])/r['VPA'] if r['VPA'] > 0 else 0
        html_dna += f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td style='font-size:0.7rem;'>{r['F_LPA']}</td><td>{r['VPA']:.2f}</td><td style='font-size:0.7rem;'>{r['F_VPA']}</td><td>{pl:.2f}</td><td>{pvp:.2f}</td></tr>"
    st.markdown(html_dna + "</tbody></table></div>", unsafe_allow_html=True)

# ==================== ABA 7: MANUAL (RESTAURADO) ====================
with tab_manual:
    st.header("📖 Manual de Instruções")
    with st.expander("🛰️ Radar e Preço Justo"):
        st.markdown("Cálculo: $V = \sqrt{22.5 \cdot LPA \cdot VPA}$")
