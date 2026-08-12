"""
Case Poliedro — Passo 16b (pedido do Gui, 05/08): distância do PARCEIRO POLIEDRO
mais próximo, agregada por REGIÃO (distrito em SP, bairro no RJ), pra usar na
página "Renda x ENEM" do dashboard — mesmo espírito do `19b` (enriquecimento
avulso que roda DEPOIS do arquivo principal, não durante).

Por que isso é um passo "b" e não faz parte do `poliedro_16` direto: a
distância até o parceiro mais próximo (`distancia_parceiro_atual_km`) só é
calculada no PASSO 29 — porque só lá a gente sabe quais escolas já são
clientes Poliedro (isso vem da pesquisa manual do passo 19, que roda depois
do 16). Ou seja, a ordem real de dependência é 15 → 16 → 29 → 16b (esse
arquivo), mesmo o nome sugerindo o contrário. Rode nessa ordem.

Agregação: MEDIANA da distância entre as escolas de cada região (não média —
mesmo motivo do resto do projeto: 1 escola isolada não deve puxar o número
da região inteira) e não MÍNIMO — o mínimo mostraria só "o ponto mais perto
possível", que exagera o quão bem servida a região está; a mediana representa
melhor a distância de uma escola "típica" daquela região até o parceiro mais
próximo.

Chave de junção: distrito (SP) / bairro (RJ) do passo 29, que já usa a MESMA
lógica de nomeação do `regiao` do passo 15/16 (confirmado por inspeção: os
nomes batem 1:1, incluindo maiúsculas/acentos).

Gera: sobrescreve data/outputs/16_regioes_sp_rj_com_renda.csv com a coluna
`distancia_parceiro_mais_proximo_km` adicionada ao final.
"""

from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")


def calcular_distancia_mediana_por_regiao() -> pd.DataFrame:
    """Mediana de distancia_parceiro_atual_km (passo 29) agrupada por (cidade, regiao)."""
    escolas = pd.read_csv(OUT_DIR / "29_universo_completo_powerbi.csv", sep=";", decimal=",", dtype={"codigo_escola": str})
    escolas["regiao"] = escolas["distrito"].where(escolas["cidade"] == "São Paulo", escolas["bairro"])

    mediana = (
        escolas.groupby(["cidade", "regiao"])["distancia_parceiro_atual_km"]
        .median()
        .round(2)
        .rename("distancia_parceiro_mais_proximo_km")
        .reset_index()
    )
    return mediana


def main():
    regioes = pd.read_csv(OUT_DIR / "16_regioes_sp_rj_com_renda.csv", sep=";", decimal=",")
    if "distancia_parceiro_mais_proximo_km" in regioes.columns:
        regioes = regioes.drop(columns=["distancia_parceiro_mais_proximo_km"])  # idempotente, roda de novo sem duplicar

    mediana = calcular_distancia_mediana_por_regiao()
    regioes = regioes.merge(mediana, on=["cidade", "regiao"], how="left")

    tem_distancia = regioes["distancia_parceiro_mais_proximo_km"].notna()
    print(f"[Sanity check] Regiões com distância até parceiro calculada: {tem_distancia.sum()} de {len(regioes)} "
          f"({tem_distancia.mean() * 100:.1f}%) — as demais são regiões de cidade sem nenhum parceiro Poliedro ainda "
          f"(RJ tinha 0 até 05/08; agora tem a Escola Mater, ver poliedro_19).")
    print(f"[Sanity check] distancia_parceiro_mais_proximo_km — min {regioes['distancia_parceiro_mais_proximo_km'].min():.2f} "
          f"| mediana {regioes['distancia_parceiro_mais_proximo_km'].median():.2f} "
          f"| máx {regioes['distancia_parceiro_mais_proximo_km'].max():.2f}")

    regioes.to_csv(OUT_DIR / "16_regioes_sp_rj_com_renda.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Atualizado {OUT_DIR / '16_regioes_sp_rj_com_renda.csv'} com distancia_parceiro_mais_proximo_km")


if __name__ == "__main__":
    main()
