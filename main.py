# IA Rockefeller — Versão COMPLETA com Abas Restauradas
# Core otimizado + TODAS as abas originais restauradas

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import sqlite3

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# ==================== CACHE YFINANCE ====================
@st.cache_data(ttl=1800, show_spinner=False)
def carregar_historico(ticker, periodo="30d"):
    try:
        return yf.Ticker(ticker).history(period=periodo)
    except:
        return pd.DataFrame()

# ==================== SQLITE ====================
def conectar_db():
    return sqlite3.connect("carteira.db", check_same_thread=False)

def salvar_dados_usuario(dados):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS carteira (chave TEXT PRIMARY KEY, valor TEXT)")
    for k, v in dados.items():
        c.execute("REPLACE INTO carteira VALUES (?, ?)", (k, json.dumps(v)))
    conn.commit()
    conn.close()

def carregar_dados_usuario():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS carteira (chave TEXT PRIMARY KEY, valor TEXT)")
    c.execute("SELECT chave, valor FROM carteira")
    dados = {k: json.loads(v) for k, v in c.fetchall()}
    conn.close()
    return dados

# ==================== DADOS INICIAIS ====================
dados_salvos = carregar_dados_usuario()

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.40

# ==================== ATIVOS ====================
ativos = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "BBAS3": "BBAS3.SA",
    "ITUB4": "ITUB4.SA",
    "BTC": "BTC-USD",
    "NVDA": "NVDA",
    "AAPL": "AAPL"
}

# ==================== CÁLCULOS ====================
def calcular_dados(lista):
    res = []
    for nome, t in lista.items():
        hist = carregar_historico(t)

        # Garante que o ativo apareça mesmo sem dados
        if hist.empty:
            res.append({
                "Ativo": nome,
                "Preço": np.nan,
                "Justo": np.nan,
                "Status": "⚠️ SEM DADOS",
                "Ação": "🟡 ESPERAR",
                "V_Cru": 0
            })
            continue

        try:
            info = yf.Ticker(t).fast_info
        except:
            info = {}

        p = hist['Close'].iloc[-1]
        if t in ["NVDA", "AAPL", "BTC-USD"]:
            p *= cambio_hoje

        m30 = hist['Close'].mean()
        if t in ["NVDA", "AAPL", "BTC-USD"]:
            m30 *= cambio_hoje

        lpa = info.get('eps', 0) or 0
        vpa = info.get('bookValue', 0) or 0
        justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m30

        status = "✅ DESCONTADO" if p < justo else "❌ SOBREPREÇO"
        acao = "✅ COMPRAR" if p < m30 and status == "✅ DESCONTADO" else "⚠️ ESPERAR"

        res.append({
            "Ativo": nome,
            "Preço": round(p, 2),
            "Justo": round(justo, 2),
            "Status": status,
            "Ação": acao,
            "V_Cru": p
        })
    return pd.DataFrame(res)

# ==================== INTERFACE ====================
st.title("💰 IA Rockefeller")

# ====== ABAS ======
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Painel",
    "🔍 Radar",
    "🎯 Estratégia",
    "🏦 Carteira",
    "🧬 DNA",
    "📈 Backtest",
    "📖 Manual"
])

df = calcular_dados(ativos)

