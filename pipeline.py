"""
Pipeline: Mapeamento de Escolas Privadas em Municípios com Alto Potencial Econômico
Versão INTEGRADA:
- Métrica de riqueza: % população em faixas de renda domiciliar per capita alta (Censo 2022, Tabela 10296)
- Filtro de elegibilidade: população 0-17 anos >= 1000 (Censo 2022, Tabela 9514 via SIDRA)
- PIB per capita mantido só como coluna de CONTEXTO (não entra no score)
- Escolas privadas: exclui filantrópicas (APAE etc) e outliers de porte (>150 salas)
- Coluna de internet removida (sem variância, 98%+ das escolas já têm)
Custo: zero (arquivos Excel locais + APIs públicas do IBGE + SQLite local)
"""

import re
import time
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sqlalchemy import create_engine

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO GLOBAL
# ---------------------------------------------------------------------------
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

CAMINHO_PIB_EXCEL = RAW_DIR / "PIB dos Municípios - base de dados 2010-2023.xlsx"
CAMINHO_TABELA_RENDA = RAW_DIR / "Tabela_10296__1_.xlsx"
CAMINHO_ZIP_INEP = RAW_DIR / "microdados_censo_escolar_2023.zip"
CAMINHO_CACHE_IDADE = RAW_DIR / "populacao_0_17_por_municipio.csv"
CAMINHO_CACHE_CORRESPONDENCIA = RAW_DIR / "correspondencia_municipios_ibge.csv"
CAMINHO_DB_SQLITE = "mercado_educacional_local.db"

URL_INEP_MICRODADOS = "https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2023.zip"

TP_DEPENDENCIA_PRIVADA = 4
CATEGORIAS_PRIVADAS_VALIDAS = [1, 2, 3]  # Exclui 4 = Filantrópica (APAE etc)
LIMITE_MAXIMO_SALAS = 150               # Remove outliers (polos de EAD, etc)
POPULACAO_MINIMA_0_17 = 1000            # Piso de elegibilidade

CODIGOS_UF = [
    "11", "12", "13", "14", "15", "16", "17", "21", "22", "23", "24", "25",
    "26", "27", "28", "29", "31", "32", "33", "35", "41", "42", "43", "50",
    "51", "52", "53",
]

engine = create_engine(f"sqlite:///{CAMINHO_DB_SQLITE}")


# ---------------------------------------------------------------------------
# UTILITÁRIOS DE REDE
# ---------------------------------------------------------------------------
def criar_sessao_com_retry(verify_ssl: bool = False) -> requests.Session:
    """Cria sessão HTTP com retry automático e SSL verification opcional."""
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=(500, 502, 503, 504, 408, 429),
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.verify = verify_ssl
    return session


def verificar_integridade_zip(caminho_zip: Path) -> bool:
    """Verifica se o arquivo ZIP não está corrompido."""
    try:
        with zipfile.ZipFile(caminho_zip, "r") as z:
            return z.testzip() is None
    except Exception as e:
        print(f"[!] Erro ao verificar ZIP: {e}")
        return False


