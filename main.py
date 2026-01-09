import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO PARA MOBILE
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Forçar cor branca e evitar quebras de texto */
    .stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; white-space: nowrap !important; }
    
    .mobile-table-container { 
        overflow-x: auto; 
        width: 100%; 
        -webkit-overflow-scrolling: touch;
    }

    .rockefeller-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Courier New', Courier, monospace;
        margin-bottom: 20px;
        font-size: 0.85rem;
    }
    .rockefeller-table th {
        background-color: #1a1a1a;
        color: #58a6ff !important;
        text-align: center !important;
        padding: 10px;
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
    
    /* Estilo para o Manual Didático */
    .manual-section {
        border-left: 3px solid #58a6ff;
        padding-left: 15px;
        margin-bottom: 25px;
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
                "Ativo": nome_exibicao, 
                "Dias A/B": f"🟢{(variacoes > 0).sum()}/🔴{(variacoes < 0).sum()}", 
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

    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""
    <div class="mobile-table-container">
        <table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
            <tbody>
                {"".join([f"<tr><td>{row['Ativo']}</td><td>{row['Dias A/B']}</td><td>{row['Pico']}</td><td>{row['Fundo']}</td><td>{row['Alerta']}</td></tr>" for _, row in df_vol.iterrows()])}
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_vol, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🌡️ Sentimento de Mercado")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    st.progress(score / 100)
    st.write(f"Índice de Ativos Caros: **{int(score)}%**")

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    ativos_selecionados = st.multiselect("Habilite seus ativos:", options=df_radar["Ativo"].unique(), default=["PETR4.SA"])

    if ativos_selecionados:
        lista_c = []
        renda_total = 0
        v_ativos_total = 0
        df_grafico = pd.DataFrame()
        
        st.write("📝 **Configure suas posições:**")
        cols = st.columns(2)
        
        for i, nome in enumerate(ativos_selecionados):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=1, key=f"q_{nome}")
                pm = st.number_input(f"PM:", min_value=0.0, value=0.0, step=0.01, key=f"p_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                t_raw = info["Ticker_Raw"]
                p_val = float(info["Preço"])
                v_agora = qtd * p_val
                lucro = (p_val - pm) * qtd if pm > 0 else 0
                r_mes = (info["Div_Ano"] * qtd) / 12
                
                lista_c.append({
                    "Ativo": nome, "Qtd": qtd, "Total": f"{v_agora:.2f}", "Lucro": f"{lucro:.2f}", "Renda": f"{r_mes:.2f}"
                })
                renda_total += r_mes
                v_ativos_total += v_agora
                df_grafico[nome] = yf.Ticker(t_raw).history(period="30d")['Close']

        html_carteira = f"""
        <div class="mobile-table-container">
            <table class="rockefeller-table">
                <thead><tr><th>Ativo</th><th>Qtd</th><th>Total (R$)</th><th>Lucro</th><th>Renda/Mês</th></tr></thead>
                <tbody>
                    {"".join([f"<tr><td>{row['Ativo']}</td><td>{row['Qtd']}</td><td>{row['Total']}</td><td>{row['Lucro']}</td><td>{row['Renda']}</td></tr>" for row in lista_c])}
                </tbody>
            </table>
        </div>
        """
        st.markdown(html_carteira, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("💰 Patrimônio Global")
        with st.sidebar:
            st.header("⚙️ Ajustes")
            v_na_xp = st.number_input("Saldo (R$):", value=0.0)
            g_joias = st.number_input("Ouro (g):", value=0.0)
            v_minerais = st.number_input("Bens (R$):", value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['Preço'].values[0])
        patri_global = v_ativos_total + v_na_xp + (g_joias * p_ouro) + v_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa", f"R$ {v_ativos_total:,.2f}")
        m2.metric("Dividendos", f"R$ {renda_total:,.2f}")
        m3.metric("PATRIMÔNIO", f"R$ {patri_global:,.2f}")

        st.markdown("---")
        st.subheader("📈 Comparativo de Performance")
        st.line_chart(df_grafico)

# ==================== ABA 2: MANUAL DIDÁTICO ====================
with tab_manual:
    st.header("📖 Guia de Operação - Sistema Rockefeller")
    st.write("Siga este manual para interpretar os dados e gerir sua riqueza com precisão matemática.")

    st.markdown("### 1. Radar de Ativos (Inteligência de Preço)")
    st.markdown("""
    <div class="manual-section">
    Este módulo identifica distorções de preço no curto prazo.
    <ul>
        <li><b>Preço (R$):</b> Valor atual de mercado. Ativos em dólar são convertidos automaticamente.</li>
        <li><b>Média 30d:</b> O ponto de equilíbrio. Representa o valor comum do ativo no último mês.</li>
        <li><b>Status 🔥 BARATO:</b> O preço está abaixo da média. Indica uma <b>oportunidade de compra</b> técnica.</li>
        <li><b>Status 💎 CARO:</b> O preço está acima da média. Indica que o mercado pode estar supervalorizado.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 2. Raio-X de Volatilidade (Análise de Risco)")
    st.markdown("""
    <div class="manual-section">
    Entenda a "agressividade" do mercado nos últimos 30 dias.
    <ul>
        <li><b>Dias A/B (Alta/Baixa):</b> Se houver muito mais 🔴 do que 🟢, o ativo está em forte tendência de queda.</li>
        <li><b>Pico e Fundo:</b> Mostra a variação máxima positiva e negativa. Útil para saber o quanto o ativo costuma oscilar.</li>
        <li><b>Alerta 🚨 RECORDE:</b> O sinal mais importante. Indica que o preço hoje atingiu a <b>mínima absoluta</b> dos últimos 30 dias. É o sinal clássico de "fundo de mercado".</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 3. Gestor de Carteira Dinâmica (Seu Patrimônio)")
    st.markdown("""
    <div class="manual-section">
    Onde você controla seus investimentos reais.
    <ul>
        <li><b>Habilitação:</b> Use o seletor para ativar apenas o que você possui. Isso limpa sua visão e ajusta os gráficos.</li>
        <li><b>PM (Preço Médio):</b> Insira quanto você pagou por cada cota. O sistema usa isso para calcular seu <b>Lucro Real</b>.</li>
        <li><b>Renda/Mês:</b> Uma estimativa de quanto você recebe de "salário" por mês em dividendos, baseada no histórico real de pagamentos.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 4. Patrimônio Global e Gráficos")
    st.markdown("""
    <div class="manual-section">
    A visão final do seu império financeiro.
    <ul>
        <li><b>Gráfico Dinâmico:</b> Mostra a linha de tendência de todos os ativos que você habilitou. Se você tem 3 ações, verá 3 linhas para comparar qual performa melhor.</li>
        <li><b>Ouro e Minerais:</b> Diferente da bolsa, aqui você insere bens físicos. O sistema precifica o Ouro automaticamente pela cotação internacional.</li>
        <li><b>Patrimônio Total:</b> A soma de TUDO: Dinheiro na XP + Ações + Ouro + Minerais.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 **Dica Estratégica:** Quando o Radar mostrar 'BARATO' e o Raio-X mostrar 'RECORDE', você está diante do melhor cenário de compra possível.")
