"""
Case Poliedro — Passo 16 (roadmap 3.0, pedido do Gui em 23/07: "vamos avançar
no setor censitário IBGE"): RENDA DO RESPONSÁVEL POR BAIRRO (RJ) E DISTRITO (SP).

Fonte: IBGE, Censo 2022, "Agregados por Setores Censitários — Rendimento do
Responsável" (publicado 08/05/2026), agregado por bairro e por distrito —
não precisamos do join espacial pesado (setor censitário + shapefile +
geopandas) que estava cotado como próximo passo no poliedro_11: o IBGE já
entrega pronto no nível de bairro/distrito, a mesma unidade que o passo 15
já usa por cidade (distrito em SP, bairro no RJ).

Colunas confirmadas via dicionário oficial baixado do IBGE (NÃO adivinhadas —
ver data/raw/dicionario_renda_2022.xlsx):
  V06001 = pessoas responsáveis em domicílios particulares permanentes ocupados
  V06002 = moradores em domicílios particulares permanentes ocupados
  V06003 = variância do número de moradores (não usado aqui)
  V06004 = rendimento nominal MÉDIO mensal do responsável (R$)
  V06005 = variância do rendimento (não usado aqui)
  V06006 = rendimento nominal MEDIANO mensal do responsável (R$)
Usamos V06006 (mediana) como indicador principal — mais robusto a outliers
(1 morador rico distorce a média de um bairro pequeno, não distorce a
mediana) — e reportamos V06004 (média) junto, como contexto.

O arquivo de distrito também trazia uma coluna `PERE0115_NOVA` que bate com
V06006 em 99,5% das linhas mas NÃO está documentada no dicionário oficial —
descartada aqui por não ser uma fonte confiável/rastreável.

Chave geográfica: `CD_DIST`/`CD_BAIRRO` do IBGE começam com o código de
município (7 dígitos) + sequencial — filtramos por prefixo (São Paulo:
3550308, Rio de Janeiro: 3304557), sem precisar de nome de município.

Match de nome com o passo 15 (fontes diferentes: Censo Escolar x Censo IBGE):
os nomes não vêm no mesmo formato (Censo Escolar no RJ vem em CAIXA ALTA sem
acento, ex. "GAVEA"; IBGE vem em Title Case com acento, ex. "Gávea"). Chave
de junção normalizada (maiúsculo + sem acento) nos dois lados — validamos a
taxa de match no sanity check, não presumimos 100%.

Revisão 24/07 (o passo 15 passou a agregar o RJ por Região Administrativa
oficial, não mais por bairro cru — ver lá pro motivo): o IBGE não publica
renda por RA diretamente, só por bairro. Então aqui agregamos a renda dos
BAIRROS de cada RA numa média PONDERADA pela população do bairro (`V06002`,
moradores em domicílios — mesma fonte, evita que um bairro minúsculo e rico
distorça a RA inteira). Usa o mesmo dicionário `RA_POR_BAIRRO_RJ` do passo
15 (importado de lá, não duplicado).

Limitação que fica documentada, não escondida: V06004/V06006 medem renda do
RESPONSÁVEL pelo domicílio, não renda per capita domiciliar (que é o que a
Parte 1 usa no nível de município, Tabela 10296 SIDRA). É uma métrica
correlata mas não idêntica — mistura tamanho de família com renda do
responsável. Ainda assim, mais precisa que nada, no nível de bairro/distrito
que a Parte 1 não tem.

Gera: data/outputs/16_regioes_sp_rj_com_renda.csv
"""

import unicodedata
from pathlib import Path

import pandas as pd

from poliedro_15_regioes_sp_rj import RA_POR_BAIRRO_RJ

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

PREFIXO_MUNICIPIO = {"São Paulo": "3550308", "Rio de Janeiro": "3304557"}


def normalizar_nome(nome: str) -> str:
    """Maiúsculo + sem acento, pra casar nomes de bairro/distrito entre Censo Escolar e IBGE renda."""
    if pd.isna(nome):
        return nome
    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().upper()


def carregar_renda_distrito_sp() -> pd.DataFrame:
    """Renda do responsável por distrito, só São Paulo capital."""
    df = pd.read_csv(RAW_DIR / "renda_distrito_2022.csv", sep=";", encoding="latin-1")
    df["CD_DIST"] = df["CD_DIST"].astype(str)
    df = df[df["CD_DIST"].str.startswith(PREFIXO_MUNICIPIO["São Paulo"])].copy()
    df["regiao_norm"] = df["NM_DIST"].apply(normalizar_nome)
    for col in ["V06004", "V06006"]:
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)
    return df.rename(columns={"V06004": "renda_media_responsavel", "V06006": "renda_mediana_responsavel"})[
        ["regiao_norm", "renda_media_responsavel", "renda_mediana_responsavel"]
    ]


