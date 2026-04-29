"""
Curvas de Kaplan-Meier — LTA (Figuras para o Paper)

Gera duas figuras de alta resolução para inclusão no paper LaTeX:
  1. Proporção de cura por forma clínica (Cutânea vs Mucosa)
  2. Proporção de cura por co-infecção HIV (HIV+ vs HIV-)

Cada figura inclui intervalo de confiança, teste de log-rank e tamanho amostral.

Entrada: dataset_lta0725/dataset_prepared.csv
Saída:   latex_paper/template-latex/figures/km_forma_clinica.png
         latex_paper/template-latex/figures/km_hiv.png
"""
"""Gera curvas de Kaplan-Meier para inclusão no paper (forma clínica e HIV)."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import os

df = pd.read_csv("dataset_lta0725/dataset_prepared.csv", low_memory=False)

# Preparar dados
surv = df.dropna(subset=["tempo_encerramento", "evolucao"]).copy()
surv = surv[surv["tempo_encerramento"] > 0]
surv["evento_cura"] = (surv["evolucao"] == 1).astype(int)

os.makedirs("latex_paper/template-latex/figures", exist_ok=True)

# =========================================================================
# FIGURA 1: Forma clínica (Cutânea vs Mucosa)
# =========================================================================
fig1, ax1 = plt.subplots(figsize=(8, 5))

subset = surv[surv["clas_forma"].isin([1, 2])]
config = {1: ("Cutânea", "#4CAF50"), 2: ("Mucosa", "#F44336")}

for val, (label, color) in config.items():
    mask = subset["clas_forma"] == val
    kmf = KaplanMeierFitter()
    kmf.fit(subset.loc[mask, "tempo_encerramento"],
            event_observed=subset.loc[mask, "evento_cura"],
            label=f"{label} (n={mask.sum():,})")
    kmf.plot_cumulative_density(ax=ax1, ci_show=True, color=color)

# Log-rank
mask_c = subset["clas_forma"] == 1
mask_m = subset["clas_forma"] == 2
lr = logrank_test(
    subset.loc[mask_c, "tempo_encerramento"], subset.loc[mask_m, "tempo_encerramento"],
    event_observed_A=subset.loc[mask_c, "evento_cura"],
    event_observed_B=subset.loc[mask_m, "evento_cura"],
)
p_str = "p < 0,001" if lr.p_value < 0.001 else f"p = {lr.p_value:.3f}"
ax1.text(0.05, 0.95, f"Log-rank: {p_str}", transform=ax1.transAxes,
         fontsize=11, verticalalignment="top",
         bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

ax1.set_title("Proporção de Cura por Forma Clínica", fontsize=13, fontweight="bold")
ax1.set_xlabel("Tempo desde notificação (dias)", fontsize=11)
ax1.set_ylabel("Proporção curada", fontsize=11)
ax1.set_xlim(0, 1000)
ax1.set_ylim(0, 1)
ax1.legend(fontsize=11, loc="lower right")
ax1.grid(True, alpha=0.3)
fig1.tight_layout()
fig1.savefig("latex_paper/template-latex/figures/km_forma_clinica.png", dpi=300, bbox_inches="tight")
print("Salvo: figures/km_forma_clinica.png")
plt.close(fig1)

# =========================================================================
# FIGURA 2: Co-infecção HIV
# =========================================================================
fig2, ax2 = plt.subplots(figsize=(8, 5))

subset = surv[surv["cli_co_hiv"].isin([1, 2])]
config = {1: ("HIV+ ", "#F44336"), 2: ("HIV−", "#4CAF50")}

for val, (label, color) in config.items():
    mask = subset["cli_co_hiv"] == val
    kmf = KaplanMeierFitter()
    kmf.fit(subset.loc[mask, "tempo_encerramento"],
            event_observed=subset.loc[mask, "evento_cura"],
            label=f"{label} (n={mask.sum():,})")
    kmf.plot_cumulative_density(ax=ax2, ci_show=True, color=color)

# Log-rank
mask_pos = subset["cli_co_hiv"] == 1
mask_neg = subset["cli_co_hiv"] == 2
lr = logrank_test(
    subset.loc[mask_pos, "tempo_encerramento"], subset.loc[mask_neg, "tempo_encerramento"],
    event_observed_A=subset.loc[mask_pos, "evento_cura"],
    event_observed_B=subset.loc[mask_neg, "evento_cura"],
)
p_str = "p < 0,001" if lr.p_value < 0.001 else f"p = {lr.p_value:.3f}"
ax2.text(0.05, 0.95, f"Log-rank: {p_str}", transform=ax2.transAxes,
         fontsize=11, verticalalignment="top",
         bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

ax2.set_title("Proporção de Cura por Co-infecção HIV", fontsize=13, fontweight="bold")
ax2.set_xlabel("Tempo desde notificação (dias)", fontsize=11)
ax2.set_ylabel("Proporção curada", fontsize=11)
ax2.set_xlim(0, 1000)
ax2.set_ylim(0, 1)
ax2.legend(fontsize=11, loc="lower right")
ax2.grid(True, alpha=0.3)
fig2.tight_layout()
fig2.savefig("latex_paper/template-latex/figures/km_hiv.png", dpi=300, bbox_inches="tight")
print("Salvo: figures/km_hiv.png")
plt.close(fig2)
