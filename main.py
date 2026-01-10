import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO (INTEGRAL - PRESERVADO)
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

# CRIAÇÃO DAS ABAS
tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🔍 Radar Carteira Modelo",
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
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
                preco_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
                if t in ["NVDA", "AAPL"] and lpa > 0: preco_justo *= cambio_hoje

                status_m = "✅ DESCONTADO" if p_atual < preco_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "✅ COMPRAR" if p_atual < m_30 and status_m == "✅ DESCONTADO" else "⚠️ ESPERAR"
                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", 
                    "Justo": f"{preco_justo:.2f}", "Status M": status_m, "Ação": acao,
                    "V_Cru": p_atual, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(),
                    "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(), "Var_H": variacoes.iloc[-1]
                })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = calcular_dados(modelo_huli_tickers)

if 'carteira' not in st.session_state: st.session_state.carteira = {}

# ==================== ABA 1: PAINEL DE CONTROLE (PRESERVADO) ====================
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
                lucro = v_agora - investido
                total_investido_acumulado += investido
                v_ativos_atualizado += v_agora
                st.session_state.carteira[nome] = {"atual": v_agora}
                lista_c.append({"Ativo": nome, "Qtd": qtd, "PM": f"{pm_calc:.2f}", "Total": f"{v_agora:.2f}", "Lucro": f"{lucro:.2f}"})
                df_grafico[nome] = yf.Ticker(info["Ticker_Raw"]).history(period="30d")['Close']

        troco_real = capital_xp - total_investido_acumulado
        html_c = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']}</td><td>R$ {r['Total']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c])}</tbody>
        </table></div>"""
        st.markdown(html_c, unsafe_allow_html=True)

        st.subheader("💰 Patrimônio Global")
        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['V_Cru'].values[0])
        patri_global = v_ativos_atualizado + troco_real
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (Saldo XP)", f"R$ {troco_real:,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")
        st.line_chart(df_grafico)

# ==================== ABA 2: RADAR CARTEIRA MODELO (MELHORADA - IGUAL AO PAINEL) ====================
with tab_radar_modelo:
    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    html_radar_mod = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_mod, unsafe_allow_html=True)

    st.subheader("📊 Raio-X de Volatilidade (Ativos Modelo)")
    html_vol_mod = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol_mod, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado (Modelo Huli)")
    caros_mod = len(df_radar_modelo[df_radar_modelo['Status M'] == "❌ SOBREPREÇO"])
    score_mod = (caros_mod / len(df_radar_modelo)) * 100 if len(df_radar_modelo) > 0 else 0
    st.progress(score_mod / 100)
    st.write(f"Índice de Sobrepreço na Carteira Modelo: **{int(score_mod)}%**")

# ==================== ABA 3: ESTRATÉGIA HULI (PRESERVADA) ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli: Próximos Passos")
    valor_aporte = st.number_input("Aporte mensal planejado (R$):", min_value=0.0, value=0.0)
    if ativos_sel:
        metas = {nome: st.slider(f"{nome} (%)", 0, 100, 100 // len(ativos_sel), key=f"meta_h_{nome}") for nome in ativos_sel}
        if sum(metas.values()) == 100:
            plano = []
            for nome in ativos_sel:
                v_at = st.session_state.carteira[nome]["atual"]
                v_id = (v_ativos_atualizado + valor_aporte) * (metas[nome] / 100)
                nec = v_id - v_at
                plano.append({"Ativo": nome, "Ação": "APORTAR" if nec > 0 else "AGUARDAR", "Valor": f"R$ {max(0, nec):.2f}"})
            st.table(pd.DataFrame(plano))

# ==================== ABA 4: CARTEIRA MODELO HULI (PRESERVADA) ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("• Energia: TAEE11, EGIE3, ALUP11 | • Bancos: BBAS3, ITUB4")
    with col2:
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida</b></div>', unsafe_allow_html=True)
        st.write("• Bitcoin | • Nvidia | • Apple")

# ==================== ABA 5: MANUAL DE INSTRUÇÕES (MELHORADA/EXPANDIDA) ====================
with tab_manual:
    st.header("📖 Manual do Sistema IA Rockefeller")
    
    st.markdown("### 🏛️ 1. Lógica de Avaliação (Fórmula de Graham)")
    st.markdown("""<div class="manual-section">
    Para eliminar o achismo, usamos o <b>Número de Graham</b>. Ele define o valor intrínseco de uma empresa baseado no lucro e patrimônio real.
    <ul>
        <li><b>Cálculo:</b> Raiz Quadrada de (22.5 * LPA * VPA).</li>
        <li><b>✅ DESCONTADO:</b> O preço atual é menor que o Valor Justo. A empresa está "em promoção" perante seus fundamentos.</li>
        <li><b>❌ SOBREPREÇO:</b> O preço atual excedeu o limite de segurança. Risco de queda para ajuste ao valor real.</li>
    </ul>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 📊 2. Radar e Raio-X de Volatilidade")
    st.markdown("""<div class="manual-section">
    <ul>
        <li><b>Ação ✅ COMPRAR:</b> Só é ativada quando o ativo está barato tecnicamente (abaixo da média de 30 dias) <b>E</b> fundamentalmente (descontado por Graham).</li>
        <li><b>Dias A/B (Alta/Baixa):</b> Se um ativo tem muitos dias de baixa (🔴) mas fundamentos bons, a chance de reversão explosiva é maior.</li>
        <li><b>🚨 RECORDE:</b> Alerta crítico! O preço caiu abaixo da mínima do mês. Se for uma "Vaca Leiteira", é o melhor momento histórico do mês para comprar.</li>
    </ul>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 🧮 3. Gestor de Carteira e Patrimônio")
    st.markdown("""<div class="manual-section">
    <ul>
        <li><b>PM (Preço Médio):</b> É o seu custo de aquisição. O lucro real só existe se o Preço Atual estiver acima do seu PM.</li>
        <li><b>Troco (Saldo XP):</b> É o seu poder de fogo. Mantenha sempre um saldo para aproveitar os alertas de 'RECORDE'.</li>
        <li><b>Sentimento de Mercado:</b> Se o índice de 'Ativos Caros' estiver acima de 70%, evite grandes aportes. O mercado está eufórico e perigoso.</li>
    </ul>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 🎯 4. Rebalanceamento Huli")
    st.markdown("""<div class="manual-section">
    Nunca compre o que você quer, compre o que sua <b>Meta (%)</b> pede. O sistema calcula automaticamente qual ativo ficou para trás na sua carteira e direciona seu novo aporte para ele, garantindo que você compre sempre o que está mais barato na sua própria carteira.
    </div>""", unsafe_allow_html=True)
