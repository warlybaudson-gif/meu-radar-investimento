import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÕES DE IDENTIDADE E LAYOUT
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. ESTILO TOTAL BLACK (IDENTIDADE VISUAL)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 12px !important; color: #ffffff !important; border-collapse: collapse !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; white-space: nowrap !important; padding: 8px 4px !important; }
    td { background-color: #000000 !important; color: #ffffff !important; white-space: nowrap !important; border-bottom: 1px solid #222 !important; padding: 8px 4px !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 10px; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Consolidação Yahoo Finance) ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "USDBRL=X"]
dados_radar = []
dados_volatilidade = []

try:
    # Busca o câmbio para converter Nvidia e Ouro
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.20 

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            # Conversão para Ativos Globais
            if t in ["NVDA", "GC=F"]:
                if t == "GC=F": 
                    p_atual = (p_atual / 31.1035) * cambio_hoje # Onça para Grama em R$
                else: 
                    p_atual = p_atual * cambio_hoje # USD para R$
            
            m_30 = hist_30d['Close'].mean()
            if t == "NVDA": m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X"] else 0.0
            
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0
            
            nome_exibicao = "Jóias (Ouro)" if t == "GC=F" else ("Nvidia" if t == "NVDA" else t)

            dados_radar.append({
                "Ativo": nome_exibicao, "Ticker_Raw": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": status, "Ação": acao, "Div. 12m": divs, "Var_Hoje": var_hoje,
                "Maior_Queda": variacoes.min(), "Subidas": (variacoes > 0).sum(), "Descidas": (variacoes < 0).sum()
            })
            dados_volatilidade.append({
                "Ativo": nome_exibicao, "Dias A/B": f"🟢{(variacoes > 0).sum()}/🔴{(variacoes < 0).sum()}", 
                "Pico": f"+{variacoes.max():.2f}%", "Fundo": f"{variacoes.min():.2f}%", 
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else ""
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    # 1. RADAR DE ATIVOS
    st.subheader("🛰️ Radar de Ativos")
    df_disp = df_radar.copy()
    for c in ["Preço", "Média 30d", "Div. 12m"]: df_disp[c] = df_disp[c].apply(lambda x: f"R$ {x:.2f}")
    st.table(df_disp[["Ativo", "Preço", "Média 30d", "Status", "Ação", "Div. 12m"]])

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

    # 4. GESTOR DE PATRIMÔNIO REAL (XP + ATIVOS FÍSICOS)
    st.markdown("---")
    st.subheader("🧮 Gestor de Patrimônio Real")
    c_in, c_out = st.columns([1, 1.2])
    with c_in:
        with st.expander("Configurar Carteira", expanded=True):
            v_env = st.number_input("Saldo na XP (R$):", value=50.0)
            g_joias = st.number_input("Jóias (Gramas de Ouro):", value=0.0)
            v_minerais = st.number_input("Minerais Raros (R$):", value=0.0)
            st.write("---")
            p_sug = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0] if not df_radar.empty else 30.0
            p_pg = st.number_input("Preço de Compra/Cota (R$):", value=float(p_sug))
            c_at = st.number_input("Cotas Atuais:", value=0)
            pm_at = st.number_input("PM Atual:", value=0.0)
    
    with c_out:
        p_ouro_grama = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0] if not df_radar.empty else 0
        val_joias_total = g_joias * p_ouro_grama
        n_cotas = int(v_env // p_pg)
        troco = v_env % p_pg
        patri_total = (n_cotas * p_pg) + troco + val_joias_total + v_minerais
        n_pm = ((c_at * pm_at) + (n_cotas * p_pg)) / (c_at + n_cotas) if (c_at + n_cotas) > 0 else 0
        
        m1, m2 = st.columns(2)
        m1.metric("Cotas Novas", f"{n_cotas} un")
        m2.metric("Valor em Jóias", f"R$ {val_joias_total:.2f}")
        
        st.metric("PATRIMÔNIO CONSOLIDADO", f"R$ {patri_total:.2f}", f"Troco em Conta: R$ {troco:.2f}")
        if c_at > 0: st.metric("Novo Preço Médio (XP)", f"R$ {n_pm:.2f}")

    # 5. RENDA E TENDÊNCIA
    st.markdown("---")
    col_renda, col_grafico = st.columns([1, 1.5])
    with col_renda:
        st.subheader("💰 Renda Passiva")
        a_div = st.selectbox("Simular Ativo:", df_radar['Ativo'].unique(), index=2)
        q_s = st.number_input("Minhas Cotas:", value=100)
        v_div = df_radar[df_radar['Ativo'] == a_div]['Div. 12m'].values[0]
        st.metric(f"Receita Est. {a_div}", f"R$ {(v_div * q_s / 12):.2f}/mês")
    
    with col_grafico:
        st.subheader("📈 Tendência")
        sel_graf = st.selectbox("Analisar gráfico de:", df_radar['Ativo'].unique())
        tick_final = df_radar[df_radar['Ativo'] == sel_graf]['Ticker_Raw'].values[0]
        st.line_chart(yf.Ticker(tick_final).history(period="30d")['Close'])

# ==================== ABA 2: MANUAL DIDÁTICO COMPLETO ====================
with tab_manual:
    st.header("📖 Guia Estratégico IA Rockefeller")
    st.write("Este manual detalha cada pilar do sistema para que você tome decisões baseadas em dados, não em emoções.")

    with st.expander("🛰️ 1. Radar de Ativos (Inteligência de Mercado)", expanded=True):
        st.markdown("""
        O Radar monitora o preço justo de cada ativo comparando-o com seu histórico recente.
        * **Preço Atual:** Valor em tempo real (Nvidia e Ouro convertidos para Real).
        * **Média 30d:** A 'linha de equilíbrio' do preço no último mês.
        * **Status 🔥 BARATO:** O ativo caiu abaixo da média mensal. Oportunidade técnica de compra.
        * **Status 💎 CARO:** O ativo subiu além da média. Momento de cautela.
        * **Ação:** Recomendação direta baseada no preço vs. média.
        """)

    with st.expander("🌡️ 2. Termômetro de Ganância (Sentimento das Massas)"):
        st.markdown("""
        Indica se o mercado está em um momento de otimismo exagerado ou pessimismo extremo.
        * **Medo (0-25%):** Maioria dos ativos barata. Momento histórico de compra.
        * **Neutro (25-50%):** Equilíbrio. Mantenha sua estratégia de aportes regulares.
        * **Euforia (75-100%):** Quase tudo caro. Risco de bolha ou correção iminente.
        """)

    with st.expander("📊 3. Raio-X de Volatilidade (Análise de Risco)"):
        st.markdown("""
        Analisa a força e a queda de cada ativo nos últimos 30 dias.
        * **Dias A/B (🟢/🔴):** Quantas vezes o ativo fechou no positivo ou negativo no mês.
        * **Pico/Fundo:** Os valores máximos e mínimos atingidos. Útil para saber se você está comprando no topo.
        * **Alerta 🚨 RECORDE:** Dispara quando o ativo bate a menor mínima do mês hoje.
        """)

    with st.expander("🧮 4. Gestor de Patrimônio Real (Matemática da Riqueza)"):
        st.markdown("""
        Sua central de consolidação patrimonial.
        * **Ativos Digitais (XP):** Calcula quantas ações você pode comprar com seu saldo e qual será seu novo **Preço Médio (PM)**.
        * **Ativos Físicos (Jóias):** O sistema transforma gramas de ouro em valor financeiro atualizado pela bolsa de Nova York.
        * **Minerais Raros:** Espaço para incluir o valor de bens físicos que não oscilam na bolsa (pedras, coleções).
        * **Troco:** O saldo que permanecerá na sua conta após a execução da ordem sugerida.
        """)

    with st.expander("💰 5. Renda Passiva (O Caminho da Liberdade)"):
        st.markdown("""
        Calcula o quanto seus ativos trabalham para você.
        * **Dividend Yield:** Baseado no que o ativo pagou nos últimos 12 meses.
        * **Receita Mensal:** Projeção de quanto você recebe de 'aluguel' das suas ações e fundos imobiliários.
        """)

    st.info("💡 **Dica Rockefeller:** O segredo da riqueza não é prever o futuro, mas sim ter um sistema que reage aos dados do presente.")
