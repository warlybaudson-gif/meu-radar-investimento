import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# ==================== 1. SISTEMA DE MEMÓRIA (Salvamento Real) ====================
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
if 'carteira' not in st.session_state:
    st.session_state.carteira = st.session_state.storage.get("carteira", {})

# ==================== 2. CONFIGURAÇÕES E ESTILO ====================
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

# ==================== 3. PROCESSAMENTO DE DADOS (Lógica Central) ====================
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
                
                lpa, vpa = info.get('trailingEps', 0), info.get('bookValue', 0)
                dy = info.get('dividendYield', 0)
                
                # Dados brutos para conta armada no DNA
                lucro = info.get('netIncomeToCommon', 0)
                patri = info.get('totalStockholderEquity', 0)
                acoes = info.get('sharesOutstanding', 1)

                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
                if t in ["NVDA", "AAPL"]: p_justo *= cambio_hoje
                
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                
                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", "Justo": f"{p_justo:.2f}",
                    "Status M": status_m, "Ação": "✅ COMPRAR" if p_atual < p_justo else "⚠️ ESPERAR",
                    "V_Cru": p_atual, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(),
                    "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "Var_H": variacoes.iloc[-1], "LPA": lpa, "VPA": vpa, "DY": f"{dy*100:.2f}%",
                    "L_Bruto": lucro, "P_Bruto": patri, "Q_Acoes": acoes
                })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = calcular_dados(modelo_huli_tickers)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Dividendos (DY)</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td style='color:#00ff00'>{r['DY']}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)
    
    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    capital_xp = st.number_input("💰 Capital Total XP (R$):", value=float(st.session_state.storage.get("capital_xp", 0.0)))
    
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])
    total_investido_acumulado, v_ativos_atualizado, lista_c, df_grafico = 0, 0, [], pd.DataFrame()

    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                saved_at = st.session_state.carteira.get(nome, {"q": 0, "i": 0.0})
                qtd = st.number_input(f"Qtd ({nome}):", value=int(saved_at["q"]), key=f"q_{nome}")
                inv = st.number_input(f"Investido R$ ({nome}):", value=float(saved_at["i"]), key=f"i_{nome}")
                st.session_state.carteira[nome] = {"q": qtd, "i": inv}
                p_atual = df_radar[df_radar["Ativo"] == nome].iloc[0]["V_Cru"]
                v_agora = qtd * p_atual
                total_investido_acumulado += inv
                v_ativos_atualizado += v_agora
                lista_c.append({"Ativo": nome, "Qtd": qtd, "PM": inv/qtd if qtd>0 else 0, "Total": v_agora, "Lucro": v_agora-inv})
                df_grafico[nome] = yf.Ticker(df_radar[df_radar["Ativo"] == nome].iloc[0]["Ticker_Raw"]).history(period="30d")['Close']

    if st.button("💾 Salvar Dados da Carteira"):
        st.session_state.storage["capital_xp"] = capital_xp
        st.session_state.storage["carteira"] = st.session_state.carteira
        salvar_dados(st.session_state.storage)
        st.success("Tudo salvo!")

    if not df_grafico.empty:
        st.subheader("📈 Comparativo 30 dias")
        st.line_chart(df_grafico)

# ==================== ABA 2: RADAR CARTEIRA MODELO ====================
with tab_radar_modelo:
    st.subheader("🔍 Radar: Carteira Modelo Tio Huli")
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço</th><th>Dividendos (DY)</th><th>LPA</th><th>VPA</th><th>Preço Justo</th><th>Status</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td style='color:#00ff00'>{r['DY']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{r['Justo']}</td><td>{r['Status M']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)

# ==================== ABA 3: ESTRATÉGIA HULI ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli")
    valor_aporte = st.number_input("Quanto pretende investir hoje? (R$):", min_value=0.0)
    if ativos_sel:
        st.write("Defina seu peso ideal (%) para cada ativo selecionado:")
        metas = {n: st.slider(f"{n} (%)", 0, 100, 100//len(ativos_sel)) for n in ativos_sel}
        if sum(metas.values()) == 100:
            for n in ativos_sel:
                v_id = (v_ativos_atualizado + valor_aporte) * (metas[n]/100)
                nec = v_id - (st.session_state.carteira[n]['q'] * df_radar[df_radar['Ativo']==n]['V_Cru'].iloc[0])
                st.write(f"➡️ **{n}**: {'Aportar R$ ' + str(round(nec,2)) if nec > 0 else 'Já atingiu a meta'}")

# ==================== ABA 4: CARTEIRA MODELO HULI ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b><br><small>Foco em Dividendos</small></div>', unsafe_allow_html=True)
        st.write("TAEE11, EGIE3, ALUP11 (Energia) | SAPR11, SBSP3 (Saneamento) | BBAS3, ITUB4 (Bancos)")
    with col2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda</b><br><small>Segurança e Reserva</small></div>', unsafe_allow_html=True)
        st.write("Ouro (OZ1D), Dólar (IVVB11), Tesouro Selic")

# ==================== ABA 5: DNA FINANCEIRO (COM RESOLUÇÃO) ====================
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")
    df_combined = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
    html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dividendos (DY)</th><th>LPA</th><th>Resolução LPA</th><th>VPA</th><th>Resolução VPA</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
    for _, r in df_combined.iterrows():
        res_lpa = f"{r['L_Bruto']:,.0f}/{r['Q_Acoes']:,.0f}" if r['L_Bruto'] else "N/A"
        res_vpa = f"{r['P_Bruto']:,.0f}/{r['Q_Acoes']:,.0f}" if r['P_Bruto'] else "N/A"
        pl = float(r['Preço'])/r['LPA'] if r['LPA']>0 else 0
        pvp = float(r['Preço'])/r['VPA'] if r['VPA']>0 else 0
        html_dna += f"<tr><td>{r['Ativo']}</td><td style='color:#00ff00'>{r['DY']}</td><td>{r['LPA']:.2f}</td><td style='font-size:0.7rem;color:#888'>{res_lpa}</td><td>{r['VPA']:.2f}</td><td style='font-size:0.7rem;color:#888'>{res_vpa}</td><td>{pl:.2f}</td><td>{pvp:.2f}</td></tr>"
    st.markdown(html_dna + "</tbody></table></div>", unsafe_allow_html=True)

# ==================== ABA 7: MANUAL ====================
with tab_manual:
    st.header("📖 Manual de Instruções")
    with st.expander("Fórmula de Graham"):
        st.write("Usamos $V = \sqrt{22.5 \cdot LPA \cdot VPA}$ para ativos de valor.")
