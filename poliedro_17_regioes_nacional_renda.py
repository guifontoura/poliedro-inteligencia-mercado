"""
Case Poliedro — Passo 17 (roadmap 3.0, pedido do Gui em 24/07: "vamos começar
a escalar para todas as 318 cidades"): REGIÃO + RENDA EM ESCALA NACIONAL.

SEGUNDA correção de rumo (24/07 à noite, Gui pediu pra investigar a fundo —
valeu a pena, achou um problema real na primeira versão). A primeira versão
deste script (commit anterior) tinha uma falha conceitual: quando a cidade
não tinha bairro cadastrado no produto de RENDA do IBGE (128 das 318), o
script caía pra agrupar as próprias escolas por `NO_DISTRITO` — mas
`NO_DISTRITO` no Censo Escolar é degenerado em 86,8% dos casos NACIONALMENTE
(4.903 de 5.647 escolas têm `NO_DISTRITO` == nome do próprio município,
porque a "sede" do município tecnicamente é o nome do município mesmo, ou
porque a escola preencheu errado). Isso colapsava cidades inteiras — como
Campinas — numa única linha "Campinas: 47 escolas", escondendo bairros reais
como Cambuí que a própria escola já declarou certinho.

Investigação (a pedido do Gui, "investigue a fundo"): comparamos a
qualidade de `NO_BAIRRO` vs `NO_DISTRITO` no Censo Escolar, nacionalmente:
  - NO_BAIRRO: só 62 de 5.647 vazios (1,1%), só 3 iguais ao nome do
    município — é um campo BOM. Campinas sozinha tem Cambuí, Taquaral,
    Barão Geraldo, Botafogo, Vila Brandina etc. todos discriminados.
  - NO_DISTRITO: 4.903 de 5.647 (86,8%) iguais ao nome do município — é o
    campo RUIM (mesmo problema que já tínhamos achado isolado no Rio).
Conclusão: o gargalo nunca foi a qualidade do NOSSO dado de bairro — é que
o produto de RENDA do IBGE só publica renda por bairro em 190 das 318
cidades (ver primeira versão do docstring). A correção certa não é trocar
de unidade de agrupamento (isso jogava fora dado bom); é separar duas
responsabilidades:
  1. Agrupar ENEM/volume/leads por BAIRRO sempre (`NO_BAIRRO`, universal,
     confiável) — nunca mais por distrito.
  2. Casar com renda no melhor nível que o IBGE tiver PRA CADA CIDADE: bairro
     quando existir (190 cidades) — match fino, um valor de renda por
     bairro; senão, distrito (as 318 têm) — nesse caso o valor de renda é
     mais grosseiro (às vezes a cidade inteira como "1 distrito" — não é
     erro, é a granularidade real que existe pra essa cidade), e a coluna
     `nivel_renda` deixa isso explícito, nunca escondido.

Resultado prático: Campinas agora aparece com os bairros reais (Cambuí,
Taquaral, Barão Geraldo...) com ENEM e volume por bairro — só a RENDA que
fica no nível de distrito (mais grosseira) pra essa cidade específica,
porque é o que o IBGE oferece lá.

Mitigação de inconsistência de nome (grafia, ex. "RECREIO" vs "RECREIO DOS
BANDEIRANTES") em escala nacional: match em duas camadas — exato após
normalizar (maiúsculo, sem acento), depois fuzzy (difflib, limiar 0.90)
contra a lista oficial do IBGE do mesmo município. `confianca_match` fica
registrado por linha.

Limitação que segue documentada, não escondida: fuzzy match não é perfeito;
renda mede o RESPONSÁVEL pelo domicílio, não per capita; e quando o nível de
renda é "distrito" numa cidade pequena, o valor pode representar a cidade
inteira, não aquele bairro específico — checar a coluna `nivel_renda` antes
de usar num argumento de precisão fina.

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


def carregar_escolas_318_cidades() -> pd.DataFrame:
    """Escolas elegíveis das 318 cidades, sempre com bairro como unidade (campo confiável nacionalmente)."""
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
    end["bairro_norm"] = end["NO_BAIRRO"].apply(normalizar_nome)
    end["distrito_norm"] = end["NO_DISTRITO"].apply(normalizar_nome)
    return end


def agregar_por_bairro(escolas: pd.DataFrame) -> pd.DataFrame:
    """Volume + ENEM ponderado por BAIRRO (sempre) — só entre escolas com ENEM confiável."""
    conf = escolas[escolas["confiavel_enem"] & escolas["bairro_norm"].notna()].copy()

    def media_ponderada(g: pd.DataFrame) -> float:
        return (g["enem_media_geral"] * g["qtd_participantes_enem"]).sum() / g["qtd_participantes_enem"].sum()

    chave = ["codigo_municipio", "nome_municipio_ibge", "uf", "bairro_norm"]
    linhas = []
    for chaves, g in conf.groupby(chave):
        linhas.append(dict(zip(chave, chaves)) | {
            "bairro": g["NO_BAIRRO"].mode().iat[0],
            "distrito_mais_comum": g["distrito_norm"].mode().iat[0] if g["distrito_norm"].notna().any() else None,
            "qtd_escolas_confiaveis": len(g),
            "qtd_participantes_enem": int(g["qtd_participantes_enem"].sum()),
            "enem_ponderado": round(media_ponderada(g), 1),
        })
    agr = pd.DataFrame(linhas)

    volume_total = escolas[escolas["bairro_norm"].notna()].groupby(chave).size().rename("qtd_escolas_elegiveis").reset_index()
    agr = agr.merge(volume_total, on=chave, how="left")
    agr["amostra_significativa"] = agr["qtd_escolas_confiaveis"] >= MIN_ESCOLAS_CONFIAVEIS_PARA_RANK
    return agr


def contar_golden_leads_por_bairro(escolas: pd.DataFrame, agr: pd.DataFrame) -> pd.DataFrame:
    """Quantas Golden Leads existem em cada bairro."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str})
    ids = escolas[escolas["bairro_norm"].notna()][["CO_ENTIDADE", "codigo_municipio", "bairro_norm"]].copy()
    ids["CO_ENTIDADE"] = ids["CO_ENTIDADE"].astype(str)
    ids = ids.merge(golden[["codigo_escola"]], left_on="CO_ENTIDADE", right_on="codigo_escola", how="inner")
    contagem = ids.groupby(["codigo_municipio", "bairro_norm"]).size().rename("qtd_golden_leads").reset_index()
    agr = agr.merge(contagem, on=["codigo_municipio", "bairro_norm"], how="left")
    agr["qtd_golden_leads"] = agr["qtd_golden_leads"].fillna(0).astype(int)
    return agr


