"""
Case Poliedro — Passo 17 (roadmap 3.0, pedido do Gui em 24/07: "vamos começar
a escalar para todas as 318 cidades"): REGIÃO + RENDA EM ESCALA NACIONAL.

Correção de rumo no meio do desenvolvimento (24/07, documentada porque a
primeira tentativa deste script estava errada e vale registrar o motivo):
a primeira versão usava bairro pra todas as 318 cidades, baseado na
suposição de que "bairro generaliza melhor que distrito" (o padrão visto no
Rio). Testamos e a taxa de match ficou em 48,6% — baixa demais pra confiar.
Investigando a causa raiz (não só tentando de novo com outro parâmetro):
o problema não era erro de grafia, era que **128 das 318 cidades simplesmente
não têm bairro cadastrado no produto de renda do IBGE** — incluindo cidades
grandes como São Paulo, Campinas, Goiânia e Brasília, que usam DISTRITO como
menor nível administrativo oficial, sem "bairro" formalizado no cadastro do
IBGE. "Bairro" não é uma divisão administrativa universal no Brasil — cada
município decide se cadastra isso ou não; já `NO_DISTRITO` tem 100% de
cobertura no IBGE (as 318 cidades têm pelo menos 1 distrito, mesmo que seja
só a "sede" = a cidade inteira como 1 distrito só, quando não é subdividida).

Regra final (verificada, não a intuição inicial): **usar bairro quando o
IBGE tem bairro cadastrado pra aquele município (190 das 318); usar distrito
como fallback nas outras 128** (onde na pior das hipóteses o "distrito" é a
cidade inteira — não perde informação, só não ganha o detalhe de bairro que
não existe pra comparar de qualquer forma).

Mitigação de inconsistência de nome (o problema achado no RJ: "RECREIO" vs
"RECREIO DOS BANDEIRANTES" etc.) em escala nacional, sem corrigir cidade por
cidade manualmente: match em duas camadas — (1) exato após normalizar
(maiúsculo, sem acento); (2) fuzzy (difflib, limiar 0.90) contra a lista
oficial do IBGE do mesmo município. Confiança do match fica registrada por
linha (`confianca_match`: exato / fuzzy / sem_match) — nunca escondida atrás
de um número que pode estar errado.

Limitação que segue documentada, não escondida: fuzzy match não é perfeito,
e mesmo com bairro/distrito corretos, o valor de renda mede o RESPONSÁVEL
pelo domicílio, não renda per capita (mesma ressalva do passo 16). Uma
checagem manual amostral antes de virar decisão comercial é recomendada.

Gera: data/outputs/17_regioes_nacional_com_renda.csv
"""

import difflib
import unicodedata
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

MIN_ESCOLAS_CONFIAVEIS_PARA_RANK = 3
MIN_PARTICIPANTES_CONFIAVEL = 10
LIMIAR_FUZZY = 0.90


def normalizar_nome(nome) -> str:
    """Maiúsculo + sem acento — mesma normalização usada no passo 15/16."""
    if pd.isna(nome):
        return nome
    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().upper()


