import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. ESTILO E CONFIGURAÇÃO (PRESERVADO INTEGRALMENTE)
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

# ABAS (ADICIONADA A DE DNA)
tab_painel, tab_radar_modelo, tab_dna, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🔍 Radar Carteira Modelo",
    "🧬 DNA (LPA/VPA)",
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
    "📖 Manual de Instruções"
])

# --- PROCESSAMENTO DE DADOS (LÓGICA PRESERVADA) ---
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

def coletar(lista):
    dados = []
    for nome, t in lista.items():
        try:
            a = yf.Ticker(t)
            h = a.history(period="30d")
            info = a.info
            if not h.empty:
                p = h['Close'].iloc[-1]
                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    p = (p / 31.1035) * cambio if t == "GC=F" else p * cambio
                m30 = h['Close'].mean()
                if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]: m30 *= cambio
                if t == "GC=F": m30 = (m30 / 31.1035) * cambio
                lpa, vpa = info.get('trailingEps', 0), info.get('bookValue', 0)
                lpa = lpa * cambio if t in ["NVDA", "AAPL"] else lpa
                vpa = vpa * cambio if t in ["NVDA", "AAPL"] else vpa
                pj = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m30
                status = "✅ DESCONTADO" if p < pj else "❌ SOBREPREÇO"
                var = h['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"
                dados.append({
                    "Ativo": nome, "Preço": p, "Justo": pj, "LPA": lpa, "VPA": vpa,
                    "Status": status, "Ação": acao, "Var_Min": var.min(), "Var_Max": var.max(),
                    "Dias_A": (var > 0).sum(), "Dias_B": (var < 0).sum(), "Var_H": var.iloc[-1]
                })
        except: continue
    return pd.DataFrame(dados)

df_p = coletar(tickers_map)
df_m = coletar(modelo_huli_tickers)
if 'carteira' not in st.session_state: st.session_state.carteira = {}

# ==================== ABA 1: PAINEL DE CONTROLE (RESTALRADO INTEGRAL) ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_p.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)
    
    st.subheader("📊 Raio-X de Volatilidade")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_p.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Outros Bens")
        g_ouro = st.number_input("Ouro Físico (g):", value=0.0)
        v_bens = st.number_input("Outros Bens (R$):", value=0.0)

    st.subheader("🧮 Gestor de Carteira Dinâmica")
    cap_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", value=0.0)
    sel = st.multiselect("Habilite seus ativos:", df_p["Ativo"].unique(), default=["PETR4.SA"])
    
    v_total_investido, v_atual_bolsa = 0, 0
    if sel:
        c1, c2 = st.columns(2)
        for i, n in enumerate(sel):
            with [c1, c2][i % 2]:
                q = st.number_input(f"Qtd ({n}):", key=f"q_{n}")
                inv = st.number_input(f"Investido R$ ({n}):", key=f"i_{n}")
                p_at = df_p[df_p["Ativo"] == n]["Preço"].values[0]
                v_at = q * p_at
                v_atual_bolsa += v_at
                v_total_investido += inv
                st.session_state.carteira[n] = {"atual": v_at}
        
        troco = cap_xp - v_total_investido
        p_ouro = df_p[df_p["Ativo"] == "Jóias (Ouro)"]["Preço"].values[0]
        patri = v_atual_bolsa + troco + (g_ouro * p_ouro) + v_bens
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_atual_bolsa:,.2f}")
        m2.metric("Saldo XP/Bens", f"R$ {(troco + v_bens + (g_ouro * p_ouro)):,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri:,.2f}")

# ==================== ABA 2: RADAR MODELO (ESPELHO DO PAINEL) ====================
with tab_radar_modelo:
    st.subheader("🔍 Radar: Carteira Modelo Tio Huli")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_m.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)
    st.subheader("📊 Raio-X de Volatilidade (Modelo)")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_m.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# ==================== ABA 3: DNA FINANCEIRO (LPA/VPA) ====================
