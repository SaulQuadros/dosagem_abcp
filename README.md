# App de Dosagem ABCP (Streamlit)

Este app reproduz a lógica principal de dosagem de concreto pelo método **ABCP**,
com entradas agrupadas, resultados automáticos e uma aba de **tabelas** (somente leitura)
para consulta. Preparado para rodar localmente ou no **Streamlit Cloud** a partir de um repositório GitHub.

## 📦 Estrutura
```text
abcp_streamlit_app/
├── app.py                 # Aplicativo Streamlit (tabs: Dosagem e Tabelas)
├── core/
│   └── abcp.py            # Cálculos e leitura de prévias das tabelas
├── data/
│   ├── 04_Dosagem_Concreto_ABCP_sem-leg.xlsx   # (coloque aqui seu Excel)
│   └── README_DATA.txt
├── requirements.txt
└── README.md
```

## ▶️ Como rodar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔧 Entradas e lógica (resumo)
- **N33 (L/m³)** → entrada `Consumo de Água (Tabela 2) — L/m³`.
- **P33 (kg/m³)** = N33 × ρ_água / 1000 (ρ_água editável).
- **Cc (kg/m³)** = max( P33 / (a/c), Cc_min ).
- **Volumes absolutos**: V_c = Cc/ρ_c; V_w = P33/ρ_w; V_g = Σ(Cb_i/ρ_b_i).
- **Vm** = 1 − (V_c + V_w + V_g).
- **Cm (seca)** = Vm × ρ_areia(grão).
- **Umidade** U% (base seca): Cm(úmida) = Cm(seca) × (1+U); Água na areia = Cm(úmida) − Cm(seca).
- **Água a adicionar (kg/m³)** = P33 − Água na areia.
- **Volume p/ obra**: V_areia(seca, aparente) = Cm(seca)/ρ_areia(aparente); com inchamento I%: ×(1+I).

> **Importante:** A aba **Tabelas** pode carregar seu Excel (aba *Água - Cimento*, etc.) para consulta visual.
O cálculo do **Ca** no app é uma entrada manual (L/m³), mantendo a fidelidade dimensional.
Se quiser automatizar o lookup do Ca a partir da sua planilha, podemos mapear a Tabela 2 no código.

## 🧾 Campos de Identificação
Na barra lateral:
- **Nome do Projeto**
- **Técnico Responsável**
- **Tipo de Uso do Concreto**
- **Fabricado em** (Usina/Canteiro)

Esses campos são exibidos no app e podem ser agregados em relatórios/exportações futuras.

## 🚀 Deploy no Streamlit Cloud
1. Crie um repositório no GitHub e faça upload desta pasta.
2. Em *New app*, aponte para `app.py` e selecione o repositório.
3. Garanta que `requirements.txt` está no repositório.
4. (Opcional) Coloque seu Excel em `data/` para exibir as tabelas na segunda aba.

## ✅ Próximos incrementos (opcionais)
- Leitura automática do **Ca** (Tabela 2) do seu Excel.
- Inclusão de **absorção** de agregados (água livre × absorvida).
- Geração de **PDF** do traço com cabeçalho (projeto/técnico/uso/fabricação).
- Aba extra para **verificação de consistência** (Vm>0, limites, etc.).
