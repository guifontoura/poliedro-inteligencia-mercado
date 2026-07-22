"""
Case Poliedro — Passo 5: SCORE DE DESTAQUE DE ESCOLAS (Parte 2 do case).

Aplicado às 4 cidades de maior score_priorizacao (Parte 1, versão com média
ENEM ponderada por participante — revisão de 21/07): Belo Horizonte, Niterói,
Goiânia e Vitória. Critério de escolha: simplesmente o topo do ranking da
Parte 1 — evita qualquer viés de escolha arbitrária. O case pede "pelo menos
3 cidades"; usamos 4 para não descartar Vitória (topo da versão anterior,
não-ponderada) nem Goiânia (topo da versão corrigida) — mantém as duas
análises já validadas e evita decidir arbitrariamente entre elas.

Metodologia (2 critérios, um de cada base exigida pelo case):

1. QUALIDADE ACADÊMICA — ENEM 2025 (peso 0.60)
   Média geral (5 áreas) dos participantes vinculados à escola. Por quê: é o
   proxy mais direto e externo de resultado educacional — não depende de
   autodeclaração da escola (diferente dos indicadores de infraestrutura, que
   são preenchidos pela própria gestão escolar no Censo).
   Peso maior que infraestrutura porque, para o objetivo de "share de
   prestígio", resultado acadêmico é o que constrói reputação publicamente
   visível (rankings de vestibular, etc.) — infraestrutura é insumo, não é
   o resultado em si.

2. INFRAESTRUTURA DE PRESTÍGIO — Censo Escolar 2025 (peso 0.40)
   Índice 0-5 somando: laboratório de ciências, laboratório de informática,
   biblioteca, quadra de esportes coberta, auditório. Por quê: são os
   equipamentos que sinalizam investimento em experiência educacional
   ampliada (não é só "ter aula") — categoria historicamente associada a
   escolas de ticket mais alto.

Critério de confiabilidade: escolas com menos de 10 participantes do ENEM
vinculados (amostra pequena, média pode ser ruído estatístico) recebem uma
sinalização e não competem pelo Top 5 de cada cidade — aparecem separadas.
Volume de matrículas (QT_MAT_MED) é reportado como contexto, não entra no
score (mesmo tratamento que PIB per capita nas versões anteriores deste
projeto: dado relevante para leitura, não para ranquear).

Reprodutibilidade: os percentis de ENEM e infraestrutura são calculados sobre
o universo nacional de 5.647 escolas elegíveis (Parte 1), não só dentro de
cada cidade — isso evita que uma cidade pequena (poucas escolas) tenha
percentis instáveis.

Gera: data/outputs/02_escolas_destaque_top3_cidades.csv
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

PESO_ENEM = 0.60
PESO_INFRA = 0.40
MIN_PARTICIPANTES_CONFIAVEL = 10
TOP_N_CIDADES = 4
TOP_N_ESCOLAS_POR_CIDADE = 5

COLS_INFRA = [
    "IN_LABORATORIO_CIENCIAS", "IN_LABORATORIO_INFORMATICA",
    "IN_BIBLIOTECA", "IN_QUADRA_ESPORTES_COBERTA", "IN_AUDITORIO",
]


def carregar_base_escolas_com_enem() -> pd.DataFrame:
    """Reconstrói a base de escolas elegíveis + ENEM (mesma lógica do passo 4)."""
    escolas = pd.read_csv(RAW_DIR / "escolas_privadas_elegiveis_2025.csv", dtype={"codigo_municipio": str})
    enem = pd.read_csv(RAW_DIR / "enem_2025_medias_por_escola.csv")
    escolas["codigo_escola"] = escolas["CO_ENTIDADE"].astype("int64")
    return escolas.merge(
        enem[["codigo_escola", "qtd_participantes_enem", "enem_media_geral"]],
        on="codigo_escola", how="left",
    )


def restringir_ao_escopo_100k(escolas: pd.DataFrame) -> pd.DataFrame:
    """Aplica o mesmo filtro de escopo (>100k habitantes) usado na Parte 1."""
    pop_total = pd.read_csv(RAW_DIR / "populacao_total_por_municipio.csv", dtype={"codigo_municipio": str})
    municipios_100k = set(pop_total[pop_total["populacao_total"] > 100_000]["codigo_municipio"])
    return escolas[escolas["codigo_municipio"].isin(municipios_100k)].copy()


def calcular_score_destaque(escolas: pd.DataFrame) -> pd.DataFrame:
    """Calcula o índice de infraestrutura e o score de destaque ponderado (percentil nacional)."""
    df = escolas.copy()
    for col in COLS_INFRA:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["indice_infra"] = df[COLS_INFRA].sum(axis=1)

    df["confiavel_enem"] = df["qtd_participantes_enem"].fillna(0) >= MIN_PARTICIPANTES_CONFIAVEL

    df["percentil_enem"] = df["enem_media_geral"].rank(pct=True)
    df["percentil_infra"] = df["indice_infra"].rank(pct=True)

    # Sem ENEM confiável -> não recebe percentil de ENEM (fica de fora do ranking principal)
    df.loc[~df["confiavel_enem"], "percentil_enem"] = pd.NA

    df["score_destaque"] = (
        df["percentil_enem"] * PESO_ENEM + df["percentil_infra"] * PESO_INFRA
    ).round(4)

    return df


def selecionar_top5_por_cidade(df: pd.DataFrame, cidades_prioritarias: pd.DataFrame) -> pd.DataFrame:
    """Seleciona as 3 cidades de maior score_priorizacao e o Top 5 de escolas em cada uma."""
    top3_cidades = cidades_prioritarias.head(TOP_N_CIDADES)
    print(f"[Parte 2] Cidades selecionadas (top {TOP_N_CIDADES} da Parte 1): "
          f"{', '.join(top3_cidades['nome_municipio_ibge'] + '/' + top3_cidades['uf'])}")

    df_cidades = df[df["codigo_municipio"].isin(top3_cidades["codigo_municipio"])].copy()
    df_cidades = df_cidades.merge(
        top3_cidades[["codigo_municipio", "nome_municipio_ibge", "uf"]], on="codigo_municipio", how="left"
    )

    df_rankeavel = df_cidades.dropna(subset=["score_destaque"]).copy()
    top5 = (
        df_rankeavel.sort_values(["codigo_municipio", "score_destaque"], ascending=[True, False])
        .groupby("codigo_municipio")
        .head(TOP_N_ESCOLAS_POR_CIDADE)
    )
    return top5.sort_values(["nome_municipio_ibge", "score_destaque"], ascending=[True, False])


def exibir_resumo(top5: pd.DataFrame, df_cidades_completo: pd.DataFrame) -> None:
    print("\n" + "=" * 110)
    print("TOP 5 ESCOLAS DE DESTAQUE POR CIDADE")
    print("=" * 110)
    cols = ["nome_municipio_ibge", "NO_ENTIDADE", "enem_media_geral", "qtd_participantes_enem",
            "indice_infra", "QT_MAT_MED", "score_destaque"]
    print(top5[cols].to_string(index=False))

    sem_enem_confiavel = (~df_cidades_completo["confiavel_enem"]).sum()
    print(f"\n[Sanity check] Escolas nas 3 cidades sem ENEM confiável (<{MIN_PARTICIPANTES_CONFIAVEL} participantes "
          f"ou sem dado): {sem_enem_confiavel} de {len(df_cidades_completo)}")
    print(f"[Sanity check] indice_infra — min: {df_cidades_completo['indice_infra'].min():.0f} | "
          f"média: {df_cidades_completo['indice_infra'].mean():.2f} | max: {df_cidades_completo['indice_infra'].max():.0f}")


def main():
    cidades_prioritarias = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})

    escolas = carregar_base_escolas_com_enem()
    escolas = restringir_ao_escopo_100k(escolas)
    escolas_com_score = calcular_score_destaque(escolas)

    top5 = selecionar_top5_por_cidade(escolas_com_score, cidades_prioritarias)
    df_cidades_completo = escolas_com_score[
        escolas_com_score["codigo_municipio"].isin(cidades_prioritarias.head(TOP_N_CIDADES)["codigo_municipio"])
    ]

    exibir_resumo(top5, df_cidades_completo)
    top5.to_csv(OUT_DIR / "02_escolas_destaque_top3_cidades.csv", index=False)
    print(f"\n[✓] Salvo em {OUT_DIR / '02_escolas_destaque_top3_cidades.csv'}")


if __name__ == "__main__":
    main()