def carregar_renda_ibge() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Renda do responsável por bairro e por distrito, nacional (IBGE Censo 2022)."""
    renda_b = pd.read_csv(RAW_DIR / "renda_bairro_2022.csv", sep=";", encoding="latin-1")
    renda_b["CD_BAIRRO"] = renda_b["CD_BAIRRO"].astype(str)
    renda_b["codigo_municipio"] = renda_b["CD_BAIRRO"].str[:7]
    renda_b["nome_norm"] = renda_b["NM_BAIRRO"].apply(normalizar_nome)

    renda_d = pd.read_csv(RAW_DIR / "renda_distrito_2022.csv", sep=";", encoding="latin-1")
    renda_d["CD_DIST"] = renda_d["CD_DIST"].astype(str)
    renda_d["codigo_municipio"] = renda_d["CD_DIST"].str[:7]
    renda_d["nome_norm"] = renda_d["NM_DIST"].apply(normalizar_nome)

    for df in (renda_b, renda_d):
        for col in ["V06004", "V06006"]:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)
        df.rename(columns={"V06004": "renda_media_responsavel", "V06006": "renda_mediana_responsavel"}, inplace=True)

    return renda_b, renda_d


def carregar_escolas_318_cidades(cidades_com_bairro_ibge: set) -> pd.DataFrame:
    """Escolas elegíveis das 318 cidades, com a coluna 'regiao' já resolvida (bairro ou distrito, por cidade)."""
    end = pd.read_csv(RAW_DIR / "escolas_com_endereco.csv", dtype={"codigo_municipio": str})
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})
    end = end[end["codigo_municipio"].isin(cidades["codigo_municipio"])].copy()
    end = end.merge(cidades[["codigo_municipio", "nome_municipio_ibge", "uf"]], on="codigo_municipio", how="left")

    enem = pd.read_csv(RAW_DIR / "enem_2025_medias_por_escola.csv")
    end = end.merge(
        enem[["codigo_escola", "qtd_participantes_enem", "enem_media_geral"]],
        left_on="CO_ENTIDADE", right_on="codigo_escola", how="left",
    )
    end["confiavel_enem"] = end["qtd_participantes_enem"].fillna(0) >= MIN_PARTICIPANTES_CONFIAVEL

    cod7 = end["codigo_municipio"].str[:7]
    end["nivel_regiao"] = cod7.isin(cidades_com_bairro_ibge).map({True: "bairro", False: "distrito"})
    end["regiao"] = end["NO_BAIRRO"].where(end["nivel_regiao"] == "bairro", end["NO_DISTRITO"])
    end["regiao_norm"] = end["regiao"].apply(normalizar_nome)
    return end


def agregar_por_regiao(escolas: pd.DataFrame) -> pd.DataFrame:
    """Volume + ENEM ponderado por região (bairro OU distrito, a depender da cidade) — só ENEM confiável."""
    conf = escolas[escolas["confiavel_enem"] & escolas["regiao_norm"].notna()].copy()

    def media_ponderada(g: pd.DataFrame) -> float:
        return (g["enem_media_geral"] * g["qtd_participantes_enem"]).sum() / g["qtd_participantes_enem"].sum()

    chave = ["codigo_municipio", "nome_municipio_ibge", "uf", "nivel_regiao", "regiao_norm"]
    linhas = []
    for chaves, g in conf.groupby(chave):
        linhas.append(dict(zip(chave, chaves)) | {
            "regiao": g["regiao"].mode().iat[0],  # forma mais comum de escrita, só pra exibição
            "qtd_escolas_confiaveis": len(g),
            "qtd_participantes_enem": int(g["qtd_participantes_enem"].sum()),
            "enem_ponderado": round(media_ponderada(g), 1),
        })
    agr = pd.DataFrame(linhas)

    volume_total = escolas[escolas["regiao_norm"].notna()].groupby(chave).size().rename("qtd_escolas_elegiveis").reset_index()
    agr = agr.merge(volume_total, on=chave, how="left")
    agr["amostra_significativa"] = agr["qtd_escolas_confiaveis"] >= MIN_ESCOLAS_CONFIAVEIS_PARA_RANK
    return agr


def contar_golden_leads_por_regiao(escolas: pd.DataFrame, agr: pd.DataFrame) -> pd.DataFrame:
    """Quantas Golden Leads existem em cada região."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str})
    ids = escolas[escolas["regiao_norm"].notna()][["CO_ENTIDADE", "codigo_municipio", "regiao_norm"]].copy()
    ids["CO_ENTIDADE"] = ids["CO_ENTIDADE"].astype(str)
    ids = ids.merge(golden[["codigo_escola"]], left_on="CO_ENTIDADE", right_on="codigo_escola", how="inner")
    contagem = ids.groupby(["codigo_municipio", "regiao_norm"]).size().rename("qtd_golden_leads").reset_index()
    agr = agr.merge(contagem, on=["codigo_municipio", "regiao_norm"], how="left")
    agr["qtd_golden_leads"] = agr["qtd_golden_leads"].fillna(0).astype(int)
    return agr


