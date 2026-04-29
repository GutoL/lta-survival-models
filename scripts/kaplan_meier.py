"""
Curvas de Kaplan-Meier — LTA (Análise Exploratória Completa)

Gera uma figura 2x3 com curvas de Kaplan-Meier estratificadas por:
  1. Geral (sem estratificação)
  2. Forma clínica (Cutânea vs Mucosa)
  3. Droga inicial (Antimonial vs Anfotericina B vs Pentamidina)
  4. Co-infecção HIV (HIV+ vs HIV-)
  5. Faixa etária (0-12, 13-18, 19-40, 41-60, 61+)
  6. Raça/Cor (Branca, Preta, Parda, Indígena)

Cada painel inclui teste de log-rank e tamanho amostral por grupo.

Entrada: dataset_lta0725/dataset_prepared.csv
Saída:   outputs/kaplan_meier_cura.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test
import os

# =============================================================================
# LOAD
# =============================================================================
df = pd.read_csv("dataset_lta0725/dataset_prepared.csv", low_memory=False)
print(f"Dataset: {len(df):,} registros")

# =============================================================================
# PREPARAR DADOS PARA SURVIVAL
# =============================================================================
surv = df.copy()
surv = surv.dropna(subset=["tempo_encerramento"])
surv = surv[surv["tempo_encerramento"] > 0]
surv["evento_cura"] = (surv["evolucao"] == 1).astype(int)
print(f"Registros para análise: {len(surv):,}")
print(f"Eventos (cura): {surv['evento_cura'].sum():,} ({surv['evento_cura'].mean()*100:.1f}%)")

# =============================================================================
# CRIAR FAIXA ETÁRIA
# =============================================================================
bins = [0, 12, 18, 40, 60, 120]
labels_age = ["0-12", "13-18", "19-40", "41-60", "61+"]
surv["faixa_etaria"] = pd.cut(surv["idade"], bins=bins, labels=labels_age, right=True)

# =============================================================================
# LABELS PARA EXIBIÇÃO
# =============================================================================
strat_config = {
    "clas_forma": {
        "title": "Forma Clínica",
        "filter": lambda s: s[s["clas_forma"].isin([1, 2])],
        "col": "clas_forma",
        "labels": {1: "Cutânea", 2: "Mucosa"},
        "colors": {1: "#4CAF50", 2: "#F44336"},
    },
    "tra_droga_": {
        "title": "Droga Inicial",
        "filter": lambda s: s[s["tra_droga_"].isin([1, 2, 3])],
        "col": "tra_droga_",
        "labels": {1: "Antimonial", 2: "Anfotericina B", 3: "Pentamidina"},
        "colors": {1: "#2196F3", 2: "#FF9800", 3: "#9C27B0"},
    },
    "cli_co_hiv": {
        "title": "Co-infecção HIV",
        "filter": lambda s: s[s["cli_co_hiv"].isin([1, 2])],
        "col": "cli_co_hiv",
        "labels": {1: "HIV+", 2: "HIV-"},
        "colors": {1: "#F44336", 2: "#4CAF50"},
    },
    "faixa_etaria": {
        "title": "Faixa Etária",
        "filter": lambda s: s.dropna(subset=["faixa_etaria"]),
        "col": "faixa_etaria",
        "labels": {l: l for l in labels_age},
        "colors": dict(zip(labels_age, ["#2196F3", "#4CAF50", "#FF9800", "#F44336", "#9C27B0"])),
    },
    "cs_raca": {
        "title": "Raça/Cor",
        "filter": lambda s: s[s["cs_raca"].isin([1, 2, 4, 5])],
        "col": "cs_raca",
        "labels": {1: "Branca", 2: "Preta", 4: "Parda", 5: "Indígena"},
        "colors": {1: "#2196F3", 2: "#9C27B0", 4: "#FF9800", 5: "#4CAF50"},
    },
}

# =============================================================================
# GERAR FIGURA COM SUBPLOTS
# =============================================================================
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.flatten()

# --- Painel 0: Curva geral ---
kmf = KaplanMeierFitter()
kmf.fit(surv["tempo_encerramento"], event_observed=surv["evento_cura"], label="Geral")
kmf.plot_cumulative_density(ax=axes[0], ci_show=True, color="#333333")
axes[0].set_title("Geral", fontsize=13, fontweight="bold")

# --- Painéis 1-5: Estratificados ---
for idx, (key, cfg) in enumerate(strat_config.items(), start=1):
    ax = axes[idx]
    subset = cfg["filter"](surv)
    col = cfg["col"]

    groups = sorted(cfg["labels"].keys(), key=lambda x: str(x))
    for grp in groups:
        mask = subset[col] == grp
        if mask.sum() < 10:
            continue
        kmf_s = KaplanMeierFitter()
        kmf_s.fit(subset.loc[mask, "tempo_encerramento"],
                  event_observed=subset.loc[mask, "evento_cura"],
                  label=f"{cfg['labels'][grp]} (n={mask.sum():,})")
        kmf_s.plot_cumulative_density(ax=ax, ci_show=False, color=cfg["colors"][grp])

    ax.set_title(cfg["title"], fontsize=13, fontweight="bold")
    ax.legend(fontsize=9, loc="lower right")

    # Log-rank test
    test_data = subset.dropna(subset=[col, "tempo_encerramento", "evento_cura"])
    if test_data[col].nunique() >= 2:
        try:
            result = multivariate_logrank_test(
                test_data["tempo_encerramento"],
                test_data[col],
                test_data["evento_cura"],
            )
            p = result.p_value
            p_str = f"p < 0.001" if p < 0.001 else f"p = {p:.3f}"
            ax.text(0.05, 0.95, f"Log-rank: {p_str}", transform=ax.transAxes,
                    fontsize=10, verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        except Exception:
            pass

# --- Formatação comum ---
for ax in axes:
    ax.set_xlabel("Tempo desde notificação (dias)", fontsize=10)
    ax.set_ylabel("Proporção curada", fontsize=10)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

fig.suptitle("Análise de Sobrevivência — Proporção de Cura (Kaplan-Meier)\n"
             "Leishmaniose Tegumentar Americana, Brasil 2007–2025",
             fontsize=15, fontweight="bold", y=1.02)
fig.tight_layout()

os.makedirs("outputs", exist_ok=True)
output_path = "outputs/kaplan_meier_cura.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"\nGráfico salvo em: {output_path}")
plt.close()