# ---------------------------------------------------------------------------
# BLOCO A — PIB PER CAPITA (SÓ CONTEXTO, NÃO ENTRA NO SCORE)
# ---------------------------------------------------------------------------
def extrair_pib_per_capita_contexto(
    ano: int = 2023,
    caminho_excel: Optional[Path] = None
) -> pd.DataFrame:
    """Extrai PIB per capita municipal do Excel do IBGE. Uso: coluna de contexto apenas."""
    arquivo = caminho_excel or CAMINHO_PIB_EXCEL

    if not arquivo.exists():
        print(f"[IBGE-PIB] ⚠ Arquivo não encontrado: {arquivo}. Contexto de PIB será omitido.")
        return pd.DataFrame(columns=["codigo_municipio", "pib_per_capita_contexto"])

    print("[IBGE-PIB] Lendo PIB per capita (coluna de contexto)...")

    try:
        df = pd.read_excel(arquivo, sheet_name="PIB dos Municípios")
    except ValueError:
        df = pd.read_excel(arquivo, sheet_name=0)

    df_ano = df[df["Ano"] == ano].copy()

    col_codigo = "Código do Município"
    col_pib = "Produto Interno Bruto per capita, \na preços correntes\n(R$ 1,00)"

    if col_codigo not in df_ano.columns or col_pib not in df_ano.columns:
        print(f"[IBGE-PIB] ⚠ Colunas esperadas não encontradas. Contexto de PIB será omitido.")
        return pd.DataFrame(columns=["codigo_municipio", "pib_per_capita_contexto"])

    df_limpo = df_ano[[col_codigo, col_pib]].copy()
    df_limpo.columns = ["codigo_municipio", "pib_per_capita_contexto"]
    df_limpo["codigo_municipio"] = df_limpo["codigo_municipio"].astype(str).str.strip()
    df_limpo["pib_per_capita_contexto"] = pd.to_numeric(df_limpo["pib_per_capita_contexto"], errors="coerce")
    df_limpo = df_limpo.dropna(subset=["pib_per_capita_contexto"])
    df_limpo = df_limpo.drop_duplicates(subset="codigo_municipio", keep="first")

    print(f"[IBGE-PIB] ✓ {len(df_limpo)} municípios (contexto apenas, não entra no score)")
    return df_limpo


# ---------------------------------------------------------------------------
# BLOCO B — CORRESPONDÊNCIA DE MUNICÍPIOS (Nome+UF → Código IBGE)
# ---------------------------------------------------------------------------
def obter_correspondencia_municipios() -> pd.DataFrame:
    """Busca a lista oficial de municípios do IBGE (código + nome + UF)."""
    if CAMINHO_CACHE_CORRESPONDENCIA.exists():
        print("[IBGE-Localidades] Correspondência de municípios: carregando do cache...")
        return pd.read_csv(CAMINHO_CACHE_CORRESPONDENCIA, dtype=str)

    print("[IBGE-Localidades] Buscando lista oficial de municípios...")
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    resposta = requests.get(url, timeout=60)
    resposta.raise_for_status()
    dados = resposta.json()

    registros = []
    for municipio in dados:
        codigo = str(municipio["id"])
        nome = municipio["nome"]

        # Validação defensiva: alguns municípios podem ter mesorregiao = None
        try:
            uf_sigla = municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        except (TypeError, KeyError):
            # Se falhar, tenta extrair UF direto do campo de região
            try:
                uf_sigla = municipio["regiao"]["sigla"]
            except (TypeError, KeyError):
                # Se ainda falhar, pula este município
                print(f"[!] Aviso: Não foi possível extrair UF para o município ID {codigo}. Pulando...")
                continue

        registros.append({
            "codigo_municipio": codigo,
            "nome_municipio_ibge": nome,
            "uf": uf_sigla,
            "chave_nome_uf": f"{nome} ({uf_sigla})"
        })

    df_correspondencia = pd.DataFrame(registros)
    df_correspondencia.to_csv(CAMINHO_CACHE_CORRESPONDENCIA, index=False)
    print(f"[IBGE-Localidades] ✓ {len(df_correspondencia)} municípios mapeados")
    return df_correspondencia


