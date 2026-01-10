import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO (PRESERVADO)
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

# ABAS
tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🔍 Radar Carteira Modelo",
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
    "📖 Manual de Instruções"
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

def calcular_tudo(lista):
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
                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
                if t in ["NVDA", "AAPL"]: p_justo *= cambio_hoje
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_atual < m_30 and status_m == "✅ DESCONTADO" else "⚠️ ESPERAR"
                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", "Justo": f"{p_justo:.2f}",
                    "Status M": status_m, "Ação": acao, "V_Cru": p_atual, "Var_Min": variacoes.min(),
                    "Var_Max": variacoes.max(), "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "Var_H": variacoes.iloc[-1]
                })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_tudo(tickers_map)
df_radar_modelo = calcular_tudo(modelo_huli_tickers)
if 'carteira' not in st.session_state: st.session_state.carteira = {}

# ==================== ABA 1: PAINEL DE CONTROLE (INTEGRAL) ====================
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
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=0.0, step=100.0)
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])
    total_investido_acumulado, v_ativos_atualizado = 0, 0
    lista_c, df_grafico = [], pd.DataFrame()
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, value=0, key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, value=0.0, key=f"i_{nome}")
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                p_atual = info["V_Cru"]
                pm_calc = investido / qtd if qtd > 0 else 0.0
                v_agora = qtd * p_atual
                total_investido_acumulado += investido
                v_ativos_atualizado += v_agora
                st.session_state.carteira[nome] = {"atual": v_agora}
                lista_c.append({"Ativo": nome, "Qtd": qtd, "PM": f"{pm_calc:.2f}", "Total": f"{v_agora:.2f}", "Lucro": f"{(v_agora - investido):.2f}"})
                df_grafico[nome] = yf.Ticker(info["Ticker_Raw"]).history(period="30d")['Close']
        troco_real = capital_xp - total_investido_acumulado
        st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']}</td><td>R$ {r['Total']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c])}</tbody>
        </table></div>""", unsafe_allow_html=True)
        patri_global = v_ativos_atualizado + troco_real
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_ativos_atualizado:,.2f}"); m2.metric("Troco (XP)", f"R$ {troco_real:,.2f}"); m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")
        st.line_chart(df_grafico)

# ==================== ABA 2: RADAR CARTEIRA MODELO (NOVA - IGUAL AO PAINEL) ====================
with tab_radar_modelo:
    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)
    st.subheader("📊 Raio-X de Volatilidade (Ativos Modelo)")
    html_vol_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol_m, unsafe_allow_html=True)
    st.subheader("🌡️ Sentimento de Mercado (Modelo)")
    caros_m = len(df_radar_modelo[df_radar_modelo['Status M'] == "❌ SOBREPREÇO"])
    score_m = (caros_m / len(df_radar_modelo)) * 100 if len(df_radar_modelo) > 0 else 0
    st.progress(score_m / 100); st.write(f"Índice de Sobrepreço: **{int(score_m)}%**")

# ==================== ABA 3: ESTRATÉGIA HULI (RESTAURADA) ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli: Próximos Passos")
    valor_aporte = st.number_input("Quanto você pretende investir este mês? (R$):", min_value=0.0, value=0.0, step=100.0)
    if not ativos_sel: st.warning("Selecione seus ativos na aba 'Painel de Controle' primeiro.")
    else:
        st.subheader("📊 1. Defina sua Alocação Ideal (%)")
        metas = {nome: st.slider(f"{nome} (%)", 0, 100, 100 // len(ativos_sel), key=f"meta_{nome}") for nome in ativos_sel}
        if sum(metas.values()) == 100:
            st.subheader("📈 2. Plano de Rebalanceamento")
            plano_huli = []
            for nome in ativos_sel:
                v_atual = st.session_state.carteira[nome]["atual"]
                porc_atual = (v_atual / v_ativos_atualizado * 100) if v_ativos_atualizado > 0 else 0
                valor_ideal = (v_ativos_atualizado + valor_aporte) * (metas[nome] / 100)
                necessidade = valor_ideal - v_atual
                decisao = "✅ APORTAR" if necessidade > 0 else "✋ AGUARDAR"
                plano_huli.append({"Ativo": nome, "Atual (%)": f"{porc_atual:.1f}%", "Meta (%)": f"{metas[nome]:.0f}%", "Decisão": decisao, "Quanto Comprar": f"R$ {max(0, necessidade):.2f}"})
            st.table(pd.DataFrame(plano_huli))
            st.markdown("---")
            st.subheader("🏁 Meta de Sobrevivência (Liberdade Financeira)")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                custo = st.number_input("Custo de vida mensal (R$):", min_value=0.0, value=3000.0)
                renda_est = st.slider("Rendimento mensal (%)", 0.1, 2.0, 0.8)
            pat_nec = custo / (renda_est / 100)
            prog = (patri_global / pat_nec) * 100 if pat_nec > 0 else 0
            with col_m2: st.metric("Patrimônio Alvo", f"R$ {pat_nec:,.2f}")
            st.write(f"Você já percorreu **{prog:.1f}%** do caminho!"); st.progress(min(prog/100, 1.0))

# ==================== ABA 4: CARTEIRA MODELO HULI (RESTAURADA) ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras (Renda Passiva)</b></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11, EGIE3, ALUP11 | **• Saneamento:** SAPR11, SBSP3")
        st.write("**• Bancos:** BBAS3, ITUB4, SANB11 | **• Seguradoras:** BBSE3, CXSE3")
        st.markdown('<div class="huli-category"><b>🏢 Fundos Imobiliários (Renda Mensal)</b></div>', unsafe_allow_html=True)
        st.write("**• Logística:** HGLG11, XPLG11, BTLG11 | **• Shoppings:** XPML11, VISC11")
    with col2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda (Segurança)</b></div>', unsafe_allow_html=True)
        st.write("**• Ouro:** OZ1D ou GOLD11 | **• Dólar:** IVVB11 (S&P 500) | **• Tesouro Selic**")
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida (Crescimento)</b></div>', unsafe_allow_html=True)
        st.write("**• Cripto:** Bitcoin (BTC), Ethereum (ETH) | **• Tech:** Nvidia (NVDA), Apple (AAPL)")

# ==================== ABA 5: MANUAL DE INSTRUÇÕES (EXPANDIDO) ====================
with tab_manual:
    st.header("📖 Manual de Instruções IA Rockefeller")
    st.markdown("### 🏛️ 1. Inteligência de Preço: Graham e Médias")
    st.markdown("""<div class="manual-section">Para eliminar o achismo, o sistema utiliza a <b>Fórmula de Graham (√22.5 * LPA * VPA)</b>. 
    Esta métrica define o valor intrínseco de uma empresa. O botão '✅ COMPRAR' só é ativado se o preço atual estiver abaixo do valor de Graham E abaixo da média dos últimos 30 dias.</div>""", unsafe_allow_html=True)
    st.markdown("### 📊 2. Operação do Radar e Raio-X")
    st.markdown("""<div class="manual-section"><b>• Dias A/B:</b> Placar de altas e baixas. Ativos com muitos dias de queda (🔴) e fundamentos sólidos são as melhores janelas de entrada.<br>
    <b>• Alerta RECORDE:</b> Dispara quando o preço atinge a mínima do mês. É o sinal definitivo de pânico do mercado, ideal para 'Vacas Leiteiras'.</div>""", unsafe_allow_html=True)
    st.markdown("### 🧮 3. Gestão de Riqueza")
    st.markdown("""<div class="manual-section"><b>• Rebalanceamento:</b> O sistema nunca sugere comprar o que você quer, mas sim o que sua carteira precisa para manter o equilíbrio.<br>
    <b>• Sobrevivência:</b> O cálculo é baseado na regra da renda perpétua. O objetivo é que seu custo de vida seja coberto por 0.8% a 1% de rendimento do seu patrimônio total.</div>""", unsafe_allow_html=True)
