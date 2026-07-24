"""
Case Poliedro — Passo 15 (bônus, pedido pela recrutadora na entrevista de
23/07: "SP e RJ são praças importantes, como delimitar range de influência
por região?"): DETALHAMENTO REGIONAL EM SÃO PAULO E RIO DE JANEIRO.

Nome do arquivo revisado (23/07, feedback do Gui): "distrito" não descreve
bem o que o script faz — só São Paulo usa distrito como unidade; Rio de
Janeiro usa bairro. "Regiões" é o nome correto e genérico, já que a unidade
de agregação varia por cidade (ver abaixo o motivo).

Por que a unidade varia por cidade: testamos distrito e bairro nas duas.
Bairro é mais granular (o nome que a família reconhece), mas em muitos casos
tem só 1-2 escolas — ranking com amostra tão pequena é ruído, não sinal
(mesmo problema que já motivou o piso de 10 participantes ENEM pra
"confiável" em outras partes do projeto). Distrito é a divisão administrativa
oficial, mais grosseira, estatisticamente mais estável — seria a escolha
padrão se estivesse disponível em ambas as cidades.

Descoberta ao rodar (23/07): São Paulo e Rio de Janeiro NÃO têm a mesma
estrutura no Censo. São Paulo tem `NO_DISTRITO` de verdade (88 distritos
distintos entre as escolas elegíveis). Rio de Janeiro tem `NO_DISTRITO`
igual a "Rio de Janeiro" pra 100% das escolas — o campo não é subdividido
ali, só existe bairro.

Revisão 24/07 (Gui: "acha mais eficiente juntar em zonas maiores?"): sim,
mas usando a Região Administrativa (RA) OFICIAL da Prefeitura do Rio, não a
"zona" informal (Zona Sul/Norte/Oeste/Central — só 4-5 categorias, grosseiro
demais, sem força administrativa). RA é o equivalente oficial ao distrito de
São Paulo (citação da Wikipédia: "o que equivale aos distritos de São
Paulo") — 33 no total, mesma ordem de grandeza dos 88 distritos de SP.
Tabela bairro→RA vinda da Wikipédia ("Regiões administrativas da cidade do
Rio de Janeiro", fonte oficial: Prefeitura/IPP). Cada linha do CSV de saída
tem uma coluna `granularidade` avisando qual unidade está sendo usada
(distrito em SP, regiao_administrativa no RJ).

Limitação importante (documentada, não escondida): o score_priorizacao da
Parte 1 usa 3 componentes (40% renda, 30% volume, 30% ENEM). Aqui só
conseguimos volume + ENEM — renda domiciliar per capita do IBGE (Tabela
10296) só existe no nível de município, não de distrito/bairro. Por isso
este script NÃO gera um "score" único comparável ao score_priorizacao — mostra
os dois componentes disponíveis lado a lado, sem forçar um peso artificial
pro terceiro que não temos. Renda por região é o próximo passo (setor
censitário IBGE, roadmap 3.0, ver poliedro_16).

Teste de sanidade (23/07): comparamos os distritos de maior ENEM ponderado
em São Paulo com a média da cidade #1 do ranking nacional (Belo Horizonte,
646,2). Vila Mariana (701,8) e Moema (679,0) sozinhos já superam Belo
Horizonte inteira — evidência concreta de que o score de São Paulo (29º
lugar nacional) é diluição de escala, não fraqueza real da praça.

Gera: data/outputs/15_regioes_sp_rj.csv
"""

import unicodedata
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

MUNICIPIOS_ALVO = {"3550308": "São Paulo", "3304557": "Rio de Janeiro"}
MIN_ESCOLAS_CONFIAVEIS_PARA_RANK = 3
MIN_PARTICIPANTES_CONFIAVEL = 10


def _sem_acento(texto) -> str:
    """Maiúsculo + sem acento — usado só pra CASAR chaves (RA_POR_BAIRRO_RJ foi digitado com acentuação
    inconsistente); o valor exibido (`regiao`) continua vindo do dicionário original, com acento certo."""
    if pd.isna(texto):
        return texto
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii").strip().upper()

