from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any, Union
from pathlib import Path

def compute_abcp(
    ac: float,
    Ca_L: float,
    rho_w: float,
    Cc_min: float,
    rho_c: float,
    rho_s_grain: float,
    rho_b_menor: float,
    rho_b_maior: float,
    Cb_total: float,
    perc_b_menor: int,
    U_areia: float,
    I_inch: float,
    rho_s_bulk: float,
) -> Dict[str, Any]:
    """Calcula dosagem ABCP principal (1 m³).
    Entradas em unidades usuais (kg/m³, %, etc.).
    Retorna massas, volumes e conversões volumétricas p/ obra.
    """
    # Água de dosagem em massa (kg/m³), a partir de Ca em L/m³ e rho_w:
    P33 = Ca_L * (rho_w / 1000.0)

    # Consumo de cimento (kg/m³) respeitando mínimo
    Cc_calc = P33 / max(ac, 1e-9)
    Cc = max(Cc_calc, Cc_min)

    # Distribuição de brita
    frac_menor = np.clip(perc_b_menor/100.0, 0, 1)
    Cb_menor = Cb_total * frac_menor
    Cb_maior = Cb_total * (1.0 - frac_menor)

    # Volumes absolutos
    V_c = Cc / rho_c
    V_w = P33 / rho_w
    V_g_menor = Cb_menor / rho_b_menor
    V_g_maior = Cb_maior / rho_b_maior
    V_g_total = V_g_menor + V_g_maior

    Vm = 1.0 - (V_c + V_w + V_g_total)
    Vm = max(Vm, 0.0)  # não permitir negativo

    # Areia (massa seca e úmida)
    Cm_seca = Vm * rho_s_grain
    U = U_areia / 100.0
    Cm_umida = Cm_seca * (1.0 + U)
    agua_areia = Cm_umida - Cm_seca  # N47 - N46 = N48

    # Água efetiva a adicionar (massa)
    agua_adicionar_kg = P33 - agua_areia
    # Conversão para litragem
    V_areia_seca_aparente = Cm_seca / rho_s_bulk
    I = I_inch / 100.0
    V_areia_med_m3 = V_areia_seca_aparente * (1.0 + I)
    V_areia_med_L = V_areia_med_m3 * 1000.0

    return dict(
        P33=P33, Cc=Cc,
        Cb_menor=Cb_menor, Cb_maior=Cb_maior,
        V_c=V_c, V_w=V_w, V_g_total=V_g_total, Vm=Vm,
        Cm_seca=Cm_seca, Cm_umida=Cm_umida,
        agua_areia=agua_areia, agua_adicionar_kg=agua_adicionar_kg,
        V_areia_med_m3=V_areia_med_m3, V_areia_med_L=V_areia_med_L
    )

def load_tables_preview(excel_path: Union[str, bytes, Path]) -> Dict[str, pd.DataFrame]:
    """Carrega pré-visualizações das tabelas do Excel (somente leitura).
    Retorna até 3 abas como DataFrames.
    """
    previews: Dict[str, pd.DataFrame] = {}
    try:
        # Tenta ler algumas abas conhecidas
        xls = pd.ExcelFile(excel_path, engine="openpyxl")
        for name in xls.sheet_names:
            # Limitar a leitura para não ficar pesado
            df = pd.read_excel(xls, sheet_name=name, header=None, nrows=60, usecols="A:Z", engine="openpyxl")
            previews[name] = df
            if len(previews) >= 3:
                break
    except Exception as e:
        previews["Aviso"] = pd.DataFrame({"Mensagem": [f"Não foi possível ler o Excel: {e}"]})
    return previews
