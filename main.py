import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO (INTEGRAL - SEM ALTERAÇÕES)
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

# ABAS (MANTIDAS)
tab_painel, tab_huli, tab_modelo, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
    "📖 Manual de Instruções"
])

# --- PROCESSAMENTO DE DADOS (PRESERVADO) ---
tickers_map = {
    "PETR4.SA": "PETR4.SA", "VALE3.SA": "VALE3.SA", "MXRF11.SA": "MXRF11.SA", 
    "BTC-USD": "BTC-USD", "Nvidia": "NVDA", "Jóias (Ouro)": "GC=F", 
    "Nióbio": "NGLOY", "Grafeno": "FGPHF", "Câmbio USD/BRL": "USDBRL=X"
}

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.40

# --- NOVO: ESTADO PARA PREÇO TETO ---
if 'precos_teto' not in st.session_state:
    st.session_state.precos_teto = {k: 0.0 for k in tickers_map.keys()}

dados_radar = []
for nome_exibicao, t in tickers_map.items():
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                p_atual = (p_atual / 31.1035) * cambio_hoje if t == "GC=F" else p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0

            # Lógica de Margem de Segurança (Preço Teto)
            teto = st.session_state.precos_teto.get(nome_exibicao, 0.0)
            margem_status = "✅ OK" if teto == 0 or p_atual <= teto else "❌ CARO"

            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 and margem_status == "✅ OK" else "⚠️ ESPERAR"

            dados_radar.append({
                "Ativo": nome_exibicao, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", 
                "Média 30d": f"{m_30:.2f}", "Status": status, "Ação": acao,
                "Margem": margem_status, "V_Cru": p_atual, "Var_Min": variacoes.min(), 
                "Var_Max": variacoes.max(), "Dias_A": (variacoes > 0).sum(), 
                "Dias_B": (variacoes < 0).sum(), "Var_H": var_hoje
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)

if 'carteira' not in st.session_state:
    st.session_state.carteira = {}

# ==================== ABA 1: PAINEL DE CONTROLE (ADICIONADO CONFIG DE TETO) ====================
with tab_painel:
    with st.expander("🎯 Configurar Preço Teto (Margem de Segurança)"):
        st.write("Defina o valor máximo que aceita pagar por cada ativo.")
        c_teto = st.columns(3)
        for idx, nome in enumerate(tickers_map.keys()):
            with c_teto[idx % 3]:
                st.session_state.precos_teto[nome] = st.number_input(f"Teto {nome}:", min_value=0.0, value=st.session_state.precos_teto[nome], key=f"teto_in_{nome}")

    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Média 30d</th><th>Margem</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Média 30d']}</td><td>{r['Margem']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)

    # --- RESTANTE DO PAINEL (PRESERVADO) ---
    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
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

        st.markdown("---")
        st.subheader("💰 Patrimônio Global")
        with st.sidebar:
            st.header("⚙️ Outros Bens")
            g_joias = st.number_input("Ouro Físico (g):", value=0.0)
            v_bens = st.number_input("Outros Bens (R$):", value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['V_Cru'].values[0])
        patri_global = v_ativos_atualizado + troco_real + (g_joias * p_ouro) + v_bens
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (Saldo XP)", f"R$ {troco_real:,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")
        st.line_chart(df_grafico)

# ==================== ABA 2: ESTRATÉGIA HULI (PRESERVADA) ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli: Próximos Passos")
    valor_aporte = st.number_input("Quanto você pretende investir este mês? (R$):", min_value=0.0, value=0.0, step=100.0)

    if not ativos_sel:
        st.warning("Selecione seus ativos na aba 'Painel de Controle' primeiro.")
    else:
        st.subheader("📊 1. Defina sua Alocação Ideal (%)")
        metas = {}
        cols_metas = st.columns(len(ativos_sel))
        for i, nome in enumerate(ativos_sel):
            with cols_metas[i]:
                metas[nome] = st.slider(f"{nome} (%)", 0, 100, 100 // len(ativos_sel), key=f"meta_{nome}")
        
        soma_metas = sum(metas.values())
        if soma_metas == 100:
            st.subheader("📈 2. Plano de Rebalanceamento")
            plano_huli = []
            for nome in ativos_sel:
                v_atual = st.session_state.carteira[nome]["atual"]
                porc_atual = (v_atual / v_ativos_atualizado * 100) if v_ativos_atualizado > 0 else 0
                meta_porc = metas[nome]
                valor_ideal = (v_ativos_atualizado + valor_aporte) * (meta_porc / 100)
                necessidade = valor_ideal - v_atual
                decisao = "✅ APORTAR" if necessidade > 0 else "✋ AGUARDAR"
                sugestao_valor = f"R$ {necessidade:.2f}" if necessidade > 0 else "---"
                plano_huli.append({"Ativo": nome, "Atual (%)": f"{porc_atual:.1f}%", "Meta (%)": f"{meta_porc:.0f}%", "Decisão": decisao, "Quanto Comprar": sugestao_valor})
            st.table(pd.DataFrame(plano_huli))

            st.markdown("---")
            st.subheader("🏁 Meta de Sobrevivência")
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                custo_mensal = st.number_input("Custo de vida mensal (R$):", min_value=0.0, value=3000.0)
                renda_mensal_estimada = st.slider("Rendimento mensal da carteira (%)", 0.1, 2.0, 0.8)
            pat_necessario = custo_mensal / (renda_mensal_estimada / 100)
            progresso = (patri_global / pat_necessario) * 100 if pat_necessario > 0 else 0
            with col_meta2:
                st.metric("Patrimônio Alvo", f"R$ {pat_necessario:,.2f}")
            st.progress(min(progresso/100, 1.0))

# ==================== ABA 3: CARTEIRA MODELO HULI (PRESERVADA) ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("• Energia: TAEE11, EGIE3 | • Saneamento: SAPR11 | • Bancos: BBAS3")
    with col2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda</b></div>', unsafe_allow_html=True)
        st.write("• Ouro | • Dólar | • Tesouro Selic")

# ==================== ABA 4: MANUAL DIDÁTICO (PRESERVADO) ====================
with tab_manual:
    st.header("📖 Guia de Operação - Sistema Rockefeller")
    st.markdown("### 1. Radar e Preço Teto")
    st.markdown("""<div class="manual-section"><b>Margem ✅ OK:</b> O preço está abaixo do seu Teto definido. 
    <b>Ação ✅ COMPRAR:</b> Só aparece se o ativo estiver barato E dentro da margem.</div>""", unsafe_allow_html=True)
