import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Tenta importar o Plotly para o gráfico de Margem de Segurança
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO (MANUTENÇÃO INTEGRAL)
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

# CRIAÇÃO DAS ABAS (INTEGRANDO TODAS AS FUNÇÕES)
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
    cambio_hoje = 5.50

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
                # Ajuste de escala para ativos dolarizados
                lpa_aj = lpa * cambio_hoje if t in ["NVDA", "AAPL"] else lpa
                vpa_aj = vpa * cambio_hoje if t in ["NVDA", "AAPL"] else vpa
                
                p_justo = np.sqrt(22.5 * lpa_aj * vpa_aj) if lpa_aj > 0 and vpa_aj > 0 else m_30
                
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_atual < m_30 and status_m == "✅ DESCONTADO" else "⚠️ ESPERAR"
                
                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": p_atual, "Justo": p_justo,
                    "Status M": status_m, "Ação": acao, "V_Cru": p_atual, "Var_Min": variacoes.min(),
                    "Var_Max": variacoes.max(), "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "Var_H": variacoes.iloc[-1], "LPA": lpa_aj, "VPA": vpa_aj
                })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = calcular_dados(modelo_huli_tickers)

if 'carteira' not in st.session_state: st.session_state.carteira = {}
if 'carteira_modelo' not in st.session_state: st.session_state.carteira_modelo = {}

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)
    
    if HAS_PLOTLY:
        st.subheader("📉 Margem de Segurança (Graham vs Atual)")
        fig = go.Figure(data=[
            go.Bar(name='Preço Mercado', x=df_radar['Ativo'], y=df_radar['Preço'], marker_color='#58a6ff'),
            go.Bar(name='Preço Justo', x=df_radar['Ativo'], y=df_radar['Justo'], marker_color='#238636')
        ])
        fig.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=0.0)
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])
    
    total_investido_acumulado, v_ativos_atualizado = 0, 0
    lista_c = []
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                qtd = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, key=f"i_{nome}")
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                p_atual = info["V_Cru"]
                v_agora = qtd * p_atual
                total_investido_acumulado += investido
                v_ativos_atualizado += v_agora
                st.session_state.carteira[nome] = {"atual": v_agora}
                lista_c.append({"Ativo": nome, "Qtd": qtd, "Total": v_agora, "Lucro": v_agora - investido})
        
        tr_xp = capital_xp - total_investido_acumulado
        st.subheader("💰 Patrimônio Global")
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (XP) + Bens", f"R$ {tr_xp:,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {(v_ativos_atualizado + tr_xp):,.2f}")

# ==================== ABA 2: RADAR CARTEIRA MODELO ====================
with tab_radar_modelo:
    st.subheader("🔍 Radar Tio Huli")
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)

    st.subheader("🧮 Gestor de Carteira Modelo")
    cap_m = st.number_input("Capital para Modelo (R$):", value=0.0, key="cap_m")
    sel_m = st.multiselect("Ativos Modelo:", df_radar_modelo["Ativo"].unique(), key="sel_m")
    
    v_total_m = 0
    if sel_m:
        for n_m in sel_m:
            q_m = st.number_input(f"Qtd ({n_m}):", key=f"qm_{n_m}")
            p_m = df_radar_modelo[df_radar_modelo["Ativo"] == n_m]["V_Cru"].values[0]
            v_total_m += (q_m * p_m)
            st.session_state.carteira_modelo[n_m] = {"atual": q_m * p_m}
        st.metric("Total em Ativos Modelo", f"R$ {v_total_m:,.2f}")

# ==================== ABA 3: ESTRATÉGIA HULI ====================
with tab_huli:
    st.header("🎯 Plano de Aporte")
    valor_aporte = st.number_input("Valor do Aporte Mensal (R$):", value=0.0)
    if ativos_sel:
        plano = []
        for nome in ativos_sel:
            v_at = st.session_state.carteira[nome]["atual"] if nome in st.session_state.carteira else 0
            v_id = (v_ativos_atualizado + valor_aporte) / len(ativos_sel)
            nec = v_id - v_at
            plano.append({"Ativo": nome, "Ação": "APORTAR" if nec > 0 else "OK", "Valor": f"R$ {max(0, nec):.2f}"})
        st.table(pd.DataFrame(plano))

# ==================== ABA 4: CARTEIRA MODELO HULI ====================
with tab_modelo:
    st.header("🏦 Composição Estratégica Huli")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b><br>Renda Passiva: TAEE11, EGIE3, BBAS3, ITUB4</div>', unsafe_allow_html=True)
        st.markdown('<div class="huli-category"><b>🏢 FIIs</b><br>HGLG11, XPML11, XPLG11</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda</b><br>Segurança: Ouro e IVVB11</div>', unsafe_allow_html=True)
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b><br>Crescimento: BTC, NVDA, AAPL</div>', unsafe_allow_html=True)

# ==================== ABA 5: DNA FINANCEIRO ====================
with tab_dna:
    st.header("🧬 DNA: LPA e VPA")
    df_combined = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
    html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>LPA</th><th>VPA</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
    for _, r in df_combined.iterrows():
        p_l = r['Preço'] / r['LPA'] if r['LPA'] > 0 else 0
        p_vp = r['Preço'] / r['VPA'] if r['VPA'] > 0 else 0
        html_dna += f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{p_l:.2f}</td><td>{p_vp:.2f}</td></tr>"
    st.markdown(html_dna + "</tbody></table></div>", unsafe_allow_html=True)

# ==================== ABA 6: BACKTESTING ====================
with tab_backtest:
    st.header("📈 Backtesting de Oportunidade")
    if not df_radar.empty:
        ativo_bt = st.selectbox("Simular 'Efeito Pânico' em:", df_radar["Ativo"].unique())
        d = df_radar[df_radar["Ativo"] == ativo_bt].iloc[0]
        queda_max = abs(d["Var_Min"])
        st.success(f"📌 Se você comprasse **{ativo_bt}** no fundo deste mês, seu lucro seria de **{queda_max:.2f}%** hoje.")

# ==================== ABA 7: MANUAL ====================
with tab_manual:
    st.header("📖 Guia Rockefeller")
    st.write("Fórmula de Graham: sqrt(22.5 * LPA * VPA)")
    st.write("Ação COMPRAR: Ativo abaixo da média 30d E abaixo do Preço Justo.")