def casar_com_renda(agr: pd.DataFrame, renda_b: pd.DataFrame, renda_d: pd.DataFrame) -> pd.DataFrame:
    """Match exato -> fuzzy (limiar 0.90), usando a tabela de renda certa (bairro ou distrito) por linha."""
    renda_b_por_mun = {cod: g for cod, g in renda_b.groupby("codigo_municipio")}
    renda_d_por_mun = {cod: g for cod, g in renda_d.groupby("codigo_municipio")}

    resultado = []
    for _, row in agr.iterrows():
        tabela = renda_b_por_mun if row["nivel_regiao"] == "bairro" else renda_d_por_mun
        renda_mun = tabela.get(row["codigo_municipio"])
        match, confianca = None, "sem_match"

        if renda_mun is not None:
            exato = renda_mun[renda_mun["nome_norm"] == row["regiao_norm"]]
            if len(exato):
                match, confianca = exato.iloc[0], "exato"
            else:
                candidatos = difflib.get_close_matches(
                    row["regiao_norm"], renda_mun["nome_norm"].tolist(), n=1, cutoff=LIMIAR_FUZZY
                )
                if candidatos:
                    match = renda_mun[renda_mun["nome_norm"] == candidatos[0]].iloc[0]
                    confianca = "fuzzy"

        nova = row.to_dict()
        nova["confianca_match"] = confianca
        nova["renda_media_responsavel"] = match["renda_media_responsavel"] if match is not None else None
        nova["renda_mediana_responsavel"] = match["renda_mediana_responsavel"] if match is not None else None
        resultado.append(nova)

    return pd.DataFrame(resultado)


def exibir_resumo(df: pd.DataFrame) -> None:
    print(f"[Sanity check] Regiões mapeadas nacionalmente: {len(df):,} em {df['codigo_municipio'].nunique()} cidades")
    print(f"[Sanity check] Nível usado: \n{df.drop_duplicates('codigo_municipio')['nivel_regiao'].value_counts()}")
    print(f"\n[Sanity check] Distribuição de confiança do match de renda:\n{df['confianca_match'].value_counts()}")
    taxa = (df["confianca_match"] != "sem_match").mean()
    print(f"[Sanity check] Taxa de match (exato+fuzzy): {taxa * 100:.1f}%")

    sig = df[df["amostra_significativa"] & df["renda_mediana_responsavel"].notna()]
    print(f"\n[Sanity check] Regiões com amostra significativa E renda encontrada: {len(sig):,}")
    print("\n--- Top 15 nacional: regiões ricas com POUCA presença de Golden Leads (renda alta, <=1 lead) ---")
    oportunidade = sig[sig["qtd_golden_leads"] <= 1].sort_values("renda_mediana_responsavel", ascending=False)
    cols = ["nome_municipio_ibge", "uf", "nivel_regiao", "regiao", "renda_mediana_responsavel", "enem_ponderado", "qtd_golden_leads"]
    print(oportunidade[cols].head(15).to_string(index=False))


def main():
    renda_b, renda_d = carregar_renda_ibge()
    cidades_com_bairro_ibge = set(renda_b["codigo_municipio"].unique())

    escolas = carregar_escolas_318_cidades(cidades_com_bairro_ibge)
    agr = agregar_por_regiao(escolas)
    agr = contar_golden_leads_por_regiao(escolas, agr)
    resultado = casar_com_renda(agr, renda_b, renda_d)

    exibir_resumo(resultado)
    resultado = resultado.drop(columns=["regiao_norm"]).sort_values(
        ["nome_municipio_ibge", "renda_mediana_responsavel"], ascending=[True, False]
    )
    resultado.to_csv(OUT_DIR / "17_regioes_nacional_com_renda.csv", index=False)
    print(f"\n[✓] Salvo em {OUT_DIR / '17_regioes_nacional_com_renda.csv'}")


if __name__ == "__main__":
    main()
