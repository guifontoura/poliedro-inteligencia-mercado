"""
Case Poliedro — Passo 29c (pedido do Gui, 09/08): TABELA-PONTE de segmento
Golden Leads pro slicer em Bloco "Golden Leads x Outras Escolas" da página 1.

Mesmo problema estrutural do 29b (faixas de rank): a coluna `segmento_golden_lead`
criada direto em `29_universo_completo_powerbi` (1ª tentativa) só marca UM valor
por escola ("Golden Leads (1.127)" ou em branco) — funciona como liga/desliga de
1 bloco só, mas não dá pra ter um 2º bloco "Outras Escolas (4.444)" que mostre
honestamente TODAS as escolas quando clicado. Pra isso, uma Golden Lead precisa
aparecer em DUAS categorias ao mesmo tempo: "Golden Leads" (porque é uma) e
"Outras Escolas" (porque toda escola pesquisada entra nessa contagem de 4.444,
Golden Leads incluídas) — exatamente o mesmo tipo de sobreposição do Top 5/Top 10/
Demais escolas, resolvido com o mesmo mecanismo: tabela-ponte many-to-many.

TODA escola do universo ganha 1 linha "Outras Escolas (N)" (N = total, hoje 4.444).
Só as Golden Leads ganham uma 2ª linha extra "Golden Leads (M)" (M = golden leads,
hoje 1.127). Escola comum aparece 1x; Golden Lead aparece 2x. No Power BI, o slicer
em Bloco aponta pro campo `segmento_golden_lead` DESTA tabela (não mais da coluna
homônima em `29_universo_completo_powerbi`, que fica lá sem uso, inofensiva),
relacionada à tabela principal por `codigo_escola` com direção de filtro "Ambas".

Por que não bookmark (pedido explícito do Gui, mesmo motivo já documentado no 29b
e no card de limitações da página 3): bookmark de página inteira é frágil, quebra
silenciosamente se qualquer visual da página mudar depois.

Os números "(1.127)"/"(4.444)" ficam embutidos no VALOR da coluna, recalculados a
cada rodada deste script — não são texto digitado manualmente num botão do Power BI
(era esse o problema dos 4 botões antigos que este passo substitui).

`segmento_ordem` existe só pra Golden Leads aparecer antes de Outras Escolas no
slicer (não a ordem alfabética default do Power BI): configurar "Ordenar por
Coluna" em `segmento_golden_lead` apontando pra esta coluna, no Power BI Desktop.

Limitação conhecida (mesma do 29b): relacionamento bidirecional pode causar
ambiguidade de filtro em modelos com muitas tabelas — seguro aqui (poucas tabelas,
poucas linhas), não é padrão pra copiar sem pensar em modelos maiores.

Gera: data/outputs/29c_golden_leads_bridge.csv (separador ';', decimal ',').
"""

import sys
from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")


def carregar_universo() -> pd.DataFrame:
    """Lê codigo_escola + produto_alvo do passo 29, com erro explícito se faltar."""
    caminho = OUT_DIR / "29_universo_completo_powerbi.csv"
    try:
        return pd.read_csv(caminho, sep=";", decimal=",", dtype={"codigo_escola": str})[
            ["codigo_escola", "produto_alvo"]
        ]
    except FileNotFoundError:
        print(f"ERRO: não achei '{caminho}'. Rode `python poliedro_29_universo_completo_powerbi.py` antes deste passo.",
              file=sys.stderr)
        sys.exit(1)


def montar_bridge_golden_leads(escolas: pd.DataFrame) -> pd.DataFrame:
    """Toda escola ganha 1 linha 'Outras Escolas (N)'; Golden Leads ganham uma 2ª linha 'Golden Leads (M)'."""
    total = len(escolas)
    eh_golden = escolas["produto_alvo"] == "Poliedro"
    n_golden = int(eh_golden.sum())

    # Emoji igual aos botões antigos (pedido do Gui, 09/08) — só estética, não muda a lógica de filtro.
    rotulo_outras = f"🔵 Outras Escolas ({total:,})".replace(",", ".")
    rotulo_golden = f"🟡 Golden Leads ({n_golden:,})".replace(",", ".")

    outras = escolas[["codigo_escola"]].copy()
    outras["segmento_golden_lead"] = rotulo_outras
    outras["segmento_ordem"] = 2

    golden = escolas.loc[eh_golden, ["codigo_escola"]].copy()
    golden["segmento_golden_lead"] = rotulo_golden
    golden["segmento_ordem"] = 1

    return pd.concat([golden, outras], ignore_index=True)


def exibir_resumo(bridge: pd.DataFrame, total_escolas: int) -> None:
    print(f"[Sanity check] Total de linhas na tabela-ponte: {len(bridge):,}")
    print(f"[Sanity check] Distribuição por segmento:\n{bridge['segmento_golden_lead'].value_counts()}")
    rotulo_outras = bridge.loc[bridge["segmento_ordem"] == 2, "segmento_golden_lead"].iloc[0]
    escolas_em_outras = bridge.loc[bridge["segmento_golden_lead"] == rotulo_outras, "codigo_escola"].nunique()
    print(f"[Sanity check] Escolas cobertas por '{rotulo_outras}' (deve ser TODAS): {escolas_em_outras:,} de "
          f"{total_escolas:,} ({'OK, bate' if escolas_em_outras == total_escolas else 'DIVERGÊNCIA — investigar'})")
    rotulo_golden = bridge.loc[bridge["segmento_ordem"] == 1, "segmento_golden_lead"].iloc[0]
    escolas_em_golden = bridge.loc[bridge["segmento_golden_lead"] == rotulo_golden, "codigo_escola"].nunique()
    print(f"[Sanity check] Escolas em '{rotulo_golden}': {escolas_em_golden:,} (deve ser <= total)")


def main():
    escolas = carregar_universo()
    bridge = montar_bridge_golden_leads(escolas)
    exibir_resumo(bridge, total_escolas=len(escolas))
    # encoding='utf-8-sig' grava o BOM UTF-8 — sem ele o Power Query às vezes abre o CSV como
    # Windows-1252 por padrão e corrompe os emoji (texto acentuado comum passa batido, emoji não).
    bridge.to_csv(OUT_DIR / "29c_golden_leads_bridge.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print(f"\n[✓] Salvo em {OUT_DIR / '29c_golden_leads_bridge.csv'}")


if __name__ == "__main__":
    main()
