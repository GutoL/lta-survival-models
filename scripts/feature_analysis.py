"""
Análise de Features — LTA

Script exploratório para identificar colunas com alta ausência (>= 90%),
predominância de um único valor (>= 95%), e listar as colunas candidatas
a features para modelagem.

Entrada: dataset_lta0725/dataset_main.csv
Saída:   console (texto)
"""
import pandas as pd

df = pd.read_csv("dataset_lta0725/dataset_main.csv", low_memory=False)
print(f"Total registros: {len(df):,}\n")

print("=" * 80)
print("1. COLUNAS COM ALTA AUSÊNCIA (>= 90%)")
print("=" * 80)
missing = df.isnull().sum() / len(df) * 100
high_missing = missing[missing >= 90].sort_values(ascending=False)
for col, pct in high_missing.items():
    print(f"  {col:<20} {pct:>6.1f}% ausente")

print(f"\n{'=' * 80}")
print("2. COLUNAS COM VALOR ÚNICO OU PREDOMINÂNCIA >= 95%")
print("=" * 80)
for col in df.columns:
    non_null = df[col].dropna()
    if len(non_null) == 0:
        continue
    top_freq = non_null.value_counts(normalize=True).iloc[0] * 100
    top_val = non_null.value_counts().index[0]
    n_unique = non_null.nunique()
    if top_freq >= 95 or n_unique == 1:
        print(f"  {col:<20} valor '{top_val}' = {top_freq:.1f}% | {n_unique} valor(es) único(s)")

print(f"\n{'=' * 80}")
print("3. COLUNAS RESTANTES — CANDIDATAS A FEATURES")
print("=" * 80)

# Excluir: 100% ausentes, >90% ausentes, outcomes, identificadores
exclude_high_missing = set(high_missing.index)
outcomes = {"cli_mucosa", "cli_cicatr", "clas_forma"}
ids_admin = {
    "id_agravo", "id_unidade", "id_regiona", "id_rg_resi", "id_pais",
    "dt_digita", "dt_transus", "dt_transdm", "dt_transsm", "dt_transrm",
    "dt_transrs", "dt_transse", "nu_lote_i", "dt_invest", "dt_encerra",
    "dt_obito", "titulo"
}

exclude = exclude_high_missing | outcomes | ids_admin
remaining = [c for c in df.columns if c not in exclude]

for col in remaining:
    non_null = df[col].dropna()
    if len(non_null) == 0:
        continue
    miss_pct = df[col].isnull().sum() / len(df) * 100
    n_unique = non_null.nunique()
    top_val = non_null.value_counts().index[0]
    top_pct = non_null.value_counts(normalize=True).iloc[0] * 100
    print(f"  {col:<20} missing={miss_pct:>5.1f}% | únicos={n_unique:>6} | top='{top_val}' ({top_pct:.1f}%)")
