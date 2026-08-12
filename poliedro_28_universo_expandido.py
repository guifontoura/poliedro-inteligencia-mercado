"""
Case Poliedro — Passo 28 (roadmap 3.0, pedido do Gui em 28/07): UNIVERSO
EXPANDIDO — junta os alvos do Sistema Poliedro e do Sistema Polígono numa
base única, no mesmo formato do `04_golden_leads_segmentadas.csv`.

Por que este passo existe: o `04` (e, por consequência, o dataset de Power BI
do passo 14) só carrega as escolas acima de 0,70 de `score_destaque` — o
recorte "Golden Lead", que é o ICP do Poliedro. Com o Polígono no portfólio,
metade do mercado relevante fica invisível: são 1.110 escolas na faixa
0,40-0,70 com porte de EM relevante, somando ~234 mil matrículas — quase o
mesmo tamanho do pool Poliedro (1.150 escolas, ~254 mil). Ver
`poliedro_25_produto_alvo.py` pros critérios e as limitações.

O que este passo NÃO muda: a resposta formal ao case (passos 01, 02 e 04
originais) continua intocada. Este arquivo é adicional, consumido só pelo
passo 14 quando existe.

Também acopla aqui, no mesmo passo, o ENEM 2024 (passo 27), pra viabilizar
duas coisas no Power BI: (a) comparar o desempenho de cada escola entre duas
edições e (b) usar a média de 2 anos, que é menos ruidosa que a de um ano só
— ver o achado de estabilidade no README.

Entrada:  data/outputs/25_produto_alvo.csv
          data/outputs/funil_escolas_pontuadas.csv
          data/outputs/04_golden_leads_segmentadas.csv (pra herdar rede_propria_poliedro)
          data/raw/enem_2024_medias_por_escola.csv (opcional)
Gera:     data/outputs/04b_universo_expandido_segmentado.csv
"""

import sys
from pathlib import Path

import pandas as pd

from poliedro_filtros import remover_sistema_s

OUT_DIR = Path("data/outputs")
RAW_DIR = Path("data/raw")
CAMINHO_SAIDA = OUT_DIR / "04b_universo_expandido_segmentado.csv"

MIN_ESCOLAS_CONFIAVEIS_PARA_RANK = 3


def carregar(caminho, passo_anterior, **kwargs):
    """Lê um CSV do pipeline apontando qual passo rodar caso ele não exista."""
    try:
        return pd.read_csv(caminho, **kwargs)
    except FileNotFoundError:
        print(
            f"ERRO: não achei '{caminho}'. Rode `python {passo_anterior}` antes deste passo.",
            file=sys.stderr,
        )
        sys.exit(1)


def classificar_segmento_comercial(linha):
    """Rotula a posição competitiva da escola dentro do próprio município."""
    if linha["n_escolas_confiaveis_municipio"] < MIN_ESCOLAS_CONFIAVEIS_PARA_RANK:
        return "Sem comparação local (poucas escolas na cidade)"
    if linha["rank_municipio"] == 1:
        return "Líder local"
    if 2 <= linha["rank_municipio"] <= 5:
        return "Desafiante (2º-5º local)"
    return "Outras posições"


def montar_universo_expandido():
    """Seleciona alvos Poliedro + Polígono e recalcula a posição local de cada um."""
    produto = carregar(
        OUT_DIR / "25_produto_alvo.csv", "poliedro_25_produto_alvo.py", sep=";",
        dtype={"codigo_escola": str, "codigo_municipio": str},
    )
    funil = carregar(
        OUT_DIR / "funil_escolas_pontuadas.csv", "poliedro_05b_score_destaque_nacional.py",
        dtype={"codigo_escola": str, "codigo_municipio": str},
    )

    alvos = produto[produto["produto_alvo"].isin(["Poliedro", "Polígono"])][
        ["codigo_escola", "produto_alvo"]
    ]
    universo = funil[funil["confiavel_enem"] == True].merge(  # noqa: E712
        alvos, on="codigo_escola", how="inner"
    )

    # Escopo do projeto: Sistema S fica de fora (ver poliedro_filtros.py).
    # Precisa ser reaplicado aqui porque este passo monta o universo direto do
    # funil, sem passar pelo 09.
    universo = remover_sistema_s(universo)

    # Posição local recalculada sobre TODAS as escolas confiáveis do município
    # (não só sobre as do universo expandido) — senão a posição de uma escola
    # Polígono ficaria inflada por ignorar as Poliedro que estão acima dela.
    confiaveis = funil[funil["confiavel_enem"] == True].copy()  # noqa: E712
    confiaveis["rank_municipio"] = confiaveis.groupby("codigo_municipio")["score_destaque"].rank(
        ascending=False, method="min"
    )
    confiaveis["n_escolas_confiaveis_municipio"] = confiaveis.groupby("codigo_municipio")[
        "codigo_municipio"
    ].transform("count")
    posicoes = confiaveis[
        ["codigo_escola", "rank_municipio", "n_escolas_confiaveis_municipio"]
    ]
    universo = universo.merge(posicoes, on="codigo_escola", how="left")
    universo["segmento_comercial"] = universo.apply(classificar_segmento_comercial, axis=1)
    return universo


