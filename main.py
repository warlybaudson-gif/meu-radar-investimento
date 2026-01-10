import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURAÇÕES E ESTILO
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
    .manual-section { border-left: 3px solid #58a6ff; padding-left: 15px; margin-bottom: 25px; }
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

try:
    cambio_hoje = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
except:
    cambio_hoje = 5.37

dados_radar = []
for nome_exibicao, t in tickers_map.items():
    try:
        ativo = yf.Ticker(t)
        hist_30d = ativo.history(period="30d")
        if not hist_30d.empty:
            p_atual = hist_30d['Close'].iloc[-1]
            if t in ["NVDA", "GC=F", "NGLOY", "FGPHF"]:
                p_atual = (p_atual / 31.1035) * cambio_hoje if t == "GC=F" else p_atual * cambio_hoje
            
            m_30 = hist_30d['Close'].mean()
            if t in ["NVDA", "NGLOY", "FGPHF"]: m_30 *= cambio_hoje
            if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje

            dados_radar.append({
                "Ativo": nome_exibicao, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", 
                "Média 30d": f"{m_30:.2f}", "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO", 
                "V_Cru": p_atual, "Var_Min": hist_30d['Close'].pct_change().min(), "Var_Max": hist_30d['Close'].pct_change().max()
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)

with tab_painel:
    # 🛰️ RADAR E TERMÔMETRO
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Média 30d</th><th>Status</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Média 30d']}</td><td>{r['Status']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado")
    caros = len(df_radar[df_radar['Status'] == "💎 CARO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    st.progress(score / 100)
    st.write(f"Índice de Ativos Caros: **{int(score)}%**")

    # 🧮 GESTOR COM CÁLCULO DE TROCO
    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    
    # Campo para o Total na XP
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=1000.0, step=100.0)
    
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])

    total_investido_acumulado = 0
    v_ativos_atualizado = 0
    lista_c = []
    
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                qtd = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, value=0, key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, value=0.0, key=f"i_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                p_atual = info["V_Cru"]
                
                pm_calc = investido / qtd if qtd > 0 else 0.0
                v_agora = qtd * p_atual
                lucro = v_agora - investido
                
                total_investido_acumulado += investido
                v_ativos_atualizado += v_agora
                
                lista_c.append({
                    "Ativo": nome, "Qtd": qtd, "PM": f"{pm_calc:.2f}",
                    "Valor Atual": f"{v_agora:.2f}", "Lucro": f"{lucro:.2f}"
                })

        # CÁLCULO DO TROCO
        troco_real = capital_xp - total_investido_acumulado

        html_c = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Total Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']}</td><td>R$ {r['Valor Atual']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c])}</tbody>
        </table></div>"""
        st.markdown(html_c, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("💰 Patrimônio Global")
        
        with st.sidebar:
            st.header("⚙️ Outros Bens")
            g_joias = st.number_input("Ouro Físico (g):", value=0.0)
            v_bens = st.number_input("Outros Bens (R$):", value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['V_Cru'].values[0])
        patri_global = v_ativos_atualizado + troco_real + (g_joias * p_ouro) + v_bens
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Valor em Ativos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (Saldo XP)", f"R$ {troco_real:,.2f}", delta_color="normal")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")

# ==================== ABA 2: MANUAL DIDÁTICO ====================
with tab_manual:
    st.header("📖 Guia de Operação")
    st.markdown("""
    <div class="manual-section">
    <b>Como funciona o Troco:</b><br>
    1. No campo 'Capital Total', coloque todo o dinheiro que você enviou para a XP.<br>
    2. Abaixo, preencha quanto você usou desse dinheiro para comprar cada ativo.<br>
    3. O sistema subtrai o investido do capital total e mostra o <b>Troco</b> (seu saldo parado na conta).
    </div>
    """, unsafe_allow_html=True)
