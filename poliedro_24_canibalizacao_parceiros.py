"""
Case Poliedro — Passo 24 (roadmap 3.0, pedido do Gui em 28/07): RISCO DE
CANIBALIZAÇÃO ENTRE PARCEIROS — distância de cada lead até a escola PARCEIRA
mais próxima na mesma cidade.

Por que este passo existe (e por que o passo 18 não bastava): o
`poliedro_18` só mede distância até as 4 unidades PRÓPRIAS do Poliedro. Mas
desde 24/07 (Colégio Contato/Maceió) e 28/07 (mais 6 clientes ocultos
achados na pesquisa manual do Gui) sabemos que existem 39 escolas
clientes/parceiras do Sistema Poliedro sob marcas diferentes. Vender pro
vizinho de uma escola parceira tira aluno dela e derruba a chance de
renovação — o risco comercial é o mesmo do passo 18, com um agravante: ao
contrário da unidade própria, o parceiro pode simplesmente sair.

DECISÃO DE PRODUTO (Gui, 28/07): este script NÃO exclui nenhuma escola da
lista de prospecção. Ele apenas SINALIZA a distância. Motivo: o objetivo de
negócio aqui não é evitar a praça, é o oposto — são justamente as praças
onde o Poliedro já tem parceiro que interessam, porque a pergunta que a
direção quer responder é "o nosso parceiro atual é a melhor escolha nessa
região, ou deveríamos trocar?". Excluir por proximidade apagaria exatamente
o dado necessário pra responder isso. O corte por raio (ex.: 2km) é decisão
de política comercial do Poliedro e pode ser aplicado depois, a jusante,
filtrando a coluna `distancia_km`.

Método: haversine (linha reta), só dentro do MESMO município — mesma escolha
do passo 18, com as mesmas limitações (subestima distância real de trajeto
em cidade com relevo, rio ou via tortuosa).

Entrada:  data/outputs/14_escolas_powerbi.csv
Gera:     data/outputs/24_canibalizacao_parceiros.csv
"""

import sys
import numpy as np
import pandas as pd

CAMINHO_LEADS = "data/outputs/14_escolas_powerbi.csv"
CAMINHO_SAIDA = "data/outputs/24_canibalizacao_parceiros.csv"


def calcular_distancia_km(lat1, lon1, lat2, lon2):
    """Distância de haversine em km entre um ponto e um vetor de pontos."""
    raio_terra_km = 6371.0
    lat1_rad, lat2_rad = np.radians(lat1), np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2
    )
    return 2 * raio_terra_km * np.arcsin(np.sqrt(a))


def carregar_leads(caminho):
    """Lê o dataset consolidado de Golden Leads, com tratamento de erro claro."""
    try:
        return pd.read_csv(caminho, sep=";", decimal=",")
    except FileNotFoundError:
        print(
            f"ERRO: não achei '{caminho}'. "
            "Rode `python poliedro_14_consolidar_dataset_powerbi.py` antes deste passo.",
            file=sys.stderr,
        )
        sys.exit(1)


def separar_parceiros_e_prospects(leads):
    """Divide as leads entre escolas já clientes do Poliedro e prospects."""
    tem_coordenada = leads["LATITUDE"].notna() & leads["LONGITUDE"].notna()
    eh_cliente = leads["ja_cliente_poliedro_qualquer_marca"] == True  # noqa: E712
    parceiros = leads[eh_cliente & tem_coordenada].copy()
    prospects = leads[~eh_cliente & tem_coordenada].copy()
    return parceiros, prospects


def medir_distancia_ate_parceiro(prospects, parceiros):
    """Para cada prospect, acha o parceiro Poliedro mais próximo na mesma cidade."""
    linhas = []
    for _, prospect in prospects.iterrows():
        mesma_cidade = parceiros[
            parceiros["codigo_municipio"] == prospect["codigo_municipio"]
        ]
        if len(mesma_cidade) == 0:
            continue
        distancias = calcular_distancia_km(
            prospect["LATITUDE"],
            prospect["LONGITUDE"],
            mesma_cidade["LATITUDE"].values,
            mesma_cidade["LONGITUDE"].values,
        )
        indice_mais_proximo = int(np.argmin(distancias))
        parceiro = mesma_cidade.iloc[indice_mais_proximo]
        linhas.append(
            {
                "prospect": prospect["NO_ENTIDADE"],
                "codigo_escola": prospect["codigo_escola"],
                "cidade": prospect["cidade"],
                "UF": prospect["UF"],
                "bairro_prospect": prospect["bairro"],
                "segmento_comercial": prospect["segmento_comercial"],
                "score_destaque": prospect["score_destaque"],
                "parceiro_mais_proximo": parceiro["NO_ENTIDADE"],
                "bairro_parceiro": parceiro["bairro"],
                "parceiro_eh_unidade_propria": parceiro["rede_propria_poliedro"],
                "distancia_km": round(float(distancias[indice_mais_proximo]), 2),
            }
        )
    return pd.DataFrame(linhas)


def classificar_proximidade(distancia_km):
    """Rotula a distância em faixas legíveis — SINAL, não critério de exclusão."""
    if distancia_km <= 1:
        return "mesmo entorno (<=1km)"
    if distancia_km <= 2:
        return "muito proximo (1-2km)"
    if distancia_km <= 5:
        return "proximo (2-5km)"
    return "distante (>5km)"


def main():
    leads = carregar_leads(CAMINHO_LEADS)
    parceiros, prospects = separar_parceiros_e_prospects(leads)
    print(
        f"Parceiros/clientes com coordenada: {len(parceiros)} | "
        f"prospects com coordenada: {len(prospects)}"
    )

    resultado = medir_distancia_ate_parceiro(prospects, parceiros)
    if resultado.empty:
        print("AVISO: nenhum prospect divide município com um parceiro. Nada a gerar.")
        return

    resultado["faixa_proximidade"] = resultado["distancia_km"].apply(
        classificar_proximidade
    )
    resultado = resultado.sort_values("distancia_km").reset_index(drop=True)
    resultado.to_csv(CAMINHO_SAIDA, sep=";", index=False)

    # --- resumo de sanidade (min/média/máx + contagens) ---
    print(f"\nGerado: {CAMINHO_SAIDA} ({len(resultado)} prospects em praça com parceiro)")
    print(
        f"distancia_km — min {resultado['distancia_km'].min():.2f} | "
        f"mediana {resultado['distancia_km'].median():.2f} | "
        f"média {resultado['distancia_km'].mean():.2f} | "
        f"máx {resultado['distancia_km'].max():.2f}"
    )
    print("\nContagem por faixa de proximidade:")
    print(resultado["faixa_proximidade"].value_counts().to_string())
    print(f"\nCidades cobertas: {resultado['cidade'].nunique()}")
    print("\nOs 10 casos mais próximos de um parceiro atual:")
    print(
        resultado.head(10)[
            ["prospect", "cidade", "parceiro_mais_proximo", "distancia_km"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
