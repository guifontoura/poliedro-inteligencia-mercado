"""
Case Poliedro — gráfico de funil de priorização de escolas, tema escuro.

Revisão de 21/07: o funil agora termina em "869 Golden Leads (score >= 0,70)".
Antes havia um 5º estágio "129 Golden Leads (score >= 0,90)" — foi removido
daqui porque deixou de ser um subconjunto mais estreito numa hierarquia de
funil; virou uma TAG de segmento comercial dentro do universo de 869 (ver
poliedro_09_icp_poliedro.py e poliedro_10_segmentacao_comercial.py). Manter
os dois no mesmo funil sugeria uma hierarquia de exclusão que não existe mais.

Correção de auditoria (22/07): as 4 contagens do funil estavam hardcoded como
números literais — se a base de dados mudasse (nova rodada do Censo/ENEM),
o gráfico ficaria desatualizado silenciosamente. Agora são calculadas ao
vivo a partir dos CSVs gerados pelo próprio pipeline (poliedro_03,
poliedro_05b, poliedro_09).

Gera: data/outputs/funil_escolas.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/outputs")

BG = "#141B2C"
GOLD = "#D4AF37"
WHITE = "#F5F7FA"
MUTED = "#9AA7BD"
BORDER = "#2E3D54"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": WHITE,
    "font.family": "DejaVu Sans",
})

def contar_etapas() -> list[tuple[str, int, str]]:
    """Lê os CSVs reais do pipeline e conta cada estágio do funil — nada hardcoded."""
    elegiveis = pd.read_csv(RAW_DIR / "escolas_privadas_elegiveis_2025.csv", dtype={"codigo_municipio": str})
    pontuadas = pd.read_csv(OUT_DIR / "funil_escolas_pontuadas.csv", dtype={"codigo_municipio": str})
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_municipio": str})

    return [
        ("Escolas privadas elegíveis (nacional)", len(elegiveis), "#4A5A75"),
        ("No recorte >100k hab.", len(pontuadas), "#5C7099"),
        ("Com ENEM confiável (pontuáveis)", int(pontuadas["confiavel_enem"].sum()), "#7C93B8"),
        ("Golden Leads (score ≥ 0,70)", len(golden), GOLD),
    ]


etapas = contar_etapas()

fig, ax = plt.subplots(figsize=(11.5, 5.0), dpi=200)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

n = len(etapas)
row_h = 1.0
bar_h = 0.42
max_v = 10.0

for i, (label, val, cor) in enumerate(etapas):
    y_top = (n - 1 - i) * row_h
    pct = val / etapas[0][1] * 100
    width = max(val / etapas[0][1] * max_v, 0.35)
    left = (max_v - width) / 2

    ax.text(0, y_top + 0.62, label, fontsize=13, color=WHITE, fontweight="bold", va="bottom", ha="left")
    ax.text(max_v, y_top + 0.62, f"{val:,.0f}".replace(",", ".") + f"   ({pct:.1f}%)",
            fontsize=13, color=(GOLD if cor == GOLD else MUTED), fontweight="bold", va="bottom", ha="right")

    ax.barh(y_top + 0.15, width, height=bar_h, left=left, color=cor, edgecolor=BORDER, linewidth=0.6, zorder=3)

ax.set_xlim(-0.1, max_v + 0.1)
ax.set_ylim(-0.3, n * row_h - 0.05)
ax.axis("off")

plt.tight_layout(pad=0.3)
plt.savefig("data/outputs/funil_escolas.png", facecolor=BG, bbox_inches="tight", pad_inches=0.15)
print("[✓] Salvo em data/outputs/funil_escolas.png")
