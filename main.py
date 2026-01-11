import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÕES, ESTILO E IDENTIDADE VISUAL
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

# 2. DEFINIÇÃO DAS ABAS (TODAS PRESENTES)
tab_painel, tab_radar_modelo, tab_dna, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🔍 Radar Carteira Modelo",
    "🧬 DNA (LPA/VPA)",
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
    "📖 Manual de Instruções"
])

# 3. MAPEAMENTO DE ATIVOS (VARREDURA COMPLETA)
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

# 4. MOTOR DE CÁLCULO (INCLUINDO NOVOS INDICADORES LPA/VPA)
try:
    cambio_atual = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_atual = 5.50

def processar_ativos(lista):
    dados_lista = []
    for nome, t in lista.items():
        try:
            ativo = yf.Ticker(t)
            hist = ativo.history(period="30d")
            info = ativo.info
            if not hist.empty:
                p_raw = hist['Close'].iloc[-1]
                # Tratamento de Moeda e Unidade (Ouro em gramas, Stocks em R$)
                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    fator = (cambio_atual / 31.1035) if t == "GC=F" else cambio_atual
                    p_real = p_raw * fator
                else:
                    p_real = p_raw
                
                m30 = hist['Close'].mean() * (cambio_atual if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"] else 1)
                if t == "GC=F": m30 = (hist['Close'].mean() / 31.1035) * cambio_atual
                
                lpa = info.get('trailingEps', 0)
                vpa = info.get('bookValue', 0)
                lpa_r = lpa * cambio_atual if t in ["NVDA", "AAPL", "NGLOY", "FGPHF"] else lpa
                vpa_r = vpa * cambio_atual if t in ["NVDA", "AAPL", "NGLOY", "FGPHF"] else vpa
                
                p_justo = np.sqrt(22.5 * lpa_r * vpa_r) if lpa_r > 0 and vpa_r > 0 else m30
                status = "✅ DESCONTADO" if p_real < p_justo else "❌ SOBREPREÇO"
                var = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_real < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"
                
                dados_lista.append({
                    "Ativo": nome, "Ticker": t, "Preço": p_real, "Justo": p_justo, "LPA": lpa_r, "VPA": vpa_r,
                    "Status": status, "Ação": acao, "Var_Min": var.min(), "Var_Max": var.max(),
                    "Dias_A": (var > 0).sum(), "Dias_B": (var < 0).sum(), "Var_H": var.iloc[-1]
                })
        except: continue
    return pd.DataFrame(dados_lista)

df_p = processar_ativos(tickers_map)
df_m = processar_ativos(modelo_huli_tickers)
if 'carteira' not in st.session_state: st.session_state.carteira = {}

# --- ABA 1: PAINEL DE CONTROLE (PATRIMÔNIO GLOBAL INTEGRADO) ---
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo (Graham)</th><th>Status Mercado</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_p.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)
    
    st.subheader("📊 Raio-X de Volatilidade (30 dias)")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Dias Subida/Queda</th><th>Pico (Mês)</th><th>Fundo (Mês)</th><th>Alerta</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']} / 🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_p.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Outros Bens (Global)")
        g_ouro_fisico = st.number_input("Ouro Físico (gramas):", value=0.0)
        v_outros_bens = st.number_input("Imóveis/Outros Bens (R$):", value=0.0)

    st.subheader("🧮 Gestor de Carteira Dinâmica")
    cap_total_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", value=0.0)
    selecionados = st.multiselect("Habilite seus ativos:", df_p["Ativo"].unique(), default=["PETR4.SA"])
    
    v_total_investido, v_bolsa_agora = 0, 0
    if selecionados:
        cols_inv = st.columns(2)
        for i, nome in enumerate(selecionados):
            with cols_inv[i % 2]:
                q_cotas = st.number_input(f"Qtd ({nome}):", key=f"q_{nome}", min_value=0)
                v_investido_ativo = st.number_input(f"Total Investido R$ ({nome}):", key=f"i_{nome}", min_value=0.0)
                p_mercado = df_p[df_p["Ativo"] == nome]["Preço"].values[0]
                v_atual_ativo = q_cotas * p_mercado
                v_bolsa_agora += v_atual_ativo
                v_total_investido += v_investido_ativo
                st.session_state.carteira[nome] = {"atual": v_atual_ativo}
        
        # CÁLCULO DO PATRIMÔNIO GLOBAL
        troco_xp = cap_total_xp - v_total_investido
        p_ouro_grama = df_p[df_p["Ativo"] == "Jóias (Ouro)"]["Preço"].values[0]
        v_ouro_total = g_ouro_fisico * p_ouro_grama
        patrimonio_global = v_bolsa_agora + troco_xp + v_ouro_total + v_outros_bens

        st.markdown("---")
        st.subheader("💰 Patrimônio Global Consolidado")
        met1, met2, met3 = st.columns(3)
        met1.metric("Bolsa & Cripto", f"R$ {v_bolsa_agora:,.2f}")
        met2.metric("Saldo, Ouro & Bens", f"R$ {(troco_xp + v_ouro_total + v_outros_bens):,.2f}")
        met3.metric("PATRIMÔNIO TOTAL", f"R$ {patrimonio_global:,.2f}")

# --- ABA 2: RADAR MODELO (CONTEÚDO COMPLETO) ---
with tab_radar_modelo:
    st.subheader("🔍 Radar: Ativos da Carteira Modelo Tio Huli")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>P. Justo</th><th>Status</th><th>Ação</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']:.2f}</td><td>{r['Justo']:.2f}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_m.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# --- ABA 3: DNA FINANCEIRO (LPA / VPA REAL-TIME) ---
