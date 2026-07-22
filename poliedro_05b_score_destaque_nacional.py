"""
Case Poliedro — Passo 5b: SCORE DE DESTAQUE, UNIVERSO NACIONAL (>100k hab.).

Correção de falha de reprodutibilidade (21/07): o funil de priorização
(poliedro_07), a segmentação comercial (poliedro_09) e a geocodificação
(poliedro_11) dependiam de um arquivo `funil_escolas_pontuadas.csv` que nunca
tinha um script gerador — foi calculado uma vez direto no ambiente do
assistente e nunca versionado. Este script existe pra fechar esse buraco.

É a MESMA fórmula do `poliedro_05_score_escolas.py` (score_destaque = 60%
percentil ENEM + 40% percentil infraestrutura), só que SEM restringir a
nenhuma cidade específica — enquanto o poliedro_05 recorta pra Top 4 cidades
(pra montar o Top 5 de escolas da Parte 2), este aqui mantém as 5.647
escolas do escopo >100k, usado pelas leituras de portfólio/cross-sell
(funil, segmentação comercial), não pela resposta formal ao case.

Nota sobre escopo do percentil (22/07): ao contrário do poliedro_05 (que
rankeia sobre as 5.647 elegíveis, pois lá o "confiável" é só uma flag
informativa e não afeta o Top 5 de cada cidade — o mesmo grupo de 5 escolas
sai na frente com qualquer um dos dois escopos), aqui os percentis são
calculados só entre as 4.121 escolas com ENEM confiável (>=10 participantes).
Por quê: aqui SIM a contagem final ("quantas Golden Leads existem") depende
do escopo, e deixar escolas de amostra pequena — cuja própria média não
confiamos o bastante pra ranqueá-las — ainda contribuir como "concorrência"
no percentil de quem é confiável seria inconsistente. Rankear só entre
confiáveis é a comparação mais "maçã com maçã". Resultado: 869 Golden Leads
(score >= 0,70) e 129 com score >= 0,90 — os mesmos números já usados no
deck e no METODOLOGIA.md.

Gera: data/outputs/funil_escolas_pontuadas.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

PESO_ENEM = 0.60
PESO_INFRA = 0.40
MIN_PARTICIPANTES_CONFIAVEL = 10

COLS_INFRA = [
    "IN_LABORATORIO_CIENCIAS", "IN_LABORATORIO_INFORMATICA",
    "IN_BIBLIOTECA", "IN_QUADRA_ESPORTES_COBERTA", "IN_AUDITORIO",
]


def carregar_base_escolas_com_enem() -> pd.DataFrame:
    """Mesma base do poliedro_05: escolas elegíveis + médias ENEM por escola."""
    escolas = pd.read_csv(RAW_DIR / "escolas_privadas_elegiveis_2025.csv", dtype={"codigo_municipio": str})
    enem = pd.read_csv(RAW_DIR / "enem_2025_medias_por_escola.csv")
    escolas["codigo_escola"] = escolas["CO_ENTIDADE"].astype("int64")
    return escolas.merge(
        enem[["codigo_escola", "qtd_participantes_enem", "enem_media_geral"]],
        on="codigo_escola", how="left",
    )


def restringir_ao_escopo_100k(escolas: pd.DataFrame) -> pd.DataFrame:
    """Aplica o filtro de escopo (>100k habitantes) — mesmo critério usado em toda Parte 1/2."""
    pop_total = pd.read_csv(RAW_DIR / "populacao_total_por_municipio.csv", dtype={"codigo_municipio": str})
    municipios_100k = set(pop_total[pop_total["populacao_total"] > 100_000]["codigo_municipio"])
    return escolas[escolas["codigo_municipio"].isin(municipios_100k)].copy()


def calcular_score_destaque(escolas: pd.DataFrame) -> pd.DataFrame:
    """Índice de infraestrutura + score de destaque, percentil só entre as escolas com ENEM confiável.

    Escopo do percentil (ver nota no docstring do módulo): calculado só entre
    as escolas com >= 10 participantes ENEM, não sobre as 5.647 elegíveis —
    pra não deixar escolas de amostra não-confiável influenciarem o percentil
    de quem é confiável. Reproduz os 869 Golden Leads / 129 com score>=0,90
    já publicados no deck.
    """
    df = escolas.copy()
    for col in COLS_INFRA:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["indice_infra"] = df[COLS_INFRA].sum(axis=1)

    df["confiavel_enem"] = df["qtd_participantes_enem"].fillna(0) >= MIN_PARTICIPANTES_CONFIAVEL

    df["percentil_enem"] = np.nan
    df.loc[df["confiavel_enem"], "percentil_enem"] = (
        df.loc[df["confiavel_enem"], "enem_media_geral"].rank(pct=True)
    )
    df["percentil_infra"] = np.nan
    df.loc[df["confiavel_enem"], "percentil_infra"] = (
        df.loc[df["confiavel_enem"], "indice_infra"].rank(pct=True)
    )

    df["score_destaque"] = (
        df["percentil_enem"] * PESO_ENEM + df["percentil_infra"] * PESO_INFRA
    ).round(4)

    return df


def exibir_resumo(df: pd.DataFrame) -> None:
    print(f"[Sanity check] Escolas no recorte >100k hab.: {len(df):,}")
    print(f"[Sanity check] Escolas com ENEM confiável (>= {MIN_PARTICIPANTES_CONFIAVEL} participantes): "
          f"{df['confiavel_enem'].sum():,}")
    conf = df[df["confiavel_enem"]]
    print(f"[Sanity check] Golden Leads (score_destaque >= 0.70) entre as confiáveis: "
          f"{(conf['score_destaque'] >= 0.70).sum():,}")
    print(f"[Sanity check] score_destaque (confiáveis) — min: {conf['score_destaque'].min():.3f} | "
          f"média: {conf['score_destaque'].mean():.3f} | max: {conf['score_destaque'].max():.3f}")


def main():
    escolas = carregar_base_escolas_com_enem()
    escolas = restringir_ao_escopo_100k(escolas)
    escolas_com_score = calcular_score_destaque(escolas)

    exibir_resumo(escolas_com_score)
    escolas_com_score.to_csv(OUT_DIR / "funil_escolas_pontuadas.csv", index=False)
    print(f"\n[✓] Salvo em {OUT_DIR / 'funil_escolas_pontuadas.csv'}")


if __name__ == "__main__":
    main()
