"""
Case Poliedro — Passo 29 (pedido do Gui, 30/07): UNIVERSO COMPLETO PARA POWER BI
(3ª página do dashboard — "explorador de mercado").

Por que este passo existe: as páginas 1 e 2 do Power BI (`14_escolas_powerbi.csv`)
só mostram as 2.144 escolas já classificadas como alvo comercial (Poliedro ou
Polígono). Isso esconde do time comercial o resto do mercado — pedido
concreto do Gui: "uma aba mais abrangente pra pesquisar as escolas em Santos
(não apenas Golden Leads) [...] 'nosso parceiro é o 2º colocado, mas podemos
expandir pra essa outra escola que fica bem distante e tem números
razoáveis'". Esse tipo de decisão exige ver TODAS as escolas confiáveis da
cidade, não só as que já passaram no corte de score.

Universo usado: as 4.444 escolas de `25_produto_alvo.csv` — mesmo universo
nacional de `funil_escolas_pontuadas.csv` filtrado por ENEM confiável
(>=10 participantes) e sem Sistema S (SESI/SENAI/SESC/SENAC), a mesma base
que os passos 09/25 já usam. Escolas SEM ENEM confiável (participação baixa
demais pra um score estável) ficam de fora — mesma limitação de sempre,
não é dado faltando, é dado que não dá pra confiar no score.

`rank_municipio`/`segmento_comercial` são recalculados aqui sobre O UNIVERSO
INTEIRO (não só sobre quem já é Golden Lead/Polígono) — é isso que permite
enxergar, por ex., que a 5ª colocada de uma cidade tem porte e nota
razoáveis mesmo sem ainda ter sido classificada como produto_alvo. Mesma
lógica de tag do passo 09 (`poliedro_09_icp_poliedro.py`), só que sem o corte
`score_destaque >= 0.70` antes de aplicar a tag.

LIMITAÇÃO IMPORTANTE (deixar explícita pro time comercial): a pesquisa manual
de sistema de ensino (passo 19) só cobriu as 1.127 Golden Leads originais.
Para as ~3.317 escolas que só aparecem nesta 3ª página (fora do recorte
Poliedro/Polígono), `sistema_ensino_identificado` vem como "Fora do escopo da
pesquisa (passo 19)" — não pesquisamos essas ainda, é diferente de "Não
pesquisado ainda" (que aqui fica reservado só pras 1.017 escolas Polígono,
que JÁ estavam no escopo mas não foram priorizadas na pesquisa manual).

Revisão 30/07 (pedido do Gui): este arquivo passa a ser a FONTE ÚNICA tanto da
página 1 (Sistema Poliedro) quanto da página 3 (explorador geral) — antes, a
página 1 usava `14_escolas_powerbi.csv`, que estruturalmente NUNCA poderia
mostrar o "ranking real" de uma cidade porque só contém as escolas já
classificadas Poliedro/Polígono (as `nenhum` nem existem naquele arquivo).
Com as duas páginas lendo este arquivo, a página 1 aplica um FILTRO
DESTRAVADO (slicer, não filtro de página fixo) com `produto_alvo = Poliedro`
pré-selecionado — o usuário pode marcar "Selecionar tudo" no próprio slicer
pra ver o ranking completo da cidade sem trocar de página.

Também adicionados nesta revisão (pedido do Gui):
- ENEM 2024 + `delta_enem_2025_2024` + `enem_media_2anos` (mesma lógica do
  passo 28, agora pro universo inteiro — 90% de cobertura).
- `distancia_parceiro_atual_km` + `nome_parceiro_mais_proximo`: distância
  (haversine, mesmo método do passo 24) de CADA escola até o cliente/parceiro
  Poliedro mais próximo na mesma cidade — generalizado do passo 24 (que só
  cobria os prospects de Poliedro+Polígono) pro universo inteiro, com
  auto-exclusão pra quem já é o próprio parceiro. Custo: ~5s pra rodar as
  4.444 linhas nacionais, tudo local (numpy/pandas, sem chamada de API) —
  praticamente gratuito.

Gera: data/outputs/29_universo_completo_powerbi.csv
Formato do CSV: separador ';' e decimal ',' (padrão brasileiro, igual ao 14).
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from poliedro_filtros import remover_sistema_s
from poliedro_14_consolidar_dataset_powerbi import (
    CORRECOES_BAIRRO_RJ,
    carregar_renda_ibge,
    casar_renda_por_escola,
    categorizar_renda,
    normalizar_nome,
)

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

MIN_ESCOLAS_CONFIAVEIS_PARA_RANK = 3

# --- Normalização de sistema_ensino_identificado (pedido do Gui, 31/07) -----
# `poliedro_19` guarda o texto LIVRE que a pesquisa manual escreveu — 320
# strings distintas pra ~1.128 registros, cheias de duplicata (ex.: "Anglo",
# "Anglo (Cogna/SOMOS)" e "Sistema Anglo de Ensino" são o MESMO sistema).
# Esta função consolida pro Power BI SEM tocar em `poliedro_19` (o texto cru
# e a fonte da pesquisa continuam intactos lá — normalização é só de exibição
# pra este dataset). Regra escolhida com o Gui:
#   - confianca "provavel_proprio" -> sempre "Próprio / material autoral"
#     (é a inferência de que a escola não usa sistema de terceiro; não
#     importa qual grupo/mantenedora, pro filtro comercial o que importa é
#     "não tem sistema licenciado pra derrubar" ou não).
#   - confianca "nao_identificado" -> "Não identificado" (pesquisa rodou e
#     não achou sinal nem pra confirmar nem pra inferir — DIFERENTE de
#     "próprio", que é uma inferência positiva de que não há sistema).
#   - confianca "confirmado" -> nome do sistema, com as variações de grafia
#     e sufixo (Cogna/SOMOS, Arco Educação etc.) unificadas na marca certa.
# Achado ao construir isto: ~15 registros dizem "próprio (Sistema X de
# Ensino)" com um NOME de sistema dentro do parêntese (CEV, GGE, Pentágono,
# COPE, Bionatus, Tamandaré, Arbos, Gabarito...) — ou seja, o texto já cita
# um sistema regional real, só que embrulhado com o prefixo "próprio" por
# quem pesquisou. Colapsar esses pro bucket genérico apagaria um nome de
# concorrente de verdade. Regra: se o parêntese contém a palavra "Sistema"
# seguida de nome próprio, mantém o nome extraído; só cai em "Próprio /
# material autoral" quando o parêntese descreve grupo/rede/pedagogia sem
# nomear um sistema comercial.
_SISTEMA_OVERRIDES_EXATOS = {
    "Sistema de Ensino Poliedro (Ensino Médio) + Sistema Positivo (Infantil/Fundamental)":
        "Poliedro (EM) + Positivo (Infantil/Fund.)",
    # "Ari de Sá" e "SAS" são a MESMA marca (achado do Gui, 05/08): a própria
    # família Ari de Sá criou o "SAS = Sistema Ari de Sá", hoje operado pelo
    # Grupo Arco Educação — não são dois sistemas concorrentes, é um só.
    "SAS (Sistema Ari de Sá)": "SAS (Arco Educação)",
    "próprio (Olimpo Educação)": "Olimpo Educação",
    "próprio (Olimpo Educação, Coleção Zeus)": "Olimpo Educação",
    "próprio (Coleção Zeus, Olimpo Educação)": "Olimpo Educação",
    "próprio (marca/sistema Olimpo)": "Olimpo Educação",
    "próprio (Elite Rede de Ensino, Kit Pedagógico próprio)": "Elite (Rede/Sistema de Ensino)",
    "Sistema Elite de Ensino": "Elite (Rede/Sistema de Ensino)",
    "Somos Educação (marca não especificada)": "SOMOS Educação (marca não especificada)",
    # falsos-positivos do heurístico "contém 'Sistema'" — são pedagogia/holding,
    # não sistema apostilado comercial que a escola compra de terceiro:
    "próprio (Rede Salesiana, Sistema Preventivo de Dom Bosco)": "Próprio / material autoral",
    "próprio (SEB - Sistema Educacional Brasileiro)": "Próprio / material autoral",
    # variações de grafia do mesmo sistema regional (GGE):
    "próprio (Sistema GGE de Ensino)": "GGE",
    "Sistema GGE de Ensino": "GGE",
    "Sistema GGE de Ensino (mantido pela Rede Divina Providência)": "GGE",
    "próprio (Sistema GGE — Coleção Mundus)": "GGE",
    # Pesquisa 05/08 (pedido do Gui) — 2 casos que o heurístico "contém Sistema"
    # tinha extraído como se fossem sistema próprio/regional, mas são outra coisa:
    # 1) Colégio Pentágono (SP, códigos 35137133/35153163/35139497): Gui achou o
    #    CNPJ oficial (Instituto Pentágono de Educação) e a lista de material 2024
    #    (PDF oficial colegiopentagono.com) — livros avulsos de Atual/FTD/Moderna/
    #    Ática, não um sistema apostilado licenciado. Fazem simulado ENEM via
    #    Bernoulli, mas isso é só o simulado, não o material didático do dia a dia.
    #    NÃO confundir com o outro "Colégio Pentágono" do Rio (pentagono.g12.br,
    #    código 33075425), que já está corretamente separado como "SAS (Arco Educação)".
    "próprio (Sistema Pentágono)": "Livro didático avulso (múltiplas editoras)",
    # 2) "Sistema Ser" (código 35449143, Centro Educacional Vila Verde, Praia
    #    Grande/SP) — confirmado via ser.com.br: marca real da SOMOS/Cogna (usa
    #    conteúdo das editoras Ática/Scipione), uma das 6 marcas do grupo no
    #    mercado de SAE (Anglo, Maxi, SER, pH, Farias Brito, GEO). NÃO é o mesmo
    #    que "Colégio Ser" (rede com unidades em Taboão da Serra/Sorocaba/
    #    Campinas) — essa rede é apenas CLIENTE do sistema pH, coincidência de nome.
    "Sistema Ser": "SER (Cogna/SOMOS)",
    # Pesquisa 05/08 (pedido do Gui) — mais correções e padronização:
    # sistemas regionais próprios só tinham o prefixo "Sistema..." tirado do
    # texto de pesquisa; mantém cada um como marca distinta (não são a mesma
    # coisa, não viram "Próprio"), só remove o prefixo redundante.
    "próprio (Sistema CEV de Ensino)": "CEV",
    "próprio (Sistema Gabarito)": "Gabarito",
    "próprio (Sistema Educacional Escola Parque)": "Escola Parque",
    "próprio (Sistema Bionatus)": "Bionatus",
    "próprio (Sistema COPE)": "COPE",
    "próprio (Sistema Educacional Arbos)": "Arbos",
    "próprio (Sistema Educacional Dominicanas)": "Dominicanas",
    "Sistema de Ensino Estrela (Rede La Salle)": "Estrela (Rede La Salle)",
    # duplicatas por falta de sufixo/rede — mesma marca, unificar:
    "Marista": "Marista (FTD, rede fechada)",
    "Geekie One": "Geekie One (Arco Educação)",
    # instituição própria de uma escola/congregação só, sem vínculo comercial
    # de terceiros — cai no bucket genérico (pedido do Gui, 05/08):
    "Mãe de Deus (Rede ICM, próprio)": "Próprio / material autoral",
    "Mary Ward (material institucional)": "Próprio / material autoral",
    # "Educação por Princípios" (Colégio Shallon, Goiânia) é uma METODOLOGIA
    # pedagógica adotada por várias escolas cristãs independentes no Brasil,
    # não um sistema apostilado de uma empresa — não achei nenhum vendor por
    # trás dela na pesquisa (05/08); tratando como material próprio. Se você
    # tiver uma fonte melhor, me avisa que eu reverto.
    "Educação por Princípios (metodologia própria/franquia)": "Próprio / material autoral",
    # livros avulsos de editoras diferentes por matéria — não é sistema
    # apostilado único, é só compra de livro didático solto (pedido do Gui, 05/08):
    "FTD + Moderna/Santillana": "Livro didático avulso (múltiplas editoras)",
    "FTD + SM": "Livro didático avulso (múltiplas editoras)",
}

# (padrão a procurar, nome canônico) — primeiro que bater vence.
_SISTEMA_REGRAS = [
    (r"anglo", "Anglo (Cogna/SOMOS)"),
    (r"bernoulli", "Bernoulli"),
    (r"positivo", "Positivo (Arco Educação)"),
    (r"objetivo", "Objetivo"),
    (r"farias brito", "Farias Brito (SFB)"),
    (r"\betapa\b", "Etapa"),
    (r"eleva", "Eleva"),
    (r"\bmaxi\b", "Maxi (Cogna/SOMOS)"),
    (r"pol[íi]gono", "Polígono"),
    (r"poliedro", "Poliedro"),
    (r"\bcoc\b", "COC (Arco Educação)"),
    (r"pit[áa]goras", "Pitágoras (Cogna/SOMOS)"),
    (r"sae digital|sae educa[çc][ãa]o", "SAE Digital (Cogna/SOMOS)"),
    (r"\bsas\b", "SAS (Arco Educação)"),
    (r"\bib\b|baccalaureate", "IB (International Baccalaureate)"),
    (r"livro did[áa]tico avulso", "Livro didático avulso (múltiplas editoras)"),
    (r"ecossistema az|plataforma az|\baz\b.*(seb|conexia)", "AZ (Grupo SEB/Conexia)"),
    # Pesquisa 05/08 (pedido do Gui): confirmar quais "Sistema X" residuais são
    # subsidiárias de grupo grande. Fontes: somoseducacao.com.br/sistemaph.php
    # (pH) e abcdacomunicacao.com.br/amplia-... (Amplia nasceu como "Plataforma
    # Eleva" em 2014 e hoje é da SOMOS/Cogna) — ambas confirmadas via busca.
    (r"\bph\b", "pH (Cogna/SOMOS)"),
    (r"amplia", "Amplia (Cogna/SOMOS)"),
]


def normalizar_sistema_ensino(sistema: str, confianca: str) -> str:
    """Consolida o texto livre da pesquisa manual numa marca/status canônico (ver nota acima)."""
    if confianca == "provavel_proprio":
        return "Próprio / material autoral"
    if confianca == "nao_identificado":
        # Revisão 31/07 (pedido do Gui): unificado com o "nunca pesquisado" —
        # ver comentário na chamada desta função em montar_universo_completo().
        return "Pendente de pesquisa"
    if confianca != "confirmado" or not isinstance(sistema, str):
        return sistema  # linhas "não pesquisado"/"fora do escopo" (preenchidas depois) passam direto
    if sistema in _SISTEMA_OVERRIDES_EXATOS:
        return _SISTEMA_OVERRIDES_EXATOS[sistema]
    for padrao, canonico in _SISTEMA_REGRAS:
        if re.search(padrao, sistema, flags=re.IGNORECASE):
            return canonico
    if sistema.lower().startswith("confessional") or sistema.lower().startswith("próprio") or sistema.lower().startswith("proprio"):
        m = re.search(r"[Ss]istema\s+[A-ZÀ-Ý][\wÀ-ÿ]*(?:\s+[\wÀ-ÿ]+){0,4}", sistema)
        return m.group(0) if m else "Próprio / material autoral"
    return sistema


def carregar_universo_confiavel() -> pd.DataFrame:
    """Mesma base de poliedro_09/25: ENEM confiável, sem Sistema S, com erro explícito se faltar."""
    caminho = OUT_DIR / "funil_escolas_pontuadas.csv"
    try:
        df = pd.read_csv(caminho, dtype={"codigo_municipio": str})
    except FileNotFoundError:
        print(f"ERRO: não achei '{caminho}'. Rode `python poliedro_07_funil.py` antes deste passo.", file=sys.stderr)
        sys.exit(1)
    df = df[df["confiavel_enem"] == True].copy()  # noqa: E712
    df = remover_sistema_s(df)
    df["codigo_escola"] = df["codigo_escola"].astype(str)
    return df


def taggear_segmento_comercial(row) -> str:
    """Mesma tag do passo 09, aplicada ao universo INTEIRO (não só score>=0.70)."""
    if row["n_escolas_confiaveis_municipio"] < MIN_ESCOLAS_CONFIAVEIS_PARA_RANK:
        return "Sem comparação local (poucas escolas na cidade)"
    if row["rank_municipio"] == 1:
        return "Líder local"
    if 2 <= row["rank_municipio"] <= 5:
        return "Desafiante (2º-5º local)"
    return "Outras posições"


def montar_coluna_segmento_golden_lead(produto_alvo: pd.Series) -> pd.Series:
    """Marca 'Golden Leads (N)' pra escola com produto_alvo == 'Poliedro' (score_destaque >= 0,70,
    ver poliedro_25), em branco pras demais (pedido do Gui, 09/08, pra substituir os 2 bookmarks
    'Golden Leads'/'Outras Escolas' da página 1 — bookmark de página inteira dá erro/quebra
    silenciosamente, mesmo motivo documentado na faixa_rank_cidade da página 3).

    Por que só UM valor marcado (não 'Golden Leads' vs 'Outras Escolas' como 2 categorias): o
    Gui confirmou que quer manter o comportamento atual, em que 'Outras Escolas' não é o
    complemento de Golden Leads — é 'sem filtro nenhum', mostra o universo inteiro (4.444),
    Golden Leads incluídas. Um bloco de slicer selecionado sempre FILTRA pro valor clicado —
    não existe um valor de coluna que signifique 'mostra tudo'. Por isso o desenho final
    (pedido do Gui, 09/08) usa só 1 valor marcado e o botão de "desligar o filtro" é o ícone
    nativo de limpar seleção do próprio slicer do Power BI (Formatar visual > Cabeçalho do
    segmentador de dados > Ícone de limpar seleção) — não é bookmark, é recurso nativo do slicer.

    O '(N)' vem embutido no VALOR da coluna (não é medida DAX) — mesmo padrão do resto do
    pipeline: cada rodada do script recalcula o texto com a contagem real daquele momento, sem
    precisar editar rótulo de botão manualmente feito no Power BI Desktop."""
    total_golden = int((produto_alvo == "Poliedro").sum())
    rotulo = f"Golden Leads ({total_golden:,})".replace(",", ".")
    return produto_alvo.apply(lambda p: rotulo if p == "Poliedro" else None)


def classificar_faixa_rank_cidade(rank_municipio: int) -> str:
    """Agrupa rank_municipio em 3 faixas (pedido do Gui, 07/08) pro slicer em Bloco da página 3 —
    rank_municipio é numérico contínuo (1, 2, 3...) e não dá pra segmentar direto em Blocos com
    sentido de negócio; esta coluna existe só pra isso, não é usada em nenhum score."""
    if rank_municipio <= 5:
        return "Top 5"
    if rank_municipio <= 10:
        return "Top 10"
    return "Demais escolas"


def montar_universo_completo() -> pd.DataFrame:
    escolas = carregar_universo_confiavel()

    # 1. Flag de rede própria (mesma regra do passo 09 — nome contém "POLIEDRO").
    escolas["rede_propria_poliedro"] = escolas["NO_ENTIDADE"].str.contains("POLIEDRO", case=False, na=False)

    # 2. Rank e segmento comercial sobre o universo INTEIRO da cidade.
    escolas["rank_municipio"] = escolas.groupby("codigo_municipio")["score_destaque"].rank(
        method="first", ascending=False
    ).astype(int)
    escolas["n_escolas_confiaveis_municipio"] = escolas.groupby("codigo_municipio")["codigo_municipio"].transform("count")
    escolas["segmento_comercial"] = escolas.apply(taggear_segmento_comercial, axis=1)
    escolas["faixa_rank_cidade"] = escolas["rank_municipio"].apply(classificar_faixa_rank_cidade)

    # 3. produto_alvo — reaproveita o passo 25 em vez de duplicar a regra de corte.
    produto = pd.read_csv(OUT_DIR / "25_produto_alvo.csv", sep=";", decimal=",", dtype={"codigo_escola": str})[
        ["codigo_escola", "produto_alvo"]
    ]
    escolas = escolas.merge(produto, on="codigo_escola", how="left")
    escolas["produto_alvo"] = escolas["produto_alvo"].fillna("nenhum")
    escolas["segmento_golden_lead"] = montar_coluna_segmento_golden_lead(escolas["produto_alvo"])

    # 4. Cidade/UF.
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})[
        ["codigo_municipio", "nome_municipio_ibge", "uf", "score_priorizacao"]
    ]
    escolas = escolas.merge(cidades, on="codigo_municipio", how="left")
    escolas = escolas.rename(columns={"nome_municipio_ibge": "cidade", "uf": "UF", "score_priorizacao": "score_priorizacao_cidade"})

    # 5. Geo/bairro/distrito/lat-long (mesma fonte do passo 14).
    geo = pd.read_csv(RAW_DIR / "escolas_com_endereco_ampliado.csv", dtype={"codigo_municipio": str, "CO_ENTIDADE": str})[
        ["CO_ENTIDADE", "NO_BAIRRO", "NO_DISTRITO", "LATITUDE", "LONGITUDE", "CO_CEP", "DS_ENDERECO", "NU_ENDERECO"]
    ].rename(columns={"CO_ENTIDADE": "codigo_escola"})
    escolas = escolas.merge(geo, on="codigo_escola", how="left")
    escolas["bairro"] = escolas["NO_BAIRRO"].replace(CORRECOES_BAIRRO_RJ)
    escolas = escolas.rename(columns={"NO_DISTRITO": "distrito", "CO_CEP": "cep"})
    escolas = escolas.drop(columns=["NO_BAIRRO"])
    escolas["cep"] = escolas["cep"].astype("Int64")
    # Endereço legível pro tooltip do mapa (pedido do Gui, 31/07) — substitui a
    # exibição de LATITUDE/LONGITUDE cru, que só polui a legenda sem ajudar o
    # time comercial a localizar a escola de verdade.
    cep_fmt = escolas["cep"].apply(lambda c: f"{c:08d}"[:5] + "-" + f"{c:08d}"[5:] if pd.notna(c) else "")
    escolas["endereco_completo"] = (
        escolas["DS_ENDERECO"].fillna("").str.strip()
        + escolas["NU_ENDERECO"].apply(lambda n: f", {str(n).strip()}" if pd.notna(n) and str(n).strip() else "")
        + escolas["bairro"].apply(lambda b: f" - {b}" if pd.notna(b) and b else "")
        + cep_fmt.apply(lambda c: f" - CEP {c}" if c else "")
    ).str.strip(" -")
    escolas.loc[escolas["DS_ENDERECO"].isna() | (escolas["DS_ENDERECO"].str.strip() == ""), "endereco_completo"] = pd.NA
    escolas = escolas.drop(columns=["DS_ENDERECO", "NU_ENDERECO"])
    escolas["granularidade_geo"] = escolas["cidade"].map(
        {"São Paulo": "distrito", "Rio de Janeiro": "bairro"}
    ).fillna("nao_aplicavel")

    # 6. Renda por bairro/distrito (mesma lógica do passo 14 — quartis reais IBGE Censo 2022).
    escolas["bairro_norm"] = escolas["bairro"].apply(normalizar_nome)
    escolas["distrito_norm"] = escolas["distrito"].apply(normalizar_nome)
    renda_b, renda_d, cidades_com_bairro_ibge = carregar_renda_ibge()
    escolas["renda_mediana_responsavel"] = casar_renda_por_escola(escolas, renda_b, renda_d, cidades_com_bairro_ibge)
    escolas["renda_categoria"] = escolas["renda_mediana_responsavel"].apply(categorizar_renda)
    escolas = escolas.drop(columns=["bairro_norm", "distrito_norm"])

    # 7. Sistema de ensino identificado — SÓ existe pesquisa manual pras 1.127 Golden Leads originais.
    #    IMPORTANTE: aqui distinguimos "não pesquisado ainda" (estava no escopo, passo 19, mas não
    #    priorizado) de "fora do escopo da pesquisa" (nunca fez parte da lista de 2.144 do passo 19/14).
    sistema = pd.read_csv(OUT_DIR / "19_sistema_ensino_identificado.csv", sep=";", decimal=",", dtype={"codigo_escola": str})[
        ["codigo_escola", "sistema_ensino_identificado", "confianca"]
    ]
    escolas = escolas.merge(sistema, on="codigo_escola", how="left")
    escolas["sistema_ensino_identificado"] = escolas.apply(
        lambda r: normalizar_sistema_ensino(r["sistema_ensino_identificado"], r["confianca"]), axis=1
    )
    no_escopo_pesquisa_19 = escolas["produto_alvo"].isin(["Poliedro", "Polígono"])
    # Revisão 31/07 (pedido do Gui): unificar "nunca pesquisado" e "pesquisou e
    # não achou" num único rótulo "Pendente de pesquisa" — a ideia agora é o
    # time comercial ir preenchendo essa planilha manualmente conforme for
    # prospectando, então não importa comercialmente SE já tentou antes; o
    # que importa é "ainda não tem resposta". `confianca` continua guardando
    # o histórico técnico (nao_identificado/nao_pesquisado) pra quem quiser
    # a distinção depois — só a coluna de exibição principal foi unificada.
    escolas.loc[no_escopo_pesquisa_19 & escolas["sistema_ensino_identificado"].isna(), "sistema_ensino_identificado"] = "Pendente de pesquisa"
    escolas.loc[no_escopo_pesquisa_19 & escolas["confianca"].isna(), "confianca"] = "nao_pesquisado"
    escolas["sistema_ensino_identificado"] = escolas["sistema_ensino_identificado"].fillna("Fora do escopo da pesquisa")
    escolas["confianca"] = escolas["confianca"].fillna("fora_do_escopo")

    # 7b. Achados avulsos de fora do escopo original (passo 19, revisão 30/07) — escolas que o
    #     Gui pesquisou por conta própria explorando esta 3ª página. Sobrescreve o valor padrão
    #     "Fora do escopo da pesquisa" só pras escolas que já têm achado registrado.
    caminho_fora_escopo = OUT_DIR / "19b_sistema_ensino_fora_do_escopo.csv"
    if caminho_fora_escopo.exists():
        fora_escopo = pd.read_csv(caminho_fora_escopo, sep=";", decimal=",", dtype={"codigo_escola": str})
        fora_escopo = fora_escopo.set_index("codigo_escola")
        escolas = escolas.set_index("codigo_escola")
        escolas.update(fora_escopo[["sistema_ensino_identificado", "confianca"]])
        escolas = escolas.reset_index()
        n_achados = fora_escopo.index.isin(escolas["codigo_escola"]).sum()
        print(f"[Achados fora do escopo] {n_achados} escola(s) de '{caminho_fora_escopo.name}' aplicada(s).")
        # Achado (05/08, Gui: "próprio (SIELP) 1 (0,09%)" aparecendo isolado no
        # donut): o update acima injeta o texto CRU do 19b sem repassar por
        # normalizar_sistema_ensino() — qualquer achado "próprio (X)" das ~89
        # escolas fora do escopo (SIELP, Harmonia, Bom Jesus etc.) escapava da
        # normalização e virava fatia isolada em vez de cair em "Próprio /
        # material autoral". Reaplicar a normalização aqui é idempotente pras
        # linhas que já vieram certas do passo 19 (mesma regra, mesmo valor).
        escolas["sistema_ensino_identificado"] = escolas.apply(
            lambda r: normalizar_sistema_ensino(r["sistema_ensino_identificado"], r["confianca"]), axis=1
        )

    escolas["ja_cliente_poliedro_qualquer_marca"] = (
        escolas["rede_propria_poliedro"].fillna(False)
        | escolas["sistema_ensino_identificado"].str.contains("Poliedro", na=False)
    )

    # Coluna de EXIBIÇÃO só pro slicer (pedido do Gui, 05/08): Power BI não deixa
    # customizar o texto de formato de uma coluna True/false (só oferece o preset
    # "True/false" no dropdown) — a única forma de trocar por "Sim"/"Não" é ter uma
    # coluna de texto separada. Mantemos a booleana intacta (bookmarks e filtros
    # já configurados nela continuam funcionando); troque só o CAMPO DO SLICER pra
    # esta coluna nova no Power BI Desktop.
    escolas["ja_cliente_poliedro_sim_nao"] = escolas["ja_cliente_poliedro_qualquer_marca"].map(
        {True: "Sim", False: "Não"}
    )

    # 7c. Versão "Top N + Outros" pra gráfico de pizza/rosca (pedido do Gui, 31/07):
    # o campo bruto tem ~56 valores distintos — não cabe legível num donut. Aqui
    # agrupamos só entre os sistemas CONFIRMADOS (57 confianca="confirmado"); os
    # 2 status "Pendente de pesquisa" e "Fora do escopo da pesquisa" NÃO entram no
    # corte — ficam como estão, porque misturar "sistema minoritário confirmado"
    # com "não sabemos ainda" no mesmo balde "Outros" confundiria o time comercial.
    LIMIAR_SISTEMA_ENSINO_GRAFICO = 25  # teste com 10 deu 15 fatias — ainda cheio; 25 bate com o mockup (~8-9 fatias)
    confirmados = escolas.loc[escolas["confianca"] == "confirmado", "sistema_ensino_identificado"]
    contagem = confirmados.value_counts()
    sistemas_grandes = set(contagem[contagem >= LIMIAR_SISTEMA_ENSINO_GRAFICO].index)
    escolas["sistema_ensino_top_outros"] = escolas["sistema_ensino_identificado"].where(
        (escolas["confianca"] != "confirmado") | escolas["sistema_ensino_identificado"].isin(sistemas_grandes),
        "Outros (sistema minoritário)",
    )

    # 8. ENEM 2024 + delta + média de 2 anos (pedido do Gui, 30/07) — mesma lógica do
    #    passo 28, generalizada pro universo inteiro (lá só cobria as 2.144 já classificadas).
    escolas = acoplar_enem_2024(escolas)

    # 9. Distância até o parceiro/cliente Poliedro (qualquer marca) mais próximo NA MESMA
    #    cidade — pedido do Gui, 30/07: "distância segura do nosso parceiro atual" como
    #    critério de decisão. Mesma lógica/haversine do passo 24, generalizada pra TODAS as
    #    escolas (não só os prospects de Poliedro+Polígono) e com auto-exclusão (um parceiro
    #    não conta distância até si mesmo). Custo computacional é baixíssimo — é
    #    groupby+haversine local em ~4.400 linhas, sem chamada de API nenhuma.
    escolas = calcular_distancia_parceiro_mais_proximo(escolas)

    escolas["score_destaque"] = escolas["score_destaque"].round(3)

    # 10. Chave de junção com 16_regioes_sp_rj_com_renda (pedido do Gui, 06/08: sincronizar
    #     a segmentação SP/RJ do dashboard entre a tabela de escolas e a tabela de regiões,
    #     hoje sem relacionamento nenhum no modelo). `regiao`/`chave_regiao` só existem pra
    #     São Paulo (usa `distrito`) e Rio de Janeiro (usa `bairro`) — a tabela 16 só cobre
    #     essas 2 cidades, então preencher `regiao` com `bairro` bruto de QUALQUER cidade
    #     (bug da 1ª versão: usava `.where(cidade=="São Paulo", bairro)`, que pega o bairro de
    #     TODAS as outras ~300 cidades também) geraria 2.264 chaves que nunca vão casar com
    #     nada — ruído, não sinal. Fica NaN fora de SP/RJ de propósito.
    escolas["regiao"] = pd.NA
    escolas.loc[escolas["cidade"] == "São Paulo", "regiao"] = escolas.loc[escolas["cidade"] == "São Paulo", "distrito"]
    escolas.loc[escolas["cidade"] == "Rio de Janeiro", "regiao"] = escolas.loc[escolas["cidade"] == "Rio de Janeiro", "bairro"]
    escolas["chave_regiao"] = escolas["cidade"].str.cat(escolas["regiao"], sep="|")

    # Tabela enxuta pro Power BI — mesmo espírito da Seção 10 do POWER_BI_GUIA.md
    # (cada coluna a mais é ruído pra quem só quer decidir rápido). As colunas cruas
    # do Censo (auditório, biblioteca etc., herdadas de funil_escolas_pontuadas.csv)
    # ficam de fora daqui; quem precisar delas usa o arquivo de origem.
    colunas_finais = [
        "codigo_escola", "NO_ENTIDADE", "codigo_municipio", "cidade", "UF",
        "segmento_comercial", "produto_alvo", "rank_municipio", "n_escolas_confiaveis_municipio",
        "score_destaque", "enem_media_geral", "qtd_participantes_enem", "QT_MAT_MED", "indice_infra",
        "rede_propria_poliedro", "ja_cliente_poliedro_qualquer_marca",
        "sistema_ensino_identificado", "confianca",
        "bairro", "distrito", "regiao", "chave_regiao", "granularidade_geo", "LATITUDE", "LONGITUDE", "cep", "endereco_completo",
        "renda_mediana_responsavel", "renda_categoria", "score_priorizacao_cidade",
        "distancia_parceiro_atual_km", "nome_parceiro_mais_proximo",
    ]
    for opcional in ["enem_media_geral_2024", "qtd_participantes_enem_2024",
                      "enem_media_2anos", "delta_enem_2025_2024"]:
        if opcional in escolas.columns:
            colunas_finais.append(opcional)
    colunas_finais.append("sistema_ensino_top_outros")  # sempre no fim — nunca insira coluna nova no meio (ver guia)
    colunas_finais.append("ja_cliente_poliedro_sim_nao")
    colunas_finais.append("faixa_rank_cidade")
    colunas_finais.append("segmento_golden_lead")
    return escolas[colunas_finais]


def acoplar_enem_2024(escolas: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta ENEM 2024 + média de 2 anos, se o passo 27 já rodou (mesma lógica do passo 28)."""
    caminho = RAW_DIR / "enem_2024_medias_por_escola.csv"
    if not caminho.exists():
        print(f"[Aviso] '{caminho}' não encontrado — rode `python poliedro_27_extrair_enem_2024.py` "
              "pra habilitar a comparação entre anos. Seguindo só com 2025.")
        return escolas
    enem24 = pd.read_csv(caminho, dtype={"codigo_escola": str})
    escolas = escolas.merge(enem24, on="codigo_escola", how="left")
    peso_2025 = escolas["qtd_participantes_enem"].fillna(0)
    peso_2024 = escolas["qtd_participantes_enem_2024"].fillna(0)
    soma_pesos = peso_2025 + peso_2024
    escolas["enem_media_2anos"] = (
        escolas["enem_media_geral"].fillna(0) * peso_2025
        + escolas["enem_media_geral_2024"].fillna(0) * peso_2024
    ) / soma_pesos.where(soma_pesos > 0)
    escolas["delta_enem_2025_2024"] = escolas["enem_media_geral"] - escolas["enem_media_geral_2024"]
    return escolas