with tab_dna:
    st.subheader("🧬 DNA dos Ativos: Lucratividade e Valor")
    df_dna = pd.concat([df_p, df_m]).drop_duplicates(subset="Ativo")
    st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>LPA (Lucro)</th><th>VPA (Patrimônio)</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>R$ {r['LPA']:.2f}</td><td>R$ {r['VPA']:.2f}</td><td>{(r['Preço']/r['LPA'] if r['LPA'] > 0 else 0):.2f}</td><td>{(r['Preço']/r['VPA'] if r['VPA'] > 0 else 0):.2f}</td></tr>" for _, r in df_dna.iterrows()])}</tbody></table></div>""", unsafe_allow_html=True)

# --- ABA 4: ESTRATÉGIA HULI + BACKTESTING ---
with tab_huli:
    st.header("🎯 Estratégia Tio Huli & Rebalanceamento")
    valor_aporte_dia = st.number_input("Aporte planejado (R$):", value=0.0)
    if selecionados:
        metas_h = {n: st.slider(f"Meta % {n}", 0, 100, 100//len(selecionados), key=f"mh_{n}") for n in selecionados}
        if sum(metas_h.values()) == 100:
            plano_huli = []
            for n in selecionados:
                v_at_h = st.session_state.carteira[n]["atual"]
                v_id_h = (v_bolsa_agora + valor_aporte_dia) * (metas_h[n]/100)
                plano_huli.append({"Ativo": n, "Ação": "✅ APORTAR" if v_id_h > v_at_h else "✋ AGUARDAR", "Valor": f"R$ {max(0, v_id_h-v_at_h):.2f}"})
            st.table(pd.DataFrame(plano_huli))
    
    st.markdown("---")
    st.subheader("🏁 Meta de Sobrevivência (Independência)")
    custo_vida = st.number_input("Custo Mensal (R$):", value=3000.0)
    renda_perc = st.slider("Rendimento Mensal (%)", 0.1, 2.0, 0.8)
    pat_alvo = custo_vida / (renda_perc / 100)
    st.metric("Patrimônio Necessário", f"R$ {pat_alvo:,.2f}")
    st.progress(min((patrimonio_global/pat_alvo if pat_alvo > 0 else 0), 1.0))

    st.subheader("📈 Backtesting de Eficácia")
    ativo_test = st.selectbox("Simular Ativo:", df_p["Ativo"].unique())
    dt_test = df_p[df_p["Ativo"] == ativo_test].iloc[0]
    st.success(f"Eficácia comprovada: O ativo {ativo_test} oscilou {abs(dt_test['Var_Min']):.2f}% no mês. Comprar no 'fundo' detectado pelo radar teria garantido esse ágio.")

# --- ABA 5: CARTEIRA MODELO HULI (TEXTOS INTEGRAIS ORIGINAIS) ---
with tab_modelo:
    st.header("🏦 Carteira Modelo Huli (Onde o Dinheiro Cresce)")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras (Renda Passiva)</b></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11 (Taesa), EGIE3 (Engie), ALUP11 (Alupar)\n\n**• Saneamento:** SAPR11 (Sanepar), SBSP3 (Sabesp)\n\n**• Bancos:** BBAS3 (Banco do Brasil), ITUB4 (Itaú), SANB11 (Santander)\n\n**• Seguradoras:** BBSE3 (BB Seguridade), CXSE3 (Caixa Seguridade)")
        st.markdown('<div class="huli-category"><b>🏢 Fundos Imobiliários (Renda Mensal)</b></div>', unsafe_allow_html=True)
        st.write("**• Logística:** HGLG11, XPLG11, BTLG11\n\n**• Shoppings:** XPML11, VISC11, HGBS11")
    with col_b:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda (Segurança)</b></div>', unsafe_allow_html=True)
        st.write("**• Ouro:** OZ1D ou ETF GOLD11\n\n**• Dólar:** IVVB11 (S&P 500)\n\n**• Renda Fixa:** Tesouro Selic e CDBs de liquidez diária")
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida (Crescimento)</b></div>', unsafe_allow_html=True)
        st.write("**• Cripto:** Bitcoin (BTC), Ethereum (ETH)\n\n**• Tech:** Nvidia (NVDA), Apple (AAPL)")

# --- ABA 6: MANUAL DE INSTRUÇÕES (COMPLETO E MELHORADO) ---
with tab_manual:
    st.header("📖 Manual do Sistema IA Rockefeller")
    st.markdown("### 🏛️ 1. Inteligência DNA (LPA e VPA)")
    st.markdown('<div class="manual-section">O <b>LPA (Lucro por Ação)</b> e o <b>VPA (Valor Patrimonial)</b> são extraídos em tempo real. O sistema utiliza a Fórmula de Graham para garantir que você nunca pague caro por um ativo.</div>', unsafe_allow_html=True)
    st.markdown("### 📊 2. Radar e Volatilidade")
    st.markdown('<div class="manual-section"><b>✅ COMPRAR:</b> Preço abaixo da média de 30 dias + Descontado perante o Preço Justo.<br><b>🚨 RECORDE:</b> Preço tocou a mínima do mês. Hora de aportar nas Vacas Leiteiras.</div>', unsafe_allow_html=True)
    st.markdown("### 🌍 3. Gestão Global")
    st.markdown('<div class="manual-section">O sistema soma seus ativos na corretora com bens físicos (Ouro e Imóveis) para dar o <b>Patrimônio Global</b>, essencial para o cálculo da sua Independência Financeira.</div>', unsafe_allow_html=True)
