import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

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

# --- PROCESSAMENTO DE DADOS (INTEGRAL ORIGINAL) ---
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
                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
                if t in ["NVDA", "AAPL"]: p_justo *= cambio_hoje
                status_m = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
                variacoes = hist['Close'].pct_change() * 100
                
                if p_atual < m_30 and status_m == "✅ DESCONTADO": acao = "✅ COMPRAR"
                elif p_atual > p_justo * 1.2: acao = "🛑 VENDER"
                else: acao = "⚠️ ESPERAR"

                res.append({
                    "Ativo": nome_ex, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", "Justo": f"{p_justo:.2f}",
                    "Status M": status_m, "Ação": acao, "V_Cru": p_atual, "Var_Min": variacoes.min(),
                    "Var_Max": variacoes.max(), "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "Var_H": variacoes.iloc[-1], "LPA": lpa, "VPA": vpa
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
    if not df_radar.empty:
        html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status (C/B)</th><th>Decisão</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td style='color:{'#00ff00' if r['Status M'] == '✅ DESCONTADO' else '#ff4b4b'}'>{'BARATO' if r['Status M'] == '✅ DESCONTADO' else 'CARO'}</td><td style='font-weight:bold; color:{'#00ff00' if r['Ação'] == '✅ COMPRAR' else '#ff4b4b' if r['Ação'] == '🛑 VENDER' else '#f1c40f'}'>{r['Ação'].replace('✅ ', '').replace('🛑 ', '').replace('⚠️ ', '')}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
        </table></div>"""
        st.markdown(html_radar, unsafe_allow_html=True)
    
    st.subheader("📊 Raio-X de Volatilidade")
    if not df_radar.empty:
        html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
        </table></div>"""
        st.markdown(html_vol, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado")
    if not df_radar.empty:
        caros = len(df_radar[df_radar['Status M'] == "❌ SOBREPREÇO"])
        score = (caros / len(df_radar)) * 100
        st.progress(score / 100)
        st.write(f"Índice de Ativos Caros: **{int(score)}%**")

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=0.0, step=100.0)
    
    opcoes_ativos = df_radar["Ativo"].unique() if not df_radar.empty else []
    ativos_sel = st.multiselect("Habilite seus ativos:", opcoes_ativos)
    
    total_investido_acumulado, v_ativos_atualizado = 0, 0
    lista_c, df_grafico = [], pd.DataFrame()
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, key=f"i_{nome}")
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

        st.subheader("💰 Patrimônio Global")
        with st.sidebar:
            st.header("⚙️ Outros Bens")
            g_joias = st.number_input("Ouro Físico (gramas):", min_value=0.0, value=0.0)
            v_bens = st.number_input("Outros Bens/Imóveis (R$):", min_value=0.0, value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['V_Cru'].values[0]) if "Jóias (Ouro)" in df_radar['Ativo'].values else 0
        valor_ouro_total = g_joias * p_ouro
        patri_global = v_ativos_atualizado + troco_real + valor_ouro_total + v_bens

        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (XP) + Bens", f"R$ {(troco_real + valor_ouro_total + v_bens):,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")
        if not df_grafico.empty:
            st.line_chart(df_grafico)

# ==================== ABA 2: RADAR CARTEIRA MODELO ====================
with tab_radar_modelo:
    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    if not df_radar_modelo.empty:
        html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Status Mercado</th><th>Ação</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
        </table></div>"""
        st.markdown(html_radar_m, unsafe_allow_html=True)

    st.subheader("📊 Raio-X de Volatilidade (Ativos Modelo)")
    if not df_radar_modelo.empty:
        html_vol_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
        </table></div>"""
        st.markdown(html_vol_m, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado (Modelo)")
    if not df_radar_modelo.empty:
        caros_m = len(df_radar_modelo[df_radar_modelo['Status M'] == "❌ SOBREPREÇO"])
        score_m = (caros_m / len(df_radar_modelo)) * 100
        st.progress(score_m / 100)
        st.write(f"Índice de Sobrepreço Modelo: **{int(score_m)}%**")

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira: Ativos Modelo")
    capital_xp_m = st.number_input("💰 Capital na Corretora para Ativos Modelo (R$):", min_value=0.0, value=0.0, step=100.0, key="cap_huli")
    
    opcoes_modelo = df_radar_modelo["Ativo"].unique() if not df_radar_modelo.empty else []
    ativos_sel_m = st.multiselect("Habilite ativos da Carteira Modelo:", opcoes_modelo, key="sel_huli")
    
    total_investido_acum_m, v_ativos_atual_m = 0, 0
    df_grafico_m = pd.DataFrame()
    if ativos_sel_m:
        cols_m = st.columns(2)
        for i, nome in enumerate(ativos_sel_m):
            with cols_m[i % 2]:
                st.markdown(f"**{nome}**")
                qtd_m = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, key=f"q_m_{nome}")
                investido_m = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, key=f"i_m_{nome}")
                info_m = df_radar_modelo[df_radar_modelo["Ativo"] == nome].iloc[0]
                p_atual_m = info_m["V_Cru"]
                v_agora_m = qtd_m * p_atual_m
                total_investido_acum_m += investido_m
                v_ativos_atual_m += v_agora_m
                st.session_state.carteira_modelo[nome] = {"atual": v_agora_m}
                df_grafico_m[nome] = [v_agora_m] # Dados para o gráfico de barras
        
        st.subheader("💰 Patrimônio Global (Estratégia Modelo)")
        patri_global_m = v_ativos_atual_m + (capital_xp_m - total_investido_acum_m)
        m1_m, m2_m = st.columns(2)
        m1_m.metric("Total em Ativos Modelo", f"R$ {v_ativos_atual_m:,.2f}")
        m2_m.metric("PATRIMÔNIO MODELO TOTAL", f"R$ {patri_global_m:,.2f}")
        
        # AJUSTE PARA O ERRO DA IMAGEM: Só desenha o gráfico se houver colunas e valores
        if not df_grafico_m.empty and v_ativos_atual_m > 0:
            st.bar_chart(df_grafico_m.T)

# ==================== ABA 3: ESTRATÉGIA HULI ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli: Próximos Passos")
    valor_aporte = st.number_input("Quanto você pretende investir este mês? (R$):", min_value=0.0, value=0.0, step=100.0)
    if ativos_sel:
        metas = {nome: st.slider(f"{nome} (%)", 0, 100, 100 // len(ativos_sel), key=f"meta_h_{nome}") for nome in ativos_sel}
        if sum(metas.values()) == 100:
            plano = []
            for nome in ativos_sel:
                v_at = st.session_state.carteira.get(nome, {"atual": 0})["atual"]
                v_id = (v_ativos_atualizado + valor_aporte) * (metas[nome] / 100)
                nec = v_id - v_at
                plano.append({"Ativo": nome, "Ação": "APORTAR" if nec > 0 else "AGUARDAR", "Valor": f"R$ {max(0, nec):.2f}"})
            st.table(pd.DataFrame(plano))

# ==================== ABA 4: CARTEIRA MODELO HULI ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras (Renda Passiva)</b></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11, EGIE3, ALUP11 | **• Saneamento:** SAPR11, SBSP3")
        st.write("**• Bancos:** BBAS3, ITUB4, SANB11 | **• Seguradoras:** BBSE3, CXSE3")
    with col2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda (Segurança)</b></div>', unsafe_allow_html=True)
        st.write("**• Ouro:** OZ1D ou ETF GOLD11 | **• Dólar:** IVVB11 (S&P 500)")
        st.write("**• Renda Fixa:** Tesouro Selic e CDBs de liquidez diária")
        st.markdown('<div class="huli-category"><b>🐎 Cavalos de Corrida (Crescimento)</b></div>', unsafe_allow_html=True)
        st.write("**• Cripto:** Bitcoin (BTC) e Ethereum (ETH) | **• Tech:** Nvidia (NVDA), Apple (AAPL)")

# ==================== ABA 5: DNA FINANCEIRO ====================
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")
    if not df_radar.empty or not df_radar_modelo.empty:
        df_combined = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
        html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>LPA (Lucro)</th><th>VPA (Patrimônio)</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
        for _, r in df_combined.iterrows():
            p_l = float(r['V_Cru']) / r['LPA'] if r['LPA'] > 0 else 0
            p_vp = float(r['V_Cru']) / r['VPA'] if r['VPA'] > 0 else 0
            html_dna += f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{p_l:.2f}</td><td>{p_vp:.2f}</td></tr>"
        html_dna += "</tbody></table></div>"
        st.markdown(html_dna, unsafe_allow_html=True)

# ==================== ABA 6: BACKTESTING ====================
with tab_backtest:
    st.header("📈 Backtesting de Oportunidade")
    if not df_radar.empty:
        ativo_bt = st.selectbox("Selecione um ativo para simular o 'Efeito Pânico':", df_radar["Ativo"].unique())
        d = df_radar[df_radar["Ativo"] == ativo_bt].iloc[0]
        p_atual = float(d["V_Cru"])
        queda_max = abs(float(d["Var_Min"]))
        preco_fundo = p_atual / (1 + (queda_max/100))
        st.metric("Lucro Potencial (Fundo vs Hoje)", f"{queda_max:.2f}%")

# ==================== ABA 7: MANUAL DE INSTRUÇÕES ====================
with tab_manual:
    st.header("📖 Manual - IA Rockefeller")
    st.markdown("* **Preço Justo:** Graham ($\sqrt{22.5 \cdot LPA \cdot VPA}$).")
    st.markdown("* **Status:** BARATO se preço < Preço Justo.")