# ==================== ABA 1 ====================
with tab1:
    st.subheader("🧠 Terminal Executivo — Centro de Decisão")

    if df.empty:
        st.warning("Sem dados para exibir")
    else:
        # ===== KPIs =====
        col1, col2, col3, col4 = st.columns(4)
        descontados = len(df[df['Status'] == "✅ DESCONTADO"])
        sobre = len(df[df['Status'] == "❌ SOBREPREÇO"])
        margem_media = ((df['Justo'] - df['Preço']) / df['Justo']).mean() * 100

        col1.metric("Ativos Descontados", descontados)
        col2.metric("Ativos Sobrepreço", sobre)
        col3.metric("Margem Média (%)", f"{margem_media:.1f}%")
        col4.metric("Total Monitorado", len(df))

        st.markdown("---")

        # ===== TABELA PRINCIPAL =====
        st.markdown("### 📊 Visão Consolidada")
        # ===== SINAL OPERACIONAL =====
        df_exec = df.copy()
        def sinal(row):
            if row['Preço'] < row['Justo'] * 0.85:
                return "🟢 COMPRAR"
            elif row['Preço'] > row['Justo'] * 1.10:
                return "🔴 VENDER"
            else:
                return "🟡 ESPERAR"
        df_exec['Decisão'] = df_exec.apply(sinal, axis=1)

        st.dataframe(df_exec[['Ativo','Preço','Justo','Status','Decisão']], use_container_width=True)

        st.markdown("---")

        # ===== RANKING =====
        st.markdown("### 🏆 Ranking por Margem de Segurança")
        df_rank = df.copy()
        df_rank['Margem'] = (df_rank['Justo'] - df_rank['Preço']) / df_rank['Justo']
        df_rank = df_rank.sort_values('Margem', ascending=False)
        st.dataframe(df_rank[['Ativo','Preço','Justo','Margem']], use_container_width=True)

        st.markdown("---")

        # ===== ALERTAS =====
        st.markdown("### ⚠️ Alertas Inteligentes")
        for _, r in df_rank.iterrows():
            if r['Margem'] > 0.25:
                st.success(f"{r['Ativo']} com alta margem de segurança")
            elif r['Margem'] < 0:
                st.error(f"{r['Ativo']} acima do valor justo")

        st.markdown("---")

        # ===== GESTÃO =====
        st.markdown("### 🧮 Gestão de Capital")
        capital = st.number_input("Capital total (R$)", value=dados_salvos.get("capital", 0.0), step=100.0)
        alocacao = capital / max(descontados, 1)
        st.info(f"Sugestão de alocação por ativo descontado: R$ {alocacao:,.2f}")

        if st.button("💾 Salvar Painel Executivo"):
            salvar_dados_usuario({"capital": capital})
            st.success("Painel salvo com sucesso")

# ==================== ABA 2 ====================
with tab2:
    st.subheader("🔍 Radar de Oportunidades — Foco em Ação")

    if df.empty:
        st.warning("Sem dados disponíveis")
    else:
        df_radar = df.copy()
        df_radar['Margem'] = (df_radar['Justo'] - df_radar['Preço']) / df_radar['Justo']

        # Critério de oportunidade
        oportunidades = df_radar[df_radar['Margem'] > 0.15].sort_values('Margem', ascending=False)

        col1, col2, col3 = st.columns(3)
        col1.metric("Oportunidades", len(oportunidades))
        col2.metric("Margem Média", f"{oportunidades['Margem'].mean()*100:.1f}%" if not oportunidades.empty else "0%")
        col3.metric("Melhor Margem", f"{oportunidades['Margem'].max()*100:.1f}%" if not oportunidades.empty else "0%")

        st.markdown("---")

        st.markdown("### 🟢 Ativos com Margem de Segurança")
        if oportunidades.empty:
            st.info("Nenhum ativo com margem suficiente no momento")
        else:
            st.dataframe(
                oportunidades[['Ativo','Preço','Justo','Margem']],
                use_container_width=True
            )

# ==================== ABA 3 ====================
with tab3:
    st.subheader("🎯 Estratégia de Aporte — Plano de Execução")

    if df.empty:
        st.warning("Sem dados para montar estratégia")
    else:
        df_plan = df.copy()
        df_plan['Margem'] = (df_plan['Justo'] - df_plan['Preço']) / df_plan['Justo']
        df_plan = df_plan[df_plan['Margem'] > 0]

        aporte = st.number_input("Aporte mensal disponível (R$)", min_value=0.0, step=100.0)

        if aporte <= 0:
            st.info("Informe um valor de aporte para gerar a estratégia")
        else:
            # Prioriza maiores margens
            df_plan = df_plan.sort_values('Margem', ascending=False)
            pesos = df_plan['Margem'] / df_plan['Margem'].sum()
            df_plan['Aporte Sugerido'] = pesos * aporte

            st.markdown("### 📌 Distribuição Recomendada")
            st.dataframe(
                df_plan[['Ativo','Preço','Justo','Margem','Aporte Sugerido']],
                use_container_width=True
            )

            st.markdown("---")
            st.markdown("### 🧠 Lógica da Estratégia")
            st.markdown("""
            • Capital distribuído proporcionalmente à margem de segurança  
            • Quanto maior o desconto, maior o aporte  
            • Estratégia defensiva, focada em valor
            """)

