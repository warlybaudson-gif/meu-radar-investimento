import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações Visuais
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="centered")
st.title("💰 IA Rockefeller: Gestão & Radar")

# 2. Painel de Controle Lateral
st.sidebar.header("🎚️ Painel de Controle")
capital = st.sidebar.number_input("Seu Capital Disponível (R$)", min_value=0.0, value=1000.0)

# 3. Processamento e Lógica de Alerta
radar = ["VALE3.SA", "PETR4.SA", "MXRF11.SA", "BTC-USD"]
dados_final = []
alertas = []

with st.spinner('Sincronizando com o mercado...'):
    for ativo in radar:
        ticker = yf.Ticker(ativo)
        # Pegamos o histórico para preço atual e média
        hist_30d = ticker.history(period="30d")
        preco_atual = hist_30d['Close'].iloc[-1]
        media_30 = hist_30d['Close'].mean()
        
        status_preco = "Barato" if preco_atual < media_30 else "Caro"
        recomenda = "Comprar" if status_preco == "Barato" else "Vender"
        
        if recomenda == "Comprar":
            alertas.append(ativo)
        
        moeda = "$" if "USD" in ativo else "R$"
        divs = ticker.dividends
        yield_pct = (divs.tail(12).sum() / preco_atual) * 100 if not divs.empty else 0.0

        dados_final.append({
            "Ativo": ativo,
            "Preço": f"{moeda} {preco_atual:,.2f}",
            "Status": status_preco,
            "Ação": recomenda,
            "DY (12m)": f"{yield_pct:.2f}%"
        })

# Criar o DataFrame para exibir e exportar
df = pd.DataFrame(dados_final)

# --- EXIBIÇÃO DE NOTIFICAÇÃO ---
if alertas:
    st.error(f"🚨 ALERTA DE OPORTUNIDADE: {', '.join(alertas)} estão em ponto de COMPRA!")

# Exibição da Tabela
st.table(df)

# --- NOVIDADE: BOTÃO DE EXPORTAR PARA EXCEL (CSV) ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar dados para Excel",
    data=csv,
    file_name='radar_IA_rockefeller.csv',
    mime='text/csv',
)
st.divider()

# 4. Gráfico e Alocação
st.subheader("📈 Tendência e Planejamento")
escolha = st.selectbox("Analisar gráfico de:", radar)
st.line_chart(yf.Ticker(escolha).history(period="30d")['Close'])

if st.button("Calcular Cotas de MXRF11"):
    p_fii = yf.Ticker("MXRF11.SA").history(period="1d")['Close'].iloc[-1]
    st.success(f"Com seu capital, você compra {int(capital // p_fii)} cotas de MXRF11.")