def _haversine_km(lat1, lon1, lat2, lon2):
    """Distância em linha reta (km) entre um ponto e um vetor de pontos."""
    raio_terra_km = 6371.0
    lat1_rad, lat2_rad = np.radians(lat1), np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2
    return 2 * raio_terra_km * np.arcsin(np.sqrt(a))


def calcular_distancia_parceiro_mais_proximo(escolas: pd.DataFrame) -> pd.DataFrame:
    """Pra cada escola, distância até o cliente/parceiro Poliedro (qualquer marca) mais
    próximo NA MESMA cidade — mesmo método do passo 24 (haversine, só dentro do município),
    generalizado pra todas as 4.444 linhas, com auto-exclusão pra quem já é parceiro."""
    tem_coord = escolas["LATITUDE"].notna() & escolas["LONGITUDE"].notna()
    parceiros = escolas[escolas["ja_cliente_poliedro_qualquer_marca"] & tem_coord]

    distancias = pd.Series(np.nan, index=escolas.index)
    nomes = pd.Series(pd.NA, index=escolas.index, dtype="object")

    for codigo_municipio, grupo_parceiros in parceiros.groupby("codigo_municipio"):
        candidatas = escolas[(escolas["codigo_municipio"] == codigo_municipio) & tem_coord]
        for idx, escola in candidatas.iterrows():
            # Auto-exclusão: um parceiro não mede distância até si mesmo.
            outros_parceiros = grupo_parceiros[grupo_parceiros["codigo_escola"] != escola["codigo_escola"]]
            if len(outros_parceiros) == 0:
                continue
            d = _haversine_km(
                escola["LATITUDE"], escola["LONGITUDE"],
                outros_parceiros["LATITUDE"].values, outros_parceiros["LONGITUDE"].values,
            )
            i_mais_proximo = int(np.argmin(d))
            distancias[idx] = round(float(d[i_mais_proximo]), 2)
            nomes[idx] = outros_parceiros.iloc[i_mais_proximo]["NO_ENTIDADE"]

    escolas["distancia_parceiro_atual_km"] = distancias
    escolas["nome_parceiro_mais_proximo"] = nomes
    return escolas