# Correções de nome de bairro no RJ (24/07, achado ao cruzar com renda IBGE
# no passo 16): NO_BAIRRO é auto-declarado por cada escola no Censo, então o
# MESMO bairro real aparece grafado de formas diferentes — fragmentando o
# agrupamento por região (ex.: 4 escolas em "RECREIO DOS BANDEIRANTES" e 1
# em "RECREIO" viravam 2 linhas separadas). Corrigido caso a caso, com fonte:
#   - RECREIO -> RECREIO DOS BANDEIRANTES (nome oficial, é o mesmo bairro)
#   - IRAJA / IRAJ -> IRAJÁ (sem acento / truncado no Censo)
#   - BARRA OLIMPICA / BARRA OLÍMPICA -> BARRA DA TIJUCA ("Barra Olímpica"
#     não é bairro oficial do IBGE, é nome popular de uma região dentro de
#     Barra da Tijuca — confirmado: não existe na lista de bairros do IBGE)
#   - FREGUESIA (JACAREPAGUA) -> FREGUESIA (JACAREPAGUÁ) (sem acento)
#   - FREGUESIA JACAREPAGU -> FREGUESIA (JACAREPAGUÁ) (truncado no Censo)
#   - FREGUESIA (bare, sem qualificador) -> FREGUESIA (JACAREPAGUÁ):
#     ASSUNÇÃO documentada, não confirmada — existem duas Freguesias no Rio
#     (Jacarepaguá e Ilha do Governador), e o Censo já tem "FREGUESIA (ILHA
#     DO GOVERNADOR)" como valor próprio quando é essa; assumimos que a
#     forma bare se refere à de Jacarepaguá (a mais populosa/mais citada).
#     Afeta só 5 das 465 escolas do RJ — baixo risco, mas fica registrado.
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