# ---------------------------------------------------------------------------
# BLOCO C — RENDA DOMICILIAR PER CAPITA (Tabela 10296)
# ---------------------------------------------------------------------------
def extrair_score_renda_municipal(
    caminho_excel: Optional[Path] = None,
    peso_renda_alta: float = 0.80,
    peso_classe_media_alta: float = 0.20
) -> pd.DataFrame:
    """Calcula, por município, a população nas faixas de renda-alvo (Censo 2022)."""
    arquivo = caminho_excel or CAMINHO_TABELA_RENDA

    if not arquivo.exists():
        raise FileNotFoundError(f"[IBGE-Renda] Tabela 10296 não encontrada: {arquivo}")

    print("[IBGE-Renda] Lendo Tabela 10296 (renda domiciliar per capita, Censo 2022)...")

    df_raw = pd.read_excel(arquivo, sheet_name="Tabela", header=None)

    linha_inicio = df_raw[df_raw[0] == "Município"].index[0] + 1
    df_dados = df_raw.iloc[linha_inicio:, [0, 1, 2]].copy()
    df_dados.columns = ["municipio_uf", "faixa_renda", "quantidade"]

    df_dados["municipio_uf"] = df_dados["municipio_uf"].ffill()
    df_dados = df_dados.dropna(subset=["faixa_renda"])

    df_dados["quantidade"] = (
        df_dados["quantidade"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .replace("-", "0")
    )
    df_dados["quantidade"] = pd.to_numeric(df_dados["quantidade"], errors="coerce").fillna(0)

    df_pivot = df_dados.pivot_table(
        index="municipio_uf",
        columns="faixa_renda",
        values="quantidade",
        aggfunc="sum"
    ).reset_index()

    faixas_renda_alta = [
        "Mais de 5 a 10 salários mínimos",
        "Mais de 10 a 15 salários mínimos",
        "Mais de 15 a 20 salários mínimos",
        "Mais de 20 salários mínimos",
    ]
    faixa_classe_media_alta = "Mais de 3 a 5 salários mínimos"

    colunas_faltando = [f for f in faixas_renda_alta + [faixa_classe_media_alta] if f not in df_pivot.columns]
    if colunas_faltando:
        raise ValueError(
            f"[IBGE-Renda] Faixas de renda não encontradas: {colunas_faltando}\n"
            f"Colunas disponíveis: {df_pivot.columns.tolist()}"
        )

    df_pivot["pop_renda_alta"] = df_pivot[faixas_renda_alta].sum(axis=1)
    df_pivot["pop_classe_media_alta"] = df_pivot[faixa_classe_media_alta]
    df_pivot["chave_nome_uf"] = df_pivot["municipio_uf"].str.strip()

    df_correspondencia = obter_correspondencia_municipios()
    df_final = df_pivot.merge(df_correspondencia, on="chave_nome_uf", how="left")

    nao_encontrados = df_final["codigo_municipio"].isna().sum()
    if nao_encontrados > 0:
        print(f"[IBGE-Renda] ⚠ {nao_encontrados} municípios não casaram por nome exato (acentuação/hífen).")
        exemplos = df_final[df_final["codigo_municipio"].isna()]["municipio_uf"].head(5).tolist()
        print(f"             Exemplos: {exemplos}")

    df_final = df_final.dropna(subset=["codigo_municipio"])
    print(f"[IBGE-Renda] ✓ {len(df_final)} municípios com renda calculada")

    return df_final[["codigo_municipio", "pop_renda_alta", "pop_classe_media_alta"]]


# ---------------------------------------------------------------------------
# BLOCO D — POPULAÇÃO 0-17 ANOS (Tabela 9514, SIDRA)
# ---------------------------------------------------------------------------
def descobrir_categorias_idade_0_a_17(tabela: str = "9514") -> dict:
    """Consulta os metadados da tabela 9514 e mapeia {idade: codigo_categoria} para 0-17 anos."""
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/metadados"
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    metadados = resposta.json()

    classificacao_idade = next(
        (c for c in metadados["classificacoes"] if "idade" in c["nome"].lower()),
        None
    )
    if not classificacao_idade:
        raise ValueError("[IBGE-Idade] Classificação de idade não encontrada nos metadados.")

    mapa_idades = {}
    for categoria in classificacao_idade["categorias"]:
        nome = categoria["nome"].strip().lower()
        if nome == "menos de 1 ano":
            mapa_idades[0] = categoria["id"]
        else:
            match = re.match(r"^(\d+)\s+anos?$", nome)
            if match:
                idade = int(match.group(1))
                if 0 <= idade <= 17:
                    mapa_idades[idade] = categoria["id"]

    print(f"[IBGE-Idade] Categorias 0-17 encontradas: {len(mapa_idades)} de 18 esperadas")
    if len(mapa_idades) < 18:
        print(f"             Faltando: {sorted(set(range(18)) - set(mapa_idades.keys()))}")

    return {"classificacao_id": classificacao_idade["id"], "categorias_idade": mapa_idades}


def extrair_populacao_0_17_municipal() -> pd.DataFrame:
    """Busca a população residente de 0 a 17 anos por município (Censo 2022, via SIDRA)."""
    if CAMINHO_CACHE_IDADE.exists():
        print("[IBGE-Idade] População 0-17 anos: carregando do cache...")
        return pd.read_csv(CAMINHO_CACHE_IDADE, dtype={"codigo_municipio": str})

    info_idade = descobrir_categorias_idade_0_a_17()
    classificacao_id = info_idade["classificacao_id"]
    codigos_categoria_str = ",".join(str(c) for c in info_idade["categorias_idade"].values())

    print("[IBGE-Idade] Buscando população 0-17 anos por município (Censo 2022)...")
    tabelas_por_uf = []

    for uf in CODIGOS_UF:
        try:
            url = (
                f"https://apisidra.ibge.gov.br/values/"
                f"t/9514/n6/in%20n3%20{uf}/v/93/p/2022/"
                f"c2/6794/c{classificacao_id}/{codigos_categoria_str}"
            )
            resposta = requests.get(url, timeout=60)
            resposta.raise_for_status()
            dados = resposta.json()

            df_uf = pd.DataFrame(dados[1:], columns=dados[0].keys())
            tabelas_por_uf.append(df_uf)
            print(f"  UF {uf}: OK ({len(df_uf)} linhas)")
            time.sleep(0.3)

        except Exception as erro:
            print(f"  UF {uf}: falhou ({erro})")

    if not tabelas_por_uf:
        raise RuntimeError("[IBGE-Idade] Nenhuma UF retornou dados de população por idade.")

    df_bruto = pd.concat(tabelas_por_uf, ignore_index=True)
    df_bruto["codigo_municipio"] = df_bruto["D1C"].astype(str)
    df_bruto["valor"] = pd.to_numeric(df_bruto["V"], errors="coerce").fillna(0)

    df_populacao = (
        df_bruto.groupby("codigo_municipio", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "populacao_0_17"})
    )

    df_populacao.to_csv(CAMINHO_CACHE_IDADE, index=False)
    print(f"[IBGE-Idade] ✓ População 0-17 calculada para {len(df_populacao)} municípios")
    return df_populacao


