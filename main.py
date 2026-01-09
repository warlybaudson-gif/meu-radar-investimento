import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO PARA ALINHAMENTO
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Forçar alinhamento central e evitar quebra de linha */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
    }
    .styled-table th {
        background-color: #1a1a1a;
        color: #58a6ff;
        text-align: center !important;
        padding: 12px 15px;
        border-bottom: 2px solid #333;
    }
    .styled-table td {
        padding: 12px 15px;
        text-align: center !important;
        border-bottom: 1px solid #222;
    }
    
    /* Scroll horizontal para celular */
    .table-container {
        overflow-x: auto;
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
                "Preço (R$)": f"{int(p_atual)}", 
                "Média 30d": f"{m_30:.2f}", 
                "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO", 
                "Ação": "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR",
                "Div_Ano": divs
            })
            
            dados_volatilidade.append({
                "Ativo": nome_display, 
                "Dias A/B": f"🟢{(variacoes > 0).sum()} / 🔴{(variacoes < 0).sum()}", 
                "Pico": f"+{variacoes.max():.2f}%", 
                "Fundo": f"{variacoes.min():.2f}%", 
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else "Normal"
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    
    # Renderização manual da tabela HTML para garantir alinhamento perfeito
    html_radar = f"""
    <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Ativo</th>
                    <th>Preço (R$)</th>
                    <th>Média 30d</th>
                    <th>Status</th>
                    <th>Ação</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f"<tr><td>{row['Ativo']}</td><td>{row['Preço (R$)']}</td><td>{row['Média 30d']}</td><td>{row['Status']}</td><td>{row['Ação']}</td></tr>" for _, row in df_radar.iterrows()])}
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
        st.table(df_vol)

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    ativos_selecionados = st.multiselect("Habilite os ativos:", options=df_radar["Ativo"].unique(), default=["PETR4.SA"])

    if ativos_selecionados:
        lista_c = []
        renda_total = 0
        v_ativos_total = 0
        
        st.write("📝 **Configure suas posições:**")
        cols = st.columns(2)
        
        for i, nome in enumerate(ativos_selecionados):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=1, key=f"q_{nome}")
                pm = st.number_input(f"PM (R$):", min_value=0.0, value=0.0, step=0.01, key=f"p_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                p_val = float(info["Preço (R$)"])
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

        st.table(pd.DataFrame(lista_c))

        st.markdown("---")
        st.subheader("💰 Patrimônio Real")
        with st.sidebar:
            st.header("⚙️ Ajustes")
            v_na_xp = st.number_input("Saldo (R$):", value=0.0)
            g_joias = st.number_input("Ouro (g):", value=0.0)
            v_minerais = st.number_input("Bens (R$):", value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço (R$)'].values[0])
        patri_global = v_ativos_total + v_na_xp + (g_joias * p_ouro) + v_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa", f"R$ {v_ativos_total:,.2f}")
        m2.metric("Renda/Mês", f"R$ {renda_total:,.2f}")
        m3.metric("PATRIMÔNIO", f"R$ {patri_global:,.2f}")

    st.markdown("---")
    st.subheader("📈 Tendência Visual")
    sel_graf = st.selectbox("Selecione o ativo para análise:", df_radar['Ativo'].unique())
    t_raw = df_radar[df_radar['Ativo'] == sel_graf]['Ticker_Raw'].values[0]
    st.line_chart(yf.Ticker(t_raw).history(period="30d")['Close'])

# ==================== ABA 2: MANUAL DE INSTRUÇÕES ====================
with tab_manual:
    st.header("📖 Guia Estratégico IA Rockefeller")
    
    st.subheader("1. Radar de Ativos (Inteligência de Preço)")
    st.markdown("""
    O Radar analisa se o preço atual está em uma zona de oportunidade ou de risco.
    - **Preço (R$):** Valor atual de mercado convertido e arredondado para leitura rápida.
    - **Média 30d:** O "preço justo" médio do último mês. Se o preço está abaixo da média, o status é **BARATO**.
    - **Ação:** Sugestão matemática baseada no desvio da média.
    """)

    st.subheader("2. Raio-X de Volatilidade (Comportamento)")
    st.markdown("""
    Analisa como o ativo se moveu nos últimos 30 dias de pregão.
    - **Dias A/B (Alta/Baixa):** Contagem de quantos dias o ativo fechou no positivo versus negativo.
    - **Pico e Fundo:** A oscilação máxima para cima e para baixo no período.
    - **Alerta 🚨 RECORDE:** Dispara se o preço atual for a mínima do mês, indicando um possível ponto de exaustão de venda.
    """)

    st.subheader("3. Gestor de Carteira Dinâmica (Controle de Ativos)")
    st.markdown("""
    Este módulo permite gerenciar o que você já comprou.
    - **Ativação:** Use a lista de seleção para exibir apenas os ativos que você possui.
    - **Cálculo de Lucro:** Ao inserir seu Preço Médio (PM), o sistema compara com o mercado e mostra seu lucro ou prejuízo nominal.
    - **Renda Passiva:** Calcula o dividendo mensal esperado baseado no histórico de 12 meses do ativo.
    """)

    st.subheader("4. Patrimônio Global (Consolidação de Riqueza)")
    st.markdown("""
    Une todos os seus pilares financeiros em um único número final.
    - **Bolsa:** Valor total das suas ações e criptos hoje.
    - **Saldo e Bens:** Soma o dinheiro parado na corretora e ativos físicos (como ouro em gramas) para calcular sua riqueza real total.
    """)
