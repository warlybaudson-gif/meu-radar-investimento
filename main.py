import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÕES DE IDENTIDADE E LAYOUT
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. ESTILO TOTAL BLACK
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

st.title("💰 IA Rockefeller - Sistema Unificado")

tab_painel, tab_manual = st.tabs(["📊 Painel & Carteira", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS (Consolidação Yahoo Finance) ---
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
            
            # Conversão para BRL
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio_hoje
                else: p_atual = p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            nomes_dict = {"GC=F": "Jóias (Ouro)", "NVDA": "Nvidia (IA)", "NGLOY": "Nióbio", "FGPHF": "Grafeno"}
            nome_display = nomes_dict.get(t, t)
            
            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0

            dados_radar.append({
                "Ativo": nome_display, "Ticker": t, "Preço": p_atual, "Média 30d": m_30, 
                "Div_Ano": divs, "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO",
                "Ação": "✅ COMPRAR" if p_atual < m_30 else "⚠️ ESPERAR"
            })
            
            dados_volatilidade.append({
                "Ativo": nome_display,
                "Dias 🟢/🔴": f"🟢{(variacoes > 0).sum()} / 🔴{(variacoes < 0).sum()}",
                "Pico": f"+{variacoes.max():.2f}%",
                "Fundo": f"{variacoes.min():.2f}%",
                "Alerta": "🚨 RECORDE" if var_hoje <= (variacoes.min() * 0.98) and var_hoje < 0 else "Estável"
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)
df_vol = pd.DataFrame(dados_volatilidade)

# ==================== ABA 1: PAINEL & CARTEIRA ====================
with tab_painel:
    # 1. RADAR E TERMÔMETRO
    c_radar, c_term = st.columns([2, 1])
    with c_radar:
        st.subheader("🛰️ Radar de Ativos")
        st.table(df_radar[["Ativo", "Preço", "Status", "Ação"]].head(8))
    with c_term:
        st.subheader("🌡️ Ganância")
        caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
        score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
        st.metric("Índice", f"{score:.0f}%")
        st.progress(score / 100)

    # 2. RAIO-X DE VOLATILIDADE
    st.markdown("---")
    st.subheader("📊 Raio-X de Volatilidade (30 Dias)")
    st.table(df_vol)

    # 3. GESTOR DE CARTEIRA DINÂMICA (A Mudança Solicitada)
    st.markdown("---")
    st.subheader("🧮 Minha Carteira Personalizada")
    
    ativos_selecionados = st.multiselect(
        "Habilite os ativos que você possui para gerenciar quantidades e lucros:",
        options=df_radar["Ativo"].unique(),
        default=["PETR4.SA"]
    )

    if ativos_selecionados:
        lista_final = []
        v_total_investido = 0
        r_total_mes = 0

        # Inputs em colunas para não ocupar muito espaço vertical
        st.write("📝 **Preencha seus dados de posse:**")
        cols = st.columns(4)
        for i, nome in enumerate(ativos_selecionados):
            with cols[i % 4]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=1, key=f"q_{nome}")
                pm = st.number_input(f"PM (R$):", min_value=0.0, value=0.0, key=f"p_{nome}")
                
                # Busca dados do radar
                row = df_radar[df_radar["Ativo"] == nome].iloc[0]
                v_atual = qtd * row["Preço"]
                lucro = (row["Preço"] - pm) * qtd if pm > 0 else 0
                r_mes = (row["Div_Ano"] * qtd) / 12
                
                lista_final.append({
                    "Ativo": nome, "Quantidade": qtd, "Preço Médio": f"R$ {pm:.2f}",
                    "Valor Atual": f"R$ {v_atual:.2f}", "Lucro/Prej": f"R$ {lucro:.2f}",
                    "Renda Mensal": f"R$ {r_mes:.2f}", "Recomendação": row["Ação"]
                })
                v_total_investido += v_atual
                r_total_mes += r_mes

        st.markdown("### 📋 Resumo Consolidado da Carteira")
        st.table(pd.DataFrame(lista_final))

        # 4. PATRIMÔNIO GLOBAL (BARRA LATERAL + MÉTRICAS)
        st.markdown("---")
        with st.sidebar:
            st.header("⚙️ Patrimônio Extra")
            saldo_cash = st.number_input("Dinheiro em conta (XP):", value=0.0)
            valor_ouro_fisico = st.number_input("Valor Ouro Físico (R$):", value=0.0)
            valor_minerais = st.number_input("Minerais Raros (R$):", value=0.0)
        
        patri_global = v_total_investido + saldo_cash + valor_ouro_fisico + valor_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Investido em Bolsa", f"R$ {v_total_investido:.2f}")
        m2.metric("Salário em Dividendos", f"R$ {r_total_mes:.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:.2f}")
    else:
        st.info("Selecione os ativos acima para abrir a tabela de gestão.")

# ==================== ABA 2: MANUAL COMPLETO ====================
with tab_manual:
    st.header("📖 Manual do Usuário - IA Rockefeller V5")
    
    with st.expander("🛰️ 1. O Radar e Ativos Estratégicos", expanded=True):
        st.markdown("""
        O Radar vigia ativos tradicionais e de alta tecnologia.
        - **Nióbio & Grafeno:** Rastreados via mineradoras globais (NGLOY e FGPHF).
        - **Conversão:** Ativos em dólar são convertidos para Real (BRL) instantaneamente.
        - **Status 🔥 BARATO:** O preço está abaixo da média de 30 dias.
        """)

    with st.expander("🧮 2. Carteira Multiativos Dinâmica"):
        st.markdown("""
        Esta é a sua principal ferramenta de controle.
        - **Habilitação:** Use o seletor para ativar apenas os ativos que você comprou.
        - **Lucro/Prejuízo:** Calculado comparando seu Preço Médio (PM) com a cotação atual do Yahoo Finance.
        - **Renda Mensal:** Projeção baseada nos últimos 12 meses de dividendos reais de cada empresa.
        """)

    with st.expander("📊 3. Raio-X e Volatilidade"):
        st.markdown("""
        - **Dias 🟢/🔴:** Mostra se o ativo está em tendência de subida ou descida consistente no mês.
        - **Alerta 🚨 RECORDE:** Dispara se o preço hoje cair abaixo do ponto mais baixo dos últimos 30 dias. É o sinal de 'fundo histórico' mensal.
        """)
