"""
Case Poliedro — Passo 19 (roadmap 3.0, pedido do Gui em 24/07: "comece a
documentar qual o sistema de ensino de cada uma das escolas"): REGISTRO
PERSISTENTE de qual sistema de ensino cada Golden Lead já usa hoje.

Por que isso importa: uma Golden Lead que já usa um sistema concorrente
(Objetivo, Anglo, SAS, Positivo...) tem uma venda mais difícil (precisa
trocar de fornecedor) do que uma que usa material próprio/apostila autoral
(mais fácil de convencer a adotar um sistema pela primeira vez) ou, no
extremo, uma que já é Poliedro (não é prospect, ver poliedro_09).

Não existe base pública estruturada com essa informação — não tem como
"baixar" isso de um dataset do INEP/IBGE. É pesquisa manual, escola por
escola, via busca no site/imprensa de cada uma. Esse script não CALCULA
nada — é um registro (memória de projeto) que cresce a cada pesquisa,
igual um cache manual. Sempre que uma nova escola for pesquisada, adicione
uma linha em `REGISTROS` abaixo e rode de novo.

Achado importante da primeira leva (10 escolas pesquisadas, SP/RJ, líderes
e desafiantes de maior score): taxa de "achado" é baixa — só 1 das 10 usa um
sistema identificável publicamente (Objetivo, um concorrente direto). As
outras 9 são majoritariamente escolas tradicionais/confessionais antigas
(Beneditina, alemã, italiana, franciscana) que não divulgam publicamente
usar sistema de terceiros — provavelmente têm apostila/material próprio,
mas isso é inferência, não confirmação. Sinal pro Gui: pesquisa via busca
pública tem retorno baixo pra esse tipo de escola tradicional; pode valer
mais a pena focar esse esforço manual no segmento "Desafiante" de escolas
MENOS tradicionais (fundadas mais recentemente, sem "Colégio + sobrenome
de família/santo" no nome) — essas tendem a divulgar mais o sistema que
usam como diferencial de marketing.

Gera: data/outputs/19_sistema_ensino_identificado.csv
"""

from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")

# codigo_escola: (sistema_identificado, confianca, fonte_resumo)
# confianca: "confirmado" (o site da própria escola/notícia cita o sistema
# por nome) | "provavel_proprio" (escola tradicional/confessional, sem
# menção pública a sistema de terceiros — inferência, não confirmação) |
# "nao_identificado" (busca não trouxe sinal suficiente pra nem inferir)
REGISTROS = {
    "33065403": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (Leblon) — confessional agostiniano, tradicional, sem menção pública a sistema de terceiros"),
    "33135371": ("não identificado", "provavel_proprio", "Colégio Cruzeiro (Jacarepaguá) — escola alemã (Deutsche Schule), pedagogia própria, sem menção a sistema de terceiros"),
    "35103524": ("não identificado", "provavel_proprio", "Dante Alighieri — currículo ítalo-brasileiro reconhecido pelo governo italiano, material próprio"),
    "33062633": ("não identificado", "provavel_proprio", "Colégio de São Bento (RJ) — tradição beneditina de 163 anos, sem menção a sistema de terceiros"),
    "35399197": ("Sistema Objetivo", "confirmado", "Objetivo Colégio Integrado — usa Coleção Didática do Sistema Objetivo (concorrente direto)"),
    "33104220": ("não identificado", "nao_identificado", "Recanto Inf. Imaculada Conceição — busca não trouxe menção a sistema de ensino"),
    "33100713": ("não identificado", "nao_identificado", "Colégio Saint John (Barra da Tijuca) — busca não trouxe menção a sistema de ensino"),
    "35143406": ("não identificado", "nao_identificado", "Augusto Laranja (Moema) — parceria Cambridge International, mas sem menção a sistema de ensino nacional"),
    "35165347": ("não identificado", "nao_identificado", "Mobile Colégio — busca não retornou informação suficiente"),
    "35105314": ("não identificado", "provavel_proprio", "Colégio Franciscano Pio XII — confessional franciscano, bilíngue Cambridge, sem menção a sistema de terceiros"),
}


def montar_tabela() -> pd.DataFrame:
    """Junta o registro manual com os dados de score/segmento já calculados."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str})
    linhas = []
    for codigo, (sistema, confianca, fonte) in REGISTROS.items():
        linhas.append({"codigo_escola": codigo, "sistema_ensino_identificado": sistema,
                        "confianca": confianca, "fonte_resumo": fonte})
    registro = pd.DataFrame(linhas)
    return golden.merge(registro, on="codigo_escola", how="inner")[
        ["codigo_escola", "NO_ENTIDADE", "codigo_municipio", "segmento_comercial", "score_destaque",
         "sistema_ensino_identificado", "confianca", "fonte_resumo"]
    ]


def exibir_resumo(df: pd.DataFrame) -> None:
    print(f"[Sanity check] Escolas pesquisadas até agora: {len(df)} de {965} Golden Leads totais "
          f"({len(df) / 965 * 100:.1f}%)")
    print(f"\n[Sanity check] Distribuição de confiança:\n{df['confianca'].value_counts()}")
    print(f"\n[Sanity check] Sistemas concorrentes confirmados: "
          f"{(df['confianca'] == 'confirmado').sum()}")


def main():
    df = montar_tabela()
    exibir_resumo(df)
    df.to_csv(OUT_DIR / "19_sistema_ensino_identificado.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '19_sistema_ensino_identificado.csv'}")


if __name__ == "__main__":
    main()
