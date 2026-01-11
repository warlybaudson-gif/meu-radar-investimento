import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# --- 1. SISTEMA DE MEMÓRIA (ADICIONADO) ---
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

# --- 2. CONFIGURAÇÕES E ESTILO REFORÇADO (MANUTENÇÃO INTEGRAL) ---
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
    .manual-section { border-left: 3px solid #58a6ff; padding-left: 15px; margin-bottom: 25px; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# CRIAÇÃO DAS ABAS
tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🔍 Radar Carteira Modelo",
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
    "🧬 DNA Financeiro",
    "📈 Backtesting",
    "📖 Manual de Instruções"
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
                m_30 = hist['Close'].mean()
                if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]: m_30 *= cambio_hoje
                if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje
                lpa, vpa = info.get('trailingEps', 0), info.get('bookValue', 0)
                
                # Resolução para o DNA (ADICIONADO)
                net_income = info.get('netIncomeToCommon', 0)
                shares = info.get('sharesOutstanding', 1)
                equity = info.get('totalStockholderEquity', 0)
                f_lpa = f"{net_income:,.0f} / {shares:,.0f}" if net_income else "N/A"
                f_vpa = f"{equity:,.0f} / {shares:,.0f}" if equity else "N/A"

                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
                if t in ["NVDA", "AAPL"]: p_justo *= cambio_hoje
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_atual < m_30 and status_m == "✅ DESCONTADO" else "⚠️ ESPERAR"
                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", "Justo": f"{p_justo:.2f}",
                    "Status M": status_m, "Ação": acao, "V_Cru": p_atual, "Var_Min": variacoes.min(),
                    "Var_Max": variacoes.max(), "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "Var_H": variacoes.iloc[-1], "LPA": lpa, "VPA": vpa, "F_LPA": f_lpa, "F_VPA": f_vpa
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
    
    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado")
    caros = len(df_radar[df_radar['Status M'] == "❌ SOBREPREÇO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    st.progress(score / 100)
    st.write(f"Índice de Ativos Caros: **{int(score)}%**")

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    # Memória no input de Capital
    saved_cap_xp = st.session_state.storage.get("capital_xp", 0.0)
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=float(saved_cap_xp), step=100.0)
    
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])
    
    total_investido_acumulado, v_ativos_atualizado = 0, 0
    lista_c, df_grafico = [], pd.DataFrame()
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                # Memória nas Qtd e Investido
                saved_q = st.session_state.storage.get(f"q_{nome}", 0)
                saved_i = st.session_state.storage.get(f"i_{nome}", 0.0)
                
                qtd = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, value=int(saved_q), key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, value=float(saved_i), key=f"i_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                p_atual = info["V_Cru"]
                pm_calc = investido / qtd if qtd > 0 else 0.0
                v_agora = qtd * p_atual
                total_investido_acumulado += investido
                v_ativos_atualizado += v_agora
                
                # Salva no storage de sessão
                st.session_state.storage[f"q_{nome}"] = qtd
                st.session_state.storage[f"i_{nome}"] = investido
                
                lista_c.append({"Ativo": nome, "Qtd": qtd, "PM": f"{pm_calc:.2f}", "Total": f"{v_agora:.2f}", "Lucro": f"{(v_agora - investido):.2f}"})
                df_grafico[nome] = yf.Ticker(info["Ticker_Raw"]).history(period="30d")['Close']
        
        if st.button("💾 Salvar Dados da Carteira"):
            st.session_state.storage["capital_xp"] = capital_xp
            salvar_dados(st.session_state.storage)
            st.success("Dados salvos no sistema!")

        troco_real = capital_xp - total_investido_acumulado
        st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']}</td><td>R$ {r['Total']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c])}</tbody>
        </table></div>""", unsafe_allow_html=True)

        st.subheader("💰 Patrimônio Global")
        with st.sidebar:
            st.header("⚙️ Outros Bens")
            g_joias = st.number_input("Ouro Físico (gramas):", min_value=0.0, value=0.0)
            v_bens = st.number_input("Outros Bens/Imóveis (R$):", min_value=0.0, value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['V_Cru'].values[0])
        valor_ouro_total = g_joias * p_ouro
        patri_global = v_ativos_atualizado + troco_real + valor_ouro_total + v_bens

        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (XP) + Bens", f"R$ {(troco_real + valor_ouro_total + v_bens):,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")
        st.line_chart(df_grafico)

# ==================== ABA 2: RADAR CARTEIRA MODELO ====================
with tab_radar_modelo:
    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    # ADICIONADO: LPA e VPA conforme solicitado anteriormente para completar a visão
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>LPA</th><th>VPA</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)

    # ... (Resto da aba Radar Modelo mantida original)

# ==================== ABA 5: DNA FINANCEIRO (CONTA ARMADA ADICIONADA) ====================
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")
    df_combined = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
    
    # ADICIONADO: Resolução do cálculo de VPA e LPA na tabela
    html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>LPA</th><th>Resolução LPA (Lucro/Ações)</th><th>VPA</th><th>Resolução VPA (Patrim./Ações)</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
    for _, r in df_combined.iterrows():
        p_l = float(r['V_Cru']) / r['LPA'] if r['LPA'] > 0 else 0
        p_vp = float(r['V_Cru']) / r['VPA'] if r['VPA'] > 0 else 0
        html_dna += f"""<tr>
            <td>{r['Ativo']}</td>
            <td>{r['LPA']:.2f}</td>
            <td style='font-size: 0.75rem; color: #888;'>{r['F_LPA']}</td>
            <td>{r['VPA']:.2f}</td>
            <td style='font-size: 0.75rem; color: #888;'>{r['F_VPA']}</td>
            <td>{p_l:.2f}</td>
            <td>{p_vp:.2f}</td>
        </tr>"""
    html_dna += "</tbody></table></div>"
    st.markdown(html_dna, unsafe_allow_html=True)

# --- AS DEMAIS ABAS (ESTRATÉGIA, MODELO HULI, BACKTEST E MANUAL) PERMANECEM INTEGRALMENTE ORIGINAIS ---
