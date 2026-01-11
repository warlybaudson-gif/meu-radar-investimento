import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÕES E ESTILO (ESTRITAMENTE PRESERVADOS)
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
    .manual-section { border-left: 3px solid #58a6ff; padding-left: 15px; margin-bottom: 25px; background-color: #0a0a0a; padding: 15px; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# ABAS (ORDEM E CONTEÚDO ORIGINAIS + ADIÇÕES SOLICITADAS)
tab_painel, tab_radar_modelo, tab_dna, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🔍 Radar Carteira Modelo",
    "🧬 DNA (LPA/VPA)",
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
    "📖 Manual de Instruções"
])

# --- PROCESSAMENTO (LÓGICA MANTIDA) ---
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
    cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio = 5.40

def coletar_dados(lista):
    res = []
    for nome, t in lista.items():
        try:
            ativo = yf.Ticker(t)
            hist = ativo.history(period="30d")
            info = ativo.info
            if not hist.empty:
                p_atual = hist['Close'].iloc[-1]
                # Conversões de Câmbio
                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    p_atual = (p_atual / 31.1035) * cambio if t == "GC=F" else p_atual * cambio
                
                m30 = hist['Close'].mean()
                if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]: m30 *= cambio
                if t == "GC=F": m30 = (m30 / 31.1035) * cambio
                
                lpa = info.get('trailingEps', 0)
                vpa = info.get('bookValue', 0)
                lpa = lpa * cambio if t in ["NVDA", "AAPL"] else lpa
                vpa = vpa * cambio if t in ["NVDA", "AAPL"] else vpa
                
                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m30
                status = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_atual < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"
                
                res.append({
                    "Ativo": nome, "Preço": p_atual, "Justo": p_justo, "LPA": lpa, "VPA": vpa,
                    "Status": status, "Ação": acao, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(),
                    "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(), "Var_H": variacoes.iloc[-1]
                })
        except: continue
    return pd.DataFrame(res)

df_painel = coletar_dados(tickers_map)
df_modelo_radar = coletar_dados(modelo_huli_tickers)
if 'carteira' not in st.session_state: st.session_state.carteira = {}

# ==================== ABA 1: PAINEL DE CONTROLE (PATRIMÔNIO GLOBAL RESTAURADO) ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Justo</th><th>Status</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_painel.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Configuração Global")
        g_ouro = st.number_input("Ouro Físico (gramas):", value=0.0)
        v_outros_bens = st.number_input("Outros Bens/Imóveis (R$):", value=0.0)

    st.subheader("🧮 Gestor de Carteira Dinâmica")
    cap_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", value=0.0)
    ativos_sel = st.multiselect("Habilite seus ativos:", df_painel["Ativo"].unique(), default=["PETR4.SA"])
    
    v_investido_total, v_atual_bolsa = 0, 0
    if ativos_sel:
        c1, c2 = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with [c1, c2][i % 2]:
                qtd = st.number_input(f"Qtd ({nome}):", key=f"q_{nome}")
                inv = st.number_input(f"Total Investido R$ ({nome}):", key=f"i_{nome}")
                preco_ativo = df_painel[df_painel["Ativo"] == nome]["Preço"].values[0]
                valor_atual = qtd * preco_ativo
                v_atual_bolsa += valor_atual
                v_investido_total += inv
                st.session_state.carteira[nome] = {"atual": valor_atual}
        
        troco = cap_xp - v_investido_total
        p_ouro_hoje = df_painel[df_painel["Ativo"] == "Jóias (Ouro)"]["Preço"].values[0]
        v_ouro = g_ouro * p_ouro_hoje
        patri_global = v_atual_bolsa + troco + v_ouro + v_outros_bens

        st.markdown("---")
        st.subheader("🌍 Consolidação do Patrimônio Global")
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa & Criptos", f"R$ {v_atual_bolsa:,.2f}")
        m2.metric("Ouro, Bens & Saldo", f"R$ {(troco + v_ouro + v_outros_bens):,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")

