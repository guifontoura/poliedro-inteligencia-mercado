"""
Case Poliedro — Passo 26 (roadmap 3.0, pedido do Gui em 28/07): RANKING LOCAL
COM A POSIÇÃO DO PARCEIRO ATUAL.

Pergunta de negócio que este passo responde (formulada pelo Gui em 28/07):
"o nosso parceiro atual é a melhor escolha nessa região, ou deveríamos
prospectar outra escola?" — para levar aos diretores o ranking da praça com
a escola parceira do Poliedro visivelmente posicionada dentro dele.

Diferença crucial em relação ao passo 22: aqui NADA é excluído. O passo 22
tirava da lista quem já era cliente (faz sentido pra montar lista de
prospecção). Aqui é o contrário — a escola parceira PRECISA aparecer, com a
posição real dela, senão a pergunta acima fica sem resposta. Mesma lógica
aplicada ao risco de canibalização no passo 24: sinaliza, não remove.

Método: para cada município onde o Poliedro tem ao menos uma escola parceira
(ou unidade própria), rankeia todas as escolas privadas com ENEM confiável
daquele município por `score_destaque` e marca:
  - `eh_parceiro_poliedro`  — escola já usa Sistema Poliedro (qualquer marca)
  - `eh_unidade_propria`    — escola é unidade da própria rede Poliedro
  - `posicao_local`         — posição no ranking do município (1 = líder)

Leitura sugerida: parceiro em posição 1-2 = praça bem representada; parceiro
em posição 5+ com escolas fortes acima = candidato a revisão (reforçar a
parceria atual ou prospectar uma escola melhor colocada). A decisão é
comercial e humana — este arquivo só expõe o dado pra ela.

Entrada:  data/outputs/14_escolas_powerbi.csv (flags de parceria)
          data/outputs/funil_escolas_pontuadas.csv (universo local completo)
Gera:     data/outputs/26_ranking_local_parceiro.csv
"""

import sys
import pandas as pd

from poliedro_filtros import remover_sistema_s

CAMINHO_LEADS = "data/outputs/14_escolas_powerbi.csv"
CAMINHO_FUNIL = "data/outputs/funil_escolas_pontuadas.csv"
CAMINHO_SAIDA = "data/outputs/26_ranking_local_parceiro.csv"

TOP_N_POR_CIDADE = 10


def carregar_arquivo(caminho, passo_anterior, **kwargs):
    """Lê um CSV do pipeline apontando qual passo gerar caso ele não exista."""
    try:
        return pd.read_csv(caminho, **kwargs)
    except FileNotFoundError:
        print(
            f"ERRO: não achei '{caminho}'. Rode `python {passo_anterior}` antes deste passo.",
            file=sys.stderr,
        )
        sys.exit(1)


def mapear_parcerias(leads):
    """Monta os conjuntos de códigos de escola parceira e de unidade própria."""
    eh_cliente = leads["ja_cliente_poliedro_qualquer_marca"] == True  # noqa: E712
    eh_propria = leads["rede_propria_poliedro"] == True  # noqa: E712
    parceiros = set(leads[eh_cliente]["codigo_escola"])
    proprias = set(leads[eh_propria]["codigo_escola"])
    return parceiros, proprias


