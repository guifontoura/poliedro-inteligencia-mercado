"""
Case Poliedro — Passo 14 (bônus, roadmap 2.0): CONSOLIDAR DATASET PARA POWER BI.

Junta as Golden Leads com os dados de cidade (nome, UF, score de
priorização), bairro/distrito/lat-long, renda do bairro (IBGE Censo 2022) e
sistema de ensino já identificado (pesquisa manual, passo 19) num único par
de tabelas prontas para importar no Power BI.

Revisão 23/07 (pedido do Gui: "podemos enriquecer com os dados dos
bairros?"): trocado `05_golden_leads_geocodificadas.csv` (bairro via ViaCEP,
só 139 das 943 escolas, só nas 10 cidades prioritárias) pelo
`NO_BAIRRO`/`NO_DISTRITO`/`LATITUDE`/`LONGITUDE` nativos do Censo Escolar.

Revisão 24/07 (pedido do Gui, 3 itens):
1. "pode aplicar os bairros" — corrige as mesmas variantes de grafia do RJ
   já achadas no passo 15 (RECREIO, IRAJÁ, BARRA OLÍMPICA, FREGUESIA), que
   até agora só valiam pro passo 15/17, não pra este dataset principal.
2. "renda do bairro, tipo 'High Ticket'/'renda alta >5SM'" — reusa a mesma
   lógica de match do passo 17 (bairro quando o IBGE tem, distrito como
   fallback) pra trazer `renda_mediana_responsavel` + uma categoria legível
   (`renda_categoria`). Faixas definidas a partir da distribuição REAL dos
   dados (não um número arbitrário): quartis de renda mediana entre as
   ~2.200 regiões nacionais já casadas no passo 17 — Q1≈1.724, mediana≈2.300,
   Q3≈3.001, P90≈5.000. Por isso: Baixa (<1.800) / Média (1.800-2.999) /
   Média-Alta (3.000-4.999) / Alta (≥5.000).
3. "sistema de ensino ao lado" — junta com
   `19_sistema_ensino_identificado.csv` (passo 19, pesquisa manual em
   andamento); escolas ainda não pesquisadas ficam "Não pesquisado ainda"
   (não fica em branco escondido — deixa explícito que falta pesquisar).

Revisão 24/07 à noite (pedido do Gui, com print do mapa oficial da
Prefeitura/IPP: "no arquivo para subir ao powerbi vamos separar cidade de SP
por distritos [...] na cidade RJ só temos a divisão por bairros. Vc acha que
seria mais eficiente juntar zonas maiores?"): este é o arquivo que ele
efetivamente importa no Power BI — até agora só o `distrito` de SP era real
(`NO_DISTRITO` do Censo funciona bem em SP), o do RJ vinha com o valor
degenerado do Censo (sempre "Rio de Janeiro", ver achado do passo 15). Ao
invés da divisão informal de "zona" (só 4-5 zonas, sem estatuto
administrativo — a pesquisa mostrou fontes divergindo até em quantas
existem), usamos a Região Administrativa (RA) oficial da Prefeitura/IPP: 33
RAs, descritas na Wikipédia como "o que equivale aos distritos de São
Paulo" — mesmo nível de granularidade que SP, mas com validade
administrativa oficial. `distrito` no RJ agora recebe a RA (via o mesmo
crosswalk `RA_POR_BAIRRO_RJ` do passo 15, para não duplicar); uma coluna
`granularidade_geo` deixa explícito que SP usa "distrito" e RJ usa "regiao_administrativa".

Modelo sugerido (ver POWER_BI_GUIA.md):
- `14_escolas_powerbi.csv` (fato): 1 linha por Golden Lead.
- `14_cidades_powerbi.csv` (dimensão, 318 linhas): 1 linha por município do
  recorte, com `top10` como flag booleana pra filtro rápido.
Relacionamento: `codigo_municipio` (N:1, escolas → cidades).

Gera: data/outputs/14_escolas_powerbi.csv, data/outputs/14_cidades_powerbi.csv

Formato do CSV: separador ';' e decimal ',' (padrão brasileiro).
"""

