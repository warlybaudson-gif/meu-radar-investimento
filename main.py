import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# ==================== PERSISTÊNCIA ====================
def salvar_dados_usuario(dados):
    with open("carteira_salva.json", "w") as f:
        json.dump(dados, f)

def carregar_dados_usuario():
    if os.path.exists("carteira_salva.json"):
        with open("carteira_salva.json", "r") as f:
            return json.load(f)
    return {}

dados_salvos = carregar_dados_usuario()

# ==================== CONFIG STREAMLIT ====================
st.set_page_config(
    page_title="IA Rockefeller",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #000000; color: #ffffff; }
.stMarkdown, .stTable, td, th, p, label { color: #ffffff !important; white-space: nowrap !important; }
.mobile-table-container { overflow-x: auto; width: 100%; }
.rockefeller-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.rockefeller-table th { background-color: #1a1a1a; color: #58a6ff; padding: 10px; }
.rockefeller-table td { padding: 10px; border-bottom: 1px solid #222; }
.huli-category { background:#1a1a1a; padding:15px; border-left:4px solid #58a6ff; margin:10px 0; }
</style>
""", unsafe_allow_html=True)

st.title("💰 IA Rockefeller")

# ==================== ABAS ====================
tab_painel, tab_radar_modelo, tab_huli, tab_modelo, tab_dna, tab_backtest, tab_manual = st.tabs([
    "📊 Painel de Controle",
    "🔍 Radar Carteira Modelo",
    "🎯 Estratégia Huli",
    "🏦 Carteira Modelo Huli",
    "🧬 DNA Financeiro",
    "📈 Backtesting",
    "📖 Manual de Instruções"
])

# ==================== SESSION STATE ====================
if "carteira" not in st.session_state:
    st.session_state.carteira = {}

if "carteira_modelo" not in st.session_state:
    st.session_state.carteira_modelo = {}

if "df_radar" not in st.session_state:
    st.session_state.df_radar = pd.DataFrame()

df_radar = st.session_state.df_radar

# ==================== ABA 1: PAINEL DE CONTROLE ====================
with tab_painel:
    st.subheader("🛰️ Radar de Ativos Estratégicos")

    if df_radar.empty:
        st.warning("⚠️ Dados do radar ainda não carregados.")
    else:
        linhas_radar = ""
        for _, r in df_radar.iterrows():
            linhas_radar += f"""
            <tr>
                <td>{r['Empresa']}</td>
                <td>{r['Ativo']}</td>
                <td>{r['Preço']}</td>
                <td>{r['Justo']}</td>
                <td>{r['DY']}</td>
                <td>{r['Status M']}</td>
                <td>{r['Ação']}</td>
            </tr>
            """

        st.markdown(f"""
        <div class="mobile-table-container">
        <table class="rockefeller-table">
            <thead>
                <tr>
                    <th>Empresa</th><th>Ativo</th><th>Preço</th>
                    <th>Justo</th><th>DY</th><th>Status</th><th>Ação</th>
                </tr>
            </thead>
            <tbody>{linhas_radar}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📊 Raio-X de Volatilidade")

    linhas_vol = ""
    for _, r in df_radar.iterrows():
        alerta = "🚨 RECORDE" if r['Var_H'] <= (r['Var_Min'] * 0.98) and r['Var_H'] < 0 else "Normal"
        linhas_vol += f"""
        <tr>
            <td>{r['Ativo']}</td>
            <td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td>
            <td>+{r['Var_Max']:.2f}%</td>
            <td>{r['Var_Min']:.2f}%</td>
            <td>{alerta}</td>
        </tr>
        """

    st.markdown(f"""
    <div class="mobile-table-container">
    <table class="rockefeller-table">
        <thead>
            <tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr>
        </thead>
        <tbody>{linhas_vol}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado")

    if 'Status M' in df_radar.columns and not df_radar.empty:
        caros = len(df_radar[df_radar['Status M'] == "❌ SOBREPREÇO"])
        score = (caros / len(df_radar)) * 100
    else:
        score = 0

    st.progress(score / 100)
    st.write(f"Índice de Ativos Caros: **{int(score)}%**")

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira Dinâmica")

    capital_xp = st.number_input("💰 Capital Total na Corretora XP (R$):", min_value=0.0, step=100.0)

    ativos_sel = st.multiselect("Habilite seus ativos:", df_radar["Ativo"].unique())

    lista_c, df_grafico = [], pd.DataFrame()

    for nome in ativos_sel:
        info = df_radar[df_radar["Ativo"] == nome].iloc[0]
        qtd = st.number_input(f"Qtd ({nome})", min_value=0)
        investido = st.number_input(f"Investido ({nome})", min_value=0.0)

        preco = info["V_Cru"]
        atual = qtd * preco

        lista_c.append({
            "Ativo": nome,
            "Qtd": qtd,
            "PM": f"{(investido/qtd if qtd else 0):.2f}",
            "Total": f"{atual:.2f}",
            "Lucro": f"{(atual-investido):.2f}"
        })

        hist = yf.Ticker(info["Ticker_Raw"]).history(period="30d")
        if not hist.empty:
            df_grafico[nome] = hist["Close"]

    if lista_c:
        st.markdown(f"""
        <div class="mobile-table-container">
        <table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Total</th><th>Lucro</th></tr></thead>
            <tbody>
            {''.join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>{r['PM']}</td><td>{r['Total']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c])}
            </tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        st.line_chart(df_grafico)

# ==================== ABA 2: RADAR CARTEIRA MODELO ====================
with tab_radar_modelo:

    if "carteira_modelo" not in st.session_state:
        st.session_state.carteira_modelo = {}

    st.subheader("🛰️ Radar de Ativos: Carteira Modelo Tio Huli")
    html_radar_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Preço (R$)</th><th>Preço Justo</th><th>Dividendos (DY)</th><th>Status Mercado</th><th>Ação</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Preço']}</td><td>{r['Justo']}</td><td>{r['DY']}</td><td>{r['Status M']}</td><td>{r['Ação']}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_radar_m, unsafe_allow_html=True)

    st.subheader("📊 Raio-X de Volatilidade (Ativos Modelo)")
    html_vol_m = f"""<div class="mobile-table-container"><table class="rockefeller-table">
        <thead><tr><th>Ativo</th><th>Dias A/B</th><th>Pico</th><th>Fundo</th><th>Alerta</th></tr></thead>
        <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>🟢{r['Dias_A']}/🔴{r['Dias_B']}</td><td>+{r['Var_Max']:.2f}%</td><td>{r['Var_Min']:.2f}%</td><td>{'🚨 RECORDE' if r['Var_H'] <= (r['Var_Min']*0.98) and r['Var_H'] < 0 else 'Normal'}</td></tr>" for _, r in df_radar_modelo.iterrows()])}</tbody>
    </table></div>"""
    st.markdown(html_vol_m, unsafe_allow_html=True)

    st.subheader("🌡️ Sentimento de Mercado (Modelo)")
    caros_m = len(df_radar_modelo[df_radar_modelo['Status M'] == "❌ SOBREPREÇO"])
    score_m = (caros_m / len(df_radar_modelo)) * 100 if len(df_radar_modelo) > 0 else 0
    st.progress(score_m / 100)
    st.write(f"Índice de Sobrepreço Modelo: **{int(score_m)}%**")

    st.markdown("---")
    st.subheader("🧮 Gestor de Carteira: Ativos Modelo")

    capital_xp_m = st.number_input(
        "💰 Capital na Corretora para Ativos Modelo (R$):",
        min_value=0.0,
        value=0.0,
        step=100.0,
        key="cap_huli"
    )

    if "Ativo" in df_radar.columns and not df_radar.empty:
    ativos_sel = st.multiselect(
        "Habilite seus ativos:",
        df_radar["Ativo"].unique(),
        default=list(df_radar["Ativo"].unique()[:1])
    )
else:
    ativos_sel = []
    st.info("ℹ️ Ativos indisponíveis enquanto o radar não for carregado.")

    total_investido_acum_m, v_ativos_atual_m = 0.0, 0.0
    lista_c_m, df_grafico_m = [], pd.DataFrame()

    if ativos_sel_m and not df_radar_modelo.empty:
        cols_m = st.columns(2)

        for i, nome in enumerate(ativos_sel_m):
            with cols_m[i % 2]:
                st.markdown(f"**{nome}**")

                qtd_m = st.number_input(
                    f"Qtd Cotas ({nome}):",
                    min_value=0,
                    key=f"q_m_{nome}"
                )

                investido_m = st.number_input(
                    f"Total Investido R$ ({nome}):",
                    min_value=0.0,
                    key=f"i_m_{nome}"
                )

                info_m = df_radar_modelo[df_radar_modelo["Ativo"] == nome]
                if info_m.empty:
                    continue

                info_m = info_m.iloc[0]
                p_atual_m = info_m["V_Cru"]
                pm_calc_m = investido_m / qtd_m if qtd_m > 0 else 0.0
                v_agora_m = qtd_m * p_atual_m

                total_investido_acum_m += investido_m
                v_ativos_atual_m += v_agora_m

                st.session_state.carteira_modelo[nome] = {"atual": v_agora_m}

                lista_c_m.append({
                    "Ativo": nome,
                    "Qtd": qtd_m,
                    "PM": f"{pm_calc_m:.2f}",
                    "Total": f"{v_agora_m:.2f}",
                    "Lucro": f"{(v_agora_m - investido_m):.2f}"
                })

                hist_m = yf.Ticker(info_m["Ticker_Raw"]).history(period="30d")
                if not hist_m.empty:
                    df_grafico_m[nome] = hist_m["Close"]

        troco_real_m = capital_xp_m - total_investido_acum_m

        st.markdown(f"""<div class="mobile-table-container"><table class="rockefeller-table">
            <thead><tr><th>Ativo</th><th>Qtd</th><th>PM</th><th>Valor Atual</th><th>Lucro/Prej</th></tr></thead>
            <tbody>{"".join([f"<tr><td>{r['Ativo']}</td><td>{r['Qtd']}</td><td>R$ {r['PM']}</td><td>R$ {r['Total']}</td><td>{r['Lucro']}</td></tr>" for r in lista_c_m])}</tbody>
        </table></div>""", unsafe_allow_html=True)

        st.subheader("💰 Patrimônio Global (Estratégia Modelo)")
        patri_global_m = v_ativos_atual_m + troco_real_m

        m1_m, m2_m = st.columns(2)
        m1_m.metric("Total em Ativos Modelo", f"R$ {v_ativos_atual_m:,.2f}")
        m2_m.metric("PATRIMÔNIO MODELO TOTAL", f"R$ {patri_global_m:,.2f}")

        if not df_grafico_m.empty:
            st.bar_chart(df_grafico_m.iloc[-1].fillna(0))

# ==================== ABA 3: ESTRATÉGIA HULI ====================
with tab_huli:
    st.header("🎯 Estratégia Tio Huli: Próximos Passos")

    v_aporte = st.number_input(
        "Quanto você pretende investir este mês? (R$):",
        min_value=0.0,
        step=100.0,
        key="aporte_huli_final_v3"
    )

    if df_radar_modelo.empty:
        st.warning("⚠️ Dados da carteira modelo indisponíveis no momento.")
    else:
        # Filtra apenas o que é prioridade (✅ COMPRAR)
        df_prioridade = df_radar_modelo[df_radar_modelo['Ação'] == "✅ COMPRAR"].copy()

        if df_prioridade.empty:
            st.warning("⚠️ No momento, nenhum ativo atingiu os critérios de COMPRA.")
        else:
            st.write("### 🛒 Plano de Execução e Renda Estimada")

            html_huli = f"""<div class="mobile-table-container"><table class="rockefeller-table">
                <thead>
                    <tr>
                        <th>Ativo</th>
                        <th>Preço (R$)</th>
                        <th>Status</th>
                        <th>Cotas</th>
                        <th>Dividendos (DY)</th>
                        <th>Renda Mensal Est.</th>
                    </tr>
                </thead>
                <tbody>"""

            total_renda_mensal = 0.0
            qtd_ativos = len(df_prioridade)

            for _, r in df_prioridade.iterrows():
                preco_v = float(r.get('V_Cru', 0))
                cotas = int((v_aporte / qtd_ativos) // preco_v) if preco_v > 0 else 0

                dy_raw = r.get('DY', '0,0%')
                try:
                    dy_decimal = float(dy_raw.replace('%', '').replace(',', '.')) / 100
                except Exception:
                    dy_decimal = 0.0

                renda_est_mes = cotas * preco_v * (dy_decimal / 12)
                total_renda_mensal += renda_est_mes

                html_huli += (
                    f"<tr>"
                    f"<td><b>{r['Ativo']}</b></td>"
                    f"<td>R$ {r['Preço']}</td>"
                    f"<td><b style='color:#00ff00'>{r['Ação']}</b></td>"
                    f"<td><b style='color:#00d4ff'>{cotas} UN</b></td>"
                    f"<td>{r['DY']}</td>"
                    f"<td style='color:#f1c40f'>R$ {renda_est_mes:.2f}</td>"
                    f"</tr>"
                )

            html_huli += "</tbody></table></div>"
            st.markdown(html_huli, unsafe_allow_html=True)

            st.success(f"💰 **Renda mensal estimada:** R$ {total_renda_mensal:.2f}")

# ==================== ABA 4: CARTEIRA MODELO HULI ====================
with tab_modelo:
    st.header("🏦 Ativos Diversificados (Onde o Tio Huli Investe)")
    st.write("Esta é a base de ativos que compõe o método dele para proteção e renda.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="huli-category"><b>🐄 Vacas Leiteiras (Renda Passiva)</b><br>'
            '<small>Foco em Dividendos e Estabilidade</small></div>',
            unsafe_allow_html=True
        )
        st.write("**• Energia:** TAEE11 (Taesa), EGIE3 (Engie), ALUP11 (Alupar)")
        st.write("**• Saneamento:** SAPR11 (Sanepar), SBSP3 (Sabesp)")
        st.write("**• Bancos:** BBAS3 (Banco do Brasil), ITUB4 (Itaú), SANB11 (Santander)")
        st.write("**• Seguradoras:** BBSE3 (BB Seguridade), CXSE3 (Caixa Seguridade)")

        st.markdown(
            '<div class="huli-category"><b>🏢 Fundos Imobiliários (Renda Mensal)</b><br>'
            '<small>Aluguéis sem Imposto de Renda</small></div>',
            unsafe_allow_html=True
        )
        st.write("**• Logística:** HGLG11, XPLG11, BTLG11")
        st.write("**• Shoppings:** XPML11, VISC11, HGBS11")

    with col2:
        st.markdown(
            '<div class="huli-category"><b>🐕 Cães de Guarda (Segurança)</b><br>'
            '<small>Reserva de Oportunidade e Valor</small></div>',
            unsafe_allow_html=True
        )
        st.write("**• Ouro:** OZ1D ou ETF GOLD11")
        st.write("**• Dólar:** IVVB11 (S&P 500)")
        st.write("**• Renda Fixa:** Tesouro Selic e CDBs de liquidez diária")

        st.markdown(
            '<div class="huli-category"><b>🐎 Cavalos de Corrida (Crescimento)</b><br>'
            '<small>Aposta no futuro e multiplicação</small></div>',
            unsafe_allow_html=True
        )
        st.write("**• Cripto:** Bitcoin (BTC) e Ethereum (ETH)")
        st.write("**• Tech:** Nvidia (NVDA), Apple (AAPL)")

# ==================== ABA 5: DNA FINANCEIRO ====================
with tab_dna:
    st.header("🧬 DNA Financeiro (LPA / VPA)")

    if df_radar.empty and df_radar_modelo.empty:
        st.warning("⚠️ Dados insuficientes para análise do DNA Financeiro.")
    else:
        df_combined = pd.concat(
            [df_radar, df_radar_modelo],
            ignore_index=True
        ).drop_duplicates(subset="Ativo")

        html_dna = """<div class="mobile-table-container"><table class="rockefeller-table">
            <thead>
                <tr>
                    <th>Ativo</th>
                    <th>LPA (Lucro)</th>
                    <th>VPA (Patrimônio)</th>
                    <th>P/L</th>
                    <th>P/VP</th>
                </tr>
            </thead>
            <tbody>"""

        for _, r in df_combined.iterrows():
            try:
                lpa = float(r.get('LPA', 0)) if pd.notna(r.get('LPA')) else 0.0
                vpa = float(r.get('VPA', 0)) if pd.notna(r.get('VPA')) else 0.0
                preco = float(r.get('V_Cru', 0))
            except Exception:
                lpa, vpa, preco = 0.0, 0.0, 0.0

            p_l = preco / lpa if lpa > 0 else 0.0
            p_vp = preco / vpa if vpa > 0 else 0.0

            html_dna += (
                f"<tr>"
                f"<td>{r['Ativo']}</td>"
                f"<td>{lpa:.2f}</td>"
                f"<td>{vpa:.2f}</td>"
                f"<td>{p_l:.2f}</td>"
                f"<td>{p_vp:.2f}</td>"
                f"</tr>"
            )

        html_dna += "</tbody></table></div>"
        st.markdown(html_dna, unsafe_allow_html=True)

# ==================== ABA 6: BACKTESTING ====================
with tab_backtest:
    st.header("📈 Backtesting de Oportunidade")

    if df_radar.empty:
        st.warning("⚠️ Dados insuficientes para backtesting.")
    else:
        ativo_bt = st.selectbox(
            "Selecione um ativo para simular o 'Efeito Pânico':",
            df_radar["Ativo"].unique()
        )

        df_bt = df_radar[df_radar["Ativo"] == ativo_bt]
        if df_bt.empty:
            st.warning("⚠️ Ativo não encontrado para backtesting.")
        else:
            d = df_bt.iloc[0]

            try:
                p_atual = float(d.get("V_Cru", 0))
                var_min = float(d.get("Var_Min", 0))
            except Exception:
                p_atual, var_min = 0.0, 0.0

            queda_max = abs(var_min)
            preco_fundo = p_atual / (1 + (queda_max / 100)) if p_atual > 0 else 0.0

            st.markdown("### 🛡️ Simulação: Compra no Fundo vs Hoje")

            c1, c2, c3 = st.columns(3)
            c1.metric("Preço de Compra (Fundo)", f"R$ {preco_fundo:.2f}")
            c2.metric("Preço de Venda (Hoje)", f"R$ {p_atual:.2f}")
            c3.metric(
                "Rendimento Realizado",
                f"{queda_max:.2f}%",
                delta=f"{queda_max:.2f}%"
            )

            st.success(
                f"📌 **Resultado:** Se você tivesse investido no momento de pânico "
                f"deste mês em **{ativo_bt}**, teria lucrado **{queda_max:.2f}%** "
                f"até o preço atual."
            )

# ==================== ABA 7: MANUAL DE INSTRUÇÕES ====================
with tab_manual:
    st.header("📖 Manual de Instruções - IA Rockefeller")

    with st.expander("🛰️ Radar de Ativos e Preço Justo", expanded=True):
        st.markdown(
            "* **Preço Justo (Graham):** Calculado pela fórmula V = √(22.5 × LPA × VPA)\n"
            "* **Status Descontado:** Preço de mercado abaixo do valor justo\n"
            "* **Ação COMPRAR:** Apenas quando abaixo da média de 30 dias e do preço justo"
        )

    with st.expander("📊 Raio-X de Volatilidade"):
        st.markdown(
            "* **Dias A/B:** Dias de alta (🟢) e baixa (🔴) no mês\n"
            "* **🚨 Alerta RECORDE:** Nova mínima dos últimos 30 dias"
        )

    with st.expander("🧬 DNA Financeiro"):
        st.markdown(
            "* **LPA:** Lucro por ação\n"
            "* **VPA:** Valor patrimonial por ação\n"
            "* **P/L:** Preço ÷ LPA\n"
            "* **P/VP:** Preço ÷ VPA"
        )