def montar_ranking_por_cidade(confiaveis, leads, parceiros, proprias):
    """Rankeia as escolas de cada município que tem parceria Poliedro."""
    municipios_com_parceria = sorted(
        set(leads[leads["codigo_escola"].isin(parceiros)]["codigo_municipio"])
    )
    nome_cidade = leads.drop_duplicates("codigo_municipio").set_index("codigo_municipio")
    linhas = []
    for codigo_municipio in municipios_com_parceria:
        local = confiaveis[confiaveis["codigo_municipio"] == codigo_municipio].copy()
        if local.empty:
            continue
        local = local.sort_values("score_destaque", ascending=False).reset_index(drop=True)
        local["posicao_local"] = local.index + 1
        total_local = len(local)

        posicoes_parceiros = local[local["codigo_escola"].isin(parceiros)][
            "posicao_local"
        ].tolist()
        melhor_posicao_parceiro = min(posicoes_parceiros) if posicoes_parceiros else None

        # mantém o Top N da cidade E qualquer parceiro que tenha ficado fora dele
        recorte = local[
            (local["posicao_local"] <= TOP_N_POR_CIDADE)
            | (local["codigo_escola"].isin(parceiros))
        ]
        for _, escola in recorte.iterrows():
            linhas.append(
                {
                    "cidade": nome_cidade.loc[codigo_municipio, "cidade"],
                    "UF": nome_cidade.loc[codigo_municipio, "UF"],
                    "posicao_local": escola["posicao_local"],
                    "total_escolas_cidade": total_local,
                    "NO_ENTIDADE": escola["NO_ENTIDADE"],
                    "codigo_escola": escola["codigo_escola"],
                    "score_destaque": escola["score_destaque"],
                    "enem_media_geral": round(escola["enem_media_geral"], 1),
                    "QT_MAT_MED": escola["QT_MAT_MED"],
                    "eh_parceiro_poliedro": escola["codigo_escola"] in parceiros,
                    "eh_unidade_propria": escola["codigo_escola"] in proprias,
                    "melhor_posicao_parceiro_na_cidade": melhor_posicao_parceiro,
                }
            )
    return pd.DataFrame(linhas)


def main():
    leads = carregar_arquivo(
        CAMINHO_LEADS, "poliedro_14_consolidar_dataset_powerbi.py", sep=";", decimal=","
    )
    escolas = carregar_arquivo(CAMINHO_FUNIL, "poliedro_05b_score_destaque_nacional.py")
    confiaveis = escolas[escolas["confiavel_enem"] == True].copy()  # noqa: E712
    # Escopo do projeto: o ranking da praça é de escolas privadas que são
    # prospect. Sistema S sai — senão uma escola SESI ocuparia posição no
    # ranking que vai pros diretores e distorceria a leitura de onde o
    # parceiro atual está colocado. Ver poliedro_filtros.py.
    confiaveis = remover_sistema_s(confiaveis)

    parceiros, proprias = mapear_parcerias(leads)
    print(f"Escolas parceiras (qualquer marca): {len(parceiros)} | unidades próprias: {len(proprias)}")

    ranking = montar_ranking_por_cidade(confiaveis, leads, parceiros, proprias)
    if ranking.empty:
        print("AVISO: nenhum município com parceria encontrado. Nada a gerar.")
        return

    ranking = ranking.sort_values(["cidade", "posicao_local"])
    ranking.to_csv(CAMINHO_SAIDA, sep=";", index=False)

    # --- resumo de sanidade ---
    print(f"\nGerado: {CAMINHO_SAIDA} ({len(ranking)} linhas)")
    print(f"Municípios com parceria mapeados: {ranking['cidade'].nunique()}")

    posicoes = (
        ranking[ranking["eh_parceiro_poliedro"]]
        .groupby("cidade")["posicao_local"]
        .min()
        .sort_values()
    )
    print(
        f"\nPosição do melhor parceiro por cidade — min {posicoes.min()} | "
        f"mediana {posicoes.median():.1f} | máx {posicoes.max()}"
    )
    print("\nDistribuição das cidades pela posição do melhor parceiro local:")
    faixas = pd.cut(
        posicoes,
        bins=[0, 1, 3, 5, 10, 10_000],
        labels=["líder (1º)", "2º-3º", "4º-5º", "6º-10º", "fora do top 10"],
    )
    print(faixas.value_counts().sort_index().to_string())
    print("\nCidades onde o parceiro está FORA do top 5 local (candidatas a revisão):")
    print(posicoes[posicoes > 5].to_string())


if __name__ == "__main__":
    main()
