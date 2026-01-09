import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO PARA CELULAR E DESKTOP
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Evita quebra de texto e permite rolagem lateral em celulares */
    .stTable { overflow-x: auto !important; display: block !important; }
    table { width: 100% !important; border-collapse: collapse !important; white-space: nowrap !important; }
    
    th { background-color: #1a1a1a !important; color: #58a6ff !important; text-align: left !important; padding: 12px !important; }
    td { background-color: #000000 !important; color: #ffffff !important; padding: 10px !important; border-bottom: 1px solid #222 !important; }
    
    /* Ajuste de métricas para não quebrar em colunas pequenas */
    div[data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "NGLOY", "FGPHF", "USDBRL=X"]
dados_radar = []
dados_volatilidade = []

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.30 

for t in tickers:
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

            nomes_dict = {"GC=F": "Jóias (Ouro)", "NVDA": "Nvidia", "NGLOY": "Nióbio", "FGPHF": "Grafeno"}
            nome_display = nomes_dict.get(t, t)
            
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0

            dados_radar.append({
                "Ativo": nome_display, 
                "Ticker_Raw": t,
                "Preço": int(p_atual), # Retirado casas decimais conforme solicitado
                "Média 30d": round(m_30, 2), 
                "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO", 
                "Ação": "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR",
                "Div_Ano": round(divs, 2)
            })
            
            dados_volatilidade.append({
                "Ativo": nome_display, 
                "Dias A/B": f"🟢{(variacoes > 0).sum()} / 🔴{(variacoes < 0).sum()}", 
                "Pico": f"+{round(variacoes.max(), 2)}%", 
                "Fundo": f"{round(variacoes.min(), 2)}%", 
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else "Normal"
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    # Exibe preço sem decimais e média com 2
    st.table(df_radar[["Ativo", "Preço", "Média 30d", "Status", "Ação"]])

    c_term, c_vol = st.columns([1, 1.5])
    with c_term:
        st.subheader("🌡️ Sentimento")
        caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
        score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
        st.progress(score / 100)
        st.write(f"Índice: **{int(score)}%**")
    with c_vol:
        st.subheader("📊 Raio-X de Volatilidade")
        st.table(df_vol)

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    ativos_selecionados = st.multiselect("Habilite os ativos:", options=df_radar["Ativo"].unique(), default=["PETR4.SA"])

    if ativos_selecionados:
        lista_c = []
        renda_total = 0
        v_ativos_total = 0
        
        st.write("📝 **Configure suas posições:**")
        cols = st.columns(2) # Reduzido para 2 colunas para melhor visualização mobile
        
        for i, nome in enumerate(ativos_selecionados):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=1, key=f"q_{nome}")
                pm = st.number_input(f"PM (R$):", min_value=0.0, value=0.0, step=0.01, key=f"p_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                v_agora = qtd * info["Preço"]
                lucro = (info["Preço"] - pm) * qtd if pm > 0 else 0
                r_mes = (info["Div_Ano"] * qtd) / 12
                
                lista_c.append({
                    "Ativo": nome, "Qtd": qtd, "Custo Total": round(pm*qtd, 2), 
                    "Valor Atual": round(v_agora, 2), "Lucro/Prej": round(lucro, 2), 
                    "Renda/Mês": round(r_mes, 2)
                })
                renda_total += r_mes
                v_ativos_total += v_agora

        st.table(pd.DataFrame(lista_c))

        st.markdown("---")
        st.subheader("💰 Patrimônio Real")
        with st.sidebar:
            st.header("⚙️ Ajustes")
            v_na_xp = st.number_input("Saldo (R$):", value=0.0)
            g_joias = st.number_input("Ouro (g):", value=0.0)
            v_minerais = st.number_input("Bens (R$):", value=0.0)

        p_ouro = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0]
        patri_global = v_ativos_total + v_na_xp + (g_joias * p_ouro) + v_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa", f"R$ {v_ativos_total:,.2f}")
        m2.metric("Renda/Mês", f"R$ {renda_total:,.2f}")
        m3.metric("PATRIMÔNIO", f"R$ {patri_global:,.2f}")

    # RETORNO DO GRÁFICO
    st.markdown("---")
    st.subheader("📈 Tendência Visual")
    sel_graf = st.selectbox("Selecione o ativo para análise de 30 dias:", df_radar['Ativo'].unique())
    t_raw = df_radar[df_radar['Ativo'] == sel_graf]['Ticker_Raw'].values[0]
    st.line_chart(yf.Ticker(t_raw).history(period="30d")['Close'])

# ==================== ABA 2: MANUAL DE INSTRUÇÕES ====================
with tab_manual:
    st.header("📖 Guia Estratégico IA Rockefeller")
    
    st.subheader("1. Radar de Ativos")
    st.markdown("""
    **O que é:** Monitoramento em tempo real de preços vs médias históricas.
    - **Preço:** Valor atual de mercado (arredondado para facilitar a leitura rápida).
    - **Média 30d:** Referência de preço justo do último mês.
    - **Status 🔥 BARATO:** O preço está abaixo da média. Oportunidade de compra.
    """)

    st.subheader("2. Raio-X de Volatilidade")
    st.markdown("""
    **O que é:** Análise do risco e oscilação do ativo.
    - **Dias A/B:** Relação de dias que o ativo subiu (verde) versus dias que caiu (vermelho).
    - **Alerta 🚨 RECORDE:** Indica que o ativo está no preço mais baixo do mês, sinalizando um possível fundo.
    """)

    st.subheader("3. Gestor de Carteira Dinâmica")
    st.markdown("""
    **O que é:** Sua ferramenta de controle pessoal de lucro e renda.
    - **Multiselect:** Escolha apenas os ativos que você possui para habilitar o preenchimento.
    - **PM (Preço Médio):** Insira o valor pago para o sistema calcular seu lucro real.
    - **Renda/Mês:** Projeção de quanto você receberá em dividendos com base na sua quantidade.
    """)

    st.subheader("4. Patrimônio Global")
    st.markdown("""
    **O que é:** Consolidação de toda sua riqueza.
    - Soma investimentos, saldo em corretora e bens físicos (ouro/minerais) em um único valor final.
    """)