import difflib
import unicodedata
from pathlib import Path

import pandas as pd

from poliedro_15_regioes_sp_rj import RA_POR_BAIRRO_RJ

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

LIMIAR_FUZZY = 0.90

# Mesma correção de grafia do RJ já usada no passo 15/17 — ver lá pro
# raciocínio completo (NO_BAIRRO auto-declarado, mesmo bairro grafado de
# formas diferentes por escolas diferentes).
CORRECOES_BAIRRO_RJ = {
    "RECREIO": "RECREIO DOS BANDEIRANTES",
    "IRAJA": "IRAJÁ",
    "IRAJ": "IRAJÁ",
    "BARRA OLIMPICA": "BARRA DA TIJUCA",
    "BARRA OLÍMPICA": "BARRA DA TIJUCA",
    "FREGUESIA (JACAREPAGUA)": "FREGUESIA (JACAREPAGUÁ)",
    "FREGUESIA JACAREPAGU": "FREGUESIA (JACAREPAGUÁ)",
    "FREGUESIA": "FREGUESIA (JACAREPAGUÁ)",
}


def normalizar_nome(nome) -> str:
    if pd.isna(nome):
        return nome
    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().upper()


def categorizar_renda(valor) -> str:
    """Faixa legível a partir da renda mediana do responsável (ver docstring pra origem dos cortes)."""
    if pd.isna(valor):
        return "Sem dado"
    if valor >= 5000:
        return "Alta (≥ R$ 5.000)"
    if valor >= 3000:
        return "Média-Alta (R$ 3.000-4.999)"
    if valor >= 1800:
        return "Média (R$ 1.800-2.999)"
    return "Baixa (< R$ 1.800)"


def carregar_renda_ibge() -> tuple[pd.DataFrame, pd.DataFrame, set]:
    renda_b = pd.read_csv(RAW_DIR / "renda_bairro_2022.csv", sep=";", encoding="latin-1")
    renda_b["CD_BAIRRO"] = renda_b["CD_BAIRRO"].astype(str)
    renda_b["codigo_municipio"] = renda_b["CD_BAIRRO"].str[:7]
    renda_b["nome_norm"] = renda_b["NM_BAIRRO"].apply(normalizar_nome)

    renda_d = pd.read_csv(RAW_DIR / "renda_distrito_2022.csv", sep=";", encoding="latin-1")
    renda_d["CD_DIST"] = renda_d["CD_DIST"].astype(str)
    renda_d["codigo_municipio"] = renda_d["CD_DIST"].str[:7]
    renda_d["nome_norm"] = renda_d["NM_DIST"].apply(normalizar_nome)

    for df in (renda_b, renda_d):
        df["V06006"] = df["V06006"].astype(str).str.replace(",", ".").astype(float)
        df.rename(columns={"V06006": "renda_mediana_responsavel"}, inplace=True)

    cidades_com_bairro_ibge = set(renda_b["codigo_municipio"].unique())
    return renda_b, renda_d, cidades_com_bairro_ibge


def _buscar(chave, renda_mun) -> "float | None":
    """Match exato -> fuzzy (limiar 0.90) contra uma tabela de renda já filtrada por município."""
    if renda_mun is None or pd.isna(chave):
        return None
    exato = renda_mun[renda_mun["nome_norm"] == chave]
    if len(exato):
        return exato.iloc[0]["renda_mediana_responsavel"]
    candidatos = difflib.get_close_matches(chave, renda_mun["nome_norm"].tolist(), n=1, cutoff=LIMIAR_FUZZY)
    if candidatos:
        return renda_mun[renda_mun["nome_norm"] == candidatos[0]].iloc[0]["renda_mediana_responsavel"]
    return None


