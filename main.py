import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Forçar cor branca em todas as tabelas e textos para evitar letras escuras */
    .stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; }
    
    .mobile-table-container { overflow-x: auto; width: 100%; }

    .rockefeller-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Courier New', Courier, monospace;
        margin-bottom: 20px;
    }
    .rockefeller-table th {
        background-color: #1a1a1a;
        color: #58a6ff !important;
        text-align: center !important;
        padding: 12px;
        border-bottom: 2px solid #333;
    }
    .rockefeller-table td {
        padding: 10px;
        text-align: center !important;
        border-bottom: 1px solid #222;
    }
    
    div[data-testid="stMetric"] { 
        background-color: #111111; 
        border: 1px solid #333333; 
        border-radius: 8px;
        text-align: center;
    }
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
tickers = list(tickers_map.values())
dados_radar = []
dados_volatilidade = []

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.40 

for nome_exibicao, t in tickers_map.items():
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio_hoje
                else: p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0

            dados_radar.append({
                "Ativo": nome_exibicao, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", 
                "Média 30d": f"{m_30:.2f}", "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO", 
                "Ação": "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR", "Div_Ano": divs
            })
            
            dados_volatilidade.append({
                "Ativo": nome_exibicao, "Dias A/B": f"🟢{(variacoes > 0).sum()} / 🔴{(variacoes < 0).sum()}", 
                "Pico": f"+{variacoes.max():.2f}%", "Fundo": f"{variacoes.min():.2f}%", 
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else "Normal"
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""
    <div class="mobile-table-container">
        <table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Média 30d</th><th>Status</th><th>Ação</th></tr></thead>
            <tbody>
                {"".join([f"<tr><td>{row['Ativo']}</td><td>{row['Preço']}</td><td>{row['Média 30d']}</td><td>{row['Status']}</td><td>{row['Ação']}</td></tr>" for _, row in df_radar.iterrows()])}
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_radar, unsafe_allow_html=True)

    c_term, c_vol = st.columns([1, 1.5])
    with c_term:
        st.subheader("🌡️ Sentimento")
        caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
        score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
        st.progress(score / 100)
        st.write(f"Índice: **{int(score)}%**")
    with c_vol:
        st.subheader("📊 Raio-X de Volatilidade")
        st.table(df_vol) # O CSS agora força cor branca aqui

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    ativos_selecionados = st.multiselect("Habilite seus ativos:", options=df_radar["Ativo"].unique(), default=["PETR4.SA"])

    if ativos_selecionados:
        lista_c = []
        renda_total = 0
        v_ativos_total = 0
        df_grafico = pd.DataFrame() # Preparação para o gráfico dinâmico
        
        st.write("📝 **Configure suas posições:**")
        cols = st.columns(2)
        
        for i, nome in enumerate(ativos_selecionados):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=1, key=f"q_{nome}")
                pm = st.number_input(f"PM (R$):", min_value=0.0, value=0.0, step=0.01, key=f"p_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                t_raw = info["Ticker_Raw"]
                p_val = float(info["Preço"])
                v_agora = qtd * p_val
                lucro = (p_val - pm) * qtd if pm > 0 else 0
                r_mes = (info["Div_Ano"] * qtd) / 12
                
                lista_c.append({
                    "Ativo": nome, "Qtd": qtd, "Custo Total": f"{pm*qtd:.2f}", 
                    "Valor Atual": f"{v_agora:.2f}", "Lucro/Prej": f"{lucro:.2f}", 
                    "Renda/Mês": f"{r_mes:.2f}"
                })
                renda_total += r_mes
                v_ativos_total += v_agora
                
                # Coleta dados para o gráfico dinâmico
                df_grafico[nome] = yf.Ticker(t_raw).history(period="30d")['Close']

        st.table(pd.DataFrame(lista_c))

        st.markdown("---")
        st.subheader("💰 Patrimônio Global")
        with st.sidebar:
            st.header("⚙️ Ajustes")
            v_na_xp = st.number_input("Saldo na XP (R$):", value=0.0)
            g_joias = st.number_input("Ouro (g):", value=0.0)
            v_minerais = st.number_input("Bens (R$):", value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0])
        patri_global = v_ativos_total + v_na_xp + (g_joias * p_ouro) + v_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Ações/FIIs", f"R$ {v_ativos_total:,.2f}")
        m2.metric("Renda Passiva", f"R$ {renda_total:,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")

        # GRÁFICO DINÂMICO DOS ATIVOS HABILITADOS
        st.markdown("---")
        st.subheader("📈 Comparativo de Performance (Ativos Habilitados)")
        st.line_chart(df_grafico)

# ==================== ABA 2: MANUAL DE INSTRUÇÕES ====================
with tab_manual:
    st.header("📖 Manual de Instruções - IA Rockefeller")
    with st.expander("🛰️ ITEM 1: Radar de Ativos Estratégicos", expanded=True):
        st.markdown("Identifica o momento de compra comparando Preço atual vs Média de 30 dias.")
    with st.expander("📊 ITEM 2: Raio-X de Volatilidade"):
        st.markdown("Analisa o risco e a frequência de altas/baixas no mês corrente.")
    with st.expander("🧮 ITEM 3: Gestor de Carteira Dinâmica"):
        st.markdown("Gerencie lucro real e dividendos apenas dos ativos que você possui na carteira.")
    with st.expander("💰 ITEM 4: Patrimônio Global"):
        st.markdown("Consolidação total de riqueza: Bolsa + Saldo Bancário + Bens Físicos.")
