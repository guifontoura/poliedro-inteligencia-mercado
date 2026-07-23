"""
Case Poliedro — Passo 16 (roadmap 3.0, pedido do Gui em 23/07: "vamos avançar
no setor censitário IBGE"): RENDA DO RESPONSÁVEL POR BAIRRO (RJ) E DISTRITO (SP).

Boa notícia (achada via pesquisa em 23/07, não presumida): o IBGE JÁ publica
renda agregada por bairro e por distrito pro Censo 2022 — não precisamos do
join espacial pesado (setor censitário + shapefile + geopandas) que o
poliedro_11 tinha deixado como "próximo passo". Existe uma pasta dedicada,
publicada recentemente (08/05/2026):

  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/

Com arquivos já agregados em CSV pra cada nível geográfico (setor, bairro,
distrito, subdistrito, município). Isso combina exatamente com a unidade que
o passo 15 já usa por cidade: distrito pra São Paulo, bairro pro Rio de
Janeiro.

IMPORTANTE — o sandbox deste assistente tem a rede bloqueada pra download
direto desse FTP (mesma limitação já documentada no poliedro_11 pro ViaCEP).
Então este script assume que os dois arquivos abaixo já estão descompactados
em data/raw/ (baixe na sua máquina e solte os CSVs lá, ou me envie os CSVs
diretamente que eu processo):

  data/raw/renda_bairro_2022.csv    <- de Agregados_por_bairros_renda_responsavel_BR_20260508_csv.zip
  data/raw/renda_distrito_2022.csv  <- de Agregados_por_distritos_renda_responsavel_BR_20260508_csv.zip

URLs de download (arquivos pequenos, ~500KB e ~300KB):
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/Agregados_por_bairros_renda_responsavel_BR_20260508_csv.zip
  https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/Agregados_por_distritos_renda_responsavel_BR_20260508_csv.zip

Regra do projeto que este script segue à risca: NÃO adivinhar nome de coluna
antes de olhar o schema real. `inspecionar_schema()` roda primeiro e imprime
colunas/dtypes/primeiras linhas de cada arquivo — só depois disso é que faz
sentido escrever a lógica de merge com `15_regioes_sp_rj.csv` (que usa
`NO_DISTRITO`/`NO_BAIRRO` do Censo Escolar, uma fonte diferente — os nomes
de bairro/distrito podem não bater 100% entre as duas fontes, isso ainda
precisa ser validado, não presumido).

Gera (depois que os CSVs de entrada existirem): nada ainda — este script,
por enquanto, só inspeciona. A lógica de merge com o passo 15 é o próximo
commit, depois que soubermos os nomes reais das colunas.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")

ARQUIVOS_ESPERADOS = {
    "bairro": RAW_DIR / "renda_bairro_2022.csv",
    "distrito": RAW_DIR / "renda_distrito_2022.csv",
}


def inspecionar_schema() -> None:
    """Mostra colunas/dtypes/primeiras linhas dos CSVs de renda — roda antes de qualquer lógica de merge."""
    for nivel, caminho in ARQUIVOS_ESPERADOS.items():
        print(f"\n=== {nivel.upper()} ({caminho}) ===")
        if not caminho.exists():
            print(f"[Ainda não baixado] Coloque o arquivo em {caminho} e rode de novo.")
            continue

        # Os agregados do IBGE costumam vir em CSV com ';' e encoding latin-1 —
        # confirmamos isso ao ler, não presumimos, por isso o try/except abaixo.
        try:
            df = pd.read_csv(caminho, sep=";", encoding="utf-8", nrows=200)
        except (UnicodeDecodeError, pd.errors.ParserError):
            df = pd.read_csv(caminho, sep=";", encoding="latin-1", nrows=200)

        print(f"Colunas ({len(df.columns)}): {list(df.columns)}")
        print(f"\nDtypes:\n{df.dtypes}")
        print(f"\nPrimeiras linhas:\n{df.head(3).to_string()}")


def main():
    print("[Passo 16] Inspecionando schema real dos arquivos de renda por bairro/distrito (IBGE Censo 2022)...")
    inspecionar_schema()
    print(
        "\n[Próximo passo] Depois de ver as colunas reais acima, escrevo a função de merge com "
        "15_regioes_sp_rj.csv (chave: nome de bairro/distrito + UF/município) e o cálculo de renda "
        "média por região. Não escrevo essa lógica antes de ver o schema de verdade."
    )


if __name__ == "__main__":
    main()
