"""
Case Poliedro — Passo 9 (protótipo, discussão em 21/07, ainda não substituiu a
leitura oficial do deck sem confirmação de Gui): SEGMENTAÇÃO COMERCIAL DENTRO
DO UNIVERSO "GOLDEN LEADS".

Revisão pós-feedback: a primeira versão deste script EXCLUÍA a líder de cada
cidade da lista de candidatas (só considerava 2º-5º lugar). Gui apontou
corretamente que isso descarta leads válidas — a tese de "focar no 2º-5º
lugar" é uma prioridade do time comercial (quem tem motivo pra trocar de
sistema), não um motivo pra tirar a líder da lista de leads possíveis.

Modelo atual: UM universo único de "Golden Leads" = todas as escolas com
score_destaque >= 0.70 (a mesma definição que já unificava 869 escolas no
projeto — sem separar "Golden Leads" de "Qualificadas" por faixa de score).
Cada escola recebe uma TAG de segmento comercial baseada na posição dela
dentro do próprio município (não é mais um filtro de exclusão):

- "Líder local": está em 1º lugar (score_destaque) entre as escolas
  confiáveis do seu município. Já é a referência acadêmica local — mais
  difícil de converter (sem motivo comercial urgente pra trocar de sistema),
  mas ainda uma lead legítima (parceria de prestígio/vitrine).
- "Desafiante (2º-5º local)": não é a líder, mas está entre as 5 primeiras
  do seu município — tese de Gui: essa escola tem motivo comercial pra
  buscar uma "arma" pra alcançar a líder. Foco primário sugerido ao time
  comercial.
- "Outras posições": 6º lugar local em diante — ainda passa no corte
  nacional de qualidade (score>=0.70), mas não está entre as primeiras da
  própria cidade.
- "Sem comparação local": município com menos de 3 escolas confiáveis — a
  posição de rank não é estatisticamente significativa nesse caso.

Limitação que continua não resolvida com dado público: não sabemos qual
sistema de ensino (Poliedro, SAS, Arco, Bernoulli, material próprio, etc.)
cada escola já usa hoje. "Desafiante" é uma tese comercial de Gui, plausível,
mas não confirmada pelos dados — precisa de pesquisa individual (ver
próximo passo de pesquisa manual de sistema de ensino) antes de virar lista
de prospecção real.

Correção de auditoria (22/07): lia funil_escolas_pontuadas.csv de um path
relativo "solto" (bare CWD) em vez de data/outputs/ — corrigido. Também
passou a incluir codigo_escola (CO_ENTIDADE) na saída, pra eliminar o merge
frágil por nome+município que o poliedro_11 fazia antes.

Gera: data/outputs/04_golden_leads_segmentadas.csv
"""

from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")

SCORE_MINIMO_GOLDEN_LEADS = 0.70
MIN_ESCOLAS_CONFIAVEIS_PARA_RANK = 3


def carregar_escolas_confiaveis() -> pd.DataFrame:
    """Escolas nacionais com score_destaque calculado e ENEM confiável (>=10 participantes vinculados)."""
    df = pd.read_csv(OUT_DIR / "funil_escolas_pontuadas.csv", dtype={"codigo_municipio": str})
    return df[df["confiavel_enem"] == True].copy()


def calcular_rank_municipal(df: pd.DataFrame) -> pd.DataFrame:
    """Posição de cada escola dentro do próprio município, por score_destaque (1 = líder local)."""
    df = df.copy()
    df["rank_municipio"] = df.groupby("codigo_municipio")["score_destaque"].rank(
        method="first", ascending=False
    ).astype(int)
    df["n_escolas_confiaveis_municipio"] = df.groupby("codigo_municipio")["codigo_municipio"].transform("count")
    return df


def taggear_segmento_comercial(row) -> str:
    """Não é filtro — toda escola do universo Golden Leads (score>=0.70) recebe uma tag."""
    if row["n_escolas_confiaveis_municipio"] < MIN_ESCOLAS_CONFIAVEIS_PARA_RANK:
        return "Sem comparação local (poucas escolas na cidade)"
    if row["rank_municipio"] == 1:
        return "Líder local"
    if 2 <= row["rank_municipio"] <= 5:
        return "Desafiante (2º-5º local)"
    return "Outras posições"


def main():
    escolas = carregar_escolas_confiaveis()
    escolas = calcular_rank_municipal(escolas)

    golden_leads = escolas[escolas["score_destaque"] >= SCORE_MINIMO_GOLDEN_LEADS].copy()
    golden_leads["segmento_comercial"] = golden_leads.apply(taggear_segmento_comercial, axis=1)

    print(f"[Golden Leads] Universo total (score_destaque >= {SCORE_MINIMO_GOLDEN_LEADS}): {len(golden_leads):,}")
    print("\n[Sanity check] Distribuição por segmento comercial:")
    print(golden_leads["segmento_comercial"].value_counts())

    cols = ["codigo_escola", "NO_ENTIDADE", "codigo_municipio", "rank_municipio", "n_escolas_confiaveis_municipio",
            "segmento_comercial", "enem_media_geral", "qtd_participantes_enem", "indice_infra",
            "QT_MAT_MED", "score_destaque"]
    saida = golden_leads.sort_values(["segmento_comercial", "score_destaque"], ascending=[True, False])[cols]
    saida.to_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", index=False)
    print(f"\n[✓] Salvo em {OUT_DIR / '04_golden_leads_segmentadas.csv'}")


if __name__ == "__main__":
    main()