def casar_renda_por_escola(escolas: pd.DataFrame, renda_b, renda_d, cidades_com_bairro_ibge) -> pd.Series:
    """Tenta bairro primeiro (mais fino); se não achar (nome não bate — ex.: Ribeirão Preto, onde o
    IBGE cadastra 'Setor Central'/'Subsetor Norte' em vez de bairro popular), cai pra distrito. Corrigido
    24/07 — a primeira versão só caía pra distrito quando a CIDADE inteira não tinha bairro no IBGE, não
    quando o bairro específico da escola não batia dentro de uma cidade que tem outros bairros cadastrados."""
    renda_b_por_mun = {cod: g for cod, g in renda_b.groupby("codigo_municipio")}
    renda_d_por_mun = {cod: g for cod, g in renda_d.groupby("codigo_municipio")}

    valores = []
    for _, row in escolas.iterrows():
        cod_mun = str(row["codigo_municipio"])
        valor = None
        if cod_mun in cidades_com_bairro_ibge:
            valor = _buscar(row["bairro_norm"], renda_b_por_mun.get(cod_mun))
        if valor is None:
            valor = _buscar(row["distrito_norm"], renda_d_por_mun.get(cod_mun))
        valores.append(valor)

    return pd.Series(valores, index=escolas.index)


