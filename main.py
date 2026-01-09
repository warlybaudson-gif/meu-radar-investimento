import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E IDENTIDADE VISUAL
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

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

st.title("💰 IA Rockefeller - O Sistema Completo")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Radar, Volatilidade e Ativos Estratégicos) ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "NGLOY", "FGPHF", "USDBRL=X"]
dados_radar = []
dados_volatilidade = []

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.25 

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            # Conversões Internacionais
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio_hoje
                else: p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            nomes_dict = {"GC=F": "Jóias (Ouro)", "NVDA": "Nvidia", "NGLOY": "Nióbio", "FGPHF": "Grafeno"}
            nome_display = nomes_dict.get(t, t)
            
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0

            dados_radar.append({
                "Ativo": nome_display, "Ticker_Raw": t, "Preço": p_atual, "Média 30d": m_30, 
                "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO", "Ação": "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR",
                "Div_Ano": divs, "Var_Hoje": var_hoje
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
    # 1. RADAR E TERMÔMETRO
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    st.table(df_radar[["Ativo", "Preço", "Média 30d", "Status", "Ação"]])

    c_term, c_vol = st.columns([1, 1.5])
    with c_term:
        st.subheader("🌡️ Termômetro de Ganância")
        caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
        score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
        st.progress(score / 100)
        st.write(f"Índice: **{score:.0f}%**")
    with c_vol:
        st.subheader("📊 Raio-X de Volatilidade")
        st.table(df_vol)

    st.markdown("---")

    # 2. CARTEIRA DINÂMICA (A Mudança Solicitada)
    st.subheader("🧮 Gestor de Carteira Multiativos")
    ativos_escolhidos = st.multiselect("Habilite os ativos da sua carteira:", options=df_radar["Ativo"].unique(), default=["PETR4.SA"])

    if ativos_escolhidos:
        lista_c = []
        renda_total = 0
        valor_ativos_total = 0
        
        st.write("📝 **Configure seus ativos selecionados:**")
        cols = st.columns(len(ativos_escolhidos) if len(ativos_escolhidos) <= 3 else 3)
        
        for i, nome in enumerate(ativos_escolhidos):
            with cols[i % 3]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=1, key=f"q_{nome}")
                pm = st.number_input(f"PM (R$):", min_value=0.0, value=0.0, key=f"p_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                v_agora = qtd * info["Preço"]
                lucro = (info["Preço"] - pm) * qtd if pm > 0 else 0
                r_mes = (info["Div_Ano"] * qtd) / 12
                
                lista_c.append({"Ativo": nome, "Qtd": qtd, "Custo": f"R$ {pm*qtd:.2f}", "Valor Atual": f"R$ {v_agora:.2f}", "Lucro": f"R$ {lucro:.2f}", "Renda/Mês": f"R$ {r_mes:.2f}"})
                renda_total += r_mes
                valor_ativos_total += v_agora

        st.table(pd.DataFrame(lista_c))

        # 3. PATRIMÔNIO REAL E CÁLCULO DE TROCO (Gestor XP)
        st.markdown("---")
        st.subheader("💰 Consolidação de Patrimônio Real")
        with st.sidebar:
            st.header("⚙️ Ajustes de Saldo")
            v_na_xp = st.number_input("Saldo em Dinheiro na XP (R$):", value=50.0)
            g_joias = st.number_input("Jóias (Gramas Ouro):", value=0.0)
            v_minerais = st.number_input("Outros Minerais (R$):", value=0.0)

        p_ouro = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0]
        patri_global = valor_ativos_total + v_na_xp + (g_joias * p_ouro) + v_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total em Ativos", f"R$ {valor_ativos_total:.2f}")
        m2.metric("Renda Passiva Mensal", f"R$ {renda_total:.2f}")
        m3.metric("PATRIMÔNIO GLOBAL", f"R$ {patri_global:.2f}")

    # 4. GRÁFICOS DE TENDÊNCIA
    st.markdown("---")
    st.subheader("📈 Tendência e Análise Visual")
    sel_graf = st.selectbox("Ver gráfico de:", df_radar['Ativo'].unique())
    t_raw = df_radar[df_radar['Ativo'] == sel_graf]['Ticker_Raw'].values[0]
    st.line_chart(yf.Ticker(t_raw).history(period="30d")['Close'])

# ==================== ABA 2: MANUAL COMPLETO ====================
with tab_manual:
    st.header("📖 Manual Rockefeller V6")
    with st.expander("🛰️ 1. Radar e Novos Ativos", expanded=True):
        st.markdown("Monitora Nvidia, Ouro, Nióbio e Grafeno com conversão automática para Real.")
    with st.expander("🧮 2. Carteira Multiativos"):
        st.markdown("Use o Multiselect para habilitar ativos. Insira Qtd e PM para ver seu lucro real e renda passiva somada.")
    with st.expander("📊 3. Volatilidade e Alertas"):
        st.markdown("🚨 RECORDE avisa se o preço caiu abaixo da mínima dos últimos 30 dias.")
