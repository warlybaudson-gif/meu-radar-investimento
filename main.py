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

            divs = ativo.dividends.last("365D").sum() if t not in ["BTC-USD", "GC=F", "USDBRL=X", "FGPHF"] else 0.0
            variacoes = hist_30d['Close'].pct_change() * 100
            var_hoje = variacoes.iloc[-1] if not pd.isna(variacoes.iloc[-1]) else 0.0

            dados_radar.append({
                "Ativo": nome_exibicao, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", 
                "Média 30d": f"{m_30:.2f}", "Status": "🔥 BARATO" if p_atual < m_30 else "💎 CARO", 
                "Div_Ano": divs, "V_Cru": p_atual, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(),
                "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(), "Var_H": var_hoje
            })
    except: continue

df_radar = pd.DataFrame(dados_radar)

with tab_painel:
    # 🛰️ RADAR E RAIO-X (HTML CONSOLIDADO)
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Média 30d</th><th>Status</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Média 30d']}</td><td>{r['Status']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)

    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Inteligente")
    ativos_sel = st.multiselect("Selecione seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])

    if ativos_sel:
        lista_c = []
        renda_total, v_ativos_total = 0, 0
        df_grafico = pd.DataFrame()
        
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                st.markdown(f"### {nome}")
                qtd = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, value=0, key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, value=0.0, step=10.0, key=f"i_{nome}")
                
                info = df_radar[df_radar["Ativo"] == nome].iloc[0]
                p_atual = info["V_Cru"]
                
                # CÁLCULOS AUTOMÁTICOS EM TEMPO REAL
                pm_calculado = investido / qtd if qtd > 0 else 0.0
                valor_atualizado = qtd * p_atual
                lucro_prejuizo = valor_atualizado - investido
                r_mes = (info["Div_Ano"] * qtd) / 12
                
                lista_c.append({
                    "Ativo": nome, "Qtd": qtd, "PM (Auto)": f"{pm_calculado:.2f}",
                    "Valor Atual": f"{valor_atualizado:.2f}", "Lucro/Prej": f"{lucro_prejuizo:.2f}", "Renda": f"{r_mes:.2f}"
                })
                renda_total += r_mes
                v_ativos_total += valor_atualizado
                df_grafico[nome] = yf.Ticker(info["Ticker_Raw"]).history(period="30d")['Close']

        st.markdown("#### Resumo da Carteira")
        html_c = f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Total Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM (Auto)']}</td><td>R$ {r['Valor Atual']}</td><td>{r['Lucro/Prej']}</td></tr>" for r in lista_c])}</tbody>
        </table></div>"""
        st.markdown(html_c, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("💰 Patrimônio Global")
        with st.sidebar:
            st.header("⚙️ Outros Bens")
            v_na_xp = st.number_input("Saldo Corretora (R$):", value=0.0)
            g_joias = st.number_input("Ouro Físico (g):", value=0.0)
            v_minerais = st.number_input("Outros Bens (R$):", value=0.0)

        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['V_Cru'].values[0])
        patri_global = v_ativos_total + v_na_xp + (g_joias * p_ouro) + v_minerais
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Ações/Criptos", f"R$ {v_ativos_total:,.2f}")
        m2.metric("Renda Mensal", f"R$ {renda_total:,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")

        st.line_chart(df_grafico)

with tab_manual:
    st.header("📖 Manual Rockefeller")
    st.markdown("""
    <div class="manual-section">
    <b>Como usar o Gestor Inteligente:</b><br>
    1. Selecione o ativo no campo de busca.<br>
    2. Insira a <b>Quantidade de Cotas</b> que você tem.<br>
    3. Insira o <b>Total Investido</b> (a soma de todas as vezes que você comprou esse ativo).<br>
    4. O sistema calculará seu <b>Preço Médio (PM)</b> e seu <b>Lucro Real</b> automaticamente, comparando com o valor de mercado agora.
    </div>
    """, unsafe_allow_html=True)