# Revisão 24/07 (Gui: "no RJ só temos bairro, acha mais eficiente juntar em
# zonas maiores?"): SIM, mas Região Administrativa (RA) oficial da Prefeitura
# — não a "zona" informal (só 4-5 zonas, grosseiro demais e sem força
# administrativa real). RA é o equivalente oficial ao distrito de SP ("o que
# equivale aos distritos de São Paulo" — Wikipédia), 33 no total, mesma
# ordem de grandeza que os 92 distritos de SP. Fonte: Wikipédia "Regiões
# administrativas da cidade do Rio de Janeiro" (tabela oficial bairro→RA).
# Bairros que não aparecem aqui (favelas/loteamentos não listados na tabela,
# ou grafias que a correção acima não cobre) ficam sem RA — não inventamos.
RA_POR_BAIRRO_RJ = {
    "ANIL": "XVI Jacarepaguá", "CURICICA": "XVI Jacarepaguá", "FREGUESIA (JACAREPAGUÁ)": "XVI Jacarepaguá",
    "GARDENIA AZUL": "XVI Jacarepaguá", "JACAREPAGUA": "XVI Jacarepaguá", "PECHINCHA": "XVI Jacarepaguá",
    "PRACA SECA": "XVI Jacarepaguá", "TANQUE": "XVI Jacarepaguá", "TAQUARA": "XVI Jacarepaguá",
    "VILA VALQUEIRE": "XVI Jacarepaguá",
    "BARRA DA TIJUCA": "XXIV Barra da Tijuca", "CAMORIM": "XXIV Barra da Tijuca", "GRUMARI": "XXIV Barra da Tijuca",
    "ITANHANGA": "XXIV Barra da Tijuca", "JOA": "XXIV Barra da Tijuca",
    "RECREIO DOS BANDEIRANTES": "XXIV Barra da Tijuca", "VARGEM GRANDE": "XXIV Barra da Tijuca",
    "VARGEM PEQUENA": "XXIV Barra da Tijuca",
    "CIDADE DE DEUS": "XXXIV Cidade de Deus",
    "CAJU": "I Portuária", "GAMBOA": "I Portuária", "SANTO CRISTO": "I Portuária", "SAUDE": "I Portuária",
    "CENTRO": "II Centro", "GLORIA": "II Centro", "LAPA": "II Centro",
    "CATUMBI": "III Rio Comprido", "CIDADE NOVA": "III Rio Comprido", "ESTACIO": "III Rio Comprido",
    "RIO COMPRIDO": "III Rio Comprido",
    "SANTA TERESA": "XXIII Santa Teresa",
    "BENFICA": "VII São Cristóvão", "MANGUEIRA": "VII São Cristóvão", "SAO CRISTOVAO": "VII São Cristóvão",
    "VASCO DA GAMA": "VII São Cristóvão",
    "PAQUETA": "XXI Ilha de Paquetá",
    "ALTO DA BOA VISTA": "VIII Tijuca", "PRACA DA BANDEIRA": "VIII Tijuca", "TIJUCA": "VIII Tijuca",
    "ANDARAI": "IX Vila Isabel", "GRAJAU": "IX Vila Isabel", "MARACANA": "IX Vila Isabel",
    "VILA ISABEL": "IX Vila Isabel",
    "ABOLICAO": "XIII Méier", "AGUA SANTA": "XIII Méier", "CACHAMBI": "XIII Méier", "ENCANTADO": "XIII Méier",
    "ENGENHO DE DENTRO": "XIII Méier", "ENGENHO NOVO": "XIII Méier", "JACARE": "XIII Méier",
    "LINS DE VASCONCELOS": "XIII Méier", "MEIER": "XIII Méier", "PIEDADE": "XIII Méier", "PILARES": "XIII Méier",
    "RIACHUELO": "XIII Méier", "ROCHA": "XIII Méier", "SAMPAIO": "XIII Méier",
    "SAO FRANCISCO XAVIER": "XIII Méier", "TODOS OS SANTOS": "XIII Méier",
    "CIDADE UNIVERSITARIA": "XX Ilha do Governador", "BANCARIOS": "XX Ilha do Governador",
    "CACUIA": "XX Ilha do Governador", "COCOTA": "XX Ilha do Governador",
    "FREGUESIA (ILHA DO GOVERNADOR)": "XX Ilha do Governador", "GALEAO": "XX Ilha do Governador",
    "JARDIM CARIOCA": "XX Ilha do Governador", "JARDIM GUANABARA": "XX Ilha do Governador",
    "MONERO": "XX Ilha do Governador", "PITANGUEIRAS": "XX Ilha do Governador",
    "PORTUGUESA": "XX Ilha do Governador", "PRAIA DA BANDEIRA": "XX Ilha do Governador",
    "RIBEIRA": "XX Ilha do Governador", "TAUA": "XX Ilha do Governador", "ZUMBI": "XX Ilha do Governador",
    "BOTAFOGO": "IV Botafogo", "CATETE": "IV Botafogo", "COSME VELHO": "IV Botafogo",
    "FLAMENGO": "IV Botafogo", "HUMAITA": "IV Botafogo", "LARANJEIRAS": "IV Botafogo", "URCA": "IV Botafogo",
    "COPACABANA": "V Copacabana", "LEME": "V Copacabana",
    "GAVEA": "VI Lagoa", "IPANEMA": "VI Lagoa", "JARDIM BOTANICO": "VI Lagoa", "LAGOA": "VI Lagoa",
    "LEBLON": "VI Lagoa", "SAO CONRADO": "VI Lagoa", "VIDIGAL": "VI Lagoa",
    "ROCINHA": "XXVII Rocinha",
    "BONSUCESSO": "X Ramos", "MANGUINHOS": "X Ramos", "OLARIA": "X Ramos", "RAMOS": "X Ramos",
    "BRAS DE PINA": "XI Penha", "PENHA": "XI Penha", "PENHA CIRCULAR": "XI Penha",
    "DEL CASTILHO": "XII Inhaúma", "ENGENHO DA RAINHA": "XII Inhaúma", "INHAUMA": "XII Inhaúma",
    "HIGIENOPOLIS": "XII Inhaúma", "MARIA DA GRACA": "XII Inhaúma", "TOMAS COELHO": "XII Inhaúma",
    "COLEGIO": "XIV Irajá", "IRAJÁ": "XIV Irajá", "VICENTE DE CARVALHO": "XIV Irajá",
    "VILA DA PENHA": "XIV Irajá", "VILA KOSMOS": "XIV Irajá", "VISTA ALEGRE": "XIV Irajá",
    "BENTO RIBEIRO": "XV Madureira", "CAMPINHO": "XV Madureira", "CASCADURA": "XV Madureira",
    "CAVALCANTI": "XV Madureira", "ENGENHEIRO LEAL": "XV Madureira", "HONORIO GURGEL": "XV Madureira",
    "MADUREIRA": "XV Madureira", "MARECHAL HERMES": "XV Madureira", "OSWALDO CRUZ": "XV Madureira",
    "QUINTINO BOCAIUVA": "XV Madureira", "ROCHA MIRANDA": "XV Madureira", "TURIACU": "XV Madureira",
    "VAZ LOBO": "XV Madureira",
    "ANCHIETA": "XXII Anchieta", "GUADALUPE": "XXII Anchieta", "PARQUE ANCHIETA": "XXII Anchieta",
    "RICARDO DE ALBUQUERQUE": "XXII Anchieta",
    "ACARI": "XXV Pavuna", "BARROS FILHO": "XXV Pavuna", "COELHO NETO": "XXV Pavuna",
    "COSTA BARROS": "XXV Pavuna", "PARQUE COLUMBIA": "XXV Pavuna", "PAVUNA": "XXV Pavuna",
    "JACAREZINHO": "XXVIII Jacarezinho",
    "COMPLEXO DO ALEMAO": "XXIX Complexo do Alemão",
    "MARE": "XXX Maré",
    "CORDOVIL": "XXXI Vigário Geral", "JARDIM AMERICA": "XXXI Vigário Geral",
    "PARADA DE LUCAS": "XXXI Vigário Geral", "VIGARIO GERAL": "XXXI Vigário Geral",
    "BANGU": "XVII Bangu", "GERICINO": "XVII Bangu", "JABOUR": "XVII Bangu", "PADRE MIGUEL": "XVII Bangu",
    "SENADOR CAMARA": "XVII Bangu", "VILA KENNEDY": "XVII Bangu",
    "CAMPO GRANDE": "XVIII Campo Grande", "COSMOS": "XVIII Campo Grande", "INHOAIBA": "XVIII Campo Grande",
    "SANTISSIMO": "XVIII Campo Grande", "SENADOR VASCONCELOS": "XVIII Campo Grande",
    "PACIENCIA": "XIX Santa Cruz", "SANTA CRUZ": "XIX Santa Cruz", "SEPETIBA": "XIX Santa Cruz",
    "BARRA DE GUARATIBA": "XXVI Guaratiba", "GUARATIBA": "XXVI Guaratiba",
    "ILHA DE GUARATIBA": "XXVI Guaratiba", "PEDRA DE GUARATIBA": "XXVI Guaratiba",
    "CAMPO DOS AFONSOS": "XXXIII Realengo", "DEODORO": "XXXIII Realengo", "JARDIM SULACAP": "XXXIII Realengo",
    "MAGALHAES BASTOS": "XXXIII Realengo", "REALENGO": "XXXIII Realengo", "VILA MILITAR": "XXXIII Realengo",
}