def carregar_renda_ra_rj() -> pd.DataFrame:
    """Renda do responsável por Região Administrativa (RJ) — bairros do IBGE agregados via
    RA_POR_BAIRRO_RJ, ponderados pela população do bairro (V06002)."""
    df = pd.read_csv(RAW_DIR / "renda_bairro_2022.csv", sep=";", encoding="latin-1")
    df["CD_BAIRRO"] = df["CD_BAIRRO"].astype(str)
    df = df[df["CD_BAIRRO"].str.startswith(PREFIXO_MUNICIPIO["Rio de Janeiro"])].copy()
    for col in ["V06002", "V06004", "V06006"]:
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    ra_normalizado = {normalizar_nome(k): v for k, v in RA_POR_BAIRRO_RJ.items()}
    df["regiao"] = df["NM_BAIRRO"].apply(normalizar_nome).map(ra_normalizado)
    sem_ra = df[df["regiao"].isna()]
    if len(sem_ra):
        print(f"[Sanity check] {len(sem_ra)} bairros do IBGE (RJ) sem RA mapeada, "
              f"excluídos da agregação: {sorted(sem_ra['NM_BAIRRO'].tolist())}")
    df = df.dropna(subset=["regiao"])

    def media_ponderada_por_pop(g: pd.DataFrame, col: str) -> float:
        return (g[col] * g["V06002"]).sum() / g["V06002"].sum()

    linhas = []
    for regiao, g in df.groupby("regiao"):
        linhas.append({
            "regiao_norm": normalizar_nome(regiao),
            "renda_media_responsavel": round(media_ponderada_por_pop(g, "V06004"), 2),
            "renda_mediana_responsavel": round(media_ponderada_por_pop(g, "V06006"), 2),
        })
    return pd.DataFrame(linhas)


def enriquecer_regioes_com_renda() -> pd.DataFrame:
    """Junta 15_regioes_sp_rj.csv (ENEM + volume) com a renda do IBGE por região."""
    regioes = pd.read_csv(OUT_DIR / "15_regioes_sp_rj.csv", sep=";", decimal=",")
    regioes["regiao_norm"] = regioes["regiao"].apply(normalizar_nome)

    renda_sp = carregar_renda_distrito_sp()
    renda_rj = carregar_renda_ra_rj()

    sp = regioes[regioes["cidade"] == "São Paulo"].merge(renda_sp, on="regiao_norm", how="left")
    rj = regioes[regioes["cidade"] == "Rio de Janeiro"].merge(renda_rj, on="regiao_norm", how="left")

    return pd.concat([sp, rj], ignore_index=True).drop(columns=["regiao_norm"])


def exibir_resumo(df: pd.DataFrame) -> None:
    match = df["renda_mediana_responsavel"].notna()
    print(f"[Sanity check] Regiões com renda encontrada: {match.sum()} de {len(df)} ({match.mean() * 100:.1f}%)")
    sem_match = df[~match][["cidade", "regiao"]]
    if len(sem_match):
        print(f"[Sanity check] Sem match (nome não bateu, revisar manualmente): \n{sem_match.to_string(index=False)}")

    sig = df[df["amostra_significativa"] & match]
    print("\n--- Renda mediana do responsável x ENEM ponderado (amostra significativa) ---")
    for cidade in ["São Paulo", "Rio de Janeiro"]:
        print(f"\n{cidade} — Top 5 por RENDA (não por ENEM, pra achar bairros nobres com ENEM mediano):")
        cols = ["regiao", "renda_mediana_responsavel", "enem_ponderado", "qtd_golden_leads"]
        print(sig[sig["cidade"] == cidade].sort_values("renda_mediana_responsavel", ascending=False)[cols].head(5).to_string(index=False))


def main():
    df = enriquecer_regioes_com_renda()
    exibir_resumo(df)
    # sep=';' e decimal=',' — formato brasileiro, pro Power BI Desktop reconhecer os decimais.
    df.to_csv(OUT_DIR / "16_regioes_sp_rj_com_renda.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '16_regioes_sp_rj_com_renda.csv'}")


if __name__ == "__main__":
    main()
