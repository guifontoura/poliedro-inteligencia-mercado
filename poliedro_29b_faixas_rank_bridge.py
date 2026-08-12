"""
Case Poliedro — Passo 29b (pedido do Gui, 07/08): TABELA-PONTE de faixas de rank
pro slicer em Bloco "Top 5 / Top 10 / Demais escolas" da página 3.

Por que isso não é só uma coluna categórica na tabela 29 (como a 1ª tentativa,
`faixa_rank_cidade` — essa coluna continua lá, inofensiva, mas não alimenta
mais o slicer): uma coluna categórica dá UM valor por escola (rank 3 vira só
"Top 5", nunca também "Top 10"). Isso faz o slicer se comportar errado pro
que o Gui pediu — clicar "Top 10" tem que trazer as escolas 1 a 10 (cumulativo,
já incluindo o Top 5), não só as 6-10. E "Demais escolas" tem que trazer TODAS
as escolas pesquisadas, não só quem ficou de fora do Top 10.

A solução (pedido explícito do Gui, 07/08: resolver no pipeline, não com
bookmark — bookmark de página inteira é frágil, quebra silenciosamente se
qualquer visual da página mudar depois) é uma TABELA-PONTE many-to-many:
cada escola aparece uma linha PARA CADA faixa que ela pertence —
escola rank 3 aparece 3x (Top 5, Top 10, Demais escolas), escola rank 8
aparece 2x (Top 10, Demais escolas), escola rank 15 aparece 1x (Demais
escolas, porque toda escola pesquisada entra nessa faixa). No Power BI, o
slicer em Bloco passa a apontar pro campo `faixa_rank_cidade` DESTA tabela
(não mais da `29_universo_completo_powerbi`), relacionada à tabela principal
por `codigo_escola` com direção de filtro "Ambas" — clicar num bloco filtra
a ponte, que propaga o filtro de volta pra tabela de escolas. É a técnica
padrão de mercado pra "Top N" clicável em Power BI (bridge table).

Limitação conhecida (documentar, não esconder): relacionamento bidirecional
pode causar ambiguidade de filtro em modelos com muitas tabelas — aqui é
seguro porque só ~7.800 linhas e poucas tabelas no modelo, mas não é um
padrão pra copiar sem pensar em modelos maiores.

`faixa_ordem` existe só pra resolver o pedido de ORDEM dos blocos (Top 5,
Top 10, Demais escolas — não a ordem alfabética que o Power BI usa por
padrão): configurar "Ordenar coluna por" em `faixa_rank_cidade` apontando
pra esta coluna, no Power BI Desktop.

Gera: data/outputs/29b_faixas_rank_bridge.csv (separador ';', decimal ',').
"""

import sys
from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")

# (nome de exibição, ordem pro slicer, limite de rank_municipio — None = sem limite/todo mundo)
_FAIXAS = [
    ("Top 5", 1, 5),
    ("Top 10", 2, 10),
    ("Demais escolas", 3, None),
]


def carregar_universo() -> pd.DataFrame:
    """Lê codigo_escola + rank_municipio do passo 29, com erro explícito se faltar."""
    caminho = OUT_DIR / "29_universo_completo_powerbi.csv"
    try:
        return pd.read_csv(caminho, sep=";", decimal=",", dtype={"codigo_escola": str})[
            ["codigo_escola", "rank_municipio"]
        ]
    except FileNotFoundError:
        print(f"ERRO: não achei '{caminho}'. Rode `python poliedro_29_universo_completo_powerbi.py` antes deste passo.",
              file=sys.stderr)
        sys.exit(1)


def montar_bridge_faixas_rank(escolas: pd.DataFrame) -> pd.DataFrame:
    """Expande 1 linha/escola em N linhas (escola, faixa) — 1 por faixa que a escola pertence, de forma cumulativa."""
    linhas = []
    for nome, ordem, limite in _FAIXAS:
        mascara = escolas["rank_municipio"] <= limite if limite is not None else pd.Series(True, index=escolas.index)
        subset = escolas.loc[mascara, ["codigo_escola"]].copy()
        subset["faixa_rank_cidade"] = nome
        subset["faixa_ordem"] = ordem
        linhas.append(subset)
    return pd.concat(linhas, ignore_index=True)


def exibir_resumo(bridge: pd.DataFrame, total_escolas: int) -> None:
    print(f"[Sanity check] Total de linhas na tabela-ponte: {len(bridge):,}")
    print(f"[Sanity check] Distribuição por faixa:\n{bridge['faixa_rank_cidade'].value_counts()}")
    escolas_em_demais = bridge.loc[bridge['faixa_rank_cidade'] == 'Demais escolas', 'codigo_escola'].nunique()
    print(f"[Sanity check] Escolas cobertas por 'Demais escolas' (deve ser TODAS): {escolas_em_demais:,} de {total_escolas:,} "
          f"({'OK, bate' if escolas_em_demais == total_escolas else 'DIVERGÊNCIA — investigar'})")
    top5 = bridge.loc[bridge['faixa_rank_cidade'] == 'Top 5', 'codigo_escola'].nunique()
    top10 = bridge.loc[bridge['faixa_rank_cidade'] == 'Top 10', 'codigo_escola'].nunique()
    print(f"[Sanity check] Escolas em 'Top 5': {top5:,} | escolas em 'Top 10' (cumulativo, já inclui Top 5): {top10:,} "
          f"({'OK, Top 10 >= Top 5' if top10 >= top5 else 'DIVERGÊNCIA — investigar'})")


def main():
    escolas = carregar_universo()
    bridge = montar_bridge_faixas_rank(escolas)
    exibir_resumo(bridge, total_escolas=len(escolas))
    bridge.to_csv(OUT_DIR / "29b_faixas_rank_bridge.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '29b_faixas_rank_bridge.csv'}")


if __name__ == "__main__":
    main()
