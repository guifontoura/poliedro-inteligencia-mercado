"""
Case Poliedro — Passo 27 (roadmap 3.0, pedido do Gui em 28/07): EXTRAÇÃO das
médias ENEM 2024 por escola, pra permitir o teste de ESTABILIDADE TEMPORAL
do `score_destaque`.

Por que este passo existe: até aqui o score de cada escola vinha de uma
única edição do ENEM (2025). Sem um segundo ano, não há como saber se a
posição de uma escola no ranking é sinal (qualidade que persiste) ou ruído
(uma turma boa num ano só). Com 2024 em mãos dá pra medir isso — é a
validação mais forte possível sem dado de conversão comercial, já que o
projeto não tem histórico de vendas pra regredir contra.

Estrutura do arquivo 2024 (inspecionada antes de escrever a lógica, não
assumida): `RESULTADOS_2024.csv` já traz CO_ESCOLA direto, igual 2025 — não
precisa cruzar com PARTICIPANTES_2024.csv (que é o cadastro socioeconômico,
sem nota e sem escola). Separador `;`, encoding latin-1, decimal `.` (a
edição 2024 usa ponto, diferente do que a leitura ingênua sugeriria — testado
com nrows=20 antes de rodar o arquivo inteiro de 1,7 GB).

Mesma limitação já documentada no passo 2 e que vale igual aqui: só cerca de
36% das linhas têm CO_ESCOLA preenchido, porque o ENEM só vincula escola
quando o participante estava matriculado nela na inscrição. A média por
escola reflete os alunos vinculados naquele ano, não todos os egressos.

Aceita o microdado tanto DESCOMPACTADO (pasta `microdados_enem_2024/`)
quanto em ZIP (`microdados_enem_2024.zip`) — procura os dois, nessa ordem.

Gera: data/raw/enem_2024_medias_por_escola.csv
"""

import sys
import zipfile
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
PASTA_DESCOMPACTADA = RAW_DIR / "microdados_enem_2024" / "DADOS" / "RESULTADOS_2024.csv"
CAMINHO_ZIP = RAW_DIR / "microdados_enem_2024.zip"
CAMINHO_NO_ZIP = "DADOS/RESULTADOS_2024.csv"
CAMINHO_SAIDA = RAW_DIR / "enem_2024_medias_por_escola.csv"

COLUNAS_NECESSARIAS = [
    "CO_ESCOLA", "CO_MUNICIPIO_ESC", "TP_DEPENDENCIA_ADM_ESC", "TP_SIT_FUNC_ESC",
    "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO",
]
COLUNAS_NOTAS = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]

TP_DEPENDENCIA_PRIVADA = 4
TP_SIT_FUNC_ATIVA = 1
TAMANHO_CHUNK = 1_000_000


def abrir_resultados_2024():
    """Devolve um handle de leitura do RESULTADOS_2024.csv, venha ele solto ou em zip."""
    if PASTA_DESCOMPACTADA.exists():
        print(f"Lendo microdado descompactado: {PASTA_DESCOMPACTADA}")
        return open(PASTA_DESCOMPACTADA, "rb"), None
    if CAMINHO_ZIP.exists():
        print(f"Lendo microdado compactado: {CAMINHO_ZIP}")
        arquivo_zip = zipfile.ZipFile(CAMINHO_ZIP)
        nomes = [n for n in arquivo_zip.namelist() if n.endswith("RESULTADOS_2024.csv")]
        if not nomes:
            print(
                f"ERRO: '{CAMINHO_ZIP}' não contém RESULTADOS_2024.csv. "
                f"Conteúdo: {arquivo_zip.namelist()[:10]}",
                file=sys.stderr,
            )
            sys.exit(1)
        return arquivo_zip.open(nomes[0]), arquivo_zip
    print(
        "ERRO: não achei o microdado do ENEM 2024. Coloque em "
        f"'{PASTA_DESCOMPACTADA}' (descompactado) ou '{CAMINHO_ZIP}' (zip). "
        "Download: https://download.inep.gov.br/microdados/microdados_enem_2024.zip",
        file=sys.stderr,
    )
    sys.exit(1)


def somar_notas_por_escola():
    """Percorre o microdado em chunks e acumula soma e contagem de notas por escola privada ativa."""
    handle, arquivo_zip = abrir_resultados_2024()
    acumulado = {}
    linhas_lidas = 0
    try:
        leitor = pd.read_csv(
            handle,
            sep=";",
            encoding="latin-1",
            usecols=COLUNAS_NECESSARIAS,
            chunksize=TAMANHO_CHUNK,
            low_memory=False,
        )
        for chunk in leitor:
            linhas_lidas += len(chunk)
            privadas = chunk[
                (chunk["TP_DEPENDENCIA_ADM_ESC"] == TP_DEPENDENCIA_PRIVADA)
                & (chunk["TP_SIT_FUNC_ESC"] == TP_SIT_FUNC_ATIVA)
                & (chunk["CO_ESCOLA"].notna())
            ].copy()
            if privadas.empty:
                continue
            for coluna in COLUNAS_NOTAS:
                privadas[coluna] = pd.to_numeric(privadas[coluna], errors="coerce")
            privadas["media_participante"] = privadas[COLUNAS_NOTAS].mean(axis=1)
            validos = privadas[privadas["media_participante"].notna()]
            agrupado = validos.groupby("CO_ESCOLA")["media_participante"].agg(["sum", "count"])
            for codigo_escola, linha in agrupado.iterrows():
                soma_atual, contagem_atual = acumulado.get(codigo_escola, (0.0, 0))
                acumulado[codigo_escola] = (
                    soma_atual + linha["sum"],
                    contagem_atual + int(linha["count"]),
                )
            print(f"  ... {linhas_lidas:,} linhas lidas | {len(acumulado):,} escolas acumuladas")
    finally:
        handle.close()
        if arquivo_zip is not None:
            arquivo_zip.close()
    return acumulado, linhas_lidas


def main():
    acumulado, linhas_lidas = somar_notas_por_escola()
    if not acumulado:
        print("ERRO: nenhuma escola privada ativa encontrada — verifique o arquivo.", file=sys.stderr)
        sys.exit(1)

    resultado = pd.DataFrame(
        [
            {
                "codigo_escola": int(codigo),
                "enem_media_geral_2024": soma / contagem,
                "qtd_participantes_enem_2024": contagem,
            }
            for codigo, (soma, contagem) in acumulado.items()
        ]
    ).sort_values("enem_media_geral_2024", ascending=False)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(CAMINHO_SAIDA, index=False)

    # --- resumo de sanidade ---
    print(f"\nGerado: {CAMINHO_SAIDA}")
    print(f"Linhas lidas no microdado: {linhas_lidas:,}")
    print(f"Escolas privadas ativas com nota: {len(resultado):,}")
    print(
        f"enem_media_geral_2024 — min {resultado['enem_media_geral_2024'].min():.1f} | "
        f"mediana {resultado['enem_media_geral_2024'].median():.1f} | "
        f"média {resultado['enem_media_geral_2024'].mean():.1f} | "
        f"máx {resultado['enem_media_geral_2024'].max():.1f}"
    )
    confiaveis = resultado[resultado["qtd_participantes_enem_2024"] >= 10]
    print(f"Escolas com >=10 participantes (recorte 'confiável'): {len(confiaveis):,}")


if __name__ == "__main__":
    main()
