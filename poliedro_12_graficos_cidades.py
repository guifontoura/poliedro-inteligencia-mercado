"""
Case Poliedro — gráficos da Parte 1 (tema escuro), a partir de
data/outputs/01_cidades_prioritarias.csv (já com a média ENEM ponderada por
participante, revisão de 21/07). Não existiam como scripts salvos antes —
tinham sido gerados uma vez direto no ambiente do assistente e nunca
versionados; corrigido aqui para reprodutibilidade.

Gera:
- data/outputs/grafico_top10_cidades_dark.png
- data/outputs/grafico_dispersao_cidades_dark.png
"""

import matplotlib.pyplot as plt
import pandas as pd

BG = "#141B2C"
CARD = "#1E2A3F"
GOLD = "#D4AF37"
WHITE = "#F5F7FA"
MUTED = "#9AA7BD"
BORDER = "#2E3D54"
FAINT = "#6B7A93"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": WHITE,
    "axes.edgecolor": BORDER,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.family": "DejaVu Sans",
    "grid.color": BORDER,
})

df = pd.read_csv("data/outputs/01_cidades_prioritarias.csv", dtype={"codigo_municipio": str})
df = df.sort_values("score_priorizacao", ascending=False).reset_index(drop=True)
top10 = df.head(10)


def grafico_top10():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    ordem = top10.iloc[::-1]
    labels = [f"{r['nome_municipio_ibge']}/{r['uf']}" for _, r in ordem.iterrows()]
    valores = ordem["score_priorizacao"].tolist()
    escolas = ordem["qtd_escolas_elegiveis"].astype(int).tolist()

    bars = ax.barh(labels, valores, color=GOLD, height=0.62, zorder=3)
    for bar, v, n in zip(bars, valores, escolas):
        ax.text(v + 0.012, bar.get_y() + bar.get_height() / 2, f"{v:.2f}  ({n} escolas)",
                va="center", fontsize=11, color=WHITE, fontweight="bold")

    ax.set_xlim(0, 1.12)
    ax.set_xlabel("Score de priorização (0-1)", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(BORDER)
    ax.tick_params(axis="y", labelsize=12)
    ax.tick_params(axis="x", labelsize=10)
    ax.grid(axis="x", alpha=0.25, zorder=0)

    plt.tight_layout(pad=0.6)
    plt.savefig("data/outputs/grafico_top10_cidades_dark.png", facecolor=BG, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print("[✓] grafico_top10_cidades_dark.png")


def grafico_dispersao():
    fig, ax = plt.subplots(figsize=(8.2, 6.8), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    top10_cods = set(top10["codigo_municipio"])
    demais = df[~df["codigo_municipio"].isin(top10_cods)]

    ax.scatter(demais["percentil_socioeconomico"], demais["enem_media_praca"],
               s=demais["qtd_escolas_elegiveis"] * 3 + 15, color=MUTED, alpha=0.35,
               edgecolors="none", zorder=2, label="Demais 308 cidades (>100k hab.)")
    ax.scatter(top10["percentil_socioeconomico"], top10["enem_media_praca"],
               s=top10["qtd_escolas_elegiveis"] * 3 + 60, color=GOLD, alpha=0.9,
               edgecolors=BG, linewidths=1.2, zorder=3, label="Top 10 prioritárias")

    # offsets manuais por cidade pra evitar sobreposição de rótulo no cluster denso (canto superior direito)
    offsets = {
        "Belo Horizonte": (8, 10), "Niterói": (8, -14), "Goiânia": (-95, -4),
        "Vitória": (8, 6), "Florianópolis": (8, 10), "Porto Alegre": (8, -16),
        "São José dos Campos": (-140, 8), "Recife": (-45, -30), "Ribeirão Preto": (-100, 14),
        "Brasília": (10, -22),
    }
    for _, r in top10.iterrows():
        dx, dy = offsets.get(r["nome_municipio_ibge"], (8, 6))
        ax.annotate(r["nome_municipio_ibge"], (r["percentil_socioeconomico"], r["enem_media_praca"]),
                    textcoords="offset points", xytext=(dx, dy), fontsize=9.5, color=WHITE, fontweight="bold")

    ax.set_xlabel("Potencial socioeconômico (renda + população 0-17, percentil)", fontsize=10.5)
    ax.set_ylabel("Qualidade média da praça — ENEM 2025 (ponderada)", fontsize=10.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(BORDER)
    ax.grid(alpha=0.2, zorder=0)
    legend = ax.legend(loc="lower right", fontsize=9, facecolor=CARD, edgecolor=BORDER, labelcolor=WHITE)

    plt.tight_layout(pad=0.6)
    plt.savefig("data/outputs/grafico_dispersao_cidades_dark.png", facecolor=BG, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print("[✓] grafico_dispersao_cidades_dark.png")


if __name__ == "__main__":
    grafico_top10()
    grafico_dispersao()
