from __future__ import annotations
import streamlit as st # type: ignore
import investpy # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
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

# 1. CONFIGURAÇÕES E ESTILO REFORÇADO (MANUTENÇÃO INTEGRAL)
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

# --- PROCESSAMENTO DE DADOS ---

modelo_huli_tickers = {
    "TAESA": "TAEE11.SA", "ENGIE": "EGIE3.SA", "ALUPAR": "ALUP11.SA",
    "SANEPAR": "SAPR11.SA", "SABESP": "SBSP3.SA", "BANCO DO BRASIL": "BBAS3.SA",
    "ITAÚ": "ITUB4.SA", "BB SEGURIDADE": "BBSE3.SA", "HGLG11": "HGLG11.SA",
    "XPML11": "XPML11.SA", "IVVB11": "IVVB11.SA", "APPLE": "AAPL",
    "RENNER": "LREN3.SA", "GRENDENE": "GRND3.SA", "MATEUS": "GMAT3.SA", 
    "VISC11": "VISC11.SA", "MAGALU": "MGLU3.SA", "XPLG11": "XPLG11.SA",
    "MXRF11": "MXRF11.SA", "CPTS11": "CPTS11.SA", "VGHF11": "VGHF11.SA",
    "VIVA11": "VIVA11.SA", "KLBN4": "KLBN4.SA", "SAPR4": "SAPR4.SA", 
    "GARE11": "GARE11.SA", "MGLU3": "MGLU3.SA"
}

ativos_estrategicos = {
    "PETR4.SA": "PETR4.SA", "VALE3.SA": "VALE3.SA", "BTC-USD": "BTC-USD", 
    "Nvidia": "NVDA", "Jóias (Ouro)": "GC=F", "Nióbio": "NGLOY", 
    "Grafeno": "FGPHF", "Câmbio USD/BRL": "USDBRL=X"
}

tickers_map = {**ativos_estrategicos, **modelo_huli_tickers}

cambio_hoje = 5.40 

def calcular_dados(lista):
    nomes_empresas = {
        "PETR4.SA": "Petrobras", "VALE3.SA": "Vale", "MXRF11.SA": "FII MXRF11",
        "BTC-USD": "Bitcoin", "NVDA": "Nvidia", "GC=F": "Ouro",
        "NGLOY": "Nióbio", "FGPHF": "First Graphene", "USDBRL=X": "Dólar", 
        "TAEE11.SA": "Taesa", "EGIE3.SA": "Engie", "ALUP11.SA": "Alupar",
        "SAPR11.SA": "Sanepar", "SBSP3.SA": "Sabesp", "BBAS3.SA": "Banco do Brasil",
        "ITUB4.SA": "Itaú", "BBSE3.SA": "BB Seguridade", "HGLG11.SA": "FII HGLG11",
        "XPML11.SA": "FII XP Malls", "IVVB11.SA": "ETF S&P 500", "AAPL": "Apple",
        "LREN3.SA": "Lojas Renner", "GRND3.SA": "Grendene", "GMAT3.SA": "Grupo Mateus",
        "VISC11.SA": "FII Vinci Shopping", "MGLU3.SA": "Magalu", "VIVA11.SA": "FII VIVA11",
        "KLBN4.SA": "Klabin", "SAPR4.SA": "Sanepar (P)", "GARE11.SA": "FII GARE11"
    }
    res = []
    for nome_ex, t in lista.items():
        try:
            t_limpo = t.replace('.SA', '')
            # Busca via Investpy para evitar erro no Win7
            hist = investpy.get_stock_historical_data(stock=t_limpo, country='brazil', from_date='19/12/2025', to_date='19/01/2026')
            info = investpy.get_stock_information(stock=t_limpo, country='brazil')
            
            if not hist.empty:
                p_atual = hist['Close'].iloc[-1]
                emp_nome = nomes_empresas.get(t, nome_ex)
                dy = info['Dividend Yield'].iloc[0] / 100 if 'Dividend Yield' in info.columns else 0
                dy_formata = f"{(dy*100):.1f}%".replace('.', ',') if dy else "0,0%"

                if t in ["NVDA", "GC=F", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]:
                    p_atual = (p_atual / 31.1035) * cambio_hoje if t == "GC=F" else p_atual * cambio_hoje
                
                m_30 = hist['Close'].mean()
                if t in ["NVDA", "NGLOY", "FGPHF", "AAPL", "BTC-USD"]: m_30 *= cambio_hoje
                if t == "GC=F": m_30 = (m_30 / 31.1035) * cambio_hoje
                
                lpa = info['EPS'].iloc[0] if 'EPS' in info.columns else 0
                vpa = info['Book Value'].iloc[0] if 'Book Value' in info.columns else 0
                p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else m_30
                if t in ["NVDA", "AAPL"]: p_justo *= cambio_hoje
                
                status_m = "DESCONTADO" if p_atual < p_justo else "SOBREPRECO"
                variacoes = hist['Close'].pct_change() * 100
                acao = "COMPRAR" if p_atual < m_30 and status_m == "DESCONTADO" else ("VENDER" if p_atual > (p_justo * 1.20) else "ESPERAR")

                res.append({
                    "Ativo": nome_ex, "Empresa": emp_nome, "Ticker_Raw": t, "Preço": f"{p_atual:.2f}", 
                    "Justo": f"{p_justo:.2f}", "DY": dy_formata, "Status M": status_m, "Ação": acao, 
                    "V_Cru": p_atual, "Var_Min": variacoes.min(), "Var_Max": variacoes.max(), 
                    "Dias_A": (variacoes > 0).sum(), "Dias_B": (variacoes < 0).sum(),
                    "Var_H": variacoes.iloc[-1] if not variacoes.empty else 0, "LPA": lpa, "VPA": vpa
                })
        except: continue
    return pd.DataFrame(res)
    
