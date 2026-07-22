"""
Case Poliedro — Passo 4: SCORE DE PRIORIZAÇÃO DE CIDADES (Parte 1 do case).

Metodologia (documentar tal qual na entrega):

Filtro de escopo obrigatório (não é critério de score, é corte binário):
- Município com população total > 100.000 habitantes (IBGE/Censo 2022).

Score de priorização, por município elegível, combina 3 critérios normalizados
por percentil (0 a 1) e ponderados:

1. POTENCIAL SOCIOECONÔMICO (peso 0.40)
   Renda domiciliar per capita alta (Censo 2022, Tabela 10296 IBGE) + volume de
   população 0-17 anos. Por quê: mede poder de compra real das famílias (não
   PIB per capita, que mistura riqueza industrial/institucional — lição já
   aprendida neste projeto) e tamanho do mercado futuro de alunos.

2. VOLUME DE ESCOLAS PRIVADAS RELEVANTES JÁ INSTALADAS (peso 0.30)
   Quantidade de escolas privadas elegíveis (Censo 2025: não-filantrópica, em
   atividade, oferece Ensino Médio) no município. Por quê: a pergunta do case
   não é só "onde tem dinheiro", é "onde já existe concentração de mercado
   educacional privado relevante" — cidade com 1 escola elegível não é praça
   de disputa de prestígio, mesmo que rica.

3. QUALIDADE MÉDIA DA PRAÇA — ENEM (peso 0.30)
   Média do ENEM 2025 (média geral das 5 áreas) das escolas elegíveis do
   município que têm dado ENEM vinculado. Por quê: é o proxy mais direto de
   prestígio acadêmico já reconhecido na praça — o critério que faltava por
   completo na versão anterior deste pipeline.

   Revisão de 21/07 (Gui apontou o risco): a média da praça é PONDERADA por
   qtd_participantes_enem de cada escola, não é mais a média simples das
   médias por escola. Motivo: média simples dá o mesmo peso a uma escola de
   15 participantes com média 800 e a uma escola de 300 participantes com
   média 650 — a cidade "parece" mais forte do que o aluno médio realmente
   experimenta ali. A versão ponderada reflete melhor a praça como um todo.
   Testado: essa mudança altera o Top 10 de fato (Florianópolis, Porto
   Alegre, Brasília, Goiânia e Jundiaí saem; entram Recife, Ribeirão Preto,
   João Pessoa, Aracaju e Uberlândia) — mas as 3 cidades usadas na Parte 2
   (Belo Horizonte, Niterói, Vitória) continuam #1-#3, então a análise de
   escolas (Parte 2) não precisou ser refeita.

Limitação documentada: 27,2% das escolas elegíveis não têm nenhum participante
do ENEM vinculado (ver poliedro_02_extrair_enem.py) — a média da praça usa só
as escolas com dado disponível, o que pode sub-representar cidades onde as
escolas privadas relevantes têm baixa adesão ao ENEM vinculado à escola.

Gera: data/outputs/01_cidades_prioritarias.csv (top 10 + tabela completa)
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POPULACAO_MINIMA_MUNICIPIO = 100_000
PESO_SOCIOECONOMICO = 0.40
PESO_VOLUME_ESCOLAS = 0.30
PESO_QUALIDADE_ENEM = 0.30


def carregar_populacao_total() -> pd.DataFrame:
    """População total por município (IBGE/SIDRA, Censo 2022) — usada no filtro de escopo."""
    return pd.read_csv(RAW_DIR / "populacao_total_por_municipio.csv", dtype={"codigo_municipio": str})


def carregar_score_renda() -> pd.DataFrame:
    """Recalcula o score de renda domiciliar por município (mesma lógica do pipeline.py original)."""
    caminho = RAW_DIR / "Tabela_10296__1_.xlsx"
    df_raw = pd.read_excel(caminho, sheet_name="Tabela", header=None)

    linha_inicio = df_raw[df_raw[0] == "Município"].index[0] + 1
    df_dados = df_raw.iloc[linha_inicio:, [0, 1, 2]].copy()
    df_dados.columns = ["municipio_uf", "faixa_renda", "quantidade"]
    df_dados["municipio_uf"] = df_dados["municipio_uf"].ffill()
    df_dados = df_dados.dropna(subset=["faixa_renda"])
    df_dados["quantidade"] = (
        df_dados["quantidade"].astype(str).str.replace(".", "", regex=False).replace("-", "0")
    )
    df_dados["quantidade"] = pd.to_numeric(df_dados["quantidade"], errors="coerce").fillna(0)

    df_pivot = df_dados.pivot_table(
        index="municipio_uf", columns="faixa_renda", values="quantidade", aggfunc="sum"
    ).reset_index()

    faixas_renda_alta = [
        "Mais de 5 a 10 salários mínimos", "Mais de 10 a 15 salários mínimos",
        "Mais de 15 a 20 salários mínimos", "Mais de 20 salários mínimos",
    ]
    faixa_classe_media_alta = "Mais de 3 a 5 salários mínimos"

    df_pivot["pop_renda_alta"] = df_pivot[faixas_renda_alta].sum(axis=1)
    df_pivot["pop_classe_media_alta"] = df_pivot[faixa_classe_media_alta]
    df_pivot["chave_nome_uf"] = df_pivot["municipio_uf"].str.strip()

    correspondencia = pd.read_csv(RAW_DIR / "correspondencia_municipios_ibge.csv", dtype=str)
    df_final = df_pivot.merge(correspondencia, on="chave_nome_uf", how="left")
    df_final = df_final.dropna(subset=["codigo_municipio"])

    pop_0_17 = pd.read_csv(RAW_DIR / "populacao_0_17_por_municipio.csv", dtype={"codigo_municipio": str})
    df_final = df_final.merge(pop_0_17, on="codigo_municipio", how="inner")

    df_final["pct_renda_alta"] = df_final["pop_renda_alta"] / df_final["populacao_0_17"]
    df_final["pct_classe_media_alta"] = df_final["pop_classe_media_alta"] / df_final["populacao_0_17"]
    df_final["score_renda"] = df_final["pct_renda_alta"] * 0.80 + df_final["pct_classe_media_alta"] * 0.20
    df_final["percentil_volume_infantil"] = df_final["populacao_0_17"].rank(pct=True)
    df_final["score_socioeconomico"] = (
        df_final["score_renda"] * 0.85 + df_final["percentil_volume_infantil"] * 0.15
    )

    return df_final[["codigo_municipio", "populacao_0_17", "score_socioeconomico"]]


def carregar_escolas_elegiveis_com_enem() -> pd.DataFrame:
    """Escolas privadas elegíveis (Censo 2025) cruzadas com médias ENEM por escola."""
    escolas = pd.read_csv(RAW_DIR / "escolas_privadas_elegiveis_2025.csv", dtype={"codigo_municipio": str})
    enem = pd.read_csv(RAW_DIR / "enem_2025_medias_por_escola.csv")
    escolas["codigo_escola"] = escolas["CO_ENTIDADE"].astype("int64")
    return escolas.merge(enem[["codigo_escola", "qtd_participantes_enem", "enem_media_geral"]],
                          on="codigo_escola", how="left")


def media_enem_ponderada_por_participante(grupo: pd.DataFrame) -> float:
    """Média do ENEM da praça, ponderada por qtd_participantes_enem de cada escola (não é média simples)."""
    valido = grupo.dropna(subset=["enem_media_geral", "qtd_participantes_enem"])
    if valido["qtd_participantes_enem"].sum() == 0:
        return float("nan")
    return (valido["enem_media_geral"] * valido["qtd_participantes_enem"]).sum() / valido["qtd_participantes_enem"].sum()


def montar_score_cidades() -> pd.DataFrame:
    """Monta o score de priorização municipal aplicando o filtro de escopo e os 3 critérios ponderados."""
    pop_total = carregar_populacao_total()
    score_renda = carregar_score_renda()
    escolas = carregar_escolas_elegiveis_com_enem()

    municipios_elegiveis = pop_total[pop_total["populacao_total"] > POPULACAO_MINIMA_MUNICIPIO].copy()
    print(f"[Filtro de escopo] Municípios com população > {POPULACAO_MINIMA_MUNICIPIO:,}: {len(municipios_elegiveis):,}")

    agg_escolas = (
        escolas.groupby("codigo_municipio")
        .agg(
            qtd_escolas_elegiveis=("codigo_escola", "count"),
            qtd_escolas_com_enem=("enem_media_geral", "count"),
        )
        .reset_index()
    )
    media_ponderada = (
        escolas.groupby("codigo_municipio")
        .apply(media_enem_ponderada_por_participante, include_groups=False)
        .rename("enem_media_praca")
        .reset_index()
    )
    agg_escolas = agg_escolas.merge(media_ponderada, on="codigo_municipio", how="left")

    df = municipios_elegiveis.merge(agg_escolas, on="codigo_municipio", how="left")
    df = df.merge(score_renda, on="codigo_municipio", how="left")

    antes = len(df)
    sem_escola = df[df["qtd_escolas_elegiveis"].isna()]["codigo_municipio"].tolist()
    if sem_escola:
        print(f"[Aviso] {len(sem_escola)} município(s) >100k sem nenhuma escola elegível, removido(s) do ranking: {sem_escola}")
    df = df.dropna(subset=["qtd_escolas_elegiveis"]).copy()

    antes_renda = len(df)
    sem_renda = df[df["score_socioeconomico"].isna()]["codigo_municipio"].tolist()
    if sem_renda:
        print(f"[Aviso] {len(sem_renda)} município(s) sem score socioeconômico (falha de correspondência de nome IBGE), removido(s): {sem_renda}")
    df = df.dropna(subset=["score_socioeconomico"]).copy()

    # Normalização por percentil dentro do universo elegível (>100k com escola)
    df["percentil_socioeconomico"] = df["score_socioeconomico"].rank(pct=True)
    df["percentil_volume_escolas"] = df["qtd_escolas_elegiveis"].rank(pct=True)
    # Para qualidade ENEM: só entre quem tem dado; quem não tem fica com o pior percentil (não zera arbitrariamente)
    df["percentil_qualidade_enem"] = df["enem_media_praca"].rank(pct=True)
    df["percentil_qualidade_enem"] = df["percentil_qualidade_enem"].fillna(df["percentil_qualidade_enem"].min())

    df["score_priorizacao"] = (
        df["percentil_socioeconomico"] * PESO_SOCIOECONOMICO
        + df["percentil_volume_escolas"] * PESO_VOLUME_ESCOLAS
        + df["percentil_qualidade_enem"] * PESO_QUALIDADE_ENEM
    ).round(4)

    correspondencia = pd.read_csv(RAW_DIR / "correspondencia_municipios_ibge.csv", dtype=str)
    df = df.merge(correspondencia[["codigo_municipio", "nome_municipio_ibge", "uf"]], on="codigo_municipio", how="left")

    df = df.sort_values("score_priorizacao", ascending=False).reset_index(drop=True)
    print(f"[Score] {len(df):,} municípios rankeados (de {antes:,} elegíveis por população)")
    return df


def exibir_resumo(df: pd.DataFrame) -> None:
    print("\n" + "=" * 100)
    print("TOP 10 CIDADES PRIORITÁRIAS")
    print("=" * 100)
    cols = ["nome_municipio_ibge", "uf", "populacao_total", "qtd_escolas_elegiveis",
            "enem_media_praca", "score_socioeconomico", "score_priorizacao"]
    print(df[cols].head(10).to_string(index=False))
    print("\n[Sanity check] score_priorizacao — min: {:.4f} | média: {:.4f} | max: {:.4f}".format(
        df["score_priorizacao"].min(), df["score_priorizacao"].mean(), df["score_priorizacao"].max()))


def main():
    df = montar_score_cidades()
    exibir_resumo(df)
    df.to_csv(OUT_DIR / "01_cidades_prioritarias.csv", index=False)
    print(f"\n[✓] Salvo em {OUT_DIR / '01_cidades_prioritarias.csv'}")


if __name__ == "__main__":
    main()