# ---------------------------------------------------------------------------
# BLOCO E — SCORE SOCIOECONÔMICO MUNICIPAL (Renda + População + Filtro)
# ---------------------------------------------------------------------------
def montar_score_socioeconomico_municipal() -> pd.DataFrame:
    """Combina renda e população infantil em um score único, com filtro de elegibilidade."""
    df_renda = extrair_score_renda_municipal()
    df_populacao = extrair_populacao_0_17_municipal()

    df = df_renda.merge(df_populacao, on="codigo_municipio", how="inner")

    antes = len(df)
    df = df[df["populacao_0_17"] >= POPULACAO_MINIMA_0_17].copy()
    print(f"[Filtro-Elegibilidade] {antes - len(df)} municípios removidos (população 0-17 < {POPULACAO_MINIMA_0_17})")
    print(f"[Filtro-Elegibilidade] {len(df)} municípios elegíveis restantes")

    df["pct_renda_alta"] = df["pop_renda_alta"] / df["populacao_0_17"]
    df["pct_classe_media_alta"] = df["pop_classe_media_alta"] / df["populacao_0_17"]

    df["score_renda"] = (
        df["pct_renda_alta"] * 0.80
        + df["pct_classe_media_alta"] * 0.20
    )

    df["percentil_volume_publico"] = df["populacao_0_17"].rank(pct=True)

    df["score_socioeconomico"] = (
        df["score_renda"] * 0.85
        + df["percentil_volume_publico"] * 0.15
    ).round(4)

    return df[["codigo_municipio", "populacao_0_17", "score_socioeconomico"]]