df_radar = calcular_dados(tickers_map)
df_radar_modelo = calcular_dados(modelo_huli_tickers)
if 'carteira' not in st.session_state: st.session_state.carteira = {}
if 'carteira_modelo' not in st.session_state: st.session_state.carteira_modelo = {}

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")
    html_radar = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Empresa</th><th>Ativo</th><th>Preço</th><th>Justo</th><th>DY</th><th>Status</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Empresa']}</td><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['DY']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar, unsafe_allow_html=True)
    
    st.subheader("📊 Raio-X de Volatilidade")
    html_vol = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{""."".join([f"<tr><td>{r['Ativo']}</td><td>{r['Dias_A']}/{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado")
    caros = len(df_radar[df_radar['Status M'] == "SOBREPRECO"])
    score = (caros / len(df_radar)) * 100 if len(df_radar) > 0 else 0
    st.progress(score / 100)
    st.write(f"Índice de Ativos Caros: **{int(score)}%**")

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")
    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, value=dados_salvos.get("capital_xp", 0.0), step=100.0)
    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique(), default=["PETR4.SA"])
    
    total_investido_acumulado, v_ativos_atualizado = 0, 0
    lista_c, df_grafico = [], pd.DataFrame()
    if ativos_sel:
        cols = st.columns(2)
        for i, nome in enumerate(ativos_sel):
            with cols[i % 2]:
                st.markdown(f"**{nome}**")
                val_qtd_salvo = dados_salvos.get(f"q_{nome}", 0)
                val_inv_salvo = dados_salvos.get(f"i_{nome}", 0.0)
                qtd = st.number_input(f"Qtd Cotas ({nome}):", min_value=0, value=val_qtd_salvo, key=f"q_{nome}")
                investido = st.number_input(f"Total Investido R$ ({nome}):", min_value=0.0, value=val_inv_salvo, key=f"i_{nome}")
                info_p = df_radar[df_radar["Ativo"] == nome].iloc[0]
                p_atual_p = info_p["V_Cru"]
                pm_calc = investido / qtd if qtd > 0 else 0.0
                v_agora = qtd * p_atual_p
                if qtd > 0:
                    if p_atual_p < pm_calc:
                        desconto = ((pm_calc - p_atual_p) / pm_calc) * 100
                        st.warning(f"**OPORTUNIDADE EM {nome}:** Está {desconto:.1f}% abaixo do seu PM (R$ {pm_calc:.2f}). Hora de comprar mais cotas!")
                    else:
                        st.info(f"**{nome}:** Acima do seu Preço Médio.")
                total_investido_acumulado += investido
                v_ativos_atualizado += v_agora
                lista_c.append({"Ativo": nome, "Qtd": qtd, "PM": f"{pm_calc:.2f}", "Total": f"{v_agora:.2f}", "Lucro": f"{(v_agora - investido):.2f}"})
        
        troco_real = capital_xp - total_investido_acumulado
        st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']}</td><td>R$ {r['Total']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c])}</tbody>
        </table></div>""", unsafe_allow_html=True)

        st.subheader("💰 Patrimônio Global")
        with st.sidebar:
            st.header("⚙️ Outros Bens")
            g_joias = st.number_input("Ouro Físico (gramas):", min_value=0.0, value=dados_salvos.get("g_joias", 0.0))
            v_bens = st.number_input("Outros Bens/Imóveis (R$):", min_value=0.0, value=dados_salvos.get("v_bens", 0.0))
        p_ouro = float(df_radar[df_radar['Ativo'] == "Jóias (Ouro)"]['V_Cru'].values[0]) if not df_radar[df_radar['Ativo'] == "Jóias (Ouro)"].empty else 350.0
        valor_ouro_total = g_joias * p_ouro
        patri_global = v_ativos_atualizado + troco_real + valor_ouro_total + v_bens
        m1, m2, m3 = st.columns(3)
        m1.metric("Bolsa/Criptos", f"R$ {v_ativos_atualizado:,.2f}")
        m2.metric("Troco (XP) + Bens", f"R$ {(troco_real + valor_ouro_total + v_bens):,.2f}")
        m3.metric("PATRIMÔNIO TOTAL", f"R$ {patri_global:,.2f}")

        st.markdown("---")
        st.subheader("🛍️ Planejador de Compras (Cotas)")
        valor_disponivel = st.number_input("Quanto pretende investir hoje? (R$):", min_value=0.0, value=500.0, step=100.0, key="calc_aporte")
        if not df_radar.empty:
            df_calc = df_radar[['Ativo', 'V_Cru', 'Ação']].copy()
            df_calc['Cotas'] = (valor_disponivel // df_calc['V_Cru']).astype(int)
            df_calc['Troco'] = (valor_disponivel % df_calc['V_Cru']).map("R$ {:.2f}".format)
            st.write(f"Com **R$ {valor_disponivel:.2f}**, você consegue comprar:")
            st.dataframe(df_calc[['Ativo', 'Cotas', 'Ação', 'Troco']], use_container_width=True, hide_index=True)
            mateus_row = df_calc[df_calc['Ativo'] == "MATEUS"]
            if not mateus_row.empty:
                qtd_mateus = mateus_row['Cotas'].values[0]
                st.info(f"**Foco GMAT3:** Seu aporte permite comprar **{qtd_mateus} cotas** do Grupo Mateus.")

        st.markdown("---")
        if st.button("💾 Salvar Minha Carteira"):
            dados_para_salvar = {"capital_xp": capital_xp, "g_joias": g_joias, "v_bens": v_bens}
            for nome in ativos_sel:
                dados_para_salvar[f"q_{nome}"] = st.session_state[f"q_{nome}"]
                dados_para_salvar[f"i_{nome}"] = st.session_state[f"i_{nome}"]
            salvar_dados_usuario(dados_para_salvar)
            st.success("Carteira salva com sucesso!")

# ==================== ABA 2: RADAR CARTEIRA MODELO ====================
with tab_radar_modelo:
    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Dividendos (DY)</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['DY']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)
    st.subheader("📊 Raio-X de Volatilidade (Ativos Modelo)")
    html_vol_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{""."".join([f"<tr><td>{r['Ativo']}</td><td>{r['Dias_A']}/{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol_m, unsafe_allow_html=True)

# ==================== ABA 3: ESTRATÉGIA HULI ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli: Próximos Passos")
    v_aporte = st.number_input("Quanto você pretende investir este mês? (R$):", min_value=0.0, step=100.0, key="aporte_huli_v3")
    df_prioridade = df_radar_modelo[df_radar_modelo['Ação'] == "COMPRAR"].copy()
    if df_prioridade.empty:
        st.warning("⚠️ No momento, nenhum ativo atingiu os critérios de COMPRA.")
    else:
        st.write(f"### 🛒 Plano de Execução e Renda Estimada")
        html_huli = f"""<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Status</th><th>Cotas</th><th>Dividendos (DY)</th><th>Renda Mensal Est.</th></tr></thead><tbody>"""
        total_renda_mensal = 0
        for _, r in df_prioridade.iterrows():
            preco_v = float(r['V_Cru'])
            cotas = int(v_aporte / len(df_prioridade) // preco_v) if preco_v > 0 else 0
            dy_decimal = float(r['DY'].replace('%', '').replace(',', '.')) / 100
            renda_est_mes = (cotas * preco_v * (dy_decimal / 12))
            total_renda_mensal += renda_est_mes
            html_huli += f"<tr><td><b>{r['Ativo']}</b></td><td>R$ {r['Preço']}</td><td><b style='color:#00ff00'>{r['Ação']}</b></td><td><b style='color:#00d4ff'>{cotas} UN</b></td><td>{r['DY']}</td><td style='color:#f1c40f'>R$ {renda_est_mes:.2f}</td></tr>"
        html_huli += "</tbody></table></div>"
        st.markdown(html_huli, unsafe_allow_html=True)

# ==================== ABA 4: CARTEIRA MODELO HULI ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="huli-category"><b>🐄 Vacas Leiteiras</b><br><small>Foco em Dividendos</small></div>', unsafe_allow_html=True)
        st.write("**• Energia:** TAEE11, EGIE3, ALUP11")
        st.write("**• Saneamento:** SAPR11, SBSP3")
        st.write("**• Bancos:** BBAS3, ITUB4")
    with col2:
        st.markdown('<div class="huli-category"><b>🐕 Cães de Guarda</b><br><small>Segurança</small></div>', unsafe_allow_html=True)
        st.write("**• Ouro/Dólar:** IVVB11, GOLD11")

# ==================== ABA 5: DNA FINANCEIRO ====================
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")
    df_combined = pd.concat([df_radar, df_radar_modelo]).drop_duplicates(subset="Ativo")
    html_dna = """<div class="mobile-table-container"><table class="rockefeller-table"><thead><tr><th>Ativo</th><th>LPA (Lucro)</th><th>VPA (Patrimônio)</th><th>P/L</th><th>P/VP</th></tr></thead><tbody>"""
    for _, r in df_combined.iterrows():
        p_l = float(r['V_Cru']) / r['LPA'] if r['LPA'] > 0 else 0
        p_vp = float(r['V_Cru']) / r['VPA'] if r['VPA'] > 0 else 0
        html_dna += f"<tr><td>{r['Ativo']}</td><td>{r['LPA']:.2f}</td><td>{r['VPA']:.2f}</td><td>{p_l:.2f}</td><td>{p_vp:.2f}</td></tr>"
    html_dna += "</tbody></table></div>"
    st.markdown(html_dna, unsafe_allow_html=True)

# ==================== ABA 6: BACKTESTING ====================
with tab_backtest:
    st.header("📈 Backtesting de Oportunidade")
    if not df_radar.empty:
        ativo_bt = st.selectbox("Selecione um ativo para simular o 'Efeito Pânico':", df_radar["Ativo"].unique())
        d = df_radar[df_radar["Ativo"] == ativo_bt].iloc[0]
        p_atual_bt = float(d["V_Cru"])
        queda_max = abs(float(d["Var_Min"]))
        preco_fundo = p_atual_bt / (1 + (queda_max/100))
        st.metric("Preço de Compra (Fundo)", f"R$ {preco_fundo:.2f}")
        st.metric("Rendimento Realizado", f"{queda_max:.2f}%")

# ==================== ABA 7: MANUAL DE INSTRUÇÕES (RESTAURAÇÃO INTEGRAL) ====================
with tab_manual:
    st.header("📖 Manual de Instruções - IA Rockefeller")
    with st.expander("🛰️ Radar de Ativos e Preço Justo", expanded=True):
        st.markdown("""
        * **Preço Justo (Graham):** Calculado pela fórmula $V = \sqrt{22.5 \cdot LPA \cdot VPA}$. Indica o valor intrínseco do ativo.
        * **Status Descontado:** Ocorre quando o preço de mercado é inferior ao Preço Justo.
        * **Ação COMPRAR:** Recomendada apenas quando o ativo está abaixo da média de 30 dias e abaixo do preço justo.
        """)
    with st.expander("📊 Raio-X de Volatilidade"):
        st.markdown("""
        * **Dias A/B:** Quantidade de dias de Alta (Verde) e Baixa (Vermelho) no último mês.
        * **🚨 Alerta RECORDE:** Dispara quando o preço atual toca ou cai abaixo da mínima histórica dos últimos 30 dias.
        """)
    with st.expander("🧬 DNA Financeiro"):
        st.markdown("""
        * **LPA (Lucro por Ação):** Quanto de lucro a empresa gera para cada ação.
        * **VPA (Valor Patrimonial):** O valor real dos bens da empresa dividido pelas ações.
        * **P/L:** Indica em quantos anos você recuperaria seu investimento através dos lucros.
        """)
    with st.expander("📈 Backtesting"):
        st.markdown("""
        Esta aba localiza o ponto mais baixo que o ativo chegou no mês e calcula exatamente quanto você teria ganho se tivesse comprado naquele momento de queda máxima.
        """)
