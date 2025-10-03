
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

def generate_traco_pdf(path, ident, inputs, outputs):
    c = canvas.Canvas(path, pagesize=A4)
    W, H = A4
    x0, y = 20*mm, H - 20*mm

    def line(txt, dy=6*mm, color=colors.black, size=11, bold=False):
        nonlocal y
        c.setFillColor(color)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x0, y, str(txt))
        y -= dy

    # Cabeçalho
    line("DOSAGEM DE CONCRETO — MÉTODO ABCP", size=14, bold=True, dy=8*mm)
    line(f"Projeto: {ident.get('projeto','')}")
    line(f"Técnico Responsável: {ident.get('tecnico','')}")
    line(f"Tipo de Uso do Concreto: {ident.get('uso','')}")
    line(f"Fabricado em: {ident.get('fabricado_em','')}")
    y -= 2*mm
    c.line(x0, y, W-20*mm, y); y -= 5*mm

    # Entradas resumidas
    line("Entradas:", bold=True)
    for k in ["ac","Ca_L","rho_w","Cc_min","rho_c","rho_s_grain","rho_b_menor","rho_b_maior","Cb_total","perc_b_menor","U_areia","I_inch","rho_s_bulk","a_areia","a_brita","U_brita"]:
        if k in inputs:
            line(f" - {k}: {inputs[k]}")

    y -= 2*mm
    c.line(x0, y, W-20*mm, y); y -= 5*mm

    # Resultados
    line("Resultados (por 1 m³):", bold=True)
    keys_order = [
        ("P33","Água (massa alvo) — P33 [kg/m³]"),
        ("Cc","Cimento — Cc [kg/m³]"),
        ("Cb_menor","Brita Menor — [kg/m³]"),
        ("Cb_maior","Brita Maior — [kg/m³]"),
        ("V_c","Volume do cimento — Vc [m³]"),
        ("V_w","Volume da água — Vw [m³]"),
        ("V_g_total","Volume das britas — Vg [m³]"),
        ("Vm","Volume da areia — Vm [m³]"),
        ("Cm_seca","Areia (seca) — [kg/m³]"),
        ("Cm_umida","Areia (úmida) — [kg/m³]"),
        ("agua_areia_total","Água na areia — [kg/m³]"),
        ("agua_brita_total","Água na brita — [kg/m³]"),
        ("agua_absorcao","Água absorvida (areia+brita) — [kg/m³]"),
        ("agua_moist_total","Água de umidade (areia+brita) — [kg/m³]"),
        ("agua_adicionar_kg","Água a adicionar — [kg/m³]"),
        ("V_areia_med_m3","Areia a medir com inchamento — [m³]"),
        ("V_areia_med_L","Areia a medir com inchamento — [L]"),
    ]
    for key, label in keys_order:
        if key in outputs:
            line(f" - {label}: {round(outputs[key],4)}")

    c.showPage()
    c.save()