def herdar_flag_rede_propria(universo):
    """Traz `rede_propria_poliedro` do passo 04; quem não estava lá entra como False."""
    caminho = OUT_DIR / "04_golden_leads_segmentadas.csv"
    if not caminho.exists():
        print("[Aviso] 04 não encontrado — rede_propria_poliedro entra toda como False.")
        universo["rede_propria_poliedro"] = False
        return universo
    golden = pd.read_csv(caminho, dtype={"codigo_escola": str})[
        ["codigo_escola", "rede_propria_poliedro"]
    ]
    universo = universo.merge(golden, on="codigo_escola", how="left")
    universo["rede_propria_poliedro"] = (
        universo["rede_propria_poliedro"].fillna(False).astype(bool)
    )
    return universo


def acoplar_enem_2024(universo):
    """Acrescenta a média ENEM 2024 e a média de 2 anos, se o passo 27 já rodou."""
    caminho = RAW_DIR / "enem_2024_medias_por_escola.csv"
    if not caminho.exists():
        print("[Aviso] ENEM 2024 não encontrado — rode `python poliedro_27_extrair_enem_2024.py` "
              "pra habilitar a comparação entre anos. Seguindo só com 2025.")
        return universo
    enem24 = pd.read_csv(caminho, dtype={"codigo_escola": str})
    universo = universo.merge(enem24, on="codigo_escola", how="left")
    # Média de 2 anos ponderada por participante: reduz o ruído amostral de
    # uma edição só (medido em 28/07: escolas com 10-19 participantes têm
    # desvio de 28 pontos entre 2024 e 2025, contra 12 pontos das com 100+).
    peso_2025 = universo["qtd_participantes_enem"].fillna(0)
    peso_2024 = universo["qtd_participantes_enem_2024"].fillna(0)
    soma_pesos = peso_2025 + peso_2024
    universo["enem_media_2anos"] = (
        universo["enem_media_geral"].fillna(0) * peso_2025
        + universo["enem_media_geral_2024"].fillna(0) * peso_2024
    ) / soma_pesos.where(soma_pesos > 0)
    universo["delta_enem_2025_2024"] = (
        universo["enem_media_geral"] - universo["enem_media_geral_2024"]
    )
    return universo


def main():
    universo = montar_universo_expandido()
    universo = herdar_flag_rede_propria(universo)
    universo = acoplar_enem_2024(universo)

    colunas = [
        "codigo_escola", "NO_ENTIDADE", "codigo_municipio", "rank_municipio",
        "n_escolas_confiaveis_municipio", "segmento_comercial", "rede_propria_poliedro",
        "enem_media_geral", "qtd_participantes_enem", "indice_infra", "QT_MAT_MED",
        "score_destaque", "produto_alvo",
    ]
    for opcional in ["enem_media_geral_2024", "qtd_participantes_enem_2024",
                     "enem_media_2anos", "delta_enem_2025_2024"]:
        if opcional in universo.columns:
            colunas.append(opcional)

    saida = universo[colunas].sort_values("score_destaque", ascending=False)
    saida.to_csv(CAMINHO_SAIDA, index=False)

    # --- resumo de sanidade ---
    print(f"\nGerado: {CAMINHO_SAIDA} ({len(saida)} escolas)")
    print("\nPor produto alvo:")
    print(saida["produto_alvo"].value_counts().to_string())
    print("\nPor segmento comercial:")
    print(saida["segmento_comercial"].value_counts().to_string())
    print(
        f"\nscore_destaque — min {saida['score_destaque'].min():.3f} | "
        f"mediana {saida['score_destaque'].median():.3f} | máx {saida['score_destaque'].max():.3f}"
    )
    if "enem_media_2anos" in saida.columns:
        cobertura = saida["enem_media_geral_2024"].notna().mean() * 100
        print(f"Cobertura do ENEM 2024 sobre o universo: {cobertura:.1f}%")


if __name__ == "__main__":
    main()