# ==================== ABA 4 ====================
with tab4:
    st.subheader("🏦 Carteira — Posições Reais")

    if df.empty:
        st.warning("Sem dados de ativos")
    else:
        st.markdown("### 📥 Registro de Posições")
        carteira = []
        valor_total = 0.0

        for _, r in df.iterrows():
            col1, col2 = st.columns([2, 1])
            with col1:
                qtd = st.number_input(f"Quantidade de {r['Ativo']}", min_value=0, key=f"carteira_{r['Ativo']}")
            with col2:
                preco_medio = st.number_input(f"Preço médio {r['Ativo']}", min_value=0.0, step=0.1, key=f"pm_{r['Ativo']}")

            valor_atual = qtd * r['Preço'] if not pd.isna(r['Preço']) else 0
            custo = qtd * preco_medio
            pl = valor_atual - custo
            valor_total += valor_atual

            carteira.append({
                "Ativo": r['Ativo'],
                "Qtd": qtd,
                "Preço Médio": preco_medio,
                "Preço Atual": r['Preço'],
                "Valor Atual": valor_atual,
                "P/L": pl
            })

        df_cart = pd.DataFrame(carteira)

        st.markdown("---")
        st.markdown("### 📊 Visão Consolidada da Carteira")
        st.dataframe(df_cart, use_container_width=True)

        st.metric("💼 Valor Total da Carteira", f"R$ {valor_total:,.2f}")

        if st.button("💾 Salvar Carteira"):
            salvar_dados_usuario({"carteira": carteira})
            st.success("Carteira salva com sucesso")

# ==================== ABA 5 ====================
with tab5:
    st.subheader("🧬 DNA Financeiro dos Ativos")

    if df.empty:
        st.warning("Sem dados para análise")
    else:
        perfis = []
        for _, r in df.iterrows():
            margem = (r['Justo'] - r['Preço']) / r['Justo'] if not pd.isna(r['Preço']) else 0
            risco = "Alto" if r['Ativo'] in ['BTC'] else "Médio"
            perfil = "Crescimento" if r['Ativo'] in ['NVDA','AAPL','BTC'] else "Valor"

            perfis.append({
                "Ativo": r['Ativo'],
                "Perfil": perfil,
                "Risco": risco,
                "Margem Segurança": f"{margem*100:.1f}%"
            })

        st.dataframe(pd.DataFrame(perfis), use_container_width=True)

# ==================== ABA 6 ====================
with tab6:
    st.subheader("📈 Backtesting Simplificado")

    ativo_bt = st.selectbox("Selecione o ativo", df['Ativo'].unique())
    df_bt = df[df['Ativo']==ativo_bt]

    if not df_bt.empty:
        preco = df_bt.iloc[0]['Preço']
        fundo = df_bt.iloc[0]['Preço'] * 0.85
        retorno = ((preco - fundo)/fundo)*100

        c1,c2,c3 = st.columns(3)
        c1.metric("Compra no fundo", f"R$ {fundo:.2f}")
        c2.metric("Preço atual", f"R$ {preco:.2f}")
        c3.metric("Retorno", f"{retorno:.1f}%")

# ==================== ABA 7 ====================
with tab7:
    st.subheader("📖 Manual de Uso – IA Rockefeller")

    st.markdown("""
    **Aba 1 – Painel Geral**  
    Mostra todos os ativos monitorados, com preço justo e ação sugerida.

    **Aba 2 – Radar Carteira Modelo**  
    Foco nos ativos selecionados para estratégia defensiva.

    **Aba 3 – Estratégia Huli**  
    Direcionamento prático de aportes.

    **Aba 4 – Carteira Modelo**  
    Estrutura conceitual de diversificação.

    **Aba 5 – DNA Financeiro**  
    Classificação por risco, perfil e margem de segurança.

    **Aba 6 – Backtesting**  
    Simulação simples de compra em pânico.
    """)
