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
# Tickers Originais + Nvidia + Ouro + Nióbio (NGLOY) + Grafeno (FGPHF)
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "NGLOY", "FGPHF", "USDBRL=X"]
dados_radar = []
dados_volatilidade = []

try:
    # Busca o câmbio atual para converter ativos em Dólar
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.25 

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            # Lógica de Conversão (Dólar -> Real)
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": 
                    p_atual = (p_atual / 31.1035) * cambio_hoje # Onça para Grama em R$
                else: 
                    p_atual = p_atual * cambio_hoje # USD para R$
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            # Nomes Amigáveis para o Painel
            nomes_dict = {
                "GC=F": "Jóias (Ouro)", "NVDA": "Nvidia (IA)", 
                "NGLOY": "Nióbio (Proxy)", "FGPHF": "Grafeno (Proxy)"
            }
            nome_display = nomes_dict.get(t, t)

            status = "🔥 BARATO" if p_atual < m_30 else "💎 CARO"
            acao = "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0
            
            dados_radar.append({
                "Ativo": nome_display, "Ticker_Raw": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": status, "Ação": acao, "Div. 12m": divs, "Var_Hoje": var_hoje,
                "Maior_Queda": variacoes.min(), "Subidas": (variacoes > 0).sum(), "Descidas": (variacoes < 0).sum()
            })
            dados_volatilidade.append({
                "Ativo": nome_display, "Dias A/B": f"🟢{(variacoes > 0).sum()}/🔴{(variacoes < 0).sum()}", 
                "Pico": f"+{variacoes.max():.2f}%", "Fundo": f"{variacoes.min():.2f}%", 
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else ""
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    # 1. RADAR DE ATIVOS
    st.subheader("🛰️ Radar de Ativos Consolidados")
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
    st.subheader("📊 Raio-X de Volatilidade (Ativos + Novos Ativos)")
    st.table(df_vol)

    # 4. GESTOR DE PATRIMÔNIO REAL
    st.markdown("---")
    st.subheader("🧮 Gestor de Patrimônio Real (XP + Novos Ativos)")
    c_in, c_out = st.columns([1, 1.2])
    with c_in:
        with st.expander("Configurar Carteira", expanded=True):
            v_env = st.number_input("Saldo na XP (R$):", value=50.0)
            g_joias = st.number_input("Jóias (Gramas Ouro):", value=0.0)
            v_minerais = st.number_input("Minerais Raros/Nióbio (R$):", value=0.0)
            st.write("---")
            p_sug = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0] if not df_radar.empty else 30.0
            p_pg = st.number_input("Preço de Compra/Cota (R$):", value=float(p_sug))
            c_at = st.number_input("Cotas Atuais (XP):", value=0)
            pm_at = st.number_input("Preço Médio Atual:", value=0.0)
    
    with c_out:
        p_ouro_hoje = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0] if not df_radar.empty else 0
        val_joias = g_joias * p_ouro_hoje
        n_cotas = int(v_env // p_pg)
        troco = v_env % p_pg
        patri_total = (n_cotas * p_pg) + troco + val_joias + v_minerais
        n_pm = ((c_at * pm_at) + (n_cotas * p_pg)) / (c_at + n_cotas) if (c_at + n_cotas) > 0 else 0
        
        m1, m2 = st.columns(2)
        m1.metric("Cotas Compráveis", f"{n_cotas} un")
        m2.metric("Valor em Jóias", f"R$ {val_joias:.2f}")
        
        st.metric("PATRIMÔNIO CONSOLIDADO", f"R$ {patri_total:.2f}", f"Troco: R$ {troco:.2f}")
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
    st.write("Manual completo para gestão de ativos digitais, metais preciosos e minerais de tecnologia.")

    with st.expander("🛰️ 1. Radar de Ativos (Inteligência Global)", expanded=True):
        st.markdown("""
        O Radar monitora o mercado e converte preços automaticamente.
        * **Nvidia e Ouro:** Cotação em tempo real convertida de Dólar para Real.
        * **Nióbio e Grafeno:** Rastreados através de mineradoras líderes (Anglo American e First Graphene).
        * **Status 🔥 BARATO:** O preço está abaixo da média de 30 dias. É uma oportunidade matemática.
        * **Ação:** ✅ COMPRAR indica que o ativo está em zona de desconto.
        """)

    with st.expander("🌡️ 2. Termômetro de Ganância"):
        st.markdown("""
        Indica o sentimento do mercado baseado na sua lista de ativos.
        * **Medo:** Hora de comprar o que está barato.
        * **Euforia:** Hora de ter cautela e não comprar no topo.
        """)

    with st.expander("🧮 3. Gestor de Patrimônio Real (Matemática da Riqueza)"):
        st.markdown("""
        Une todos os seus bens em um único número.
        * **Cotas e Troco:** Calcula o máximo de ações que você pode comprar na XP com seu saldo.
        * **Preço Médio (PM):** Informa como sua nova compra altera o seu custo histórico.
        * **Jóias e Minerais:** O sistema calcula o valor do seu ouro físico e permite adicionar o valor de minerais raros como Nióbio ou Grafeno físico.
        """)

    with st.expander("📊 4. Raio-X de Volatilidade"):
        st.markdown("""
        Analisa a segurança do ativo no mês.
        * **Pico/Fundo:** Os limites de preço do último mês.
        * **Alerta 🚨 RECORDE:** Aciona quando o preço atinge o ponto mais baixo dos últimos 30 dias.
        """)

    st.info("💡 **Dica:** Use o app para consolidar sua riqueza total, não apenas o que está na corretora.")
