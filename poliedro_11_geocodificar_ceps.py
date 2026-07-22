"""
Case Poliedro — Passo 11 (rodar LOCALMENTE, precisa de internet — o sandbox do
assistente tem a rede bloqueada para APIs externas como ViaCEP).

Geocodifica o CEP das Golden Leads localizadas nas 10 cidades prioritárias,
usando a API pública e gratuita do ViaCEP (https://viacep.com.br) para obter
bairro/logradouro. Não retorna renda — isso ainda exige um passo adicional
(cruzar com setor censitário do IBGE, mais pesado, ver nota no fim do
arquivo). Este passo é só o primeiro: sair de "só sei o CEP" para "sei o
bairro", o que já é um contexto qualitativo útil.

Escopo deliberadamente pequeno (teste primeiro, como sempre neste projeto):
só as Golden Leads (score_destaque >= 0.70) que estão nas 10 cidades
prioritárias da Parte 1 — não as 8.095 escolas nacionais.

Cache local obrigatório: nunca repete uma consulta de CEP já feita e salva em
disco (mesma prática usada no resto do pipeline).

Como rodar (na sua máquina, dentro da pasta do projeto):
    pip install requests
    python poliedro_11_geocodificar_ceps.py

Correção de auditoria (22/07): o poliedro_09 passou a exportar codigo_escola
diretamente em 04_golden_leads_segmentadas.csv, então o merge frágil por
nome+município (que existia aqui antes) foi eliminado — agora é um merge
direto por chave. Também corrigido: escolas_com_endereco.csv e
funil_escolas_pontuadas.csv agora são lidos de data/raw/ e data/outputs/
respectivamente, não de um path relativo solto.

Gera: data/outputs/05_golden_leads_geocodificadas.csv
"""

import json
import time
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")
CACHE_PATH = OUT_DIR / "_cache_viacep.json"
TIMEOUT_S = 8
PAUSA_ENTRE_CHAMADAS_S = 0.3  # gentileza com a API pública, evita bloqueio por excesso de requisições


def carregar_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def salvar_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def consultar_cep(cep: str, cache: dict) -> dict:
    """Consulta o ViaCEP para um CEP, usando cache em disco pra nunca repetir a mesma chamada de rede."""
    cep = str(cep).zfill(8)
    if cep in cache:
        return cache[cep]

    try:
        resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=TIMEOUT_S)
        resp.raise_for_status()
        dado = resp.json()
        if dado.get("erro"):
            dado = {"bairro": None, "logradouro": None, "erro": "CEP não encontrado"}
    except requests.RequestException as e:
        dado = {"bairro": None, "logradouro": None, "erro": f"Falha de rede: {e}"}

    cache[cep] = dado
    return dado


def carregar_golden_leads_top10() -> pd.DataFrame:
    """Golden Leads (score>=0.70) restritas às 10 cidades de maior score_priorizacao, já com CEP."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_municipio": str})
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})
    top10 = cidades.sort_values("score_priorizacao", ascending=False).head(10)

    enderecos = pd.read_csv(RAW_DIR / "escolas_com_endereco.csv", dtype={"codigo_municipio": str})
    enderecos = enderecos.rename(columns={"CO_ENTIDADE": "codigo_escola"})[
        ["codigo_escola", "CO_CEP", "DS_ENDERECO", "NU_ENDERECO"]
    ]

    df = golden[golden["codigo_municipio"].isin(top10["codigo_municipio"])].copy()
    df = df.merge(cidades[["codigo_municipio", "nome_municipio_ibge", "uf"]], on="codigo_municipio", how="left")
    df = df.merge(enderecos, on="codigo_escola", how="left")
    return df


def main():
    print("[Aviso] Este script precisa rodar na SUA máquina (internet liberada) — "
          "o sandbox do assistente tem a rede bloqueada pra APIs externas.")

    cache = carregar_cache()

    golden = carregar_golden_leads_top10()
    print(f"[Escopo] Golden Leads nas 10 cidades prioritárias: {len(golden)}")

    bairros, logradouros, erros = [], [], []
    for i, cep in enumerate(golden["CO_CEP"]):
        dado = consultar_cep(cep, cache)
        bairros.append(dado.get("bairro"))
        logradouros.append(dado.get("logradouro"))
        erros.append(dado.get("erro"))
        if (i + 1) % 20 == 0:
            print(f"  ...{i + 1}/{len(golden)} CEPs consultados")
            salvar_cache(cache)  # salva incrementalmente, não perde progresso se cair a conexão
        time.sleep(PAUSA_ENTRE_CHAMADAS_S)

    golden["bairro"] = bairros
    golden["logradouro_viacep"] = logradouros
    golden["erro_geocodificacao"] = erros
    salvar_cache(cache)

    com_bairro = golden["bairro"].notna().sum()
    print(f"\n[Sanity check] CEPs geocodificados com sucesso: {com_bairro} de {len(golden)} "
          f"({com_bairro / len(golden) * 100:.1f}%)")

    golden.to_csv(OUT_DIR / "05_golden_leads_geocodificadas.csv", index=False)
    print(f"[✓] Salvo em {OUT_DIR / '05_golden_leads_geocodificadas.csv'}")
    print("\nAmostra por cidade:")
    print(golden.groupby("nome_municipio_ibge")["bairro"].apply(lambda s: s.dropna().unique()[:5]))


if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# PRÓXIMO PASSO (não incluído aqui, é um pipeline maior): pra transformar
# "bairro" em "renda por bairro" de verdade (o que o Geofusion/OnMaps vende),
# precisaria:
#   1. Baixar a malha de setores censitários do IBGE (shapefile, Censo 2022)
#      e a tabela de renda por setor censitário (também IBGE, dado aberto).
#   2. Geocodificar cada escola pra lat/long (o ViaCEP não dá isso — precisaria
#      de outro serviço, ex. Nominatim/OpenStreetMap, que tem limite de uso).
#   3. Fazer um join espacial (ponto dentro de polígono) entre a lat/long da
#      escola e o setor censitário correspondente, usando geopandas.
# É um projeto à parte, não uma linha a mais neste script — vale a pena se
# você quiser ir a esse nível de detalhe depois da entrega.
# -----------------------------------------------------------------------------
