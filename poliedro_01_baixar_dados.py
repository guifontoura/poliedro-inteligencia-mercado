"""
Case Poliedro — Passo 1: DOWNLOAD (rodar localmente, precisa de internet).

Este script só baixa/cacheia dados brutos. Não faz nenhuma transformação.
Separado de propósito do pipeline.py antigo (que é de outro projeto/exercício).

Gera em data/raw/:
- microdados_censo_escolar_2025.zip   (INEP, edição mais recente confirmada em jul/2026)
- populacao_total_por_municipio.csv   (IBGE/SIDRA, Censo 2022 — usado no filtro >100k hab.)

Rode: python poliedro_01_baixar_dados.py
"""

import time
from pathlib import Path

import pandas as pd
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

CAMINHO_ZIP_CENSO_2025 = RAW_DIR / "microdados_censo_escolar_2025.zip"
CAMINHO_POPULACAO_TOTAL = RAW_DIR / "populacao_total_por_municipio.csv"

URL_CENSO_2025 = "https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2025.zip"

CODIGOS_UF = [
    "11", "12", "13", "14", "15", "16", "17", "21", "22", "23", "24", "25",
    "26", "27", "28", "29", "31", "32", "33", "35", "41", "42", "43", "50",
    "51", "52", "53",
]


def criar_sessao_com_retry() -> requests.Session:
    """Cria sessão HTTP com retry automático."""
    session = requests.Session()
    retry_strategy = Retry(total=5, backoff_factor=1, status_forcelist=(500, 502, 503, 504, 408, 429))
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.verify = False
    return session


def baixar_censo_escolar_2025() -> None:
    """Baixa o ZIP do Censo Escolar 2025 do INEP, se ainda não existir localmente."""
    if CAMINHO_ZIP_CENSO_2025.exists():
        print(f"[Censo 2025] ✓ Já existe em {CAMINHO_ZIP_CENSO_2025}, pulando download.")
        return

    print(f"[Censo 2025] Baixando de {URL_CENSO_2025} ...")
    sessao = criar_sessao_com_retry()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        resposta = sessao.get(URL_CENSO_2025, headers=headers, stream=True, timeout=300)
        resposta.raise_for_status()
        tamanho_total = int(resposta.headers.get("content-length", 0))
        baixado = 0
        with open(CAMINHO_ZIP_CENSO_2025, "wb") as arquivo:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                if bloco:
                    arquivo.write(bloco)
                    baixado += len(bloco)
                    if tamanho_total:
                        print(f"  {baixado / tamanho_total * 100:>6.1f}% | {baixado / 1024 / 1024:>8.0f} MB", end="\r")
        print(f"\n[Censo 2025] ✓ Download concluído: {baixado / 1024 / 1024:.0f} MB")
    except requests.exceptions.RequestException as e:
        print(f"[Censo 2025] ✗ Falha no download: {e}")
        print(f"              Baixe manualmente em: {URL_CENSO_2025}")
        print(f"              e salve como: {CAMINHO_ZIP_CENSO_2025}")
        raise


def descobrir_categoria_populacao_total(tabela: str = "9514") -> dict:
    """Consulta metadados da tabela 9514 e localiza a categoria 'Total' (sem chutar o ID)."""
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/metadados"
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    metadados = resposta.json()

    classificacao_idade = next(
        (c for c in metadados["classificacoes"] if "idade" in c["nome"].lower()), None
    )
    if not classificacao_idade:
        raise ValueError("[IBGE-População] Classificação de idade não encontrada nos metadados.")

    categoria_total = next(
        (cat for cat in classificacao_idade["categorias"] if cat["nome"].strip().lower() == "total"), None
    )
    if not categoria_total:
        raise ValueError(
            f"[IBGE-População] Categoria 'Total' não encontrada. "
            f"Categorias disponíveis: {[c['nome'] for c in classificacao_idade['categorias']][:10]}..."
        )

    return {"classificacao_id": classificacao_idade["id"], "categoria_total_id": categoria_total["id"]}


def baixar_populacao_total_municipal() -> None:
    """Busca população total residente por município (Censo 2022, via SIDRA), usada no filtro >100k hab."""
    if CAMINHO_POPULACAO_TOTAL.exists():
        print(f"[IBGE-População Total] ✓ Já existe em {CAMINHO_POPULACAO_TOTAL}, pulando.")
        return

    info = descobrir_categoria_populacao_total()
    classificacao_id = info["classificacao_id"]
    categoria_total_id = info["categoria_total_id"]

    print("[IBGE-População Total] Buscando população total por município (Censo 2022)...")
    tabelas_por_uf = []

    for uf in CODIGOS_UF:
        try:
            url = (
                f"https://apisidra.ibge.gov.br/values/"
                f"t/9514/n6/in%20n3%20{uf}/v/93/p/2022/"
                f"c2/6794/c{classificacao_id}/{categoria_total_id}"
            )
            resposta = requests.get(url, timeout=60)
            resposta.raise_for_status()
            dados = resposta.json()
            df_uf = pd.DataFrame(dados[1:], columns=dados[0].keys())
            tabelas_por_uf.append(df_uf)
            print(f"  UF {uf}: OK ({len(df_uf)} municípios)")
            time.sleep(0.3)
        except Exception as erro:
            print(f"  UF {uf}: falhou ({erro})")

    if not tabelas_por_uf:
        raise RuntimeError("[IBGE-População Total] Nenhuma UF retornou dados.")

    df_bruto = pd.concat(tabelas_por_uf, ignore_index=True)
    df_bruto["codigo_municipio"] = df_bruto["D1C"].astype(str)
    df_bruto["populacao_total"] = pd.to_numeric(df_bruto["V"], errors="coerce")

    df_final = df_bruto[["codigo_municipio", "populacao_total"]].dropna()
    df_final.to_csv(CAMINHO_POPULACAO_TOTAL, index=False)
    print(f"[IBGE-População Total] ✓ {len(df_final)} municípios salvos em {CAMINHO_POPULACAO_TOTAL}")
    print(f"                        Min: {df_final['populacao_total'].min():,.0f} | "
          f"Média: {df_final['populacao_total'].mean():,.0f} | "
          f"Max: {df_final['populacao_total'].max():,.0f}")


def main():
    print("=" * 90)
    print("CASE POLIEDRO — PASSO 1: DOWNLOAD DE DADOS BRUTOS")
    print("=" * 90)

    # Cada etapa é independente: falha em uma não deve impedir a outra de rodar.
    try:
        baixar_censo_escolar_2025()
    except Exception as e:
        print(f"\n[✗] Falha ao baixar Censo Escolar 2025: {type(e).__name__}: {e}")
        print("    Se preferir, baixe manualmente em:")
        print(f"    {URL_CENSO_2025}")
        print(f"    e salve como: {CAMINHO_ZIP_CENSO_2025}")

    try:
        baixar_populacao_total_municipal()
    except Exception as e:
        print(f"\n[✗] Falha ao buscar população total (IBGE/SIDRA): {type(e).__name__}: {e}")

    print("\n[✓] Passo 1 finalizado (ver mensagens acima para status de cada etapa).")


if __name__ == "__main__":
    main()
