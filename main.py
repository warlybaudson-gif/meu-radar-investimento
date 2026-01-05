import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Estilo Total Black, Mobile e Tabelas
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 12px !important; color: #ffffff !important; border-collapse: collapse !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; white-space: nowrap !important; padding: 8px 4px !important; }
    td { background-color: #000000 !important; color: #ffffff !important; white-space: nowrap !important; border-bottom: 1px solid #222 !important; padding: 8px 4px !important; }
    .stTable { overflow-x: auto !important; display: block !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_radar = []
dados_volatilidade = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            m_30 = hist_30d['Close'].mean()
            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            
            variacoes = hist_30d['Close'].pct_change() * 100
            subidas = (variacoes > 0).sum()
            descidas = (variacoes < 0).sum()
            maior_alta = variacoes.max()
            maior_queda = variacoes.min()
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0
            
            # Alerta de recorde de queda
            is_recorde = "🚨 RECORDE" if var_hoje <= (maior_queda * 0.98) and var_hoje < 0 else ""
            
            dados_radar.append({
                "Ativo": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": status, "Ação": acao, "Div. 12m": divs, "Var_Hoje": var_hoje
            })
            dados_volatilidade.append({
                "Ativo": t, "Dias A/B": f"🟢{subidas}/🔴{descidas}", 
                "Pico": f"+{maior_alta:.2f}%", "Fundo": f"{maior_queda:.2f}%", "Alerta": is_recorde
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    # 1. RADAR
    st.subheader("🛰️ Radar de Ativos")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp.drop(columns=["Var_Hoje"]))

    # 2. TERMÔMETRO DE GANÂNCIA
    st.markdown("---")
    st.subheader("🌡️ Termômetro de Ganância")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    t1, t2 = st.columns([1, 2])
    with t1:
        if score <= 25: st.error("😨 MEDO EXTREMO")
        elif score <= 50: st.warning("⚖️ NEUTRO / CAUTELA")
        elif score <= 75: st.info("🤑 GANÂNCIA")
        else: st.success("🚀 EUFORIA TOTAL")
    with t2:
        st.progress(score / 100)
        st.write(f"Índice de Ganância: **{score:.0f}%**")

    # 3. RAIO-X DE VOLATILIDADE
    st.markdown("---")
    st.subheader("📊 Raio-X de Volatilidade (30 Dias)")
    st.table(df_vol)

    # 4. RESUMO IA E ALERTAS
    st.markdown("---")
    col_ia, col_alerta = st.columns([1.5, 1])
    with col_ia:
        st.subheader("🤖 Resumo Rockefeller")
        recorde_ativo = df_vol[df_vol['Alerta'] == "🚨 RECORDE"]
        if not recorde_ativo.empty:
            st.error(f"🚨 **RECORDE DE QUEDA:** {recorde_ativo.iloc[0]['Ativo']} atingiu o fundo do mês!")
        else:
            df_radar['Desconto'] = (df_radar['Preço'] / df_radar['Média 30d']) - 1
            if not df_radar.empty:
                melhor = df_radar.sort_values(by='Desconto').iloc[0]
                st.info(f"Oportunidade técnica em **{melhor['Ativo']}** ({abs(melhor['Desconto']*100):.1f}% abaixo da média).")

    with col_alerta:
        st.subheader("🎯 Alerta de Alvo")
        ativo_alvo = st.selectbox("Ativo:", tickers, key="alvo")
        p_alvo = st.number_input("Me avise em (R$):", value=0.0)
        p_agora = df_radar[df_radar['Ativo'] == ativo_alvo]['Preço'].values[0] if not df_radar.empty else 0
        if p_alvo > 0 and p_agora <= p_alvo: st.success("🚀 ALVO ATINGIDO!")

    # 5. GESTOR XP COMPLETO
    st.markdown("---")
    st.subheader("🧮 Gestor XP (Foco PETR4)")
    c_in, c_out = st.columns([1, 1.2])
    with c_in:
        with st.expander("Configurar Ordem", expanded=True):
            v_env = st.number_input("Valor Enviado (R$):", value=50.0)
            p_sug = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0] if not df_radar.empty else 31.0
            p_pg = st.number_input("Preço da Cota (R$):", value=float(p_sug))
            c_at = st.number_input("Cotas Atuais:", value=0)
            pm_at = st.number_input("PM Atual:", value=0.0)
    
    with c_out:
        n_cotas = int(v_env // p_pg)
        troco = v_env % p_pg
        p_mkt = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0] if not df_radar.empty else p_pg
        patri = (n_cotas * p_mkt) + troco
        n_pm = ((c_at * pm_at) + (n_cotas * p_pg)) / (c_at + n_cotas) if (c_at + n_cotas) > 0 else 0
        
        m1, m2 = st.columns(2)
        m1.metric("Cotas Novas", f"{n_cotas} un")
        m2.metric("Troco", f"R$ {troco:.2f}")
        st.metric("Patrimônio Total", f"R$ {patri:.2f}", f"R$ {patri - v_env:.2f}")
        if c_at > 0: st.metric("Novo Preço Médio", f"R$ {n_pm:.2f}")

    # 6. RENDA E GRÁFICO
    st.markdown("---")
    col_renda, col_grafico = st.columns([1, 1.5])
    with col_renda:
        st.subheader("💰 Renda Passiva")
        a_div = st.selectbox("Ativo:", tickers, index=2)
        q_s = st.number_input("Minhas Cotas:", value=100, key="q_renda")
        v_div = df_radar[df_radar['Ativo'] == a_div]['Div. 12m'].values[0] if not df_radar.empty else 0
        st.metric(f"Receita Est. {a_div}", f"R$ {(v_div * q_s / 12):.2f}/mês")
    
    with col_grafico:
        st.subheader("📈 Tendência")
        sel = st.selectbox("Ativo:", tickers, key="graf")
        st.line_chart(yf.Ticker(sel).history(period="30d")['Close'])

# ==================== ABA 2: MANUAL DIDÁTICO COMPLETO ====================
with tab_manual:
    st.header("📖 Manual de Instruções - IA Rockefeller")
    st.write("Este guia explica como interpretar cada ferramenta do seu painel para tomar as melhores decisões financeiras.")

    with st.expander("🛰️ 1. Radar de Ativos", expanded=True):
        st.markdown("""
        **O que é:** Monitoramento em tempo real dos preços atuais comparados à média dos últimos 30 dias.
        * **Preço:** Valor atual da cota na Bolsa neste momento.
        * **Média 30d:** Preço médio do ativo no último mês, servindo como uma linha de 'preço justo'.
        * **Status 🔥 BARATO:** Significa que o preço atual está abaixo da média mensal, indicando uma oportunidade de compra.
        * **Status 💎 CARO:** Significa que o preço está acima da média, sugerindo cautela.
        """)

    with st.expander("🌡️ 2. Termômetro de Ganância"):
        st.markdown("""
        **O que é:** Um indicador visual do sentimento geral do mercado baseado nos ativos da sua lista.
        * **Como funciona:** Ele mede a proporção de ativos que estão 'Caros' no momento.
        * **Medo (0-25%):** Grande parte dos ativos está barata. É o melhor momento para investir.
        * **Euforia (75-100%):** Quase tudo está caro. O risco de uma queda é maior.
        """)

    with st.expander("📊 3. Raio-X de Volatilidade"):
        st.markdown("""
        **O que é:** Analisa o comportamento e a segurança de cada ativo nos últimos 30 dias.
        * **Dias Alta/Baixa:** Quantas vezes o ativo subiu ou caiu no mês.
        * **Pico Mensal:** A maior alta registrada no período.
        * **Fundo Mensal:** O menor preço atingido no mês.
        * **Alerta 🚨 RECORDE:** Aciona quando o preço de hoje bate o fundo mensal, sinalizando uma oportunidade rara.
        """)

    with st.expander("🧮 4. Gestor XP (Simulador de Ordens)"):
        st.markdown("""
        **O que é:** Ferramenta para calcular o impacto financeiro da sua compra antes de executá-la.
        * **Valor Enviado:** O montante que você transferiu para a corretora.
        * **Troco:** O saldo que sobrará em dinheiro na sua conta da corretora.
        * **Patrimônio Total:** Valor das suas cotas a preço de mercado + o troco.
        * **Novo Preço Médio:** O novo custo unitário das suas ações somando as antigas com as novas.
        """)

    with st.expander("🚀 5. Entendendo o Crescimento (PETR4)"):
        st.markdown("""
        **O que é:** Explicação sobre como o seu patrimônio realmente aumenta com o tempo.
        * **Valorização:** O aumento do preço da cota na Bolsa.
        * **Dividendos:** Dinheiro que a empresa deposita na sua conta apenas por você ser sócio.
        * **Retorno Total:** A soma da valorização + os dividendos recebidos no ano.
        """)
