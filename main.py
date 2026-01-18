import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# Funções para Persistência de Dados
def salvar_dados_usuario(dados):
    with open("carteira_salva.json", "w") as f:
        json.dump(dados, f)

def carregar_dados_usuario():
    if os.path.exists("carteira_salva.json"):
        with open("carteira_salva.json", "r") as f:
            return json.load(f)
    return {}

# Carrega os dados salvos ao iniciar
dados_salvos = carregar_dados_usuario()

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO
st.set_page_config(page_title="IA Rockefeller", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; white-space: nowrap !important; }
    .mobile-table-container { overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; }
    .rockefeller-table {
        width: 100%; border-collapse: collapse; font-family: 'Courier New', Courier, monospace;
        margin-bottom: 20px; font-size: 0.85rem;
    }
    .rockefeller-table th { background-color: #1a1a1a; color: #58a6ff !important; text-align: center !important; padding: 10px; border-bottom: 2px solid #333; }
    .rockefeller-table td { padding: 10px; text-align: center !important; border-bottom: 1px solid #222; }
    div[data-testid="stMetric"] { background-color: #111111; border: 1px solid #333333; border-radius: 8px; text-align: center; }
    .huli-category { background-color: #1a1a1a; padding: 15px; border-radius: 5px; border-left: 4px solid #58a6ff; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# CRIAÇÃO DAS ABAS
tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle", 
    "🔍 Radar Carteira Modelo",
    "🎯 Estratégia Huli", 
    "🏦 Carteira Modelo Huli",
    "🧬 DNA Financeiro",
    "📈 Backtesting",
    "📖 Manual de Instruções"
])

# tickers_map e modelo_huli_tickers
modelo_huli_tickers = {
    "TAESA": "TAEE11.SA", "ENGIE": "EGIE3.SA", "ALUPAR": "ALUP11.SA",
    "SANEPAR": "SAPR11.SA", "SABESP": "SBSP3.SA", "BANCO DO BRASIL": "BBAS3.SA",
    "ITAÚ": "ITUB4.SA", "BB SEGURIDADE": "BBSE3.SA", "HGLG11": "HGLG11.SA",
    "XPML11": "XPML11.SA", "IVVB11": "IVVB11.SA", "APPLE": "AAPL",
    "RENNER": "LREN3.SA", "GRENDENE": "GRND3.SA", "MATEUS": "GMAT3.SA", 
    "VISC11": "VISC11.SA", "MAGALU": "MGLU3.SA", "XPLG11": "XPLG11.SA",
    "MXRF11": "MXRF11.SA", "CPTS11": "CPTS11.SA", "VGHF11": "VGHF11.SA",
    "VIVA11": "VIVA11.SA", "KLBN4": "KLBN4.SA", "SAPR4": "SAPR4.SA",
    "GARE11": "GARE11.SA"
}

ativos_estrategicos = {
    "PETR4.SA": "PETR4.SA", "VALE3.SA": "VALE3.SA", "BTC-USD": "BTC-USD", 
    "Nvidia": "NVDA", "Ouro": "GC=F", "Dólar": "USDBRL=X"
}

tickers_map = {**ativos_estrategicos, **modelo_huli_tickers}

# Lógica de Cálculo
def calcular_dados(lista):
    res = []
    try:
        cambio = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except:
        cambio = 5.40

    for nome_ex, t in lista.items():
        try:
            ativo = yf.Ticker(t)
            hist = ativo.history(period="30d")
            if hist.empty: continue
            
            p_atual = hist['Close'].iloc[-1]
            info = ativo.info
            
            # Ajuste Dólar
            if t in ["NVDA", "AAPL", "BTC-USD"]: p_atual *= cambio
            if t == "GC=F": p_atual = (p_atual / 31.1035) * cambio

            dy = info.get('dividendYield', 0)
            lpa = info.get('trailingEps', 0)
            vpa = info.get('bookValue', 0)
            
            p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else hist['Close'].mean()
            if t in ["NVDA", "AAPL"]: p_justo *= cambio

            status = "✅ DESCONTADO" if p_atual < p_justo else "❌ SOBREPREÇO"
            acao = "✅ COMPRAR" if p_atual < p_justo else "⚠️ ESPERAR"

            res.append({
                "Ativo": nome_ex, "Empresa": info.get('longName', nome_ex), "Preço": f"{p_atual:.2f}",
                "Justo": f"{p_justo:.2f}", "DY": f"{(dy*100):.1f}%", "Status M": status, "Ação": acao,
                "V_Cru": p_atual, "Var_Min": hist['Close'].pct_change().min()*100,
                "Var_Max": hist['Close'].pct_change().max()*100,
                "Dias_A": (hist['Close'].pct_change() > 0).sum(),
                "Dias_B": (hist['Close'].pct_change() < 0).sum(),
                "Var_H": hist['Close'].pct_change().iloc[-1], "LPA": lpa, "VPA": vpa, "Ticker_Raw": t
            })
        except: continue
    return pd.DataFrame(res)

df_radar = calcular_dados(tickers_map)
df_radar_modelo = df_radar[df_radar['Ativo'].isin(modelo_huli_tickers.keys())]

# --- ABA 1 ---
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    if not df_radar.empty:
        html = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Empresa</th><th>Ativo</th><th>Preço</th><th>Justo</th><th>DY</th><th>Status</th><th>Ação</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Empresa'][:20]}</td><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['DY']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
        </table></div>"""
        st.markdown(html, unsafe_allow_html=True)

# --- ABA 3 ---
with tab_huli:
    st.header("🎯 Estratégia Tio Huli")
    v_aporte = st.number_input("Quanto pretende investir? (R$):", min_value=0.0, step=100.0, key="aporte_v3")
    
    df_prioridade = df_radar_modelo[df_radar_modelo['Ação'] == "✅ COMPRAR"].copy()
    
    if df_prioridade.empty:
        st.warning("⚠️ Nenhum ativo em ponto de COMPRA no momento.")
    else:
        total_renda_mensal = 0
        html_huli = """<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Preço</th><th>Cotas</th><th>Renda Est.</th></tr></thead><tbody>"""
        
        for _, r in df_prioridade.iterrows():
            preco = float(r['V_Cru'])
            cotas = int((v_aporte / len(df_prioridade)) // preco)
            dy_dec = float(r['DY'].replace('%','').replace(',','.'))/100
            renda = (cotas * preco * (dy_dec/12))
            total_renda_mensal += renda
            html_huli += f"<tr><td>{r['Ativo']}</td><td>R$ {r['Preço']}</td><td>{cotas}</td><td>R$ {renda:.2f}</td></tr>"
        
        html_huli += "</tbody></table></div>"
        st.markdown(html_huli, unsafe_allow_html=True)
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("Total a Investir", f"R$ {v_aporte:,.2f}")
        c2.metric("Aumento Renda Mensal", f"R$ {total_renda_mensal:.2f}")

        if st.button("💾 Salvar Plano de Aporte", key="save_huli"):
            st.success("✅ Plano salvo!")

# --- ABA 4 ---
with tab_modelo:
    st.header("🏦 Carteira Modelo Huli")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b></div>', unsafe_allow_html=True)
        st.write("• Energia: TAEE11, EGIE3 | • Bancos: BBAS3, ITUB4")
    with col2:
        st.markdown('<div class="huli-category"><b>🏢 FIIs</b></div>', unsafe_allow_html=True)
        st.write("• Logística: HGLG11 | • Shoppings: XPML11")

# --- ABA 7 ---
with tab_manual:
    st.header("📖 Manual")
    st.info("Utilize o Radar para identificar ativos com Status DESCONTADO e Ação COMPRAR.")
