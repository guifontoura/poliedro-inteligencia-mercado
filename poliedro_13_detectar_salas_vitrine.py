"""
Case Poliedro — Passo 13 (bônus): DETECÇÃO NACIONAL DE "SALAS VITRINE".

Generaliza a investigação ad-hoc feita em 22/07 sobre o Colégio de Aplicação
Farias Brito (Fortaleza): unidades pequenas de uma mesma rede/mantenedora, na
mesma cidade, que reportam média ENEM muito acima das unidades-irmãs maiores
— assinatura típica de "sala vitrine" (turma curada só para o ENEM).

Critério: agrupa escolas por (NU_CNPJ_MANTENEDORA, CO_MUNICIPIO). Dentro de
cada grupo com 2+ escolas, compara a menor unidade (< PARTICIPANTES_MAX_PEQUENA
participantes) contra a média ponderada das unidades-irmãs (todas com pelo
menos PARTICIPANTES_MIN_IRMA participantes). Sinaliza se a diferença for maior
que GAP_MINIMO pontos. Exclui o CNPJ 99999999999999, que é o valor-placeholder
do Censo para "mantenedora não informada" (867 escolas o usam — não é uma rede
de verdade, e agrupá-las juntaria escolas sem nenhuma relação real).

Resultado (rodado em 22/07/2026): 4 grupos confirmados nacionalmente — não é
um caso isolado do Farias Brito. Três dos quatro estão em Fortaleza/CE, um em
Uberaba/MG. Nenhum dos dois municípios está entre as Top 10 cidades
prioritárias nem entre as 3 cidades do case formal (BH/Niterói/Vitória) — ou
seja, não afeta a resposta ao case, mas afeta ~4 das 869 Golden Leads
(aparecem com score_destaque inflado e tag "Líder local"/alto rank).

Gera: data/outputs/13_salas_vitrine_suspeitas.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

CNPJ_NAO_INFORMADO = 99999999999999
PARTICIPANTES_MAX_PEQUENA = 40
PARTICIPANTES_MIN_IRMA = 60
GAP_MINIMO = 30


def carregar_escolas_com_enem_e_mantenedora() -> pd.DataFrame:
    """Junta médias ENEM por escola com CNPJ da mantenedora e município (via codigo_escola)."""
    try:
        enem = pd.read_csv(RAW_DIR / "enem_2025_medias_por_escola.csv")
        enderecos = pd.read_csv(RAW_DIR / "escolas_com_endereco.csv")
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Rode poliedro_02_extrair_enem.py e poliedro_03b_extrair_enderecos.py antes deste script."
        ) from e

    cols_mantenedora = enderecos[["CO_ENTIDADE", "NO_ENTIDADE", "CO_MUNICIPIO", "NU_CNPJ_MANTENEDORA"]].rename(
        columns={"CO_ENTIDADE": "codigo_escola"}
    )
    df = enem.merge(cols_mantenedora, on="codigo_escola", how="inner")
    df = df.dropna(subset=["NU_CNPJ_MANTENEDORA"]).copy()
    df["NU_CNPJ_MANTENEDORA"] = df["NU_CNPJ_MANTENEDORA"].astype("int64")
    df = df[df["NU_CNPJ_MANTENEDORA"] != CNPJ_NAO_INFORMADO]
    return df


def detectar_grupos_suspeitos(df: pd.DataFrame) -> pd.DataFrame:
    """Para cada (mantenedora, município) com 2+ escolas, sinaliza unidade pequena com média muito acima das irmãs."""
    grupos_suspeitos = []
    for (cnpj, municipio), grupo in df.groupby(["NU_CNPJ_MANTENEDORA", "CO_MUNICIPIO"]):
        if len(grupo) < 2:
            continue
        grupo = grupo.sort_values("qtd_participantes_enem")
        pequena = grupo.iloc[0]
        irmas = grupo.iloc[1:]
        if pequena["qtd_participantes_enem"] >= PARTICIPANTES_MAX_PEQUENA:
            continue
        if irmas["qtd_participantes_enem"].min() < PARTICIPANTES_MIN_IRMA:
            continue

        media_irmas_ponderada = np.average(irmas["enem_media_geral"], weights=irmas["qtd_participantes_enem"])
        gap = pequena["enem_media_geral"] - media_irmas_ponderada
        if gap <= GAP_MINIMO:
            continue

        grupos_suspeitos.append(
            {
                "cnpj_mantenedora": cnpj,
                "codigo_municipio": municipio,
                "escola_pequena": pequena["NO_ENTIDADE"],
                "participantes_escola_pequena": int(pequena["qtd_participantes_enem"]),
                "media_escola_pequena": round(pequena["enem_media_geral"], 1),
                "qtd_escolas_irmas": len(irmas),
                "participantes_irmas_total": int(irmas["qtd_participantes_enem"].sum()),
                "media_ponderada_irmas": round(media_irmas_ponderada, 1),
                "gap_pontos": round(gap, 1),
            }
        )

    return pd.DataFrame(grupos_suspeitos).sort_values("gap_pontos", ascending=False)


def exibir_resumo(resultado: pd.DataFrame) -> None:
    print(f"[Sanity check] Grupos suspeitos de 'sala vitrine' encontrados: {len(resultado)}")
    if len(resultado):
        print(resultado.to_string(index=False))


def main():
    df = carregar_escolas_com_enem_e_mantenedora()
    resultado = detectar_grupos_suspeitos(df)
    exibir_resumo(resultado)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(OUT_DIR / "13_salas_vitrine_suspeitas.csv", index=False)
    print(f"[✓] Salvo em {OUT_DIR / '13_salas_vitrine_suspeitas.csv'}")


if __name__ == "__main__":
    main()
