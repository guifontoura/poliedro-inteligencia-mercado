"""
Case Poliedro — Passo 14 (bônus, roadmap 2.0): CONSOLIDAR DATASET PARA POWER BI.

Junta as 869 Golden Leads com os dados de cidade (nome, UF, score de
priorização) e com o bairro geocodificado (onde existir, 167 das 869) num
único par de tabelas prontas para importar no Power BI — sem precisar
recalcular nada, só carregar e relacionar.

Modelo sugerido (ver POWER_BI_GUIA.md):
- `14_escolas_powerbi.csv` (fato, 869 linhas): 1 linha por Golden Lead.
- `14_cidades_powerbi.csv` (dimensão, 318 linhas): 1 linha por município do
  recorte, com `top10` como flag booleana pra filtro rápido.
Relacionamento: `codigo_municipio` (N:1, escolas → cidades).

Gera: data/outputs/14_escolas_powerbi.csv, data/outputs/14_cidades_powerbi.csv

Formato do CSV: separador ';' e decimal ',' (padrão brasileiro), não o padrão
internacional do pandas ('.' decimal). Isso é de propósito — o Power BI
Desktop instalado com localidade Português (Brasil) auto-detecta esse
formato ao importar, sem exigir o passo manual de "Alterar Tipo com
Localidade" no Power Query pra cada coluna decimal.
"""

from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")


def montar_tabela_escolas() -> pd.DataFrame:
    """Golden Leads + nome/UF da cidade + bairro geocodificado (quando existir)."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv")
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv")[
        ["codigo_municipio", "nome_municipio_ibge", "uf", "score_priorizacao"]
    ]
    geo = pd.read_csv(OUT_DIR / "05_golden_leads_geocodificadas.csv")[
        ["codigo_escola", "bairro", "CO_CEP"]
    ]

    escolas = golden.merge(cidades, on="codigo_municipio", how="left")
    escolas = escolas.merge(geo, on="codigo_escola", how="left")
    escolas = escolas.rename(
        columns={
            "nome_municipio_ibge": "cidade",
            "uf": "UF",
            "score_priorizacao": "score_priorizacao_cidade",
            "CO_CEP": "cep",
        }
    )
    # Int64 nullable (não float) — evita "52060460,0" no CSV pros CEPs
    # em branco (703 das 869, ainda não geocodificadas).
    escolas["cep"] = escolas["cep"].astype("Int64")
    return escolas


def montar_tabela_cidades() -> pd.DataFrame:
    """Todas as 318 cidades do recorte, com rank e flag Top10 pra filtro rápido no Power BI."""
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv").sort_values(
        "score_priorizacao", ascending=False
    ).reset_index(drop=True)
    cidades["rank_cidade"] = cidades.index + 1
    cidades["top10"] = cidades["rank_cidade"] <= 10
    return cidades


def exibir_resumo(escolas: pd.DataFrame, cidades: pd.DataFrame) -> None:
    print(f"[Sanity check] Escolas: {len(escolas):,} | Cidades: {len(cidades):,}")
    print(f"[Sanity check] Escolas com bairro geocodificado: {escolas['bairro'].notna().sum():,}")
    print(f"[Sanity check] Segmentos: {escolas['segmento_comercial'].value_counts().to_dict()}")


def main():
    escolas = montar_tabela_escolas()
    cidades = montar_tabela_cidades()
    exibir_resumo(escolas, cidades)
    # sep=';' e decimal=',' — formato brasileiro, pro Power BI Desktop
    # (localidade pt-BR) reconhecer os decimais automaticamente na importação.
    escolas.to_csv(OUT_DIR / "14_escolas_powerbi.csv", index=False, sep=";", decimal=",")
    cidades.to_csv(OUT_DIR / "14_cidades_powerbi.csv", index=False, sep=";", decimal=",")
    print(f"[✓] Salvo em {OUT_DIR / '14_escolas_powerbi.csv'} e {OUT_DIR / '14_cidades_powerbi.csv'}")


if __name__ == "__main__":
    main()
