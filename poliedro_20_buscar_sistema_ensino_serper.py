"""
Case Poliedro — Passo 20 (roadmap 3.0, pedido do Gui em 24/07: "procure a
maneira mais eficiente de gastar" as buscas de sistema de ensino): busca
em lote via Serper.dev (SERP API) pras Golden Leads que sobraram depois de
esgotar as formas gratuitas (registro manual + marca no próprio nome, ver
poliedro_19).

Por que Serper e não Tavily: Serper devolve o resultado bruto do Google
(mesmo formato que já vinha funcionando bem via WebSearch), com parâmetros
de país/idioma (gl=br, hl=pt-br) — e custa ~8x menos por consulta que o
Tavily, que soma por cima uma extração de conteúdo que a gente não precisa
(quem classifica é o Claude, não a API).

O que esse script FAZ: dispara 1 consulta por escola ainda sem registro em
REGISTROS (poliedro_19), guarda a resposta bruta em cache local (nunca
repete uma chamada já feita — cada escola vira 1 arquivo JSON em
data/raw/serper_cache/), e consolida os 3 primeiros snippets orgânicos de
cada escola num CSV pronto pra eu (Claude) ler em bloco e classificar —
sem precisar abrir página nenhuma.

O que esse script NÃO faz: não decide o sistema de ensino. Isso continua
sendo trabalho humano+IA (ver poliedro_19) — aqui é só a "Camada 1" da
arquitetura em cascata que o Gui trouxe (busca rápida e barata; só cai pra
navegação de verdade se o snippet vier inconclusivo, e isso é decidido
depois, na hora de classificar, não aqui).

Chave de API: lida de data/raw/.serper_key (NUNCA commitada — ver
.gitignore). Nunca hardcode a chave direto no código.

Gera: data/outputs/20_snippets_para_classificar.csv
"""

import asyncio
import json
import time
from pathlib import Path

import httpx
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")
CACHE_DIR = RAW_DIR / "serper_cache"
CHAVE_PATH = RAW_DIR / ".serper_key"

CONCORRENCIA_MAXIMA = 4  # nº de chamadas simultâneas em voo
TIMEOUT_SEGUNDOS = 15

# Plano gratuito do Serper permite só 5 requisições/segundo (achado nesta rodada: 697 das 947
# chamadas voltaram "429 Rate limit exceeded" porque a concorrência de 10 disparava tudo de
# uma vez, sem espaçamento). 4/s fica com margem de segurança sob o limite real de 5/s.
MAX_REQUISICOES_POR_SEGUNDO = 4.0


class LimitadorDeTaxa:
    """Espaça as chamadas pra nunca ultrapassar MAX_REQUISICOES_POR_SEGUNDO, não importa a
    concorrência configurada — é isso que faltava antes (só limitar quantas rodam ao mesmo
    tempo não limita a TAXA de disparo)."""

    def __init__(self, max_por_segundo: float):
        self._intervalo_minimo = 1.0 / max_por_segundo
        self._lock = asyncio.Lock()
        self._proxima_liberacao = 0.0

    async def aguardar_vez(self) -> None:
        async with self._lock:
            agora = asyncio.get_event_loop().time()
            espera = max(0.0, self._proxima_liberacao - agora)
            if espera > 0:
                await asyncio.sleep(espera)
            self._proxima_liberacao = max(agora, self._proxima_liberacao) + self._intervalo_minimo

# Pedido do Gui (24/07): termos genéricos, SEM nomear marcas específicas (SAS/Bernoulli/Anglo/
# etc.) — nomear marca no próprio termo de busca enviesa o Google a devolver só o que a gente já
# sabia que existia, em vez de deixar a própria escola se identificar. Os termos abaixo descrevem
# a CATEGORIA (qualquer sistema de terceiros se encaixa em pelo menos um), sem pressupor qual é
# a resposta — quem decide o nome do sistema sou eu, lendo o snippet depois, não a query.
TERMOS_SISTEMA = (
    '("sistema de ensino" OR "material didático" OR "sistema pedagógico" OR '
    '"solução educacional" OR "apostila" OR "sistema de aprendizagem")'
)


def ler_chave_api() -> str:
    """Lê a chave do Serper do arquivo local (nunca do código-fonte)."""
    try:
        return CHAVE_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError as erro:
        raise RuntimeError(
            f"Chave da API Serper não encontrada em {CHAVE_PATH}. "
            "Salve a chave nesse arquivo (1 linha, sem quebra) antes de rodar."
        ) from erro


def montar_query(nome_escola: str, cidade: str) -> str:
    """Query otimizada: nome e cidade entre aspas (frase exata) + termos de sistema entre OR."""
    return f'"{nome_escola}" "{cidade}" {TERMOS_SISTEMA}'


def carregar_escolas_pendentes() -> pd.DataFrame:
    """Golden Leads que ainda não estão no registro manual (poliedro_19)."""
    from poliedro_19_sistema_ensino_identificado import REGISTROS

    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str})
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})[
        ["codigo_municipio", "nome_municipio_ibge"]
    ]
    golden["codigo_municipio"] = golden["codigo_municipio"].astype(str)
    golden = golden.merge(cidades, on="codigo_municipio", how="left")
    ja_registradas = set(REGISTROS.keys())
    pendentes = golden[~golden["codigo_escola"].isin(ja_registradas)]
    return pendentes[["codigo_escola", "NO_ENTIDADE", "nome_municipio_ibge", "score_destaque"]].sort_values(
        "score_destaque", ascending=False
    )


