import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Tenta importar o Plotly para o gráfico
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. ESTILO E CONFIGURAÇÃO
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
    "📊 Painel de Controle", "🔍 Radar Carteira Modelo", "🧬 DNA (LPA/VPA)", 
    "🎯 Estratégia Huli", "🏦 Carteira Modelo Huli", "📖 Manual de Instruções"
])

# 3. MAPEAMENTO (RESTABELECIDO)
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

def motor_principal(lista):
    dados = []
    for nome, t in lista.items():
        try:
            a = yf.Ticker(t)
            h = a.history(period="30d")
            inf = a.info
            if not h.empty:
                p_r = h['Close'].iloc[-1]
                # Conversões de Câmbio e Ouro
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
                
                dados.append({
                    "Ativo": nome, "Preço": p_at, "Justo": pj, "LPA": lpa_f, "VPA": vpa_f,
                    "Status": status, "Ação": acao, "Var_Min": vr.min(), "Var_Max": vr.max(),
                    "Dias_A": (vr > 0).sum(), "Dias_B": (vr < 0).sum(), "Var_H": vr.iloc[-1]
                })
        except: continue
    return pd.DataFrame(dados)

df_p = motor_principal(tickers_map)
df_m = motor_principal(modelo_huli_tickers)
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

    st.subheader("🧮 Gestor de Carteira Dinâmica")
    cap_xp_total = st.number_input("💰 Capital Total na XP (R$):", value=0.0)
    ativos_sel = st.multiselect("Habilite ativos:", df_p["Ativo"].unique(), default=["PETR4.SA"])
    
    v_total_inv, v_bolsa_agora = 0, 0
    if ativos_sel:
        c1, c2 = st.columns(2)
        for i, n in enumerate(ativos_sel):
            with [c1, c2][i % 2]:
                qh = st.number_input(f"Qtd ({n}):", key=f"qh_{n}")
                ih = st.number_input(f"Investido R$ ({n}):", key=f"ih_{n}")
                pm = df_p[df_p["Ativo"] == n]["Preço"].values[0]
                va = qh * pm
                v_bolsa_agora += va
                v_total_inv += ih
                st.session_state.carteira[n] = {"atual": va}
        
        tr_xp = cap_xp_total - v_total_inv
        po = df_p[df_p["Ativo"] == "Jóias (Ouro)"]["Preço"].values[0]
        patri_glob = v_bolsa_agora + tr_xp + (g_ouro * po) + v_bens_imoveis
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa & Cripto", f"R$ {v_bolsa_agora:,.2f}")
        m2.metric("Troco, Ouro & Bens", f"R$ {(tr_xp + (g_ouro * po) + v_bens_imoveis):,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_glob:,.2f}")

# --- ABA 3: DNA (LPA/VPA) ---
with tab_dna:
    st.subheader("🧬 DNA Financeiro: LPA e VPA em Tempo Real")
    df_tot = pd.concat([df_p, df_m]).drop_duplicates(subset="Ativo")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>LPA</th><th>VPA</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{(r['Preço']/r['LPA'] if r['LPA']>0 else 0):.2f}</td><td>{(r['Preço']/r['VPA'] if r['VPA']>0 else 0):.2f}</td></tr>" for _, r in df_tot.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# --- ABA 4: ESTRATÉGIA + SOBREVIVÊNCIA + BACKTESTING ---
