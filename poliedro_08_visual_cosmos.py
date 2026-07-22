"""Visual procedural 'cosmos em expansão' para o slide do Cosmos — estrelas + anéis
concêntricos dourados, sem depender de internet/geração de imagem por IA (bloqueada
no sandbox). Paleta igual ao resto do deck dark."""
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path("data/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BG_DEEP = "#0F1626"
GOLD = "#D4AF37"
WHITE = "#F5F7FA"

random.seed(7)
np.random.seed(7)

fig, ax = plt.subplots(figsize=(6.0, 7.2), dpi=200)
fig.patch.set_facecolor(BG_DEEP)
ax.set_facecolor(BG_DEEP)

# estrelas
for _ in range(220):
    x, y = random.uniform(0, 10), random.uniform(0, 12)
    size = random.uniform(1, 14)
    alpha = random.uniform(0.15, 0.9)
    ax.scatter(x, y, s=size, color=WHITE, alpha=alpha, linewidths=0)

# centro de expansão (canto inferior esquerdo, como se o "cosmos" nascesse ali e crescesse)
cx, cy = 2.0, 2.5
for r, a in [(1.0, 0.9), (2.2, 0.6), (3.6, 0.4), (5.2, 0.25), (7.0, 0.13)]:
    circle = plt.Circle((cx, cy), r, fill=False, edgecolor=GOLD, linewidth=1.4, alpha=a)
    ax.add_patch(circle)

# núcleo
ax.scatter([cx], [cy], s=380, color=GOLD, alpha=0.95, zorder=5)
ax.scatter([cx], [cy], s=900, color=GOLD, alpha=0.18, zorder=4)

ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis("off")
plt.tight_layout(pad=0)
plt.savefig(OUT_DIR / "cosmos_visual.png", facecolor=BG_DEEP, bbox_inches="tight", pad_inches=0)
print(f"[✓] Salvo em {OUT_DIR / 'cosmos_visual.png'}")
