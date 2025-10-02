import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from core.abcp import compute_abcp, load_tables_preview

st.set_page_config(page_title="Dosagem ABCP - Concreto", page_icon="🧮", layout="wide")

# --- Sidebar: identificação do projeto ---
with st.sidebar:
    st.header("📋 Identificação")
    projeto = st.text_input("Nome do Projeto", value="Obra A - Laje")
    tecnico = st.text_input("Técnico Responsável", value="Eng. Fulano de Tal")
    uso = st.selectbox("Tipo de Uso do Concreto", ["Estrutural", "Pavimento", "Viga/LAJE", "Fundação", "Outros"], index=0)
    fabricado_em = st.selectbox("Fabricado em", ["Usina", "Canteiro"], index=0)
    st.markdown("---")
    st.caption("Preenchimentos não influenciam nos cálculos; saem em cabeçalhos/relatórios.")

st.title("🧮 Dosagem de Concreto — Método ABCP")
st.write("Preencha os **dados de entrada**. Os **resultados** são atualizados automaticamente.")

tab_calc, tab_tabelas = st.tabs(["🧪 Dosagem ABCP", "📚 Tabelas (consulta)"])

# --- Aba 1: Dosagem ---
with tab_calc:
    st.subheader("1) Entradas")
    colA, colB, colC, colD = st.columns([1,1,1,1])

    with colA:
        ac = st.number_input("Fator a/c (água/cimento)", min_value=0.30, max_value=0.70, value=0.45, step=0.01, format="%.2f")
        Ca_L = st.number_input("Consumo de Água (Tabela 2) — L/m³", min_value=120.0, max_value=260.0, value=200.0, step=5.0, format="%.1f")
        Cc_min = st.number_input("Consumo Mínimo de Cimento — kg/m³", min_value=240.0, max_value=400.0, value=320.0, step=10.0, format="%.0f")

    with colB:
        rho_w = st.number_input("Massa específica da Água — kg/m³", min_value=980.0, max_value=1020.0, value=1000.0, step=1.0, format="%.0f")
        rho_c = st.number_input("Massa específica do Cimento (grão) — kg/m³", min_value=2900.0, max_value=3300.0, value=3100.0, step=10.0, format="%.0f")
        rho_s_grain = st.number_input("Massa específica da Areia (grão) — kg/m³", min_value=2500.0, max_value=2700.0, value=2650.0, step=10.0, format="%.0f")

    with colC:
        rho_b_menor = st.number_input("Massa específica Brita Menor (grão) — kg/m³", min_value=2600.0, max_value=2800.0, value=2700.0, step=10.0, format="%.0f")
        rho_b_maior = st.number_input("Massa específica Brita Maior (grão) — kg/m³", min_value=2600.0, max_value=2800.0, value=2700.0, step=10.0, format="%.0f")
        Cb_total = st.number_input("Consumo Total de Brita — kg/m³", min_value=800.0, max_value=1300.0, value=1065.0, step=5.0, format="%.0f")

    with colD:
        perc_b_menor = st.slider("Distribuição Brita Menor (%)", min_value=0, max_value=100, value=50, step=5)
        U_areia = st.number_input("Umidade da Areia — % (base seca)", min_value=0.0, max_value=12.0, value=6.0, step=0.1, format="%.1f")
        I_inch = st.number_input("Inchamento da Areia — %", min_value=0.0, max_value=35.0, value=20.0, step=1.0, format="%.0f")

    st.markdown("—")

    st.subheader("2) Parâmetros para conversão volumétrica (obra)")
    colE, colF = st.columns(2)
    with colE:
        rho_s_bulk = st.number_input("Massa unitária aparente da Areia (seca) — kg/m³", min_value=1200.0, max_value=1800.0, value=1470.0, step=10.0, format="%.0f")
    with colF:
        pass

    st.markdown("---")

    # Cálculo
    inputs = dict(
        ac=ac, Ca_L=Ca_L, rho_w=rho_w, Cc_min=Cc_min,
        rho_c=rho_c, rho_s_grain=rho_s_grain,
        rho_b_menor=rho_b_menor, rho_b_maior=rho_b_maior,
        Cb_total=Cb_total, perc_b_menor=perc_b_menor,
        U_areia=U_areia, I_inch=I_inch, rho_s_bulk=rho_s_bulk
    )
    out = compute_abcp(**inputs)

    st.subheader("3) Resultados (por 1 m³)")
    col1, col2 = st.columns([1.2,1])
    with col1:
        st.markdown("**Massas (kg/m³)**")
        st.table(pd.DataFrame({
            "Grandeza": [
                "Água (massa alvo) — P33",
                "Cimento — Cc",
                "Brita Menor — Cb,menor",
                "Brita Maior — Cb,maior",
                "Areia (seca) — Cm,seca (N46)",
                "Areia (úmida) — Cm,úmida (N47)",
                "Água na areia — N48",
                "Água a adicionar (kg/m³)"
            ],
            "Valor (kg/m³)": [
                round(out["P33"],2),
                round(out["Cc"],2),
                round(out["Cb_menor"],2),
                round(out["Cb_maior"],2),
                round(out["Cm_seca"],2),
                round(out["Cm_umida"],2),
                round(out["agua_areia"],2),
                round(out["agua_adicionar_kg"],2),
            ]
        }))

    with col2:
        st.markdown("**Volumes (m³ e L)**")
        st.table(pd.DataFrame({
            "Grandeza": [
                "Volume da pasta de cimento",
                "Volume da água (pelo ρ_água)",
                "Volume das britas (total)",
                "Volume de areia (Vm)",
                "Areia a medir (com inchamento) — m³",
                "Areia a medir — L"
            ],
            "Valor": [
                round(out["V_c"],4),
                round(out["V_w"],4),
                round(out["V_g_total"],4),
                round(out["Vm"],4),
                round(out["V_areia_med_m3"],4),
                round(out["V_areia_med_L"],1),
            ]
        }))

    st.markdown("---")
    st.caption("Observação: Ca (L/m³) → P33 (kg/m³) via ρ_água; 'Água a adicionar' = P33 − (água trazida pela areia).")

# --- Aba 2: Tabelas ---
with tab_tabelas:
    st.subheader("Tabelas de consulta (somente leitura)")
    st.write("Você pode **carregar seu Excel** com as tabelas (aba 'Água - Cimento', etc.).")
    excel_file = st.file_uploader("Carregar Excel com tabelas (opcional)", type=["xlsx"])
    base_path = Path("data/04_Dosagem_Concreto_ABCP_sem-leg.xlsx")
    excel_path = None

    if excel_file is not None:
        excel_path = excel_file
    elif base_path.exists():
        excel_path = str(base_path)
    else:
        st.info("Coloque seu Excel em `data/04_Dosagem_Concreto_ABCP_sem-leg.xlsx` ou faça upload acima.")

    if excel_path is not None:
        previews = load_tables_preview(excel_path)
        for name, df in previews.items():
            st.markdown(f"### {name}")
            st.dataframe(df, use_container_width=True, height=320)