def casar_com_renda(agr: pd.DataFrame, renda_b: pd.DataFrame, renda_d: pd.DataFrame) -> pd.DataFrame:
    """Renda no melhor nível disponível por cidade: bairro (fino) se o IBGE tiver, senão distrito (mais grosseiro)."""
    cidades_com_bairro_ibge = set(renda_b["codigo_municipio"].unique())
    renda_b_por_mun = {cod: g for cod, g in renda_b.groupby("codigo_municipio")}
    renda_d_por_mun = {cod: g for cod, g in renda_d.groupby("codigo_municipio")}

    def buscar(chave, renda_mun):
        if renda_mun is None or pd.isna(chave):
            return None, "sem_match"
        exato = renda_mun[renda_mun["nome_norm"] == chave]
        if len(exato):
            return exato.iloc[0], "exato"
        candidatos = difflib.get_close_matches(chave, renda_mun["nome_norm"].tolist(), n=1, cutoff=LIMIAR_FUZZY)
        if candidatos:
            return renda_mun[renda_mun["nome_norm"] == candidatos[0]].iloc[0], "fuzzy"
        return None, "sem_match"

    resultado = []
    for _, row in agr.iterrows():
        cod_mun = row["codigo_municipio"]
        match, confianca, nivel_renda = None, "sem_match", "distrito (aproximado)"

        # Corrigido 24/07 (mesmo bug achado no passo 14 via Ribeirão Preto):
        # tenta bairro primeiro SEMPRE que a cidade tem bairro cadastrado no
        # IBGE; só cai pra distrito se esse match específico falhar (nome não
        # bate — ex.: IBGE cadastra "Setor Central" em vez do bairro popular)
        # — antes só caía pra distrito quando a cidade INTEIRA não tinha
        # bairro, perdendo casos onde o bairro existe mas não bate o nome.
        if cod_mun in cidades_com_bairro_ibge:
            match, confianca = buscar(row["bairro_norm"], renda_b_por_mun.get(cod_mun))
            if match is not None:
                nivel_renda = "bairro"
        if match is None:
            match, confianca = buscar(row["distrito_mais_comum"], renda_d_por_mun.get(cod_mun))

        nova = row.to_dict()
        nova["nivel_renda"] = nivel_renda
        nova["confianca_match"] = confianca
        nova["renda_media_responsavel"] = match["renda_media_responsavel"] if match is not None else None
        nova["renda_mediana_responsavel"] = match["renda_mediana_responsavel"] if match is not None else None
        resultado.append(nova)

    return pd.DataFrame(resultado)


