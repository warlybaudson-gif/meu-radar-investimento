import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO
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
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")
tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS ---
tickers_map = {
    "PETR4.SA": "PETR4.SA", "VALE3.SA": "VALE3.SA", "MXRF11.SA": "MXRF11.SA", 
    "BTC-USD": "BTC-USD", "Nvidia": "NVDA", "Jóias (Ouro)": "GC=F", 
    "Nióbio": "NGLOY", "Grafeno": "FGPHF", "Câmbio USD/BRL": "USDBRL=X"
}

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.37

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

            # Lógica da Ação
            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"

            dados_radar.append({
                "Ativo": nome_exibicao, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", 
                "Média 30d": f"{m_30:.2f}", "Status": status, "Ação": acao,
                "V_Cru": p_atual, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(),
                "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(), "Var_H": var_hoje,
                "Div_Ano": ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)

with tab_painel:
    # 🛰️ RADAR (COM COLUNA AÇÃO)
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Média 30d</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Média 30d']}</td><td>{r['Status']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)

    # 📊 RAIO-X
    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    # 🌡️ TERMÔMETRO
    st.subheader("🌡️ Sentimento de Mercado")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    st.progress(score / 100)
    st.write(f"Índice de Ativos Caros: **{int(score)}%**")

    # 🧮 GESTOR
    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=0.0, step=100.0)
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])

    total_investido_acumulado = 0
    v_ativos_atualizado = 0
    renda_total = 0
    lista_c = []
    df_grafico = pd.DataFrame()
    
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
                renda_total += (info["Div_Ano"] * qtd) / 12
                lista_c.append({"Ativo": nome, "Qtd": qtd, "PM": f"{pm_calc:.2f}", "Valor Atual": f"{v_agora:.2f}", "Lucro": f"{lucro:.2f}"})
                df_grafico[nome] = yf.Ticker(info["Ticker_Raw"]).history(period="30d")['Close']

        troco_real = capital_xp - total_investido_acumulado

        html_c = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']}</td><td>R$ {r['Valor Atual']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c])}</tbody>
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
        m1.metric("Valor em Ativos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (Saldo XP)", f"R$ {troco_real:,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")
        st.line_chart(df_grafico)
        
        # ==================== ABA: ESTRATÉGIA TIO HULI ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli: Próximos Passos")
    st.write("Não compre o que você quer, compre o que sua carteira precisa para manter o equilíbrio.")
    
    # Entrada do Aporte Mensal
    valor_aporte = st.number_input("Quanto você pretende investir este mês? (R$):", min_value=0.0, value=0.0, step=100.0)

    if not ativos_sel:
        st.warning("Selecione seus ativos na aba 'Painel de Controle' primeiro.")
    else:
        st.markdown("---")
        st.subheader("📊 1. Defina sua Alocação Ideal (%)")
        
        metas = {}
        cols_metas = st.columns(len(ativos_sel))
        for i, nome in enumerate(ativos_sel):
            with cols_metas[i]:
                metas[nome] = st.slider(f"{nome} (%)", 0, 100, 100 // len(ativos_sel), key=f"meta_{nome}")
        
        soma_metas = sum(metas.values())
        if soma_metas != 100:
            st.error(f"⚠️ A soma das metas é {soma_metas}%. Ajuste para fechar em 100%.")
        else:
            st.markdown("---")
            st.subheader("📈 2. Plano de Rebalanceamento")
            
            plano_huli = []
            for nome in ativos_sel:
                # Recupera o valor atualizado que calculamos na aba Painel
                v_atual = st.session_state.carteira[nome]["atual"]
                porc_atual = (v_atual / v_ativos_atualizado * 100) if v_ativos_atualizado > 0 else 0
                meta_porc = metas[nome]
                
                # Cálculo da "fatia" ideal considerando o novo aporte
                valor_ideal = (v_ativos_atualizado + valor_aporte) * (meta_porc / 100)
                necessidade = valor_ideal - v_atual
                
                decisao = "✅ APORTAR" if necessidade > 0 else "✋ AGUARDAR"
                sugestao_valor = f"R$ {necessidade:.2f}" if necessidade > 0 else "---"

                plano_huli.append({
                    "Ativo": nome,
                    "Atual (%)": f"{porc_atual:.1f}%",
                    "Meta (%)": f"{meta_porc:.0f}%",
                    "Decisão": decisao,
                    "Quanto Comprar": sugestao_valor
                })
            
            st.table(pd.DataFrame(plano_huli))

# ==================== ABA 2: MANUAL DIDÁTICO (COLOQUE ABAIXO DA HULI) ====================
with tab_manual:
    st.header("📖 Guia de Operação - Sistema Rockefeller")
    # ... (Cole aqui aquele código longo do manual que te passei antes)

# ==================== ABA 2: MANUAL DIDÁTICO (ORIGINAL COMPLETO) ====================
with tab_manual:
    st.header("📖 Guia de Operação - Sistema Rockefeller")
    st.write("Siga este manual para interpretar os dados e gerir sua riqueza com precisão matemática.")

    st.markdown("### 1. Radar de Ativos (Inteligência de Preço)")
    st.markdown("""
    <div class="manual-section">
    Este módulo identifica distorções de preço no curto prazo.
    <ul>
        <li><b>Preço (R$):</b> Valor atual de mercado. Ativos em dólar são convertidos automaticamente para a moeda local.</li>
        <li><b>Média 30d:</b> O ponto de equilíbrio. Representa o valor médio do ativo no último mês.</li>
        <li><b>Status 🔥 BARATO:</b> O preço atual está abaixo da média. Indica uma <b>oportunidade de compra</b> técnica.</li>
        <li><b>Status 💎 CARO:</b> O preço está acima da média. Indica que o mercado pode estar supervalorizado no momento.</li>
        <li><b>Ação ✅ COMPRAR:</b> Sugestão automática quando o preço cai abaixo da média histórica recente.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 2. Raio-X de Volatilidade (Análise de Risco)")
    st.markdown("""
    <div class="manual-section">
    Entenda a "agressividade" do mercado nos últimos 30 dias para evitar entrar em momentos de queda livre.
    <ul>
        <li><b>Dias A/B:</b> Placar de dias que o ativo fechou em alta (🟢) versus dias que fechou em baixa (🔴).</li>
        <li><b>Pico e Fundo:</b> Mostra a variação máxima positiva e negativa registrada no período de 30 dias.</li>
        <li><b>Alerta 🚨 RECORDE:</b> Indica que o preço hoje atingiu a <b>mínima absoluta</b> dos últimos 30 dias. É um sinal de possível reversão.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 3. Gestor de Carteira Dinâmica")
    st.markdown("""
    <div class="manual-section">
    Onde você controla seus investimentos reais e monitora seu saldo disponível.
    <ul>
        <li><b>Capital Total XP:</b> Digite aqui o montante total de dinheiro que você tem depositado na corretora.</li>
        <li><b>Investimento Total:</b> Ao preencher quanto você gastou em cada ativo, o sistema subtrai esse valor do seu Capital Total para gerar o <b>Troco (Saldo Livre)</b>.</li>
        <li><b>PM (Auto):</b> O Preço Médio é calculado automaticamente dividindo o seu investimento pela quantidade de cotas.</li>
        <li><b>Lucro/Prejuízo:</b> Comparação exata entre o seu custo de aquisição e o valor que o mercado está pagando agora.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 4. Patrimônio Global")
    st.markdown("""
    <div class="manual-section">
    A visão final e consolidada do seu império financeiro.
    <ul>
        <li><b>Troco (Saldo XP):</b> O dinheiro que não está em ações e está parado, pronto para novas oportunidades.</li>
        <li><b>Ouro e Bens:</b> Bens físicos que são somados ao seu valor líquido de mercado em tempo real.</li>
        <li><b>Patrimônio Total:</b> A soma de TUDO: Saldo Livre + Valor Atualizado das Ações + Ouro + Outros Bens Físicos.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

