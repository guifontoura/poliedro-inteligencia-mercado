"""
Case Poliedro — Passo 18 (roadmap 3.0, pedido do Gui em 24/07): RISCO DE
CANIBALIZAÇÃO — distância entre Golden Leads e unidades PRÓPRIAS do Poliedro.

Motivação: uma Golden Lead recomendada muito perto de uma unidade própria do
Poliedro compete por aluno com a própria rede, não só ajuda a crescer.
Precisa de um "raio de segurança".

Coordenadas das unidades próprias: achadas dentro do PRÓPRIO dado do Censo
Escolar 2025 (`escolas_com_endereco.csv`, buscando "POLIEDRO" no nome) — não
inventadas, e cruzadas com o endereço oficial publicado em
colegiopoliedro.com.br/quem-somos/rede-de-escolas-proprias/ e confirmado
pelo Gui em 24/07:

  - São Paulo — Perdizes/Água Branca (distrito oficial "Barra Funda" no
    Censo, Av. Francisco Matarazzo 913): -23.527877, -46.671849 (exata,
    endereço batido linha a linha no Censo)
  - Campinas (Taquaral): -22.887401, -47.058476 (exata)
  - São José dos Campos (Jardim Esplanada/Colinas): -23.203952, -45.909227 (exata)
  - São Paulo — Vila Mariana (Colégio, Rua Madre Cabrini 38): NÃO encontrada
    no Censo Escolar sob esse endereço (unidade pode ser nova demais pra
    constar no Censo 2025, ou registrada sob outro nome). Coordenada
    APROXIMADA usada aqui: centroide das 9 escolas do distrito Vila Mariana
    que têm lat/long no nosso próprio dado (-23.582922, -46.636499) — é uma
    aproximação de bairro, não o endereço exato do prédio. Isso importa
    porque Vila Mariana é o distrito #1 em ENEM de São Paulo E tem 6 Golden
    Leads — risco de canibalização ali merece atenção mesmo com coordenada
    aproximada.
  - "Poliedro Curso" (Unidade Paraíso e Unidade Vila Mariana, mesma rua
    Madre Cabrini 38 da unidade Colégio): NÃO entra aqui — é a marca de
    cursinho pré-vestibular, produto diferente, não compete pelo mesmo
    licenciamento de sistema de ensino K-12 que este projeto mapeia.

Método: distância de haversine (linha reta, não rota de carro/trajeto real —
mais simples e é o padrão de mercado pra esse tipo de raio de exclusividade,
mas subestima distância real em cidades com relevo/rios/vias tortuosas).
Comparação feita só dentro do MESMO município da unidade própria.

Limiar (PROVISÓRIO, sem benchmark público — decisão de política comercial,
não fato estatístico, precisa validação do time comercial do Poliedro):
diferenciado por cidade, a pedido do Gui (24/07) — "estimativa razoável pra
metrópole como SP, priorizando bairros mais ricos". Raciocínio: em São
Paulo, o trânsito denso faz com que mesmo 5km possam levar 30-45min no
horário de pico — famílias de escola particular raramente trocam de escola
pra cruzar a cidade todo dia, então o raio de canibalização real é mais
APERTADO em SP do que em cidades menores (Campinas, SJC), mesmo a cidade
sendo maior em população — é justamente a densidade/trânsito que encolhe o
raio prático, não o tamanho da cidade. Por outro lado, não vale generalizar
demais: se um bairro riquíssimo aparecer um pouco mais longe (4-5km), ainda
vale reportar como "moderado" pra decisão humana, não descartar.
  - São Paulo: 2km (alto) / 2-5km (moderado)
  - Campinas e São José dos Campos: 3km (alto) / 3-6km (moderado)

Gera: data/outputs/18_risco_canibalizacao.csv
"""

from math import asin, cos, radians, sin, sqrt
from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")

UNIDADES_PROPRIAS = [
    {"nome": "São Paulo (Perdizes/Barra Funda)", "codigo_municipio": "3550308", "lat": -23.527877, "lon": -46.671849, "exata": True},
    {"nome": "São Paulo (Vila Mariana, coord. aproximada)", "codigo_municipio": "3550308", "lat": -23.582922, "lon": -46.636499, "exata": False},
    {"nome": "Campinas (Taquaral)", "codigo_municipio": "3509502", "lat": -22.887401, "lon": -47.058476, "exata": True},
    {"nome": "São José dos Campos (Jd. Esplanada)", "codigo_municipio": "3549904", "lat": -23.203952, "lon": -45.909227, "exata": True},
]

# Limiares diferenciados por cidade (24/07, a pedido do Gui) — ver docstring
# pro raciocínio: São Paulo é mais apertado por causa da densidade/trânsito,
# não mais largo por ser cidade maior.
RAIOS_POR_MUNICIPIO_KM = {
    "3550308": {"alto": 2.0, "moderado": 5.0},  # São Paulo
}
RAIO_PADRAO_KM = {"alto": 3.0, "moderado": 6.0}  # demais cidades


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em linha reta (haversine), em km."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d_lat, d_lon = lat2 - lat1, lon2 - lon1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))  # 6371 km = raio médio da Terra


def classificar_risco(km: float, codigo_municipio: str) -> str:
    raios = RAIOS_POR_MUNICIPIO_KM.get(codigo_municipio, RAIO_PADRAO_KM)
    if km <= raios["alto"]:
        return f"ALTO (<={raios['alto']:.0f}km)"
    if km <= raios["moderado"]:
        return f"MODERADO ({raios['alto']:.0f}-{raios['moderado']:.0f}km)"
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
                "coordenada_exata": unidade["exata"],
                "escola_lead": lead["NO_ENTIDADE"],
                "cidade": lead["cidade"],
                "bairro": lead.get("bairro"),
                "segmento_comercial": lead["segmento_comercial"],
                "score_destaque": lead["score_destaque"],
                "distancia_km": round(km, 2),
                "risco_canibalizacao": classificar_risco(km, unidade["codigo_municipio"]),
            })

    return pd.DataFrame(linhas).sort_values("distancia_km")


def exibir_resumo(df: pd.DataFrame) -> None:
    print(f"[Sanity check] Golden Leads comparadas (nas unidades próprias com coordenada, exata ou aproximada): {len(df)}")
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
