
# App de Dosagem ABCP (Streamlit)

Agora com:
- **Lookup automático do Ca** (L/m³) via seu Excel (named ranges: `Tabela2Ca`, `Tabela2Dmax`, `Tabela2Slump`).
- **Absorção (areia/brita)** e **umidade** para separar **água livre** vs **absorvida**.
- **Geração de PDF** do traço com cabeçalhos de identificação.
- Aba de **tabelas (somente leitura)** para consulta do Excel.

## Estrutura
```
abcp_streamlit_app/
├── app.py
├── core/
│   ├── abcp.py         # Cálculo + lookup de Ca
│   └── pdf_utils.py    # PDF (ReportLab)
├── data/
│   ├── 04_Dosagem_Concreto_ABCP_sem-leg.xlsx   # (opcional)
│   └── README_DATA.txt
├── requirements.txt
└── README.md
```

## Rodar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Como o Ca é lido
- O app tenta os named ranges do seu Excel: `Tabela2Ca` (matriz), `Tabela2Dmax` (linhas), `Tabela2Slump` (colunas).
- Se encontrar, você seleciona Dmáx e Slump e o Ca (L/m³) é preenchido automaticamente.
- Se não encontrar, use o modo Manual.

## Água livre vs absorvida
- Entradas: `Umidade` e `Absorção` (areia e brita).
- Fórmula: **Água a adicionar (kg/m³) = P33 + Água absorvida − Água de umidade**.

## PDF do traço
- Clique em **Gerar PDF** e baixe o arquivo com os cabeçalhos: Projeto, Técnico, Uso, Fabricado em.