def carregar_escolas_sp_rj() -> pd.DataFrame:
    """Escolas elegíveis de SP e RJ, com região (distrito ou bairro, a depender da cidade) e médias ENEM."""
    end = pd.read_csv(RAW_DIR / "escolas_com_endereco.csv", dtype={"codigo_municipio": str})
    end = end[end["codigo_municipio"].isin(MUNICIPIOS_ALVO)].copy()
    end["cidade"] = end["codigo_municipio"].map(MUNICIPIOS_ALVO)

    enem = pd.read_csv(RAW_DIR / "enem_2025_medias_por_escola.csv")
    end = end.merge(
        enem[["codigo_escola", "qtd_participantes_enem", "enem_media_geral"]],
        left_on="CO_ENTIDADE", right_on="codigo_escola", how="left",
    )
    end["confiavel_enem"] = end["qtd_participantes_enem"].fillna(0) >= MIN_PARTICIPANTES_CONFIAVEL

    # NO_DISTRITO é degenerado no Rio de Janeiro (100% das escolas caem em
    # "Rio de Janeiro", 1 valor só) — o campo simplesmente não é subdividido
    # ali no Censo. Em São Paulo, NO_DISTRITO é real (88 distritos
    # distintos). Então usamos uma unidade de agregação por cidade: distrito
    # pra São Paulo, bairro pra Rio de Janeiro — e marcamos qual é qual numa
    # coluna própria, pra não escondermos a diferença de fonte.
    end["granularidade"] = end["cidade"].map({"São Paulo": "distrito", "Rio de Janeiro": "regiao_administrativa"})
    bairro_corrigido = end["NO_BAIRRO"].replace(CORRECOES_BAIRRO_RJ)
    # Normaliza (maiúsculo, sem acento) dos dois lados antes de casar — o
    # RA_POR_BAIRRO_RJ foi digitado à mão a partir da Wikipédia com acentos
    # inconsistentes, e o NO_BAIRRO bruto do Censo vem acentuado; casar sem
    # normalizar os dois lados perdia ~55 escolas por causa só de acento.
    ra_normalizado = {_sem_acento(k): v for k, v in RA_POR_BAIRRO_RJ.items()}
    regiao_administrativa = bairro_corrigido.apply(_sem_acento).map(ra_normalizado)
    end["regiao"] = end["NO_DISTRITO"].where(end["cidade"] == "São Paulo", regiao_administrativa)
    return end