# ---------------------------------------------------------------------------
# BLOCO F — ESCOLAS PRIVADAS (INEP / CENSO ESCOLAR)
# ---------------------------------------------------------------------------
def gerar_dados_mock_escolas() -> pd.DataFrame:
    """Dataset fictício para teste rápido, sem baixar os microdados completos."""
    print("[INEP] ⚠ Gerando dados fictícios (mock) para teste rápido...")
    return pd.DataFrame({
        "codigo_escola": [350001, 350002, 330001, 290001, 110001, 350003],
        "nome_escola": [
            "Colégio Premium São Paulo", "Escola Futuro",
            "Colégio Rio de Janeiro", "Escola Bahia", "Escola Rondônia", "Escola Elite"
        ],
        "codigo_municipio": ["3550308", "3550308", "3304557", "2927408", "1100205", "3550308"],
        "tipo_dependencia": [4, 4, 4, 4, 4, 4],
        "categoria_escola_privada": [1, 1, 1, 1, 1, 1],
        "quantidade_salas": [25, 12, 30, 8, 5, 18],
    })


def baixar_microdados_inep_com_retry(url: str = URL_INEP_MICRODADOS, max_tentativas: int = 5) -> None:
    """Baixa o ZIP dos microdados do INEP com retry automático e SSL desativado."""
    print(f"[INEP] Iniciando download com retry automático...")
    print(f"       URL: {url}")

    sessao = criar_sessao_com_retry(verify_ssl=False)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for tentativa in range(1, max_tentativas + 1):
        print(f"[INEP] Tentativa {tentativa}/{max_tentativas}...")
        try:
            resposta = sessao.get(url, headers=headers, stream=True, timeout=300)
            resposta.raise_for_status()

            tamanho_total = int(resposta.headers.get("content-length", 0))
            tamanho_baixado = 0
            tempo_inicio = time.time()

            with open(CAMINHO_ZIP_INEP, "wb") as arquivo:
                for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                    if bloco:
                        arquivo.write(bloco)
                        tamanho_baixado += len(bloco)
                        if tamanho_total:
                            percentual = (tamanho_baixado / tamanho_total) * 100
                            velocidade = (tamanho_baixado / 1024 / 1024) / (time.time() - tempo_inicio + 1)
                            print(f"  {percentual:>6.1f}% | {tamanho_baixado / 1024 / 1024:>8.0f} MB | {velocidade:.1f} MB/s")

            if verificar_integridade_zip(CAMINHO_ZIP_INEP):
                print("[INEP] ✓ Download e validação concluídos!")
                return
            else:
                print("[INEP] ✗ ZIP corrompido. Tentando novamente...")
                CAMINHO_ZIP_INEP.unlink()

        except requests.exceptions.RequestException as e:
            print(f"[INEP] ✗ Falha na tentativa {tentativa}: {type(e).__name__}")
            if tentativa < max_tentativas:
                time.sleep(2 ** (tentativa - 1))

    raise RuntimeError(f"[INEP] Falha após {max_tentativas} tentativas. Baixe manualmente: {url}")


