"""
Case Poliedro — Passo 3b: ENDEREÇO E CEP DAS ESCOLAS ELEGÍVEIS.

Correção de falha de reprodutibilidade (21/07): este arquivo já existia como
`data/raw/escolas_com_endereco.csv`, usado na investigação de "sala vitrine"
(cruzamento CO_CEP/NU_CNPJ_MANTENEDORA) e depois reaproveitado pelo
`poliedro_11_geocodificar_ceps.py` — mas nunca teve um script gerador
versionado, só existia como artefato solto. Reconstruído aqui a partir da
mesma fonte primária (Tabela_Escola_2025.csv), para que o pipeline rode do
zero sem depender de um CSV "que apareceu do nada".

Extrai DS_ENDERECO, NU_ENDERECO, CO_CEP e NU_CNPJ_MANTENEDORA (Censo Escolar
2025) só para as escolas já elegíveis (poliedro_03_extrair_censo.py) — não
processa as 8.095 * todas as colunas de novo, só o necessário.

Gera: data/raw/escolas_com_endereco.csv
"""

import zipfile
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
CAMINHO_ZIP = RAW_DIR / "microdados_censo_escolar_2025.zip"
CAMINHO_CSV_NO_ZIP = "microdados_censo_escolar_2025/dados/Tabela_Escola_2025.csv"

COLS_ENDERECO = ["CO_ENTIDADE", "DS_ENDERECO", "NU_ENDERECO", "CO_CEP", "NU_CNPJ_MANTENEDORA"]


def extrair_enderecos() -> pd.DataFrame:
    """Lê só as colunas de endereço/CEP do Censo 2025, para as escolas já elegíveis."""
    elegiveis = pd.read_csv(RAW_DIR / "escolas_privadas_elegiveis_2025.csv", dtype={"codigo_municipio": str})
    codigos_elegiveis = set(elegiveis["CO_ENTIDADE"].astype("int64"))

    with zipfile.ZipFile(CAMINHO_ZIP) as z:
        with z.open(CAMINHO_CSV_NO_ZIP) as f:
            enderecos = pd.read_csv(f, sep=";", encoding="latin-1", usecols=COLS_ENDERECO, low_memory=False)

    enderecos = enderecos[enderecos["CO_ENTIDADE"].isin(codigos_elegiveis)].copy()

    resultado = elegiveis.merge(enderecos, on="CO_ENTIDADE", how="left")
    return resultado


def exibir_resumo(df: pd.DataFrame) -> None:
    com_cep = df["CO_CEP"].notna().sum()
    print(f"[Sanity check] Escolas elegíveis com CEP: {com_cep:,} de {len(df):,} ({com_cep / len(df) * 100:.1f}%)")


def main():
    df = extrair_enderecos()
    exibir_resumo(df)
    df.to_csv(RAW_DIR / "escolas_com_endereco.csv", index=False)
    print(f"[✓] Salvo em {RAW_DIR / 'escolas_com_endereco.csv'}")


if __name__ == "__main__":
    main()
