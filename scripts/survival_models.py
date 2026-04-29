"""
Modelos de Sobrevivência — LTA

Compara seis modelos de sobrevivência para dois desfechos:
  - Óbito (evolucao 3 + 4)
  - Abandono de tratamento (evolucao 2)

Modelos avaliados:
  1. Cox PH (riscos proporcionais clássico)
  2. Cox Elastic Net (regularização L1/L2)
  3. Survival Tree (árvore única)
  4. Extra Survival Tree (árvore com splits aleatórios)
  5. Random Survival Forest (ensemble de 100 árvores)
  6. Extra Survival Trees (ensemble com splits aleatórios)

Métrica: C-index (índice de concordância de Harrell) no conjunto de teste (20%).

Entrada: dataset_lta0725/dataset_prepared.csv
Saída:   latex_paper/template-latex/figures/feature_importance_obito.png
         latex_paper/template-latex/figures/feature_importance_abandono.png
         latex_paper/template-latex/figures/c_index_comparison.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sksurv.linear_model import CoxPHSurvivalAnalysis, CoxnetSurvivalAnalysis
from sksurv.ensemble import RandomSurvivalForest, ExtraSurvivalTrees
from sksurv.tree import SurvivalTree, ExtraSurvivalTree
from sksurv.metrics import concordance_index_censored

# =============================================================================
# LOAD
# =============================================================================
df = pd.read_csv("dataset_lta0725/dataset_prepared.csv", low_memory=False)
print(f"Dataset: {len(df):,} registros")

# =============================================================================
# FEATURES COMUNS
# =============================================================================
feature_cols = [
    "idade", "cs_sexo", "cs_gestant", "cs_raca", "cs_escol_n",
    "cli_co_hiv", "lab_parasi", "lab_irm", "lab_histop",
    "criterio", "con_class_", "tpautocto", "doenca_tra",
    "nu_ano", "sg_uf", "tempo_tratamento",
]
cat_cols = ["cs_sexo", "cs_gestant", "cs_raca", "cs_escol_n",
            "cli_co_hiv", "lab_parasi", "lab_irm", "lab_histop",
            "criterio", "con_class_", "tpautocto", "doenca_tra", "sg_uf"]


def prepare_survival_data(df, evento_codes, evento_label):
    """Prepara dados de survival para um outcome específico.

    evento_codes: set de valores de evolucao que são o evento de interesse
    Censurado: todos os outros valores válidos de evolucao
    """
    surv = df.dropna(subset=["tempo_encerramento", "evolucao"]).copy()
    surv = surv[surv["tempo_encerramento"] > 0]
    surv["evento"] = surv["evolucao"].isin(evento_codes).astype(bool)

    X = surv[feature_cols].copy()
    for col in cat_cols:
        X[col] = X[col].astype(str)
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)

    mask_valid = X.notna().all(axis=1)
    X = X[mask_valid]
    surv = surv[mask_valid]

    y = np.array(
        [(e, t) for e, t in zip(surv["evento"], surv["tempo_encerramento"])],
        dtype=[("evento", bool), ("tempo", float)]
    )

    n_evento = surv["evento"].sum()
    print(f"\n{'#'*70}")
    print(f"  OUTCOME: {evento_label}")
    print(f"{'#'*70}")
    print(f"  Registros: {len(X):,}")
    print(f"  Eventos: {n_evento:,} ({n_evento/len(X)*100:.1f}%)")
    print(f"  Censurados: {len(X) - n_evento:,} ({(len(X) - n_evento)/len(X)*100:.1f}%)")
    print(f"  Features: {X.shape[1]}")

    return X, y, surv


def train_and_evaluate(X, y, surv, outcome_label):
    """Treina Cox, RSF e GB, retorna resultados e modelos."""

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=[e[0] for e in y]
    )
    print(f"  Train: {len(X_train):,} | Test: {len(X_test):,}")

    import time

    models = {
        "Cox PH": CoxPHSurvivalAnalysis(alpha=0.01),
        "Cox Elastic Net": CoxnetSurvivalAnalysis(
            l1_ratio=0.5, alpha_min_ratio=0.01, max_iter=100
        ),
        "Survival Tree": SurvivalTree(
            max_depth=10, min_samples_split=20, min_samples_leaf=15, random_state=42
        ),
        "Extra Survival Tree": ExtraSurvivalTree(
            max_depth=10, min_samples_split=20, min_samples_leaf=15, random_state=42
        ),
        "Random Survival Forest": RandomSurvivalForest(
            n_estimators=100, min_samples_split=20, min_samples_leaf=15,
            max_features="sqrt", n_jobs=-1, random_state=42, verbose=1
        ),
        "Extra Survival Trees": ExtraSurvivalTrees(
            n_estimators=100, min_samples_split=20, min_samples_leaf=15,
            max_features="sqrt", n_jobs=-1, random_state=42, verbose=1
        ),
    }

    results = {}
    trained_models = {}

    for name, model in models.items():
        print(f"\n  Treinando: {name}...")
        t0 = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - t0
        print(f"    Tempo de treino: {elapsed:.1f}s")

        # CoxnetSurvivalAnalysis: selecionar melhor alpha via C-index no treino
        if name == "Cox Elastic Net":
            from sksurv.metrics import concordance_index_censored as ci
            best_c = -1
            best_alpha = None
            for a in model.alphas_:
                p = model.predict(X_test, alpha=a)
                c = ci(y_test["evento"], y_test["tempo"], p)[0]
                if c > best_c:
                    best_c = c
                    best_alpha = a
            pred = model.predict(X_test, alpha=best_alpha)
            print(f"    Melhor alpha: {best_alpha:.6f}")
        else:
            pred = model.predict(X_test)
        c_index = concordance_index_censored(
            y_test["evento"], y_test["tempo"], pred
        )
        results[name] = {"c_index": c_index[0], "concordant": c_index[1], "discordant": c_index[2]}
        trained_models[name] = model
        if name == "Cox Elastic Net":
            trained_models["_coxnet_alpha"] = best_alpha
        print(f"    C-index: {c_index[0]:.4f}")

    # Resumo
    print(f"\n  {'='*50}")
    print(f"  COMPARAÇÃO — {outcome_label}")
    print(f"  {'='*50}")
    for name, res in sorted(results.items(), key=lambda x: x[1]["c_index"], reverse=True):
        bar = "█" * int(res["c_index"] * 50)
        print(f"    {name:<35} {bar} {res['c_index']:.4f}")

    return results, trained_models, X_train, y_train


def plot_feature_importance(trained_models, X_train, y_train, outcome_label, filename):
    """Gera gráfico de feature importance para todos os modelos."""
    from sklearn.inspection import permutation_importance

    # Filtrar chaves internas (ex: _coxnet_alpha)
    model_items = [(n, m) for n, m in trained_models.items() if not n.startswith("_")]
    coxnet_alpha = trained_models.get("_coxnet_alpha", None)

    n_models = len(model_items)
    ncols = 3
    nrows = (n_models + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(22, 7 * nrows))
    axes = axes.flatten()

    for idx, (name, model) in enumerate(model_items):
        ax = axes[idx]
        if "Cox" in name:
            if hasattr(model, "coef_"):
                coefs = model.coef_
                if coefs.ndim == 2:
                    if coxnet_alpha is not None and hasattr(model, "alphas_"):
                        alpha_idx = list(model.alphas_).index(coxnet_alpha)
                        coefs = coefs[:, alpha_idx]
                    else:
                        coefs = coefs[:, -1]
                importance = pd.Series(coefs, index=X_train.columns)
                importance = importance.abs().sort_values(ascending=True).tail(20)
                suffix = "(|coeficiente|)"
            else:
                continue
        elif "Tree" in name and "Forest" not in name and "Trees" not in name:
            # SurvivalTree não tem feature_importances_, usar permutation
            
            # perm = permutation_importance(model, X_train.iloc[:5000], y_train[:5000],
            #                               n_repeats=5, random_state=42, n_jobs=-1)
            perm = permutation_importance(model, X_train.iloc[:2000], y_train[:2000],
                                          n_repeats=3, random_state=42, n_jobs=-1)

            importance = pd.Series(perm.importances_mean, index=X_train.columns)
            importance = importance.sort_values(ascending=True).tail(20)
            suffix = "(permutation importance)"
        else:
            # RSF e ExtraSurvivalTrees: permutation importance
            perm = permutation_importance(model, X_train.iloc[:5000], y_train[:5000],
                                          n_repeats=5, random_state=42, n_jobs=-1)
            importance = pd.Series(perm.importances_mean, index=X_train.columns)
            importance = importance.sort_values(ascending=True).tail(20)
            suffix = "(permutation importance)"

        importance.plot(kind="barh", ax=ax, color="#2196F3", edgecolor="none")
        ax.set_title(f"{name}\n{suffix}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Importância", fontsize=10)

    # Esconder eixos vazios
    for i in range(n_models, len(axes)):
        axes[i].set_visible(False)

    fig.suptitle(f"Top 20 Features — {outcome_label}\nLTA, Brasil 2007–2025",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: {filename}")


# =============================================================================
# OUTCOME 1: ÓBITO (evolucao 3 + 4)
# =============================================================================
X_obito, y_obito, surv_obito = prepare_survival_data(
    df, evento_codes={3, 4}, evento_label="Óbito (LTA + outras causas)"
)
res_obito, models_obito, Xtrain_obito, ytrain_obito = train_and_evaluate(
    X_obito, y_obito, surv_obito, "Óbito"
)

# =============================================================================
# OUTCOME 2: ABANDONO (evolucao 2)
# =============================================================================
X_abandono, y_abandono, surv_abandono = prepare_survival_data(
    df, evento_codes={2}, evento_label="Abandono de tratamento"
)
res_abandono, models_abandono, Xtrain_abandono, ytrain_abandono = train_and_evaluate(
    X_abandono, y_abandono, surv_abandono, "Abandono"
)

# =============================================================================
# GRÁFICOS
# =============================================================================
os.makedirs("outputs", exist_ok=True)

plot_feature_importance(models_obito, Xtrain_obito, ytrain_obito,
                        "Tempo até Óbito", "latex_paper/template-latex/figures/feature_importance_obito.png")
plot_feature_importance(models_abandono, Xtrain_abandono, ytrain_abandono,
                        "Tempo até Abandono", "latex_paper/template-latex/figures/feature_importance_abandono.png")

# =============================================================================
# C-INDEX COMPARATIVO (ambos outcomes)
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

colors_list = ["#4CAF50", "#8BC34A", "#2196F3", "#03A9F4", "#FF9800", "#FF5722"]

for ax, (label, results) in zip(axes, [("Óbito", res_obito), ("Abandono", res_abandono)]):
    names = list(results.keys())
    c_vals = [results[n]["c_index"] for n in names]
    colors = colors_list[:len(names)]

    bars = ax.barh(names, c_vals, color=colors, edgecolor="none", height=0.6)
    ax.set_xlim(0.45, max(c_vals) + 0.05)
    ax.set_xlabel("C-index", fontsize=12)
    ax.set_title(f"{label}", fontsize=13, fontweight="bold")
    for bar, val in zip(bars, c_vals):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2, f"{val:.4f}",
                va="center", fontsize=10, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)

fig.suptitle("Comparação de Modelos — C-index por Outcome",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("latex_paper/template-latex/figures/c_index_comparison.png", dpi=300, bbox_inches="tight")
print(f"\nC-index comparison salvo em: figures/c_index_comparison.png")
plt.close("all")

print(f"\n{'='*70}")
print("CONCLUÍDO")
print(f"{'='*70}")