def exibir_resumo(df: pd.DataFrame) -> None:
    print(f"[Sanity check] Bairros mapeados nacionalmente: {len(df):,} em {df['codigo_municipio'].nunique()} cidades")
    print(f"\n[Sanity check] Nível de renda usado (bairro fino vs distrito grosseiro):\n{df['nivel_renda'].value_counts()}")
    print(f"\n[Sanity check] Distribuição de confiança do match de renda:\n{df['confianca_match'].value_counts()}")
    taxa = (df["confianca_match"] != "sem_match").mean()
    print(f"[Sanity check] Taxa de match (exato+fuzzy): {taxa * 100:.1f}%")

    print("\n--- Campinas (exemplo puxado pelo Gui — antes virava 1 linha só, agora mostra os bairros reais) ---")
    camp = df[df["nome_municipio_ibge"] == "Campinas"].sort_values("renda_mediana_responsavel", ascending=False)
    cols = ["bairro", "nivel_renda", "renda_mediana_responsavel", "enem_ponderado", "qtd_escolas_elegiveis", "qtd_golden_leads"]
    print(camp[cols].head(10).to_string(index=False))

    sig = df[df["amostra_significativa"] & df["renda_mediana_responsavel"].notna()]
    print(f"\n[Sanity check] Bairros com amostra significativa E renda encontrada: {len(sig):,}")
    print("\n--- Top 15 nacional: bairros ricos com POUCA presença de Golden Leads (renda alta, <=1 lead) ---")
    oportunidade = sig[sig["qtd_golden_leads"] <= 1].sort_values("renda_mediana_responsavel", ascending=False)
    cols2 = ["nome_municipio_ibge", "uf", "bairro", "nivel_renda", "renda_mediana_responsavel", "enem_ponderado", "qtd_golden_leads"]
    print(oportunidade[cols2].head(15).to_string(index=False))


def main():
    renda_b, renda_d = carregar_renda_ibge()
    escolas = carregar_escolas_318_cidades()
    agr = agregar_por_bairro(escolas)
    agr = contar_golden_leads_por_bairro(escolas, agr)
    resultado = casar_com_renda(agr, renda_b, renda_d)

    exibir_resumo(resultado)
    resultado = resultado.drop(columns=["bairro_norm", "distrito_mais_comum"]).sort_values(
        ["nome_municipio_ibge", "renda_mediana_responsavel"], ascending=[True, False]
    )
    # sep=';' e decimal=',' — formato brasileiro, pro Power BI Desktop reconhecer os decimais.
    resultado.to_csv(OUT_DIR / "17_regioes_nacional_com_renda.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '17_regioes_nacional_com_renda.csv'}")


if __name__ == "__main__":
    main()