def exibir_resumo(escolas: pd.DataFrame) -> None:
    print(f"[Sanity check] Total no universo completo: {len(escolas):,}")
    print(f"[Sanity check] Distribuição produto_alvo:\n{escolas['produto_alvo'].value_counts()}")
    print(f"[Sanity check] Distribuição segmento_comercial:\n{escolas['segmento_comercial'].value_counts()}")
    print(f"[Sanity check] Distribuição faixa_rank_cidade:\n{escolas['faixa_rank_cidade'].value_counts()}")
    golden = escolas["segmento_golden_lead"].notna().sum()
    print(f"[Sanity check] Golden Leads (segmento_golden_lead não-nulo): {golden:,} de {len(escolas):,} "
          f"— rótulo atual: '{escolas['segmento_golden_lead'].dropna().iloc[0] if golden else 'N/A'}' "
          f"(deve bater com produto_alvo == 'Poliedro': {(escolas['produto_alvo'] == 'Poliedro').sum():,})")
    print(f"[Sanity check] Escolas com bairro: {escolas['bairro'].notna().sum():,} "
          f"({escolas['bairro'].notna().mean() * 100:.1f}%)")
    print(f"[Sanity check] Escolas com renda encontrada: {escolas['renda_mediana_responsavel'].notna().sum():,} "
          f"({escolas['renda_mediana_responsavel'].notna().mean() * 100:.1f}%)")
    pesquisadas = (~escolas["sistema_ensino_identificado"].isin(
        ["Pendente de pesquisa", "Fora do escopo da pesquisa"]
    )).sum()
    print(f"[Sanity check] Escolas com sistema de ensino pesquisado: {pesquisadas:,} "
          f"({pesquisadas / len(escolas) * 100:.1f}%) — as demais são só as fora do recorte Poliedro/Polígono, "
          f"ver limitação no docstring.")
    print(f"[Sanity check] score_destaque: min={escolas['score_destaque'].min():.3f}, "
          f"média={escolas['score_destaque'].mean():.3f}, max={escolas['score_destaque'].max():.3f}")
    santos = escolas[escolas["cidade"] == "Santos"]
    if len(santos):
        print(f"[Sanity check] Santos/SP: {len(santos)} escolas confiáveis no universo completo "
              f"(spot-check pedido pelo Gui).")
    if "enem_media_2anos" in escolas.columns:
        cobertura_2024 = escolas["enem_media_geral_2024"].notna().mean() * 100
        print(f"[Sanity check] Cobertura ENEM 2024: {cobertura_2024:.1f}%")
    com_dist = escolas["distancia_parceiro_atual_km"].notna()
    print(f"[Sanity check] Escolas com distância até parceiro calculada: {com_dist.sum():,} "
          f"({com_dist.mean() * 100:.1f}%) — as demais estão em cidades sem nenhum cliente/parceiro Poliedro ainda.")
    if com_dist.sum():
        d = escolas.loc[com_dist, "distancia_parceiro_atual_km"]
        print(f"[Sanity check] distancia_parceiro_atual_km — min {d.min():.2f} | mediana {d.median():.2f} | máx {d.max():.2f}")


def main():
    escolas = montar_universo_completo()
    exibir_resumo(escolas)
    escolas.to_csv(OUT_DIR / "29_universo_completo_powerbi.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '29_universo_completo_powerbi.csv'}")


if __name__ == "__main__":
    main()
