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
oficial, não mais por bairro cru): o IBGE não publica renda por RA
diretamente, só por bairro — então nessa época agregávamos os BAIRROS de
cada RA numa média ponderada pela população.

Revisão 28/07 (o passo 15 voltou a usar bairro direto no RJ — RA escondia
diferença de renda relevante dentro da mesma região, ver docstring de
`poliedro_15_regioes_sp_rj.py`): a agregação por RA fica desnecessária aqui.
`renda_bairro_2022.csv` já vem pronto no nível de bairro, o mesmo nível que
o passo 15 agora usa — é join direto, sem ponderação nem dicionário
`RA_POR_BAIRRO_RJ` (que não é mais importado deste arquivo).

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


def carregar_renda_bairro_rj() -> pd.DataFrame:
    """Renda do responsável por bairro, só Rio de Janeiro capital — join direto, sem agregação."""
    df = pd.read_csv(RAW_DIR / "renda_bairro_2022.csv", sep=";", encoding="latin-1")
    df["CD_BAIRRO"] = df["CD_BAIRRO"].astype(str)
    df = df[df["CD_BAIRRO"].str.startswith(PREFIXO_MUNICIPIO["Rio de Janeiro"])].copy()
    df["regiao_norm"] = df["NM_BAIRRO"].apply(normalizar_nome)
    for col in ["V06004", "V06006"]:
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)
    return df.rename(columns={"V06004": "renda_media_responsavel", "V06006": "renda_mediana_responsavel"})[
        ["regiao_norm", "renda_media_responsavel", "renda_mediana_responsavel"]
    ]


def enriquecer_regioes_com_renda() -> pd.DataFrame:
    """Junta 15_regioes_sp_rj.csv (ENEM + volume) com a renda do IBGE por região."""
    regioes = pd.read_csv(OUT_DIR / "15_regioes_sp_rj.csv", sep=";", decimal=",")
    regioes["regiao_norm"] = regioes["regiao"].apply(normalizar_nome)

    renda_sp = carregar_renda_distrito_sp()
    renda_rj = carregar_renda_bairro_rj()

    sp = regioes[regioes["cidade"] == "São Paulo"].merge(renda_sp, on="regiao_norm", how="left")
    rj = regioes[regioes["cidade"] == "Rio de Janeiro"].merge(renda_rj, on="regiao_norm", how="left")

    return pd.concat([sp, rj], ignore_index=True).drop(columns=["regiao_norm"])


def marcar_regiao_oportunidade(df: pd.DataFrame) -> pd.DataFrame:
    """Sinaliza região com renda alta COMPARADA DENTRO DA PRÓPRIA CIDADE — candidata a expansão.

    Revisão 05/08 (correção do Gui): a versão anterior media ENEM abaixo da
    mediana e usava uma mediana de renda ÚNICA misturando SP e RJ — os dois
    erros que ele apontou. SP e RJ têm patamares de renda bem diferentes; uma
    mediana única fazia praticamente todo bairro do Rio (renda mais baixa em
    geral) nunca aparecer como "oportunidade", mesmo sendo o bairro mais rico
    da própria cidade — viés real que o Gui pegou antes de eu propagar ele
    pro dashboard. ENEM saiu do critério: o pedido dele foi renda alta
    RELATIVA à cidade como o fator principal.

    Critério agora: renda_mediana_responsavel >= mediana das regiões
    elegíveis DA MESMA CIDADE (mediana calculada separadamente pra São Paulo
    e Rio de Janeiro, nunca misturada). "Elegível" = amostra_significativa E
    renda encontrada.

    `qtd_golden_leads` e `distancia_parceiro_mais_proximo_km` (passo 16b)
    continuam disponíveis como colunas na tabela pra leitura manual, mas não
    entram nesse filtro — o Gui preferiu manter o critério simples e olhar
    esses dois caso a caso em vez de embutir mais uma regra automática.
    """
    base = df["amostra_significativa"] & df["renda_mediana_responsavel"].notna()
    mediana_por_cidade = df.loc[base].groupby("cidade")["renda_mediana_responsavel"].median()
    mediana_renda_da_cidade = df["cidade"].map(mediana_por_cidade)
    df["regiao_oportunidade"] = base & (df["renda_mediana_responsavel"] >= mediana_renda_da_cidade)
    return df


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

    print(f"\n[Sanity check] Regiões em 'oportunidade' (renda alta + ENEM mediano/baixo + pouco Poliedro): {df['regiao_oportunidade'].sum()}")
    print(df[df["regiao_oportunidade"]][["cidade", "regiao", "renda_mediana_responsavel", "enem_ponderado", "qtd_golden_leads"]]
          .sort_values("renda_mediana_responsavel", ascending=False).to_string(index=False))


def adicionar_chave_regiao(df: pd.DataFrame) -> pd.DataFrame:
    """Chave `cidade|regiao` — mesma coluna que o poliedro_29 agora gera, pra relacionar as
    2 tabelas no modelo do Power BI (pedido do Gui, 06/08: sincronizar a segmentação SP/RJ
    entre a tabela de escolas e a tabela de regiões, hoje sem relacionamento nenhum)."""
    df["chave_regiao"] = df["cidade"].str.cat(df["regiao"], sep="|")
    return df


def main():
    df = enriquecer_regioes_com_renda()
    df = marcar_regiao_oportunidade(df)
    df = adicionar_chave_regiao(df)
    exibir_resumo(df)
    # sep=';' e decimal=',' — formato brasileiro, pro Power BI Desktop reconhecer os decimais.
    df.to_csv(OUT_DIR / "16_regioes_sp_rj_com_renda.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '16_regioes_sp_rj_com_renda.csv'}")


if __name__ == "__main__":
    main()