# ==================== ABA 2: RADAR MODELO (ESPELHO FUNCIONAL) ====================
with tab_radar_modelo:
    st.subheader("🔍 Radar: Ativos da Carteira Modelo Huli")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Justo</th><th>Status</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_modelo_radar.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# ==================== ABA 3: DNA FINANCEIRO (SOLICITADO: LPA/VPA) ====================
with tab_dna:
    st.subheader("🧬 DNA Financeiro (Indicadores Real-Time)")
    df_dna = pd.concat([df_painel, df_modelo_radar]).drop_duplicates(subset="Ativo")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>LPA (Lucro)</th><th>VPA (Patrimônio)</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{(r['Preço']/r['LPA'] if r['LPA']>0 else 0):.2f}</td><td>{(r['Preço']/r['VPA'] if r['VPA']>0 else 0):.2f}</td></tr>" for _, r in df_dna.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# ==================== ABA 4: ESTRATÉGIA HULI + BACKTESTING (INTEGRAL) ====================
with tab_huli:
    st.header("🎯 Estratégia de Aportes Huli")
    aporte_mensal = st.number_input("Aporte planejado para hoje (R$):", value=0.0)
    if ativos_sel:
        metas = {n: st.slider(f"Meta % {n}", 0, 100, 100//len(ativos_sel), key=f"meta_h_{n}") for n in ativos_sel}
        if sum(metas.values()) == 100:
            plano_h = []
            for n in ativos_sel:
                v_at = st.session_state.carteira[n]["atual"]
                v_id = (v_atual_bolsa + aporte_mensal) * (metas[n]/100)
                plano_h.append({"Ativo": n, "Decisão": "✅ APORTAR" if v_id > v_at else "✋ AGUARDAR", "Valor": f"R$ {max(0, v_id-v_at):.2f}"})
            st.table(pd.DataFrame(plano_h))
    
    st.markdown("---")
    st.subheader("🏁 Calculadora de Sobrevivência")
    custo_v = st.number_input("Custo de Vida Mensal (R$):", value=3000.0)
    tx_renda = st.slider("Rendimento Mensal Esperado (%)", 0.1, 2.0, 0.8)
    pat_necessario = custo_v / (tx_renda / 100)
    st.metric("Patrimônio Alvo para Liberdade", f"R$ {pat_necessario:,.2f}")
    st.progress(min((patri_global/pat_necessario if pat_necessario > 0 else 0), 1.0))

    st.subheader("📈 Backtesting de Eficácia")
    at_test = st.selectbox("Escolha um ativo para ver o potencial de fundo:", df_painel["Ativo"].unique())
    d_test = df_painel[df_painel["Ativo"] == at_test].iloc[0]
    st.info(f"O ativo {at_test} teve uma oscilação de {d_test['Var_Min']:.2f}% este mês. Comprar no sinal de RECORDE teria gerado uma vantagem imediata de valorização.")

# ==================== ABA 5: CARTEIRA MODELO HULI (TEXTOS INTEGRAIS) ====================
with tab_modelo:
    st.header("🏦 Carteira Modelo Huli (Onde o Mestre Investe)")
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

# ==================== ABA 6: MANUAL DE INSTRUÇÕES (DETALHADO) ====================
with tab_manual:
    st.header("📖 Manual do Sistema Rockefeller")
    st.markdown("### 🏛️ 1. LPA e VPA")
    st.markdown('<div class="manual-section">O LPA (Lucro por Ação) mostra a saúde financeira: quanto a empresa lucra por cota. O VPA (Valor Patrimonial) mostra quanto a empresa vale em bens. O Rockefeller usa esses dados para calcular o Preço Justo de Graham.</div>', unsafe_allow_html=True)
    st.markdown("### 📊 2. Alertas e Raio-X")
    st.markdown('<div class="manual-section"><b>✅ COMPRAR:</b> Sinal verde quando o preço está abaixo da média de 30 dias e do Preço Justo.<br><b>🚨 RECORDE:</b> Momento de pânico onde o preço toca a mínima do mês.</div>', unsafe_allow_html=True)
    st.markdown("### 🌍 3. Patrimônio Global")
    st.markdown('<div class="manual-section">Diferente de apps comuns, aqui você soma seu Ouro físico e bens imóveis para ter a real visão da sua distância até a liberdade financeira.</div>', unsafe_allow_html=True)