def ler_escolas_privadas_do_zip() -> pd.DataFrame:
    """
    Extrai escolas privadas do ZIP do INEP.
    Filtros aplicados: só privadas não-filantrópicas, máx. 150 salas, sem coluna de internet.
    """
    print("[INEP] Lendo escolas privadas do arquivo ZIP...")

    colunas_necessarias = [
        "CO_ENTIDADE", "NO_ENTIDADE", "CO_MUNICIPIO",
        "TP_DEPENDENCIA", "TP_CATEGORIA_ESCOLA_PRIVADA", "QT_SALAS_UTILIZADAS",
    ]

    with zipfile.ZipFile(CAMINHO_ZIP_INEP) as zip_ref:
        caminho_csv = "microdados_censo_escolar_2023/dados/microdados_ed_basica_2023.csv"
        if caminho_csv not in zip_ref.namelist():
            raise FileNotFoundError(f"Arquivo não encontrado no ZIP: {caminho_csv}")

        with zip_ref.open(caminho_csv) as arquivo_csv:
            df_completo = pd.read_csv(
                arquivo_csv,
                sep=";",
                encoding="iso-8859-1",
                usecols=colunas_necessarias,
                dtype={"CO_MUNICIPIO": str},
                low_memory=False
            )

    print(f"[INEP] Total de registros no arquivo: {len(df_completo):,}")

    df_privadas = df_completo[df_completo["TP_DEPENDENCIA"] == TP_DEPENDENCIA_PRIVADA].copy()
    df_privadas = df_privadas[df_privadas["TP_CATEGORIA_ESCOLA_PRIVADA"].isin(CATEGORIAS_PRIVADAS_VALIDAS)].copy()
    print(f"[INEP] Privadas não-filantrópicas: {len(df_privadas):,}")

    df_privadas = df_privadas.rename(columns={
        "CO_ENTIDADE": "codigo_escola",
        "NO_ENTIDADE": "nome_escola",
        "CO_MUNICIPIO": "codigo_municipio",
        "TP_DEPENDENCIA": "tipo_dependencia",
        "TP_CATEGORIA_ESCOLA_PRIVADA": "categoria_escola_privada",
        "QT_SALAS_UTILIZADAS": "quantidade_salas",
    })

    df_privadas = df_privadas[df_privadas["quantidade_salas"] <= LIMITE_MAXIMO_SALAS].copy()
    print(f"[INEP] ✓ {len(df_privadas):,} escolas privadas carregadas (após remover outliers de porte)")

    return df_privadas


def extrair_escolas_privadas() -> pd.DataFrame:
    """Carrega escolas do ZIP (baixando se necessário) ou usa mock para teste."""
    if CAMINHO_ZIP_INEP.exists():
        if verificar_integridade_zip(CAMINHO_ZIP_INEP):
            return ler_escolas_privadas_do_zip()
        print("[INEP] ⚠ ZIP corrompido. Será re-baixado.")
        CAMINHO_ZIP_INEP.unlink()

    print(f"\n[INEP] Arquivo não encontrado: {CAMINHO_ZIP_INEP}")
    print("[1] Baixar microdados reais do INEP (~1.5 GB)")
    print("[2] Usar dados fictícios (mock) para testar agora")
    opcao = input("\nEscolha (1 ou 2): ").strip()

    if opcao == "1":
        baixar_microdados_inep_com_retry()
        return ler_escolas_privadas_do_zip()
    return gerar_dados_mock_escolas()


# ---------------------------------------------------------------------------
# BLOCO G — CRUZAMENTO FINAL, SCORE DE POTENCIAL E CARGA
# ---------------------------------------------------------------------------
def calcular_score_potencial_escola(
    df: pd.DataFrame,
    peso_municipio: float = 0.70,
    peso_porte_escola: float = 0.30
) -> pd.DataFrame:
    """
    Combina o score socioeconômico do MUNICÍPIO com o porte da ESCOLA.
    O PIB per capita NÃO entra aqui — é só coluna de contexto no resultado final.
    """
    df["percentil_score_municipio"] = df["score_socioeconomico"].rank(pct=True)
    df["percentil_porte_escola"] = df["quantidade_salas"].rank(pct=True)

    df["score_potencial"] = (
        df["percentil_score_municipio"] * peso_municipio
        + df["percentil_porte_escola"] * peso_porte_escola
    ).round(4)

    return df