def _cache_valido(cache_path: Path) -> "dict | None":
    """Carrega o cache só se ele NÃO for um erro transitório (429) — esse tipo de erro não
    deve travar a escola como 'já tentada pra sempre', tem que ser retentado numa próxima rodada."""
    if not cache_path.exists():
        return None
    dados = json.loads(cache_path.read_text(encoding="utf-8"))
    erro = dados.get("resposta", {}).get("erro", "")
    if erro.startswith("HTTP 429"):
        return None
    return dados


async def buscar_uma_escola(cliente: httpx.AsyncClient, chave: str, codigo: str, nome: str, cidade: str,
                             semaforo: asyncio.Semaphore, limitador: LimitadorDeTaxa) -> dict:
    """Busca 1 escola no Serper, com cache em disco (nunca repete uma chamada que já deu certo,
    ou que deu erro definitivo — só re-tenta erro de rate limit, ver `_cache_valido`)."""
    cache_path = CACHE_DIR / f"{codigo}.json"
    cache = _cache_valido(cache_path)
    if cache is not None:
        return cache

    query = montar_query(nome, cidade if pd.notna(cidade) else "")
    async with semaforo:
        dados = None
        # Até 4 tentativas: rate limit (429) e falha de rede transitória (timeout, conexão
        # resetada) são comuns em lotes grandes — espera crescente entre elas.
        for tentativa in range(4):
            await limitador.aguardar_vez()
            try:
                resposta = await cliente.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": chave, "Content-Type": "application/json"},
                    json={"q": query, "gl": "br", "hl": "pt-br", "num": 5},
                    timeout=TIMEOUT_SEGUNDOS,
                )
                resposta.raise_for_status()
                dados = resposta.json()
                break
            except httpx.HTTPStatusError as erro:
                dados = {"erro": f"HTTP {erro.response.status_code}: {erro.response.text[:200]}"}
                if erro.response.status_code == 429 and tentativa < 3:
                    # Rate limit é sempre transitório — vale a pena esperar e tentar de novo.
                    await asyncio.sleep(2.0 * (tentativa + 1))
                    continue
                break  # outros erros HTTP (ex.: 401 chave inválida) não se resolvem tentando de novo
            except Exception as erro:  # noqa: BLE001 — qualquer falha de rede/timeout entra aqui
                dados = {"erro": f"{type(erro).__name__}: {erro}"}
                if tentativa < 3:
                    await asyncio.sleep(1.5 * (tentativa + 1))

    resultado = {"codigo_escola": codigo, "NO_ENTIDADE": nome, "cidade": cidade, "query": query, "resposta": dados}
    cache_path.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return resultado


def extrair_snippets(resultado: dict) -> str:
    """Concatena título+snippet dos 3 primeiros resultados orgânicos — só isso vai pro CSV final."""
    dados = resultado.get("resposta", {})
    if "erro" in dados:
        return f"[ERRO NA BUSCA: {dados['erro']}]"
    organicos = dados.get("organic", [])[:3]
    partes = []
    for item in organicos:
        titulo = item.get("title", "")
        snippet = item.get("snippet", "")
        partes.append(f"{titulo} — {snippet}")
    return " | ".join(partes) if partes else "[SEM RESULTADO ORGÂNICO]"


async def rodar_lote(escolas: pd.DataFrame) -> pd.DataFrame:
    chave = ler_chave_api()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    semaforo = asyncio.Semaphore(CONCORRENCIA_MAXIMA)
    limitador = LimitadorDeTaxa(MAX_REQUISICOES_POR_SEGUNDO)

    async with httpx.AsyncClient() as cliente:
        tarefas = [
            buscar_uma_escola(cliente, chave, row["codigo_escola"], row["NO_ENTIDADE"],
                               row["nome_municipio_ibge"], semaforo, limitador)
            for _, row in escolas.iterrows()
        ]
        resultados = await asyncio.gather(*tarefas)

    linhas = []
    for r in resultados:
        linhas.append({
            "codigo_escola": r["codigo_escola"],
            "NO_ENTIDADE": r["NO_ENTIDADE"],
            "cidade": r["cidade"],
            "snippets": extrair_snippets(r),
        })
    return pd.DataFrame(linhas)


def main(limite: "int | None" = None):
    """Se `limite` for passado, roda só as N primeiras escolas (teste pequeno antes do lote completo)."""
    pendentes = carregar_escolas_pendentes()
    total_pendentes = len(pendentes)
    if limite:
        pendentes = pendentes.head(limite)
    print(f"[Info] {total_pendentes} escolas pendentes no total. Rodando {len(pendentes)} nesta chamada.")

    inicio = time.time()
    df = asyncio.run(rodar_lote(pendentes))
    duracao = time.time() - inicio

    n_erro = df["snippets"].str.startswith("[ERRO").sum()
    n_sem_resultado = df["snippets"].str.startswith("[SEM RESULTADO").sum()
    print(f"[Sanity check] {len(df)} escolas processadas em {duracao:.1f}s "
          f"({len(df) / max(duracao, 0.01):.1f} escolas/s)")
    print(f"[Sanity check] Erros de busca: {n_erro} | Sem resultado orgânico: {n_sem_resultado}")

    saida = OUT_DIR / "20_snippets_para_classificar.csv"
    if limite:
        # Rodada de teste — nunca sobrescreve o CSV consolidado, só mostra na tela.
        print("[Info] Rodada de teste (--limite): CSV final não sobrescrito. Amostra:")
        print(df.to_string())
    else:
        df.to_csv(saida, index=False, sep=";", decimal=",", encoding="utf-8")
        print(f"[✓] Salvo em {saida}")


if __name__ == "__main__":
    import sys

    limite_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limite=limite_arg)
