
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from core.abcp import compute_abcp, load_tables_preview, load_ca_lookup, lookup_ca
from core.pdf_utils import generate_traco_pdf

st.set_page_config(page_title="Dosagem ABCP - Concreto", page_icon="🧮", layout="wide")

# --- Sidebar: identificação + Excel ---
with st.sidebar:
    st.header("📋 Identificação")
    projeto = st.text_input("Nome do Projeto", value="Obra A - Laje")
    tecnico = st.text_input("Técnico Responsável", value="Eng. Fulano de Tal")
    uso = st.selectbox("Tipo de Uso do Concreto", ["Estrutural", "Pavimento", "Viga/Laje", "Fundação", "Outros"], index=0)
    fabricado_em = st.selectbox("Fabricado em", ["Usina", "Canteiro"], index=0)
    st.markdown("---")
    st.subheader("📄 Excel com Tabelas (opcional)")
    excel_file = st.file_uploader("Carregar Excel (para lookup automático do Ca)", type=["xlsx"], key="uploader_sidebar")
    st.caption("Se não carregar, você pode informar o Ca manualmente.")

st.title("🧮 Dosagem de Concreto — Método ABCP")
tab_calc, tab_tabelas = st.tabs(["🧪 Dosagem ABCP", "📚 Tabelas (consulta)"])

# Excel default path
base_excel_path = Path("data/04_Dosagem_Concreto_ABCP_sem-leg.xlsx")
excel_path = None
if excel_file is not None:
    excel_path = excel_file
elif base_excel_path.exists():
    excel_path = str(base_excel_path)

# Ca lookup (se possível)
ca_lookup = None
if excel_path is not None:
    ca_lookup = load_ca_lookup(excel_path)

# --- Aba 1: Dosagem ---
with tab_calc:
    st.subheader("1) Entradas")
    colA, colB, colC, colD = st.columns([1,1,1,1])

    with colA:
        ac = st.number_input("Fator a/c (água/cimento)", min_value=0.30, max_value=0.70, value=0.45, step=0.01, format="%.2f")
        mode = st.radio("Origem do Ca (L/m³)", ["Manual", "Excel (lookup)"], index=0 if ca_lookup is None else 1, horizontal=True)
        if mode == "Manual":
            Ca_L = st.number_input("Consumo de Água — L/m³", min_value=120.0, max_value=260.0, value=200.0, step=5.0, format="%.1f")
        else:
            dmax_label = st.selectbox("Dmáx (Tabela 2)", ca_lookup["dmax_labels"])
            slump_label = st.selectbox("Slump (Tabela 2)", ca_lookup["slump_labels"])
            Ca_L_val = lookup_ca(ca_lookup, dmax_label, slump_label)
            if Ca_L_val is None:
                st.error("Não foi possível localizar Ca na tabela. Use modo Manual.")
                Ca_L = st.number_input("Consumo de Água — L/m³", min_value=120.0, max_value=260.0, value=200.0, step=5.0, format="%.1f")
            else:
                Ca_L = float(Ca_L_val)
            st.info(f"Ca (Tabela 2): **{Ca_L:.1f} L/m³**")

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
        U_brita = st.number_input("Umidade da Brita — % (base seca)", min_value=0.0, max_value=6.0, value=0.0, step=0.1, format="%.1f")

    st.markdown("---")
    st.subheader("2) Absorção e Conversão volumétrica")
    colE, colF = st.columns(2)
    with colE:
        a_areia = st.number_input("Absorção da Areia — %", min_value=0.0, max_value=5.0, value=0.0, step=0.1, format="%.1f")
        a_brita = st.number_input("Absorção da Brita — % (total)", min_value=0.0, max_value=5.0, value=1.0, step=0.1, format="%.1f")
    with colF:
        rho_s_bulk = st.number_input("Massa unitária aparente da Areia (seca) — kg/m³", min_value=1200.0, max_value=1800.0, value=1470.0, step=10.0, format="%.0f")
        I_inch = st.number_input("Inchamento da Areia — %", min_value=0.0, max_value=35.0, value=20.0, step=1.0, format="%.0f")

    st.markdown("---")

    # Cálculo
    inputs = dict(
        ac=ac, Ca_L=Ca_L, rho_w=rho_w, Cc_min=Cc_min,
        rho_c=rho_c, rho_s_grain=rho_s_grain,
        rho_b_menor=rho_b_menor, rho_b_maior=rho_b_maior,
        Cb_total=Cb_total, perc_b_menor=perc_b_menor,
        U_areia=U_areia, I_inch=I_inch, rho_s_bulk=rho_s_bulk,
        a_areia=a_areia, a_brita=a_brita, U_brita=U_brita
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
                "Areia (seca) — Cm,seca",
                "Areia (úmida) — Cm,úmida",
                "Água na areia (umidade)",
                "Água na brita (umidade)",
                "Água absorvida (areia+brita)",
                "Água (umidade total)",
                "Água a adicionar (kg/m³)"
            ],
            "Valor (kg/m³)": [
                round(out["P33"],2),
                round(out["Cc"],2),
                round(out["Cb_menor"],2),
                round(out["Cb_maior"],2),
                round(out["Cm_seca"],2),
                round(out["Cm_umida"],2),
                round(out["agua_areia_total"],2),
                round(out["agua_brita_total"],2),
                round(out["agua_absorcao"],2),
                round(out["agua_moist_total"],2),
                round(out["agua_adicionar_kg"],2),
            ]
        }))

    with col2:
        st.markdown("**Volumes (m³ e L)**")
        st.table(pd.DataFrame({
            "Grandeza": [
                "Volume do cimento — Vc (m³)",
                "Volume da água — Vw (m³)",
                "Volume das britas — Vg (m³)",
                "Volume de areia — Vm (m³)",
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
    st.subheader("4) Gerar PDF do Traço")
    ident = dict(projeto=projeto, tecnico=tecnico, uso=uso, fabricado_em=fabricado_em)
    if st.button("Gerar PDF"):
        pdf_path = Path("traco_abcp.pdf")
        generate_traco_pdf(str(pdf_path), ident, inputs, out)
        with open(pdf_path, "rb") as f:
            st.download_button("Baixar PDF", f, file_name="traco_abcp.pdf", mime="application/pdf")

    st.caption("Obs.: Água a adicionar = P33 + Água absorvida (agregados) − Água de umidade (agregados).")

# --- Aba 2: Tabelas ---
with tab_tabelas:
    st.subheader("Tabelas de consulta (somente leitura)")
    excel_file_tab = st.file_uploader("Carregar Excel com tabelas (opcional)", type=["xlsx"], key="uploader_tab")
    base_path = Path("data/04_Dosagem_Concreto_ABCP_sem-leg.xlsx")
    xp = None
    if excel_file_tab is not None:
        xp = excel_file_tab
    elif base_path.exists():
        xp = str(base_path)
    if xp is not None:
        previews = load_tables_preview(xp)
        for name, df in previews.items():
            st.markdown(f"### {name}")
            st.dataframe(df, use_container_width=True, height=320)
    else:
        st.info("Coloque seu Excel em `data/04_Dosagem_Concreto_ABCP_sem-leg.xlsx` ou faça upload acima.")
