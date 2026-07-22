"""
Case Poliedro — visual de segmentação comercial dentro do universo de 869
Golden Leads (score_destaque >= 0.70). Substitui a leitura antiga de "129
Golden Leads vs 740 Qualificadas" por uma única barra segmentada com 4 tags
de posição dentro do próprio município (ver poliedro_09_icp_poliedro.py).

Gera: data/outputs/segmentacao_comercial.png
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
    "font.family": "DejaVu Sans",
})

df = pd.read_csv("data/outputs/04_golden_leads_segmentadas.csv")
total = len(df)
contagem = df["segmento_comercial"].value_counts()

ordem = [
    ("Desafiante (2º-5º local)", "#D4AF37", "Foco comercial primário —\nmotivo pra trocar de sistema"),
    ("Líder local", "#8C97AC", "Referência da cidade —\nparceria de prestígio/vitrine"),
    ("Outras posições", "#5C6A82", "6º lugar local em diante —\npipeline de longo prazo"),
    ("Sem comparação local (poucas escolas na cidade)", "#3A4558", "Cidade com <3 escolas confiáveis —\nsem posição comparável"),
]

fig, ax = plt.subplots(figsize=(11.5, 4.6), dpi=200)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# barra empilhada horizontal única
left = 0
bar_y = 3.0
bar_h = 1.1
for nome, cor, _ in ordem:
    val = int(contagem.get(nome, 0))
    largura = val / total * 10
    ax.barh(bar_y, largura, height=bar_h, left=left, color=cor, edgecolor=BG, linewidth=2, zorder=3)
    if largura > 0.6:
        ax.text(left + largura / 2, bar_y, f"{val}", fontsize=15, color=BG if cor == GOLD else WHITE,
                fontweight="bold", ha="center", va="center", zorder=4)
    left += largura

ax.text(0, bar_y + 0.95, f"Universo Golden Leads — score_destaque ≥ 0,70: {total} escolas",
        fontsize=13, color=WHITE, fontweight="bold", ha="left")

# legenda / cards abaixo (2 colunas x 2 linhas, mais espaço por card)
nomes_curtos = ["Desafiante (2º-5º local)", "Líder local", "Outras posições", "Sem comparação local"]
posicoes = [(0.0, 1.9), (5.2, 1.9), (0.0, 0.75), (5.2, 0.75)]
for (nome, cor, desc), nome_curto, (x, y) in zip(ordem, nomes_curtos, posicoes):
    val = int(contagem.get(nome, 0))
    ax.add_patch(plt.Rectangle((x, y), 0.3, 0.3, color=cor))
    ax.text(x + 0.45, y + 0.28, f"{nome_curto} ({val})", fontsize=11, color=WHITE, fontweight="bold", va="top")
    ax.text(x + 0.45, y - 0.05, desc, fontsize=8.5, color=MUTED, va="top", linespacing=1.4)

ax.set_xlim(-0.2, 10.2)
ax.set_ylim(0.3, 4.6)
ax.axis("off")

plt.tight_layout(pad=0.3)
plt.savefig("data/outputs/segmentacao_comercial.png", facecolor=BG, bbox_inches="tight", pad_inches=0.2)
print("[✓] Salvo em data/outputs/segmentacao_comercial.png")
print(contagem)
