"""
Case Poliedro — Passo 25 (roadmap 3.0, pedido do Gui em 28/07): PRODUTO ALVO
— separa o universo de escolas entre alvo do Sistema Poliedro e alvo do
Sistema Polígono.

Por que este passo existe: até aqui o pipeline tinha UM ranking
(`score_destaque`) e UM corte (0,70), o que pressupõe um produto só. Com o
Polígono no portfólio — linha secundária, mensalidade menor, foco em ENEM e
preparação pro mercado de trabalho em vez de vestibular ultra-concorrido
(ITA/Fuvest/Medicina) — "score baixo" deixa de significar "lead ruim" e passa
a significar "produto errado". Isso não se resolve mexendo em peso: exige
uma classificação separada.

Tamanho do mercado hoje invisível (medido em 28/07 sobre as 4.706 escolas
com ENEM confiável): a faixa 0,40-0,70 de `score_destaque` com porte
relevante soma 1.110 escolas e ~234 mil matrículas de Ensino Médio —
praticamente o mesmo tamanho do pool inteiro de Golden Leads (1.150 escolas,
~254 mil matrículas), que é o único recorte que o pipeline enxergava.

CRITÉRIOS (PROVISÓRIOS — proposta do assistente, pendente de validação com
o time comercial do Poliedro; não são fato estatístico):

  Poliedro  -> score_destaque >= 0,70
      Justificativa: o Poliedro vende prestígio e aprovação em vestibular
      concorrido. `score_destaque` é dominado pela média do ENEM (correlação
      de posto 0,98), então ele mede exatamente o atributo que o produto
      Poliedro monetiza. Corte em 0,70 mantido por continuidade com o resto
      do pipeline — mas veja a limitação sobre o corte no final deste
      docstring.

  Polígono  -> 0,40 <= score_destaque < 0,70 E QT_MAT_MED >= 100
      Justificativa de cada metade:
      - faixa 0,40-0,70 de score: mede escola de desempenho médio a
        médio-alto. Importa porque é o público que busca ENEM e ingresso em
        curso menos disputado, não ITA/Fuvest — a proposta de valor do
        Polígono. Escola abaixo de 0,40 tende a ter restrição de preço que
        nem o Polígono resolve.
      - QT_MAT_MED >= 100: mede porte do Ensino Médio. Importa porque o
        Polígono compete por preço menor, então a conta só fecha com volume
        de alunos — escola de 30 alunos no EM não sustenta a operação
        independente do encaixe pedagógico.

  nenhum    -> resto (score < 0,40, ou faixa Polígono sem porte mínimo)

LIMITAÇÕES QUE PRECISAM ESTAR NA MESA ANTES DE USAR ISSO COMERCIALMENTE:
  1. O corte em 0,70 é arbitrário e faz mais trabalho que os pesos do score.
     Testado em 28/07: a contagem de escolas acima de 0,70 varia de 817 a
     1.412 só mudando os pesos do `score_destaque`, sem mudar nenhum dado.
  2. `score_destaque` mede VALOR SE CONVERTER, não PROBABILIDADE DE
     CONVERTER. Escola de score altíssimo é a que menos tem motivo pra
     trocar de sistema ("pra que trocar time que está ganhando?"). Nenhuma
     coluna deste pipeline mede propensão — isso continua sendo um buraco
     conhecido, não resolvido aqui.
  3. Não temos preço de mensalidade em nenhuma fonte pública. O encaixe do
     Polígono por faixa de preço é INFERIDO por proxy (score + porte), não
     medido. Essa é a limitação mais séria desta classificação.

Entrada:  data/outputs/funil_escolas_pontuadas.csv
Gera:     data/outputs/25_produto_alvo.csv
"""

import sys
import pandas as pd

from poliedro_filtros import remover_sistema_s

CAMINHO_FUNIL = "data/outputs/funil_escolas_pontuadas.csv"
CAMINHO_SAIDA = "data/outputs/25_produto_alvo.csv"

CORTE_POLIEDRO = 0.70
CORTE_MINIMO_POLIGONO = 0.40
PORTE_MINIMO_POLIGONO = 100


def carregar_escolas_pontuadas(caminho):
    """Lê o universo nacional de escolas já pontuadas, com erro explícito."""
    try:
        return pd.read_csv(caminho)
    except FileNotFoundError:
        print(
            f"ERRO: não achei '{caminho}'. "
            "Rode `python poliedro_05b_score_destaque_nacional.py` antes deste passo.",
            file=sys.stderr,
        )
        sys.exit(1)


def classificar_produto_alvo(linha):
    """Decide se a escola é alvo de Poliedro, Polígono ou de nenhum dos dois."""
    score = linha["score_destaque"]
    matriculas_em = linha["QT_MAT_MED"]
    if pd.isna(score):
        return "nenhum"
    if score >= CORTE_POLIEDRO:
        return "Poliedro"
    if score >= CORTE_MINIMO_POLIGONO and matriculas_em >= PORTE_MINIMO_POLIGONO:
        return "Polígono"
    return "nenhum"


def main():
    escolas = carregar_escolas_pontuadas(CAMINHO_FUNIL)
    confiaveis = escolas[escolas["confiavel_enem"] == True].copy()  # noqa: E712
    print(f"Escolas com ENEM confiável: {len(confiaveis)} (de {len(escolas)} no total)")
    # Escopo do projeto: só escola privada que é prospect comercial. Sistema S
    # tem sistema de ensino próprio e fica de fora — ver poliedro_filtros.py.
    confiaveis = remover_sistema_s(confiaveis)
    print(f"Escolas no escopo (privadas, fora Sistema S): {len(confiaveis)}")

    confiaveis["produto_alvo"] = confiaveis.apply(classificar_produto_alvo, axis=1)

    colunas = [
        "codigo_escola",
        "NO_ENTIDADE",
        "codigo_municipio",
        "enem_media_geral",
        "qtd_participantes_enem",
        "QT_MAT_MED",
        "indice_infra",
        "score_destaque",
        "produto_alvo",
    ]
    saida = confiaveis[colunas].sort_values(
        ["produto_alvo", "score_destaque"], ascending=[True, False]
    )
    saida.to_csv(CAMINHO_SAIDA, sep=";", index=False)

    # --- resumo de sanidade ---
    print(f"\nGerado: {CAMINHO_SAIDA}")
    print("\nContagem por produto alvo:")
    resumo = confiaveis.groupby("produto_alvo").agg(
        escolas=("codigo_escola", "count"),
        matriculas_em=("QT_MAT_MED", "sum"),
        enem_medio=("enem_media_geral", "mean"),
        score_min=("score_destaque", "min"),
        score_medio=("score_destaque", "mean"),
        score_max=("score_destaque", "max"),
    )
    print(resumo.round(2).to_string())
    print(
        "\nLembrete: os cortes (0,70 / 0,40 / 100 matrículas) são PROVISÓRIOS "
        "e não foram validados com dado de conversão — ver docstring."
    )


if __name__ == "__main__":
    main()
