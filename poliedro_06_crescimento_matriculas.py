"""
Case Poliedro — Passo 6 (bônus, aprovado por Gui em 20/07): CRESCIMENTO DE MATRÍCULAS
de Ensino Médio 2023 -> 2025, por escola elegível.

Não altera os scores já fechados das Partes 1 e 2 — entra como coluna/insight de
CONTEXTO ("a escola/cidade está crescendo ou estagnada"), mesmo tratamento dado
a QT_MAT_MED e PIB per capita neste projeto: informa a leitura, não pontua.

Fonte adicional: data/raw/microdados_censo_escolar_2023.zip (já estava na pasta
de um exercício anterior — reaproveitado aqui porque QT_MAT_MED já existia
nesse schema, sem custo de novo download).

Limitação: CO_ENTIDADE é o identificador nacional de escola do INEP e é estável
entre edições — mas escolas abertas depois de 2023 não têm base de comparação
(aparecem como "sem dado 2023", não como crescimento 0 ou negativo).

Gera: data/outputs/03_crescimento_matriculas_2023_2025.csv
"""

import zipfile
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

CAMINHO_ZIP_2023 = RAW_DIR / "microdados_censo_escolar_2023.zip"
CAMINHO_CSV_2023 = "microdados_censo_escolar_2023/dados/microdados_ed_basica_2023.csv"

TP_DEPENDENCIA_PRIVADA = 4
CATEGORIAS_PRIVADAS_VALIDAS = [1, 2, 3]
TP_SITUACAO_EM_ATIVIDADE = 1


def extrair_matriculas_medio_2023() -> pd.DataFrame:
    """Extrai QT_MAT_MED de 2023 para escolas privadas elegíveis (mesmos filtros de categoria/situação)."""
    with zipfile.ZipFile(CAMINHO_ZIP_2023) as z:
        with z.open(CAMINHO_CSV_2023) as f:
            df = pd.read_csv(
                f, sep=";", encoding="latin-1", low_memory=False,
                usecols=["CO_ENTIDADE", "TP_DEPENDENCIA", "TP_CATEGORIA_ESCOLA_PRIVADA",
                         "TP_SITUACAO_FUNCIONAMENTO", "QT_MAT_MED"],
            )

    df_priv = df[
        (df["TP_DEPENDENCIA"] == TP_DEPENDENCIA_PRIVADA)
        & (df["TP_CATEGORIA_ESCOLA_PRIVADA"].isin(CATEGORIAS_PRIVADAS_VALIDAS))
        & (df["TP_SITUACAO_FUNCIONAMENTO"] == TP_SITUACAO_EM_ATIVIDADE)
    ].copy()

    return df_priv[["CO_ENTIDADE", "QT_MAT_MED"]].rename(columns={"QT_MAT_MED": "qt_mat_med_2023"})


def calcular_crescimento() -> pd.DataFrame:
    """Cruza matrículas 2023 x 2025 para as escolas elegíveis do recorte atual (>100k hab.)."""
    escolas_2025 = pd.read_csv(RAW_DIR / "escolas_privadas_elegiveis_2025.csv", dtype={"codigo_municipio": str})
    pop_total = pd.read_csv(RAW_DIR / "populacao_total_por_municipio.csv", dtype={"codigo_municipio": str})
    municipios_100k = set(pop_total[pop_total["populacao_total"] > 100_000]["codigo_municipio"])
    escolas_2025 = escolas_2025[escolas_2025["codigo_municipio"].isin(municipios_100k)].copy()

    mat_2023 = extrair_matriculas_medio_2023()

    df = escolas_2025.merge(mat_2023, on="CO_ENTIDADE", how="left")
    df = df.rename(columns={"QT_MAT_MED": "qt_mat_med_2025"})

    com_2023 = df["qt_mat_med_2023"].notna() & (df["qt_mat_med_2023"] > 0)
    print(f"[Crescimento] Escolas do recorte com dado 2023 disponível: {com_2023.sum():,} de {len(df):,} "
          f"({com_2023.mean() * 100:.1f}%) — o restante são escolas novas ou sem correspondência de código.")

    df["crescimento_pct"] = pd.NA
    df.loc[com_2023, "crescimento_pct"] = (
        (df.loc[com_2023, "qt_mat_med_2025"] - df.loc[com_2023, "qt_mat_med_2023"])
        / df.loc[com_2023, "qt_mat_med_2023"] * 100
    ).round(1)

    return df


def exibir_resumo(df: pd.DataFrame) -> None:
    valido = df["crescimento_pct"].notna()
    print(f"\n[Sanity check] crescimento_pct — min: {df.loc[valido,'crescimento_pct'].min():.1f}% | "
          f"mediana: {df.loc[valido,'crescimento_pct'].median():.1f}% | "
          f"max: {df.loc[valido,'crescimento_pct'].max():.1f}%")

    agg_cidade = (
        df[valido].groupby("codigo_municipio")["crescimento_pct"].median().reset_index()
        .rename(columns={"crescimento_pct": "crescimento_mediano_cidade_pct"})
    )
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})
    top10 = cidades.head(10).merge(agg_cidade, on="codigo_municipio", how="left")
    print("\nCrescimento mediano de matrículas EM (2023->2025) nas 10 cidades prioritárias:")
    print(top10[["nome_municipio_ibge", "uf", "crescimento_mediano_cidade_pct"]].to_string(index=False))


def main():
    df = calcular_crescimento()
    exibir_resumo(df)
    df.to_csv(OUT_DIR / "03_crescimento_matriculas_2023_2025.csv", index=False)
    print(f"\n[✓] Salvo em {OUT_DIR / '03_crescimento_matriculas_2023_2025.csv'}")


if __name__ == "__main__":
    main()