def montar_tabela_escolas() -> pd.DataFrame:
    """Golden Leads + cidade + bairro corrigido + renda + sistema de ensino identificado."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str, "codigo_municipio": str})
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})[
        ["codigo_municipio", "nome_municipio_ibge", "uf", "score_priorizacao"]
    ]
    geo = pd.read_csv(RAW_DIR / "escolas_com_endereco.csv", dtype={"codigo_municipio": str, "CO_ENTIDADE": str})[
        ["CO_ENTIDADE", "codigo_municipio", "NO_BAIRRO", "NO_DISTRITO", "LATITUDE", "LONGITUDE", "CO_CEP"]
    ].rename(columns={"CO_ENTIDADE": "codigo_escola"})
    geo = geo.drop(columns=["codigo_municipio"])  # já vem de golden, evita duplicar/conflitar

    escolas = golden.merge(cidades, on="codigo_municipio", how="left")
    escolas = escolas.merge(geo, on="codigo_escola", how="left")
    escolas = escolas.rename(
        columns={"nome_municipio_ibge": "cidade", "uf": "UF", "score_priorizacao": "score_priorizacao_cidade",
                 "NO_DISTRITO": "distrito", "CO_CEP": "cep"}
    )

    # 1. Corrige as variantes de grafia conhecidas do RJ (só afeta RJ; resto passa direto).
    escolas["bairro"] = escolas["NO_BAIRRO"].replace(CORRECOES_BAIRRO_RJ)
    escolas = escolas.drop(columns=["NO_BAIRRO"])
    escolas["cep"] = escolas["cep"].astype("Int64")

    # 1b. RJ: substitui o `distrito` degenerado do Censo (sempre "Rio de
    # Janeiro") pela Região Administrativa oficial (mesmo crosswalk do passo
    # 15) — pedido do Gui pra separar RJ em regiões maiores no Power BI, do
    # mesmo jeito que SP já é separado por distrito real.
    ra_normalizado = {normalizar_nome(k): v for k, v in RA_POR_BAIRRO_RJ.items()}
    eh_rj = escolas["cidade"] == "Rio de Janeiro"
    ra_da_escola = escolas.loc[eh_rj, "bairro"].apply(normalizar_nome).map(ra_normalizado)
    sem_ra = ra_da_escola.isna().sum()
    if sem_ra:
        bairros_sem_ra = sorted(escolas.loc[eh_rj][ra_da_escola.isna()]["bairro"].unique().tolist())
        print(f"[Sanity check] {sem_ra} escolas do RJ sem RA mapeada (bairro não reconhecido, "
              f"mantido o distrito original do Censo): {bairros_sem_ra}")
    escolas.loc[eh_rj, "distrito"] = ra_da_escola.where(ra_da_escola.notna(), escolas.loc[eh_rj, "distrito"])
    escolas["granularidade_geo"] = escolas["cidade"].map(
        {"São Paulo": "distrito", "Rio de Janeiro": "regiao_administrativa"}
    ).fillna("nao_aplicavel")

    # 2. Renda por bairro/distrito (IBGE Censo 2022).
    escolas["bairro_norm"] = escolas["bairro"].apply(normalizar_nome)
    escolas["distrito_norm"] = escolas["distrito"].apply(normalizar_nome)
    renda_b, renda_d, cidades_com_bairro_ibge = carregar_renda_ibge()
    escolas["renda_mediana_responsavel"] = casar_renda_por_escola(escolas, renda_b, renda_d, cidades_com_bairro_ibge)
    escolas["renda_categoria"] = escolas["renda_mediana_responsavel"].apply(categorizar_renda)
    escolas = escolas.drop(columns=["bairro_norm", "distrito_norm"])

    # 3. Sistema de ensino identificado (passo 19, pesquisa manual em andamento).
    sistema_path = OUT_DIR / "19_sistema_ensino_identificado.csv"
    if sistema_path.exists():
        sistema = pd.read_csv(sistema_path, sep=";", decimal=",", dtype={"codigo_escola": str})[
            ["codigo_escola", "sistema_ensino_identificado", "confianca"]
        ]
        escolas = escolas.merge(sistema, on="codigo_escola", how="left")
        escolas["sistema_ensino_identificado"] = escolas["sistema_ensino_identificado"].fillna("Não pesquisado ainda")
        escolas["confianca"] = escolas["confianca"].fillna("nao_pesquisado")

    return escolas


def montar_tabela_cidades() -> pd.DataFrame:
    """Todas as 318 cidades do recorte, com rank e flag Top10 pra filtro rápido no Power BI."""
    cidades = pd.read_csv(OUT_DIR / "01_cidades_prioritarias.csv").sort_values(
        "score_priorizacao", ascending=False
    ).reset_index(drop=True)
    cidades["rank_cidade"] = cidades.index + 1
    cidades["top10"] = cidades["rank_cidade"] <= 10
    return cidades


def exibir_resumo(escolas: pd.DataFrame, cidades: pd.DataFrame) -> None:
    print(f"[Sanity check] Escolas: {len(escolas):,} | Cidades: {len(cidades):,}")
    print(f"[Sanity check] Escolas com bairro: {escolas['bairro'].notna().sum():,} "
          f"({escolas['bairro'].notna().mean() * 100:.1f}%)")
    print(f"[Sanity check] Escolas com renda encontrada: {escolas['renda_mediana_responsavel'].notna().sum():,} "
          f"({escolas['renda_mediana_responsavel'].notna().mean() * 100:.1f}%)")
    rj = escolas[escolas["cidade"] == "Rio de Janeiro"]
    if len(rj):
        print(f"[Sanity check] RJ: {rj['distrito'].nunique()} Regiões Administrativas distintas "
              f"em {len(rj)} escolas (era 1 valor degenerado 'Rio de Janeiro' antes da correção)")
    print(f"[Sanity check] Distribuição renda_categoria:\n{escolas['renda_categoria'].value_counts()}")
    if "sistema_ensino_identificado" in escolas.columns:
        pesquisadas = (escolas["sistema_ensino_identificado"] != "Não pesquisado ainda").sum()
        print(f"[Sanity check] Escolas com sistema de ensino pesquisado: {pesquisadas:,} "
              f"({pesquisadas / len(escolas) * 100:.1f}%)")
    print(f"[Sanity check] Segmentos: {escolas['segmento_comercial'].value_counts().to_dict()}")


def main():
    escolas = montar_tabela_escolas()
    cidades = montar_tabela_cidades()
    exibir_resumo(escolas, cidades)
    escolas.to_csv(OUT_DIR / "14_escolas_powerbi.csv", index=False, sep=";", decimal=",")
    cidades.to_csv(OUT_DIR / "14_cidades_powerbi.csv", index=False, sep=";", decimal=",")
    print(f"[✓] Salvo em {OUT_DIR / '14_escolas_powerbi.csv'} e {OUT_DIR / '14_cidades_powerbi.csv'}")


if __name__ == "__main__":
    main()
