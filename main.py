import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# --- FUNÇÕES DE MEMÓRIA (ADICIONADO) ---
DB_FILE = "data_rockefeller.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f:
        json.dump(dados, f)

# Inicializa memória na sessão
if 'storage' not in st.session_state:
    st.session_state.storage = carregar_dados()

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO
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

# ABAS
tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli", "🧬 DNA Financeiro", "📈 Backtesting", "📖 Manual de Instruções"
])

# --- PROCESSAMENTO ---
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
                
                # Resolução para o DNA
                net_income = info.get('netIncomeToCommon', 0)
                shares = info.get('sharesOutstanding', 1)
                equity = info.get('totalStockholderEquity', 0)
                
                f_lpa = f"{net_income:,.0f} / {shares:,.0f}" if net_income else "N/A"
                f_vpa = f"{equity:,.0f} / {shares:,.0f}" if equity else "N/A"

                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else p_atual
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_atual < p_justo else "⚠️ ESPERAR"
                
                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", "Justo": f"{p_justo:.2f}",
                    "Status M": status_m, "Ação": acao, "V_Cru": p_atual, "Var_Min": variacoes.min(),
                    "Var_Max": variacoes.max(), "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "LPA": lpa, "VPA": vpa, "F_LPA": f_lpa, "F_VPA": f_vpa
                })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = calcular_dados(modelo_huli_tickers)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)
    
    # ... (Resto do código do painel mantido conforme original)

# ==================== ABA 2: RADAR CARTEIRA MODELO (ADIÇÃO DE COLUNAS) ====================
with tab_radar_modelo:
    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    # ADICIONADO: Colunas LPA e VPA conforme o primeiro feedback
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>LPA</th><th>VPA</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)

    # Gestor com Memória
    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira: Ativos Modelo")
    
    # Recupera valores da memória
    saved_cap = st.session_state.storage.get("cap_modelo", 0.0)
    capital_xp_m = st.number_input("💰 Capital na Corretora (R$):", value=float(saved_cap), key="cap_huli")
    
    ativos_sel_m = st.multiselect("Habilite ativos:", df_radar_modelo["Ativo"].unique(), key="sel_huli")
    
    if st.button("💾 Salvar Dados da Carteira"):
        st.session_state.storage["cap_modelo"] = capital_xp_m
        salvar_dados(st.session_state.storage)
        st.success("Dados salvos com sucesso!")

# ==================== ABA 5: DNA FINANCEIRO (ADIÇÃO DA RESOLUÇÃO) ====================
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")
    df_combined = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
    
    # ADICIONADO: Resolução do cálculo (conta armada)
    html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>LPA</th><th>Resolução LPA (Lucro/Ações)</th><th>VPA</th><th>Resolução VPA (Patrim./Ações)</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
    for _, r in df_combined.iterrows():
        p_l = float(r['V_Cru']) / r['LPA'] if r['LPA'] > 0 else 0
        p_vp = float(r['V_Cru']) / r['VPA'] if r['VPA'] > 0 else 0
        html_dna += f"""<tr>
            <td>{r['Ativo']}</td>
            <td>{r['LPA']:.2f}</td>
            <td style='font-size: 0.7rem; color: #888;'>{r['F_LPA']}</td>
            <td>{r['VPA']:.2f}</td>
            <td style='font-size: 0.7rem; color: #888;'>{r['F_VPA']}</td>
            <td>{p_l:.2f}</td>
            <td>{p_vp:.2f}</td>
        </tr>"""
    html_dna += "</tbody></table></div>"
    st.markdown(html_dna, unsafe_allow_html=True)

# ... (As demais abas: Estratégia, Modelo Huli, Backtest e Manual permanecem IGUAIS ao original)