with tab_dna:
    st.subheader("🧬 DNA dos Ativos (LPA e VPA)")
    df_full = pd.concat([df_p, df_m]).drop_duplicates(subset="Ativo")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>LPA (Lucro/Ação)</th><th>VPA (Patrimônio/Ação)</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>R$ {r['LPA']:.2f}</td><td>R$ {r['VPA']:.2f}</td><td>{(r['Preço']/r['LPA'] if r['LPA']>0 else 0):.2f}</td><td>{(r['Preço']/r['VPA'] if r['VPA']>0 else 0):.2f}</td></tr>" for _, r in df_full.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# ==================== ABA 4: ESTRATÉGIA HULI + BACKTESTING (RESTAURADO) ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli")
    aporte = st.number_input("Aporte Mensal (R$):", value=0.0)
    if sel:
        metas = {n: st.slider(f"Meta % {n}", 0, 100, 100//len(sel), key=f"m_{n}") for n in sel}
        if sum(metas.values()) == 100:
            plano = []
            for n in sel:
                v_at = st.session_state.carteira[n]["atual"]
                v_id = (v_atual_bolsa + aporte) * (metas[n]/100)
                plano.append({"Ativo": n, "Decisão": "✅ COMPRAR" if v_id > v_at else "✋ AGUARDAR", "Quanto": f"R$ {max(0, v_id-v_at):.2f}"})
            st.table(pd.DataFrame(plano))
    
    st.markdown("---")
    st.subheader("🏁 Meta de Sobrevivência")
    custo = st.number_input("Custo de Vida Mensal (R$):", value=3000.0)
    renda_est = st.slider("Rendimento Mensal (%)", 0.1, 2.0, 0.8)
    alvo = custo / (renda_est / 100)
    st.metric("Patrimônio Alvo", f"R$ {alvo:,.2f}")
    st.progress(min((patri/alvo if alvo > 0 else 0), 1.0))

    st.subheader("📈 Backtesting: Eficácia do Rockefeller")
    at_bt = st.selectbox("Simular Ativo:", df_p["Ativo"].unique())
    d_bt = df_p[df_p["Ativo"] == at_bt].iloc[0]
    st.success(f"Se você tivesse comprado {at_bt} no fundo do mês (R$ {d_bt['Preço']*(1-(abs(d_bt['Var_Min'])/100)):.2f}), seu retorno hoje seria de {abs(d_bt['Var_Min']):.2f}%.")

# ==================== ABA 5: CARTEIRA MODELO HULI (RESTAURADO INTEGRAL) ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras (Renda Passiva)</b><br><small>Foco em Dividendos e Estabilidade</small></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11 (Taesa), EGIE3 (Engie), ALUP11 (Alupar)\n\n**• Saneamento:** SAPR11 (Sanepar), SBSP3 (Sabesp)\n\n**• Bancos:** BBAS3 (Banco do Brasil), ITUB4 (Itaú), SANB11 (Santander)\n\n**• Seguradoras:** BBSE3 (BB Seguridade), CXSE3 (Caixa Seguridade)")
        st.markdown('<div class="huli-category"><b>🏢 Fundos Imobiliários (Renda Mensal)</b><br><small>Aluguéis sem Imposto de Renda</small></div>', unsafe_allow_html=True)
        st.write("**• Logística:** HGLG11, XPLG11, BTLG11\n\n**• Shoppings:** XPML11, VISC11, HGBS11")
    with col2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda (Segurança)</b><br><small>Reserva de Oportunidade e Valor</small></div>', unsafe_allow_html=True)
        st.write("**• Ouro:** OZ1D ou ETF GOLD11\n\n**• Dólar:** IVVB11 (S&P 500)\n\n**• Renda Fixa:** Tesouro Selic e CDBs de liquidez diária")
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida (Crescimento)</b><br><small>Aposta no futuro e multiplicação</small></div>', unsafe_allow_html=True)
        st.write("**• Cripto:** Bitcoin (BTC) e Ethereum (ETH)\n\n**• Tech:** Nvidia (NVDA), Apple (AAPL)")

# ==================== ABA 6: MANUAL DE INSTRUÇÕES (MELHORADO) ====================
with tab_manual:
    st.header("📖 Manual de Instruções - IA Rockefeller")
    st.markdown("### 🏛️ 1. Lógica Fundamentalista (LPA e VPA)")
    st.markdown("""<div class="manual-section">O sistema utiliza o <b>LPA (Lucro por Ação)</b> e o <b>VPA (Valor Patrimonial por Ação)</b> para calcular o Preço Justo de Graham. 
    A aba <b>DNA</b> mostra esses dados em tempo real, permitindo que você veja se a empresa é lucrativa e quanto patrimônio ela possui por trás de cada ação.</div>""", unsafe_allow_html=True)
    st.markdown("### 📊 2. Radar e Volatilidade")
    st.markdown("""<div class="manual-section"><b>✅ COMPRAR:</b> Só aparece quando o preço está abaixo da média de 30 dias E abaixo do Preço Justo.<br><b>🚨 RECORDE:</b> Indica que o ativo está na mínima do mês. É a melhor janela de oportunidade para as 'Vacas Leiteiras'.</div>""", unsafe_allow_html=True)
    st.markdown("### 🎯 3. Rebalanceamento e Sobrevivência")
    st.markdown("""<div class="manual-section">Use a aba Estratégia para saber exatamente quanto aportar em cada ativo para manter sua meta percentual. O sistema calcula a distância para sua meta de sobrevivência baseada em seu custo de vida.</div>""", unsafe_allow_html=True)