with tab_huli:
    st.header("🎯 Estratégia Tio Huli & Rebalanceamento")
    aporte_dia = st.number_input("Aporte planejado (R$):", value=0.0)
    if ativos_sel:
        metas_h = {n: st.slider(f"Meta % {n}", 0, 100, 100//len(ativos_sel), key=f"mh_{n}") for n in ativos_sel}
        if sum(metas_h.values()) == 100:
            plano = []
            for n in ativos_sel:
                va_h = st.session_state.carteira[n]["atual"]
                vid = (v_bolsa_agora + aporte_dia) * (metas_h[n]/100)
                plano.append({"Ativo": n, "Ação": "✅ APORTAR" if vid > va_h else "✋ AGUARDAR", "Valor": f"R$ {max(0, vid-va_h):.2f}"})
            st.table(pd.DataFrame(plano))
    
    st.markdown("---")
    st.subheader("🏁 Meta de Sobrevivência (Independência Financeira)")
    custo_v = st.number_input("Custo Mensal (R$):", value=3000.0)
    renda_p = st.slider("Rendimento Mensal (%)", 0.1, 2.0, 0.8)
    pat_a = custo_v / (renda_p / 100)
    st.metric("Patrimônio Alvo", f"R$ {pat_a:,.2f}")
    st.progress(min((patri_glob/pat_a if pat_a > 0 else 0), 1.0))

    st.subheader("📈 Backtesting de Eficácia")
    at_f = st.selectbox("Simular Ativo:", df_p["Ativo"].unique())
    d_f = df_p[df_p["Ativo"] == at_f].iloc[0]
    p_fundo = d_f['Preço'] * (1 - (abs(d_f['Var_Min'])/100))
    st.success(f"**Eficácia {at_f}:** Preço Atual: R$ {d_f['Preço']:.2f} | Fundo do Mês: R$ {p_fundo:.2f} | Ganho Potencial: {abs(d_f['Var_Min']):.2f}%")

# --- ABA 5: CARTEIRA MODELO (TEXTOS COMPLETOS) ---
with tab_modelo:
    st.header("🏦 Carteira Modelo Huli (Onde o Dinheiro Cresce)")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras (Renda Passiva)</b></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11 (Taesa), EGIE3 (Engie), ALUP11 (Alupar)\n\n**• Saneamento:** SAPR11 (Sanepar), SBSP3 (Sabesp)\n\n**• Bancos:** BBAS3 (Banco do Brasil), ITUB4 (Itaú), SANB11 (Santander)\n\n**• Seguradoras:** BBSE3 (BB Seguridade), CXSE3 (Caixa Seguridade)")
        st.markdown('<div class="huli-category"><b>🏢 Fundos Imobiliários (Renda Mensal)</b></div>', unsafe_allow_html=True)
        st.write("**• Logística:** HGLG11, XPLG11, BTLG11\n\n**• Shoppings:** XPML11, VISC11, HGBS11")
    with c2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda (Segurança)</b></div>', unsafe_allow_html=True)
        st.write("**• Ouro:** OZ1D ou ETF GOLD11\n\n**• Dólar:** IVVB11 (S&P 500)\n\n**• Renda Fixa:** Tesouro Selic e CDBs de liquidez diária")
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida (Crescimento)</b></div>', unsafe_allow_html=True)
        st.write("**• Cripto:** Bitcoin (BTC), Ethereum (ETH)\n\n**• Tech:** Nvidia (NVDA), Apple (AAPL)")

# --- ABA 6: MANUAL DE INSTRUÇÕES (TEXTOS COMPLETOS) ---
with tab_manual:
    st.header("📖 Manual Rockefeller")
    st.markdown("### 🏛️ 1. LPA e VPA")
    st.markdown('<div class="manual-section">O LPA (Lucro) e VPA (Patrimônio) definem o valor real. Se o DNA é forte, a queda é oportunidade. O sistema usa Graham para evitar que você compre topo.</div>', unsafe_allow_html=True)
    st.markdown("### 📊 2. Alertas e Raio-X")
    st.markdown('<div class="manual-section"><b>✅ COMPRAR:</b> Preço abaixo da média de 30 dias.<br><b>🚨 RECORDE:</b> Preço tocou a mínima do mês. Sinal de pânico e oportunidade de aporte.</div>', unsafe_allow_html=True)
    st.markdown("### 🌍 3. Patrimônio Global")
    st.markdown('<div class="manual-section">Diferente de apps comuns, aqui somamos Ouro físico e bens para dar a real visão da sua distância até a liberdade financeira.</div>', unsafe_allow_html=True)