def agregar_por_regiao(escolas: pd.DataFrame) -> pd.DataFrame:
    """Volume + ENEM ponderado por região (distrito em SP, bairro no RJ) — só entre escolas com ENEM confiável."""
    conf = escolas[escolas["confiavel_enem"]].copy()

    def media_ponderada(g: pd.DataFrame) -> float:
        return (g["enem_media_geral"] * g["qtd_participantes_enem"]).sum() / g["qtd_participantes_enem"].sum()

    linhas = []
    for (cidade, regiao), g in conf.groupby(["cidade", "regiao"]):
        linhas.append({
            "cidade": cidade,
            "granularidade": g["granularidade"].iloc[0],
            "regiao": regiao,
            "qtd_escolas_confiaveis": len(g),
            "qtd_participantes_enem": int(g["qtd_participantes_enem"].sum()),
            "enem_ponderado": round(media_ponderada(g), 1),
        })
    dist = pd.DataFrame(linhas)

    # volume total de escolas elegíveis (não só confiáveis) — contexto de mercado
    volume_total = escolas.groupby(["cidade", "regiao"]).size().rename("qtd_escolas_elegiveis").reset_index()
    dist = dist.merge(volume_total, on=["cidade", "regiao"], how="left")

    dist["amostra_significativa"] = dist["qtd_escolas_confiaveis"] >= MIN_ESCOLAS_CONFIAVEIS_PARA_RANK
    dist["rank_enem_na_cidade"] = dist.groupby("cidade")["enem_ponderado"].rank(ascending=False, method="min")
    dist["rank_volume_na_cidade"] = dist.groupby("cidade")["qtd_escolas_elegiveis"].rank(ascending=False, method="min")
    return dist


def contar_golden_leads_por_regiao(escolas: pd.DataFrame, dist: pd.DataFrame) -> pd.DataFrame:
    """Quantas Golden Leads (universo comercial, 04) existem em cada região."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str})
    escolas_ids = escolas[["CO_ENTIDADE", "cidade", "regiao"]].copy()
    escolas_ids["CO_ENTIDADE"] = escolas_ids["CO_ENTIDADE"].astype(str)
    escolas_ids = escolas_ids.merge(golden[["codigo_escola"]], left_on="CO_ENTIDADE", right_on="codigo_escola", how="inner")
    contagem = escolas_ids.groupby(["cidade", "regiao"]).size().rename("qtd_golden_leads").reset_index()
    return dist.merge(contagem, on=["cidade", "regiao"], how="left").fillna({"qtd_golden_leads": 0})


def exibir_resumo(dist: pd.DataFrame) -> None:
    print(f"[Sanity check] Regiões mapeadas: {len(dist)} ({dist['cidade'].value_counts().to_dict()})")
    print(f"[Sanity check] Regiões com amostra significativa (>=3 confiáveis): {dist['amostra_significativa'].sum()}")
    print("\n--- Top 5 por ENEM ponderado (amostra significativa) em cada cidade ---")
    sig = dist[dist["amostra_significativa"]]
    for cidade in MUNICIPIOS_ALVO.values():
        unidade = "distrito" if cidade == "São Paulo" else "região administrativa"
        print(f"\n{cidade} (unidade: {unidade}):")
        cols = ["regiao", "qtd_escolas_confiaveis", "enem_ponderado", "qtd_golden_leads"]
        print(sig[sig["cidade"] == cidade].sort_values("enem_ponderado", ascending=False)[cols].head(5).to_string(index=False))


def main():
    escolas = carregar_escolas_sp_rj()

    sem_ra = escolas[(escolas["cidade"] == "Rio de Janeiro") & escolas["regiao"].isna()]
    if len(sem_ra):
        print(f"[Sanity check] {len(sem_ra)} escolas do RJ sem Região Administrativa mapeada "
              f"(bairro não está na tabela oficial usada — ver RA_POR_BAIRRO_RJ): "
              f"{sorted(sem_ra['NO_BAIRRO'].dropna().unique().tolist())}")

    dist = agregar_por_regiao(escolas)
    dist = contar_golden_leads_por_regiao(escolas, dist)
    dist["qtd_golden_leads"] = dist["qtd_golden_leads"].astype(int)

    exibir_resumo(dist)
    dist = dist.sort_values(["cidade", "enem_ponderado"], ascending=[True, False])
    # sep=';' e decimal=',' — formato brasileiro, pro Power BI Desktop (locale
    # pt-BR) reconhecer os decimais automaticamente na importação (mesmo fix
    # já aplicado no passo 14).
    dist.to_csv(OUT_DIR / "15_regioes_sp_rj.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '15_regioes_sp_rj.csv'}")


if __name__ == "__main__":
    main()
