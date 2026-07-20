"""
Case Poliedro — Passo 3: EXTRAÇÃO de escolas privadas elegíveis (Censo Escolar 2025).

O Censo 2025 mudou de estrutura (6 tabelas separadas, não mais um CSV único —
mesma lição de sempre: nunca hardcodar esquema sem checar). Este script cruza:
- Tabela_Escola_2025.csv    -> dependência, categoria, situação, infraestrutura
- Tabela_Turma_2025.csv     -> QT_TUR_MED (nº de turmas de Ensino Médio, já
                                 agregado por escola — usado para o filtro
                                 "oferece ao menos Ensino Médio")
- Tabela_Matricula_2025.csv -> QT_MAT_MED (matrículas em Ensino Médio por escola)

Filtros de elegibilidade da ESCOLA (não confundir com filtro de ESCOPO do
município, que é população > 100k e entra depois, no passo de scoring):
- TP_DEPENDENCIA == 4 (privada)
- TP_CATEGORIA_ESCOLA_PRIVADA em [1,2,3] (exclui 4 = Filantrópica, ex: APAE)
- TP_SITUACAO_FUNCIONAMENTO == 1 (em atividade)
- QT_TUR_MED > 0 (oferece ao menos Ensino Médio)

Limitações de qualidade de dado encontradas e tratadas (documentar na entrega):
- QT_SALAS_UTILIZADAS está top-codado em 202 nesta edição (12 escolas
  diferentes, em estados diferentes, todas com exatamente 202 salas — não é
  coincidência real, é truncamento no dado de origem). Por isso QT_MAT_MED é
  usado como métrica primária de porte, e QT_SALAS_UTILIZADAS só como contexto.
- Uma escola (CENTRO EDUCACIONAL APRENDIZ, CO_ENTIDADE 31305120) reporta 4.444
  matrículas de Ensino Médio em 10 salas (444 alunos/sala) — claramente erro de
  preenchimento, muito acima de qualquer outro caso do dataset. Removida.
- Escolas "Família Agrícola" / regime de alternância aparecem com razão
  matrícula/sala naturalmente alta (60-85) por causa do modelo de internato
  rotativo — não é erro de dado, mas também não é o perfil de escola que
  interessa para este case (não são polos de prestígio urbano). A maioria já
  deve cair fora no filtro de município >100k habitantes; revisitar após esse
  filtro caso alguma sobreviva.

Gera: data/raw/escolas_privadas_elegiveis_2025.csv
"""

import zipfile
import time
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
CAMINHO_ZIP_CENSO = RAW_DIR / "microdados_censo_escolar_2025.zip"
CAMINHO_SAIDA = RAW_DIR / "escolas_privadas_elegiveis_2025.csv"

CAMINHO_TABELA_ESCOLA = "microdados_censo_escolar_2025/dados/Tabela_Escola_2025.csv"
CAMINHO_TABELA_TURMA = "microdados_censo_escolar_2025/dados/Tabela_Turma_2025.csv"
CAMINHO_TABELA_MATRICULA = "microdados_censo_escolar_2025/dados/Tabela_Matricula_2025.csv"

COLS_ESCOLA = [
    "CO_ENTIDADE", "NO_ENTIDADE", "CO_MUNICIPIO", "TP_DEPENDENCIA", "TP_CATEGORIA_ESCOLA_PRIVADA",
    "TP_SITUACAO_FUNCIONAMENTO", "QT_SALAS_UTILIZADAS",
    "IN_LABORATORIO_CIENCIAS", "IN_LABORATORIO_INFORMATICA", "IN_BIBLIOTECA", "IN_BIBLIOTECA_SALA_LEITURA",
    "IN_QUADRA_ESPORTES", "IN_QUADRA_ESPORTES_COBERTA", "IN_AUDITORIO", "IN_INTERNET",
]
COLS_TURMA = ["CO_ENTIDADE", "QT_TUR_MED", "QT_TUR_INF", "QT_TUR_FUND_AI", "QT_TUR_FUND_AF", "QT_TUR_PROF", "QT_TUR_EJA"]
COLS_MATRICULA = ["CO_ENTIDADE", "QT_MAT_MED", "QT_MAT_BAS"]

TP_DEPENDENCIA_PRIVADA = 4
CATEGORIAS_PRIVADAS_VALIDAS = [1, 2, 3]  # exclui 4 = Filantrópica
TP_SITUACAO_EM_ATIVIDADE = 1
LIMITE_MAT_POR_SALA = 150  # acima disso é erro de preenchimento, não escola grande de verdade
CO_ENTIDADE_ERRO_CONHECIDO = 31305120  # 4.444 matrículas em 10 salas — documentado acima


