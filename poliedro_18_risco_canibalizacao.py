"""
Case Poliedro — Passo 18 (roadmap 3.0, pedido do Gui em 24/07): RISCO DE
CANIBALIZAÇÃO — distância entre Golden Leads e unidades PRÓPRIAS do Poliedro.

Motivação: uma Golden Lead recomendada muito perto de uma unidade própria do
Poliedro compete por aluno com a própria rede, não só ajuda a crescer.
Precisa de um "raio de segurança".

Coordenadas das unidades próprias: achadas dentro do PRÓPRIO dado do Censo
Escolar 2025 (`escolas_com_endereco.csv`, buscando "POLIEDRO" no nome) — não
inventadas, e cruzadas com o endereço oficial publicado em
colegiopoliedro.com.br/quem-somos/rede-de-escolas-proprias/ (24/07):

  - São Paulo (Perdizes/Água Branca, distrito oficial "Barra Funda" no
    Censo — bate com o endereço da unidade "Perdizes" do site, Av. Francisco
    Matarazzo 913): -23.527877, -46.671849
  - Campinas (Taquaral): -22.887401, -47.058476
  - São José dos Campos (Jardim Esplanada/Colinas): -23.203952, -45.909227

Limitação (não escondida): o site do Poliedro também lista uma unidade em
Vila Mariana-SP (Ensino Médio, Rua Madre Cabrini 38) que NÃO aparece no
Censo Escolar 2025 sob esse endereço — pode ser uma unidade nova demais pra
constar no Censo, ou registrada sob outro nome/CNPJ que a busca por
"POLIEDRO" não capturou. Como não temos coordenada confirmada, ela NÃO entra
no cálculo de distância abaixo — Vila Mariana fica de fora, sujeito a
correção manual se você tiver a coordenada exata.

Método: distância de haversine (linha reta, não rota de carro/trajeto real —
mais simples e é o padrão de mercado pra esse tipo de raio de exclusividade,
mas subestima distância real em cidades com relevo/rios/vias tortuosas).
Comparação feita só dentro do MESMO município da unidade própria (não faz
sentido comparar Golden Lead de Santos com unidade de Campinas).

Limiar (PROVISÓRIO, sem benchmark público — decisão de política comercial,
não fato estatístico): usamos 3km como alerta "risco alto" e 3-6km como
"risco moderado", baseado em como funciona logística de escola (pais não
costumam trocar de escola pra atravessar a cidade todo dia em trânsito
denso). Isso PRECISA ser validado com o time comercial do Poliedro — pode
variar por cidade (SP tem trânsito pior que Campinas, por exemplo).

Gera: data/outputs/18_risco_canibalizacao.csv
"""

from math import asin, cos, radians, sin, sqrt
from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")

UNIDADES_PROPRIAS = [
    {"nome": "São Paulo (Perdizes/Barra Funda)", "codigo_municipio": "3550308", "lat": -23.527877, "lon": -46.671849},
    {"nome": "Campinas (Taquaral)", "codigo_municipio": "3509502", "lat": -22.887401, "lon": -47.058476},
    {"nome": "São José dos Campos (Jd. Esplanada)", "codigo_municipio": "3549904", "lat": -23.203952, "lon": -45.909227},
]

RAIO_ALTO_KM = 3.0
RAIO_MODERADO_KM = 6.0


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em linha reta (haversine), em km."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d_lat, d_lon = lat2 - lat1, lon2 - lon1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))  # 6371 km = raio médio da Terra


def classificar_risco(km: float) -> str:
    if km <= RAIO_ALTO_KM:
        return "ALTO (<=3km)"
    if km <= RAIO_MODERADO_KM:
        return "MODERADO (3-6km)"
    return "baixo"


def calcular_distancias() -> pd.DataFrame:
    golden = pd.read_csv(OUT_DIR / "14_escolas_powerbi.csv", sep=";", decimal=",", dtype={"codigo_municipio": str})
    golden = golden[golden["LATITUDE"].notna()].copy()

    linhas = []
    for unidade in UNIDADES_PROPRIAS:
        candidatas = golden[golden["codigo_municipio"] == unidade["codigo_municipio"]].copy()
        for _, lead in candidatas.iterrows():
            km = distancia_km(unidade["lat"], unidade["lon"], lead["LATITUDE"], lead["LONGITUDE"])
            linhas.append({
                "unidade_propria": unidade["nome"],
                "escola_lead": lead["NO_ENTIDADE"],
                "cidade": lead["cidade"],
                "bairro": lead.get("bairro"),
                "segmento_comercial": lead["segmento_comercial"],
                "score_destaque": lead["score_destaque"],
                "distancia_km": round(km, 2),
                "risco_canibalizacao": classificar_risco(km),
            })

    return pd.DataFrame(linhas).sort_values("distancia_km")


def exibir_resumo(df: pd.DataFrame) -> None:
    print(f"[Sanity check] Golden Leads comparadas (nas 3 cidades com unidade própria confirmada): {len(df)}")
    print(f"\n[Sanity check] Distribuição de risco:\n{df['risco_canibalizacao'].value_counts()}")
    print("\n--- Leads em risco ALTO ou MODERADO (revisar antes de indicar comercialmente) ---")
    risco = df[df["risco_canibalizacao"] != "baixo"]
    cols = ["unidade_propria", "escola_lead", "bairro", "distancia_km", "risco_canibalizacao", "segmento_comercial"]
    print(risco[cols].to_string(index=False) if len(risco) else "(nenhuma)")
    print("\n--- 10 mais próximas no geral, pra dar noção de escala das distâncias ---")
    print(df[cols].head(10).to_string(index=False))


def main():
    df = calcular_distancias()
    exibir_resumo(df)
    df.to_csv(OUT_DIR / "18_risco_canibalizacao.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '18_risco_canibalizacao.csv'}")


if __name__ == "__main__":
    main()
