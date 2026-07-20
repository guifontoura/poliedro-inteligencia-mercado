"""
Case Poliedro — Passo 2: EXTRAÇÃO de médias ENEM 2025 por escola.

Fonte: data/raw/microdados_enem_2025.zip -> DADOS/RESULTADOS_2025.csv
(estrutura 2025: arquivo já vem com CO_ESCOLA direto, diferente de edições
antigas que exigiam cruzar com PARTICIPANTES. Confirmado inspecionando o
zip antes de escrever esta lógica.)

Limitação conhecida (documentar na entrega): só ~36% das linhas de
RESULTADOS_2025.csv têm CO_ESCOLA preenchido — é o próprio ENEM que só
vincula a escola quando o participante estava matriculado nela no ato da
inscrição (concluintes de anos anteriores não têm esse vínculo). A média
por escola, portanto, reflete o desempenho dos alunos vinculados à escola
naquele ano, não de todos os egressos.

Processa em chunks (arquivo tem ~2GB descomprimido, ~4.8M participantes).
Gera: data/raw/enem_2025_medias_por_escola.csv
"""

import zipfile
import time
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
CAMINHO_ZIP_ENEM = RAW_DIR / "microdados_enem_2025.zip"
CAMINHO_SAIDA = RAW_DIR / "enem_2025_medias_por_escola.csv"

CAMINHO_CSV_NO_ZIP = "microdados_enem_2025/DADOS/RESULTADOS_2025.csv"
COLUNAS_NECESSARIAS = [
    "CO_ESCOLA", "CO_MUNICIPIO_ESC", "TP_DEPENDENCIA_ADM_ESC", "TP_SIT_FUNC_ESC",
    "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO",
]
COLUNAS_NOTAS = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]

TP_DEPENDENCIA_PRIVADA_ENEM = 4  # mesma codificação do Censo Escolar (1=federal,2=estadual,3=municipal,4=privada)
TP_SIT_FUNC_ATIVA = 1
TAMANHO_CHUNK = 1_000_000


def extrair_medias_enem_por_escola() -> pd.DataFrame:
    """Lê RESULTADOS_2025.csv em chunks e calcula média de notas por escola privada em atividade."""
    if not CAMINHO_ZIP_ENEM.exists():
        raise FileNotFoundError(
            f"[ENEM] Arquivo não encontrado: {CAMINHO_ZIP_ENEM}. "
            f"Baixe em https://download.inep.gov.br/microdados/microdados_enem_2025.zip "
            f"e salve nesse caminho."
        )

    print("[ENEM] Lendo RESULTADOS_2025.csv em chunks...")
    t0 = time.time()
    chunks_filtrados = []
    total_linhas = 0

    with zipfile.ZipFile(CAMINHO_ZIP_ENEM) as z:
        with z.open(CAMINHO_CSV_NO_ZIP) as f:
            leitor = pd.read_csv(
                f, sep=";", encoding="latin-1", usecols=COLUNAS_NECESSARIAS, chunksize=TAMANHO_CHUNK
            )
            for i, chunk in enumerate(leitor):
                total_linhas += len(chunk)
                filtrado = chunk[
                    (chunk["CO_ESCOLA"].notna())
                    & (chunk["TP_DEPENDENCIA_ADM_ESC"] == TP_DEPENDENCIA_PRIVADA_ENEM)
                    & (chunk["TP_SIT_FUNC_ESC"] == TP_SIT_FUNC_ATIVA)
                ].copy()
                chunks_filtrados.append(filtrado)
                print(f"  chunk {i + 1}: {len(chunk):,} lidas | {len(filtrado):,} elegíveis | {time.time() - t0:.1f}s")

    df_priv = pd.concat(chunks_filtrados, ignore_index=True)
    print(f"[ENEM] Total geral no arquivo: {total_linhas:,} | Elegíveis (privada+ativa+com escola): {len(df_priv):,}")

    df_priv["media_geral"] = df_priv[COLUNAS_NOTAS].mean(axis=1, skipna=True)

    agg = (
        df_priv.groupby("CO_ESCOLA")
        .agg(
            codigo_municipio_enem=("CO_MUNICIPIO_ESC", "first"),
            qtd_participantes_enem=("media_geral", "count"),
            enem_media_cn=("NU_NOTA_CN", "mean"),
            enem_media_ch=("NU_NOTA_CH", "mean"),
            enem_media_lc=("NU_NOTA_LC", "mean"),
            enem_media_mt=("NU_NOTA_MT", "mean"),
            enem_media_redacao=("NU_NOTA_REDACAO", "mean"),
            enem_media_geral=("media_geral", "mean"),
        )
        .reset_index()
        .rename(columns={"CO_ESCOLA": "codigo_escola"})
    )
    agg["codigo_escola"] = agg["codigo_escola"].astype("int64")
    agg["codigo_municipio_enem"] = agg["codigo_municipio_enem"].astype("int64").astype(str)

    return agg


def exibir_resumo(agg: pd.DataFrame) -> None:
    """Sanity check antes de confiar no resultado."""
    print(f"\n[ENEM] Escolas privadas distintas com participante vinculado: {len(agg):,}")
    print(f"[ENEM] Participantes por escola — min: {agg['qtd_participantes_enem'].min()} | "
          f"mediana: {agg['qtd_participantes_enem'].median():.0f} | max: {agg['qtd_participantes_enem'].max()}")
    print(f"[ENEM] Escolas com >=10 participantes vinculados: "
          f"{(agg['qtd_participantes_enem'] >= 10).sum():,} "
          f"({(agg['qtd_participantes_enem'] >= 10).mean() * 100:.1f}%)")
    print(f"[ENEM] Média geral — min: {agg['enem_media_geral'].min():.1f} | "
          f"média: {agg['enem_media_geral'].mean():.1f} | max: {agg['enem_media_geral'].max():.1f}")


def main():
    agg = extrair_medias_enem_por_escola()
    exibir_resumo(agg)
    agg.to_csv(CAMINHO_SAIDA, index=False)
    print(f"\n[✓] Salvo em {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
