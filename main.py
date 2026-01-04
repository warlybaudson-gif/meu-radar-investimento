import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações de Identidade
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

# 2. Harmonização Total Black e Visibilidade
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; font-size: 13px !important; color: #ffffff !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; white-space: nowrap !important; }
    td { background-color: #000000 !important; color: #ffffff !important; white-space: nowrap !important; border-bottom: 1px solid #222 !important; }
    label { color: #ffffff !important; font-weight: bold !important; }
    .streamlit-expanderHeader { background-color: #000000 !important; color: #ffffff !important; border: 1px solid #333 !important; }
    .streamlit-expanderContent { background-color: #000000 !important; border: 1px solid #333 !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 26px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 15px; border-radius: 10px; }
    .stTable { overflow-x: auto !important; display: block !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# 3. Processamento de Dados (Radar)
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD"]
dados_finais = []

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        hist_1d = ativo.history(period="1d")
        if not hist_1d.empty:
            preco_atual = hist_1d['Close'].iloc[-1]
            hist_30d = ativo.history(period="30d")
            media_30 = hist_30d['Close'].mean()
            status = "🔥 BARATO" if preco_atual < media_30 else "💎 CARO"
            acao = "✅ COMPRAR" if preco_atual < media_30 else "⚠️ ESPERAR"
            divs = ativo.dividends.last("365D").sum() if t != "BTC-USD" else 0.0
            dados_finais.append({
                "Ativo": t, "Preço": preco_atual, "Média 30d": media_30,
                "Status": status, "Ação": acao, "Div. 12m": divs
            })
    except:
        continue

df_radar = pd.DataFrame(dados_finais)

# --- BLOCO EXISTENTE: RADAR ---
st.subheader("🛰️ Radar de Ativos")
df_display = df_radar.copy()
# Formatação para exibição
for col in ["Preço", "Média 30d", "Div. 12m"]:
    df_display[col] = df_display[col].apply(lambda x: f"R$ {x:.2f}")

st.table(df_display)
csv = df_radar.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Baixar Dados (Excel/BI)", data=csv, file_name='radar_rockefeller.csv', mime='text/csv')

# --- NOVO BLOCO 1: ALERTAS DE PREÇO ALVO ---
st.markdown("---")
st.subheader("🎯 Alertas de Preço Alvo")
col_alerta1, col_alerta2 = st.columns(2)

with col_alerta1:
    alvo_ativo = st.selectbox("Selecione o ativo para monitorar:", tickers)
    preco_alvo = st.number_input(f"Me avise quando {alvo_ativo} chegar em (R$):", value=0.0)

with col_alerta2:
    if preco_alvo > 0:
        preco_agora = df_radar[df_radar['Ativo'] == alvo_ativo]['Preço'].values[0]
        if preco_agora <= preco_alvo:
            st.success(f"🚀 OPORTUNIDADE! {alvo_ativo} está em R$ {preco_agora:.2f} (Abaixo do seu alvo!)")
        else:
            distancia = ((preco_agora / preco_alvo) - 1) * 100
            st.warning(f"Ainda falta {distancia:.1f}% para atingir seu alvo.")

# --- BLOCO EXISTENTE: GESTOR XP ---
st.markdown("---")
col_calc, col_res = st.columns([1, 1.2])

with col_calc:
    st.subheader("🧮 Gestor XP")
    with st.expander("Sua Ordem", expanded=True):
        tipo_ordem = st.selectbox("Tipo de Ordem:", ("A Mercado", "Limitada", "Stop Loss", "Stop Móvel"))
        valor_xp = st.number_input("Valor enviado (R$):", value=50.0)
        pago_xp = st.number_input("Preço pago (R$):", value=31.0)
        
        # NOVO: Input para Preço Médio Atual
        cotas_atuais = st.number_input("Quantas cotas você já possui?", value=0)
        pm_atual = st.number_input("Qual seu Preço Médio atual?", value=0.0)
        
        cotas_novas = int(valor_xp // pago_xp)
        troco_xp = valor_xp % pago_xp
        
        # CÁLCULO DE NOVO PREÇO MÉDIO
        if cotas_atuais > 0:
            total_investido = (cotas_atuais * pm_atual) + (cotas_novas * pago_xp)
            total_cotas = cotas_atuais + cotas_novas
            novo_pm = total_investido / total_cotas
        else:
            novo_pm = pago_xp

        preco_petr = df_radar[df_radar['Ativo'] == "PETR4.SA"]['Preço'].values[0] if not df_radar[df_radar['Ativo'] == "PETR4.SA"].empty else pago_xp
        patrimonio_total = (cotas_novas * preco_petr) + troco_xp
        lucro_abs = patrimonio_total - valor_xp

with col_res:
    st.subheader("📊 Resultado")
    m1, m2 = st.columns(2)
    m1.metric("Cotas Novas", f"{cotas_novas} un")
    m2.metric("Troco em Conta", f"R$ {troco_xp:.2f}")
    
    st.metric("Patrimônio Total (Nesta Ordem)", f"R$ {patrimonio_total:.2f}", f"R$ {lucro_abs:.2f}")
    
    # NOVO: Exibição do Novo Preço Médio
    if cotas_atuais > 0:
        st.metric("Seu Novo Preço Médio será:", f"R$ {novo_pm:.2f}")

# --- NOVO BLOCO 2: PROJEÇÃO DE DIVIDENDOS ---
st.markdown("---")
st.subheader("💰 Projeção de Renda Passiva")
df_divs = df_radar[df_radar['Div. 12m'] > 0].copy()
if not df_divs.empty:
    col_div1, col_div2 = st.columns(2)
    with col_div1:
        ativo_div = st.selectbox("Ativo para simular renda:", df_divs['Ativo'].tolist())
        qtd_simulada = st.number_input(f"Se você tivesse X cotas de {ativo_div}:", value=100)
    
    with col_div2:
        div_ano = df_divs[df_divs['Ativo'] == ativo_div]['Div. 12m'].values[0]
        renda_ano = div_ano * qtd_simulada
        renda_mes = renda_ano / 12
        st.metric("Renda Mensal Estimada", f"R$ {renda_mes:.2f}")
        st.caption(f"Baseado nos últimos 12 meses (R$ {div_ano:.2f} por cota/ano)")

# --- BLOCO EXISTENTE: GRÁFICO ---
st.markdown("---")
st.subheader("📈 Tendência 30d")
escolha = st.selectbox("Escolha o Ativo:", tickers)
dados_grafico = yf.Ticker(escolha).history(period="30d")['Close']
st.line_chart(dados_grafico)
