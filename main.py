import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    table { width: 100% !important; color: #ffffff !important; }
    th { background-color: #1a1a1a !important; color: #58a6ff !important; }
    td { background-color: #000000 !important; border-bottom: 1px solid #222 !important; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller - Gestão 360º")

tab_painel, tab_manual = st.tabs(["📊 Painel & Carteira", "📖 Manual de Instruções"])

# --- PROCESSAMENTO DE DADOS ---
tickers = ["PETR4.SA", "VALE3.SA", "MXRF11.SA", "BTC-USD", "NVDA", "GC=F", "NGLOY", "FGPHF", "USDBRL=X"]
dados_radar = []

try:
    cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio = 5.25

for t in tickers:
    try:
        ativo = yf.Ticker(t)
        p_atual = ativo.history(period="1d")['Close'].iloc[-1]
        
        # Conversão de Moeda
        if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
            p_atual = (p_atual / 31.1035 * cambio) if t == "GC=F" else (p_atual * cambio)
        
        # Dividendos (Renda Passiva)
        div = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "FGPHF", "USDBRL=X"] else 0.0
        
        nomes = {"GC=F": "Jóias (Ouro)", "NVDA": "Nvidia", "NGLOY": "Nióbio", "FGPHF": "Grafeno"}
        dados_radar.append({"Ativo": nomes.get(t, t), "Preço": p_atual, "Div_Ano": div})
    except: continue

df_precos = pd.DataFrame(dados_radar)

with tab_painel:
    # 1. RADAR (Resumido)
    st.subheader("🛰️ Cotações em Tempo Real (BRL)")
    st.table(df_precos.set_index("Ativo"))

    st.markdown("---")
    
    # 2. GESTOR DE CARTEIRA DINÂMICA
    st.subheader("🧮 Minha Carteira de Ativos")
    
    # Chave Seletora para Habilitar Ativos
    ativos_escolhidos = st.multiselect(
        "Selecione os ativos que você possui na carteira:",
        options=df_precos["Ativo"].unique(),
        default=["PETR4.SA"]
    )

    if ativos_escolhidos:
        lista_carteira = []
        renda_total_mes = 0
        valor_total_investido = 0

        st.write("📝 **Ajuste suas quantidades e preços médios:**")
        cols = st.columns(len(ativos_escolhidos))
        
        for i, nome_ativo in enumerate(ativos_escolhidos):
            with cols[i]:
                st.markdown(f"**{nome_ativo}**")
                qtd = st.number_input(f"Qtd:", min_value=0, value=1, key=f"qtd_{nome_ativo}")
                pm = st.number_input(f"PM (R$):", min_value=0.0, value=0.0, key=f"pm_{nome_ativo}")
                
                # Cálculos Individuais
                preco_agora = df_precos[df_precos["Ativo"] == nome_ativo]["Preço"].values[0]
                div_ano = df_precos[df_precos["Ativo"] == nome_ativo]["Div_Ano"].values[0]
                
                valor_posicao = qtd * preco_agora
                renda_mes = (div_ano * qtd) / 12
                lucro_prejuizo = (preco_agora - pm) * qtd if pm > 0 else 0
                
                lista_carteira.append({
                    "Ativo": nome_ativo,
                    "Qtd": qtd,
                    "Valor Atual": f"R$ {valor_posicao:.2f}",
                    "Lucro/Prej": f"R$ {lucro_prejuizo:.2f}",
                    "Renda/Mês": f"R$ {renda_mes:.2f}"
                })
                
                valor_total_investido += valor_posicao
                renda_total_mes += renda_mes

        # Exibição da Tabela de Carteira
        st.markdown("### 📊 Resumo da Carteira")
        st.table(pd.DataFrame(lista_carteira))

        # Totais Consolidados
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        
        # Extras: Saldo e Jóias
        saldo_xp = st.sidebar.number_input("Saldo Disponível XP (R$):", value=0.0)
        valor_extra = st.sidebar.number_input("Outros Minerais/Bens (R$):", value=0.0)
        
        total_geral = valor_total_investido + saldo_xp + valor_extra
        
        m1.metric("Patrimônio em Ativos", f"R$ {valor_total_investido:.2f}")
        m2.metric("Renda Passiva Mensal", f"R$ {renda_total_mes:.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {total_geral:.2f}")

    else:
        st.info("Selecione ativos acima para começar a montar sua carteira.")

# --- MANUAL ATUALIZADO ---
with tab_manual:
    st.header("📖 Manual do Gestor Multiativos")
    with st.expander("🛠️ Como usar a Tabela Dinâmica"):
        st.markdown("""
        1. **Chave Seletora:** Use o campo 'Selecione os ativos' para habilitar apenas o que você tem interesse.
        2. **Quantidades:** Ao habilitar, uma coluna aparecerá para você digitar quantas cotas possui.
        3. **Preço Médio (PM):** Coloque o valor que você pagou. O sistema calculará automaticamente o seu lucro ou prejuízo em tempo real.
        4. **Renda Passiva:** O sistema soma os dividendos de todos os ativos selecionados e te dá um valor total mensal.
        5. **Consolidação:** No menu lateral, você pode somar o seu dinheiro parado na XP para ter o valor real da sua riqueza.
        """)