def extrair_escolas_privadas_elegiveis() -> pd.DataFrame:
    """Lê as 3 tabelas do Censo 2025, cruza por CO_ENTIDADE e aplica os filtros de elegibilidade."""
    if not CAMINHO_ZIP_CENSO.exists():
        raise FileNotFoundError(f"[Censo] Arquivo não encontrado: {CAMINHO_ZIP_CENSO}")

    t0 = time.time()
    with zipfile.ZipFile(CAMINHO_ZIP_CENSO) as z:
        with z.open(CAMINHO_TABELA_ESCOLA) as f:
            df_escola = pd.read_csv(f, sep=";", encoding="latin-1", usecols=COLS_ESCOLA, low_memory=False)
        print(f"[Censo] Tabela_Escola: {len(df_escola):,} linhas | {time.time() - t0:.1f}s")

        with z.open(CAMINHO_TABELA_TURMA) as f:
            df_turma = pd.read_csv(f, sep=";", encoding="latin-1", usecols=COLS_TURMA, low_memory=False)
        print(f"[Censo] Tabela_Turma: {len(df_turma):,} linhas | {time.time() - t0:.1f}s")

        with z.open(CAMINHO_TABELA_MATRICULA) as f:
            df_mat = pd.read_csv(f, sep=";", encoding="latin-1", usecols=COLS_MATRICULA, low_memory=False)
        print(f"[Censo] Tabela_Matricula: {len(df_mat):,} linhas | {time.time() - t0:.1f}s")

    df_priv = df_escola[
        (df_escola["TP_DEPENDENCIA"] == TP_DEPENDENCIA_PRIVADA)
        & (df_escola["TP_CATEGORIA_ESCOLA_PRIVADA"].isin(CATEGORIAS_PRIVADAS_VALIDAS))
        & (df_escola["TP_SITUACAO_FUNCIONAMENTO"] == TP_SITUACAO_EM_ATIVIDADE)
    ].copy()
    print(f"[Censo] Privadas não-filantrópicas em atividade: {len(df_priv):,}")

    df_priv = df_priv.merge(df_turma, on="CO_ENTIDADE", how="left")
    df_priv = df_priv.merge(df_mat, on="CO_ENTIDADE", how="left")

    antes = len(df_priv)
    df_priv = df_priv[df_priv["QT_TUR_MED"] > 0].copy()
    print(f"[Censo] Oferecem Ensino Médio (QT_TUR_MED>0): {len(df_priv):,} (removidas {antes - len(df_priv):,})")

    antes = len(df_priv)
    df_priv = df_priv[df_priv["CO_ENTIDADE"] != CO_ENTIDADE_ERRO_CONHECIDO].copy()
    df_priv["mat_por_sala"] = df_priv["QT_MAT_MED"] / df_priv["QT_SALAS_UTILIZADAS"]
    df_priv = df_priv[(df_priv["mat_por_sala"].isna()) | (df_priv["mat_por_sala"] <= LIMITE_MAT_POR_SALA)].copy()
    print(f"[Censo] Após remover outliers de porte (erro de preenchimento): {len(df_priv):,} (removidas {antes - len(df_priv):,})")

    df_priv["codigo_municipio"] = df_priv["CO_MUNICIPIO"].astype(str)
    return df_priv


def exibir_resumo(df: pd.DataFrame) -> None:
    """Sanity check antes de confiar no resultado."""
    print(f"\n[Censo] Total de escolas elegíveis: {len(df):,}")
    print(f"[Censo] Municípios distintos representados: {df['codigo_municipio'].nunique():,}")
    print(f"[Censo] QT_SALAS_UTILIZADAS — min: {df['QT_SALAS_UTILIZADAS'].min()} | "
          f"mediana: {df['QT_SALAS_UTILIZADAS'].median():.0f} | max: {df['QT_SALAS_UTILIZADAS'].max()} "
          f"(⚠ top-codado em 202, usar como contexto, não como métrica principal)")
    print(f"[Censo] QT_MAT_MED — min: {df['QT_MAT_MED'].min():.0f} | "
          f"mediana: {df['QT_MAT_MED'].median():.0f} | max: {df['QT_MAT_MED'].max():.0f}")


def main():
    df = extrair_escolas_privadas_elegiveis()
    exibir_resumo(df)
    df.to_csv(CAMINHO_SAIDA, index=False)
    print(f"\n[✓] Salvo em {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