def cruzar_e_salvar(
    df_escolas: pd.DataFrame,
    df_socioeconomico: pd.DataFrame,
    df_pib_contexto: pd.DataFrame
) -> pd.DataFrame:
    """Cruza escolas com o score socioeconômico do município, adiciona PIB como contexto, e salva."""
    df_escolas["codigo_municipio"] = df_escolas["codigo_municipio"].astype(str).str.strip()
    df_socioeconomico["codigo_municipio"] = df_socioeconomico["codigo_municipio"].astype(str).str.strip()

    df_cruzado = pd.merge(df_escolas, df_socioeconomico, on="codigo_municipio", how="inner")

    if df_cruzado.empty:
        print("[!] AVISO: Nenhuma correspondência encontrada no cruzamento principal (escolas x socioeconômico)")
        return pd.DataFrame()

    if not df_pib_contexto.empty:
        df_pib_contexto["codigo_municipio"] = df_pib_contexto["codigo_municipio"].astype(str).str.strip()
        df_cruzado = df_cruzado.merge(df_pib_contexto, on="codigo_municipio", how="left")

    df_cruzado = calcular_score_potencial_escola(df_cruzado)
    df_cruzado = df_cruzado.sort_values("score_potencial", ascending=False).reset_index(drop=True)

    df_cruzado.to_sql("escolas_privadas_potenciais", con=engine, if_exists="replace", index=False)
    print(f"[SQLite] ✓ {len(df_cruzado):,} registros salvos em '{CAMINHO_DB_SQLITE}'")

    return df_cruzado


# ---------------------------------------------------------------------------
# BLOCO H — APRESENTAÇÃO DOS RESULTADOS
# ---------------------------------------------------------------------------
def exibir_resultados_top_10(df_final: pd.DataFrame) -> None:
    if df_final.empty:
        return
    print("\n" + "=" * 110)
    print("TOP 10 ESCOLAS COM MAIOR POTENCIAL ECONÔMICO")
    print("=" * 110)
    colunas = [
        "nome_escola", "codigo_municipio", "score_socioeconomico",
        "quantidade_salas", "pib_per_capita_contexto", "score_potencial"
    ]
    colunas_existentes = [c for c in colunas if c in df_final.columns]
    print(df_final[colunas_existentes].head(10).to_string(index=False))
    print("=" * 110 + "\n")


def exibir_resumo_analise(df_final: pd.DataFrame) -> None:
    if df_final.empty:
        return
    print("\n" + "=" * 110)
    print("RESUMO DA ANÁLISE")
    print("=" * 110)
    print(f"Total de escolas privadas analisadas: {len(df_final):,}")
    print(f"Municípios distintos representados: {df_final['codigo_municipio'].nunique():,}")
    print(f"Score socioeconômico - Min: {df_final['score_socioeconomico'].min():.4f} | Média: {df_final['score_socioeconomico'].mean():.4f} | Max: {df_final['score_socioeconomico'].max():.4f}")
    print(f"Salas por escola - Min: {df_final['quantidade_salas'].min()} | Média: {df_final['quantidade_salas'].mean():.1f} | Max: {df_final['quantidade_salas'].max()}")
    if "pib_per_capita_contexto" in df_final.columns:
        print(f"PIB per capita (contexto) - Média: R$ {df_final['pib_per_capita_contexto'].mean():,.2f}")
    print("=" * 110 + "\n")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("\n" + "=" * 110)
    print("PIPELINE: MAPEAMENTO DE ESCOLAS PRIVADAS EM MUNICÍPIOS COM ALTO POTENCIAL SOCIOECONÔMICO")
    print("=" * 110 + "\n")

    try:
        df_socioeconomico = montar_score_socioeconomico_municipal()
        df_pib_contexto = extrair_pib_per_capita_contexto(ano=2023)
        df_escolas = extrair_escolas_privadas()

        df_final = cruzar_e_salvar(df_escolas, df_socioeconomico, df_pib_contexto)
        df_final[["nome_escola", "codigo_municipio", "score_socioeconomico", "quantidade_salas", "score_potencial"]].to_csv(
            "escolas_premium_potencial.csv", index=False)

        exibir_resultados_top_10(df_final)
        exibir_resumo_analise(df_final)

        print("[✓] Pipeline concluído com sucesso!")

    except FileNotFoundError as e:
        print(f"\n[✗] Erro: {e}")
    except ValueError as e:
        print(f"\n[✗] Erro de validação: {e}")
    except Exception as e:
        print(f"\n[✗] Erro inesperado: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    main()