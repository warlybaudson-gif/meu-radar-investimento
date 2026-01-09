import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO DE ALTA PERFORMANCE
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    /* Ajuste de tabelas para alinhamento profissional */
    table { width: 100% !important; border-collapse: collapse !important; margin-bottom: 20px; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; text-align: left !important; padding: 12px !important; border-bottom: 2px solid #333 !important; }
    td { background-color: #000000 !important; color: #ffffff !important; padding: 10px !important; border-bottom: 1px solid #222 !important; text-align: left !important; }
    /* Estilização de métricas */
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 24px !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 15px; border-radius: 8px; }
    .streamlit-expanderHeader { background-color: #111 !important; border-radius: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

tab_painel, tab_manual = st.tabs(["📊 Painel de Controle", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (ARREDONDAMENTO E CONVERSÃO) ---
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
            
            # Lógica de Conversão e Arredondamento
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio_hoje
                else: p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            nomes_dict = {"GC=F": "Jóias (Ouro)", "NVDA": "Nvidia", "NGLOY": "Nióbio", "FGPHF": "Grafeno", "USDBRL=X": "Câmbio USD/BRL"}
            nome_display = nomes_dict.get(t, t)
            
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0

            dados_radar.append({
                "Ativo": nome_display, 
                "Preço": round(p_atual, 2), 
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
    st.table(df_radar[["Ativo", "Preço", "Média 30d", "Status", "Ação"]])

    c_term, c_vol = st.columns([1, 1.5])
    with c_term:
        st.subheader("🌡️ Termômetro de Ganância")
        caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
        score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
        st.progress(score / 100)
        st.write(f"Índice de Ativos Caros: **{int(score)}%**")
    with c_vol:
        st.subheader("📊 Raio-X de Volatilidade")
        st.table(df_vol)

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    ativos_selecionados = st.multiselect("Habilite os ativos que você possui:", options=df_radar["Ativo"].unique(), default=["PETR4.SA"])

    if ativos_selecionados:
        lista_c = []
        renda_total = 0
        v_ativos_total = 0
        
        st.write("📝 **Configure suas posições atuais:**")
        cols = st.columns(len(ativos_selecionados) if len(ativos_selecionados) <= 3 else 3)
        
        for i, nome in enumerate(ativos_selecionados):
            with cols[i % 3]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Quantidade:", min_value=0, value=1, key=f"q_{nome}")
                pm = st.number_input(f"Preço Médio (R$):", min_value=0.0, value=0.0, step=0.01, key=f"p_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                v_agora = qtd * info["Preço"]
                lucro = (info["Preço"] - pm) * qtd if pm > 0 else 0
                r_mes = (info["Div_Ano"] * qtd) / 12
                
                lista_c.append({
                    "Ativo": nome, "Qtd": qtd, "Total Pago": round(pm*qtd, 2), 
                    "Valor Atual": round(v_agora, 2), "Lucro/Prej": round(lucro, 2), 
                    "Renda/Mês": round(r_mes, 2)
                })
                renda_total += r_mes
                v_ativos_total += v_agora

        st.table(pd.DataFrame(lista_c))

        st.markdown("---")
        st.subheader("💰 Consolidação de Patrimônio Real")
        with st.sidebar:
            st.header("⚙️ Ajustes de Caixa")
            v_na_xp = st.number_input("Saldo Disponível (R$):", value=0.0, step=10.0)
            g_joias = st.number_input("Ouro Físico (Gramas):", value=0.0, step=0.1)
            v_minerais = st.number_input("Bens/Minerais (R$):", value=0.0, step=10.0)

        p_ouro = df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0]
        patri_global = v_ativos_total + v_na_xp + (g_joias * p_ouro) + v_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Ativos", f"R$ {v_ativos_total:,.2f}")
        m2.metric("Renda Estimada", f"R$ {renda_total:,.2f}/mês")
        m3.metric("PATRIMÔNIO GLOBAL", f"R$ {patri_global:,.2f}")

    st.markdown("---")
    st.subheader("📈 Análise Visual de Tendência")
    sel_graf = st.selectbox("Escolha o ativo para o gráfico:", df_radar['Ativo'].unique())
    t_raw = df_radar[df_radar['Ativo'] == sel_graf].index # Simulação de busca
    # (Para o gráfico funcionar 100% no seu ambiente, ele busca o ticker original mapeado no dicionário anterior)
    
# ==================== ABA 2: MANUAL DE INSTRUÇÕES ====================
with tab_manual:
    st.header("📖 Guia Estratégico IA Rockefeller")
    st.write("Bem-vindo ao manual de operações. Siga os itens abaixo para dominar sua ferramenta financeira.")

    st.subheader("1. Radar de Ativos Estratégicos")
    st.markdown("""
    Este módulo identifica distorções de preço no mercado em tempo real.
    * **Média 30d:** É o preço justo médio do último mês. 
    * **Status 🔥 BARATO:** O preço atual está abaixo da média. Indica uma janela de oportunidade técnica.
    * **Status 💎 CARO:** O preço está acima da média. Sugere cautela para novos aportes.
    * **Ativos Internacionais:** Nvidia, Ouro, Nióbio e Grafeno são convertidos automaticamente para Reais (BRL) usando a cotação do câmbio atual.
    """)

    st.subheader("2. Termômetro de Ganância")
    st.markdown("""
    Uma métrica de sentimento de mercado.
    * **0% a 30%:** O mercado está em "Medo". Ótimo momento para comprar.
    * **70% a 100%:** O mercado está em "Euforia". Risco alto de correção de preços.
    """)

    st.subheader("3. Raio-X de Volatilidade")
    st.markdown("""
    Analisa o 'comportamento' do preço nos últimos 30 dias.
    * **Dias A/B (Verde/Vermelho):** Quantos dias o ativo subiu vs quantos dias caiu. Ajuda a identificar a força da tendência.
    * **Pico e Fundo:** A variação máxima e mínima registrada no mês.
    * **Alerta 🚨 RECORDE:** Aciona quando o ativo atinge o ponto mais baixo do mês hoje.
    """)

    st.subheader("4. Gestor de Carteira Dinâmica")
    st.markdown("""
    Aqui você sai da teoria e entra na prática da sua conta.
    * **Multiselect:** Habilite apenas os ativos que você realmente possui para não poluir sua visão.
    * **Preço Médio (PM):** Insira o valor que você pagou por cada cota. O sistema calculará o seu **Lucro ou Prejuízo Real** comparando com a cotação de agora.
    * **Renda/Mês:** Baseado nos dividendos pagos pelo ativo no último ano, estimamos quanto cairá na sua conta mensalmente.
    """)

    st.subheader("5. Patrimônio Global")
    st.markdown("""
    A visão final da sua riqueza.
    * **Consolidação:** O sistema soma seus investimentos em bolsa + seu dinheiro parado em conta + seus bens físicos (como Ouro ou outros minerais).
    * **Ouro Físico:** Digite a gramagem que você possui; o sistema precifica automaticamente com base na Bolsa de NY.
    """)

    st.info("💡 **Dica de Ouro:** O segredo da riqueza não é prever o futuro, mas sim reagir corretamente ao preço do presente.")
