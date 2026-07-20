"""
ANÁLISES COMPLEMENTARES: Mapeamento de Escolas Privadas
Gera insights segmentados por região, município, PIB e infraestrutura
para identificar oportunidades de venda de soluções educacionais premium.
"""

import sqlite3
import pandas as pd
from pathlib import Path

CAMINHO_DB = "mercado_educacional_local.db"


def conectar_banco() -> sqlite3.Connection:
    """Abre conexão com o banco SQLite."""
    conn = sqlite3.connect(CAMINHO_DB)
    return conn


def analisar_municipios_prioritarios(conn: sqlite3.Connection, top_n: int = 20) -> pd.DataFrame:
    """
    Identifica municípios prioritários para venda (concentração de escolas privadas
    em cidades ricas = alto potencial de receita).
    """
    query = """
    SELECT 
        codigo_municipio,
        COUNT(*) AS quantidade_escolas,
        ROUND(AVG(pib_per_capita_contexto), 2) AS pib_per_capita_medio,
        ROUND(SUM(quantidade_salas), 0) AS total_salas
    FROM escolas_privadas_potenciais
    GROUP BY codigo_municipio
    ORDER BY pib_per_capita_medio DESC, quantidade_escolas DESC
    LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=(top_n,))
    return df


def analisar_segmentacao_por_porte(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Segmenta escolas por tamanho (porte):
    - Pequenas: < 10 salas
    - Médias: 10-20 salas
    - Grandes: > 20 salas
    """
    query = """
    SELECT 
        CASE 
            WHEN quantidade_salas < 10 THEN 'Pequena'
            WHEN quantidade_salas BETWEEN 10 AND 20 THEN 'Média'
            ELSE 'Grande'
        END AS porte_escola,
        COUNT(*) AS quantidade,
        ROUND(AVG(pib_per_capita_contexto), 2) AS pib_per_capita_medio,
        ROUND(AVG(quantidade_salas), 1) AS salas_media,
        ROUND(AVG(score_potencial), 4) AS score_medio
    FROM escolas_privadas_potenciais
    GROUP BY porte_escola
    ORDER BY score_medio DESC
    """

    df = pd.read_sql_query(query, conn)
    return df


def analisar_oportunidades_premium(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Identifica as MELHORES oportunidades: municípios ricos + escolas grandes
    = potencial máximo de vendas de soluções educacionais premium.
    """
    query = """
    SELECT 
        nome_escola,
        codigo_municipio,
        ROUND(pib_per_capita_contexto, 2) AS pib_per_capita,
        quantidade_salas,
        ROUND(score_potencial, 4) AS score_potencial
    FROM escolas_privadas_potenciais
    WHERE score_potencial >= 0.7  -- Top 30%
    ORDER BY score_potencial DESC, pib_per_capita DESC
    """

    df = pd.read_sql_query(query, conn)
    return df


def gerar_relatorio_executivo(conn: sqlite3.Connection) -> None:
    """Gera um relatório executivo completo para apresentação comercial."""

    print("\n" + "=" * 120)
    print("RELATÓRIO EXECUTIVO: OPORTUNIDADES DE VENDA DE SOLUÇÕES EDUCACIONAIS PREMIUM")
    print("=" * 120 + "\n")

    # ========== SEÇÃO 1: MUNICIPIOS PRIORITARIOS ==========
    print("1. MUNICÍPIOS PRIORITÁRIOS (Top 10 por riqueza + concentração de escolas privadas)")
    print("-" * 120)
    df_municipios = analisar_municipios_prioritarios(conn, top_n=10)
    print(df_municipios.to_string(index=False))
    print("\n💡 INSIGHT: Direcionar sales para esses municípios oferece receita concentrada.\n")

    # ========== SEÇÃO 2: SEGMENTAÇÃO POR PORTE ==========
    print("2. SEGMENTAÇÃO POR PORTE (Pequenas, Médias, Grandes)")
    print("-" * 120)
    df_porte = analisar_segmentacao_por_porte(conn)
    print(df_porte.to_string(index=False))
    print("\n💡 INSIGHT: Escolas grandes em cidades ricas = maior orçamento de T.I. e educação.\n")

    # ========== SEÇÃO 3: OPORTUNIDADES PREMIUM (Golden Leads) ==========
    print("3. GOLDEN LEADS: Oportunidades Premium (Score ≥ 0.7)")
    print("-" * 120)
    df_premium = analisar_oportunidades_premium(conn)
    if not df_premium.empty:
        # Exibe apenas as top 15 no terminal para não inundar a tela, mas exporta todas no CSV
        print(df_premium.head(15).to_string(index=False))
        print(f"\n✨ {len(df_premium)} ESCOLAS IDENTIFICADAS COM POTENCIAL MÁXIMO DE VENDA")
        print("   (Cidades ricas + escolas grandes + em municípios desenvolvidos)\n")
    else:
        print("Nenhuma escola no segmento premium encontrada nesta execução.\n")

    # ========== SEÇÃO 4: MÉTRICAS AGREGADAS ==========
    print("4. MÉTRICAS AGREGADAS DO DATASET")
    print("-" * 120)
    query_agregado = """
    SELECT 
        COUNT(*) AS total_escolas,
        COUNT(DISTINCT codigo_municipio) AS quantidade_municipios,
        ROUND(AVG(pib_per_capita_contexto), 2) AS pib_per_capita_medio_brasil,
        ROUND(MAX(pib_per_capita_contexto), 2) AS pib_per_capita_maximo,
        ROUND(MIN(pib_per_capita_contexto), 2) AS pib_per_capita_minimo,
        ROUND(AVG(score_potencial), 4) AS score_potencial_medio
    FROM escolas_privadas_potenciais
    """
    df_agregado = pd.read_sql_query(query_agregado, conn)
    print(df_agregado.to_string(index=False))
    print("\n")

    print("=" * 120)
    print("FIM DO RELATÓRIO")
    print("=" * 120 + "\n")


def exportar_para_csv(conn: sqlite3.Connection, output_dir: Path = Path("data/outputs")) -> None:
    """
    Exporta análises em formato CSV para uso em Excel/Power BI.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Municipios prioritarios
    df_municipios = analisar_municipios_prioritarios(conn, top_n=50)
    df_municipios.to_csv(output_dir / "01_municipios_prioritarios.csv", index=False)

    # Segmentacao por porte
    df_porte = analisar_segmentacao_por_porte(conn)
    df_porte.to_csv(output_dir / "02_segmentacao_por_porte.csv", index=False)

    # Golden leads
    df_premium = analisar_oportunidades_premium(conn)
    df_premium.to_csv(output_dir / "04_golden_leads_premium.csv", index=False)

    print(f"[✓] Análises exportadas para: {output_dir}\n")


def main():
    conn = conectar_banco()

    try:
        # Gera relatório executivo
        gerar_relatorio_executivo(conn)

        # Exporta em CSV
        exportar_para_csv(conn)

        print("[✓] Análises complementares concluídas com sucesso!")

    finally:
        conn.close()


if __name__ == "__main__":
    main()