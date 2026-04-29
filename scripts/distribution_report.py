"""
Relatório de Distribuição — LTA

Gera um relatório detalhado da distribuição de cada variável do dataset
preparado, incluindo:
  - Variáveis contínuas: média, mediana, DP, quartis, min/max
  - Variáveis categóricas: contagem e percentual por valor com labels legíveis
  - Outcomes primários e secundários
  - Matriz visual de missing por coluna

Entrada: dataset_lta0725/dataset_prepared.csv
Saída:   console (texto)
"""
import pandas as pd
import numpy as np

# =============================================================================
# LOAD (dataset preparado)
# =============================================================================
INPUT = "dataset_lta0725/dataset_prepared.csv"
df = pd.read_csv(INPUT, low_memory=False)
print(f"Dataset: {len(df):,} registros x {df.shape[1]} colunas")
print(f"Fonte: {INPUT}\n")

# =============================================================================
# LABELS DOS VALORES (para exibição legível)
# =============================================================================
value_labels = {
    "cs_sexo": {"M": "Masculino", "F": "Feminino", "I": "Ignorado"},
    "cs_gestant": {1: "1º trimestre", 2: "2º trimestre", 3: "3º trimestre",
                   4: "IG ignorada", 5: "Não", 6: "Não se aplica", 9: "Ignorado"},
    "cs_raca": {1: "Branca", 2: "Preta", 3: "Amarela", 4: "Parda", 5: "Indígena", 9: "Ignorado"},
    "cs_escol_n": {43: "Analfabeto", 1: "1ª-4ª inc.", 2: "4ª comp.", 3: "5ª-8ª inc.",
                   4: "EF comp.", 5: "EM inc.", 6: "EM comp.", 7: "ES inc.",
                   8: "ES comp.", 9: "Ignorado", 10: "N/A"},
    "cli_co_hiv": {1: "Sim", 2: "Não", 9: "Ignorado"},
    "lab_parasi": {1: "Positivo", 2: "Negativo", 3: "Não realizado"},
    "lab_irm": {1: "Positivo", 2: "Negativo", 3: "Não realizado"},
    "lab_histop": {1: "Encontro parasita", 2: "Compatível", 3: "Não compatível", 4: "Não realizado"},
    "criterio": {1: "Laboratorial", 2: "Clínico-epidemiológico"},
    "con_class_": {1: "Autóctone", 2: "Importado", 3: "Indeterminado"},
    "tpautocto": {1: "Sim", 2: "Não", 3: "Indeterminado"},
    "doenca_tra": {1: "Sim", 2: "Não", 9: "Ignorado"},
    "cli_mucosa": {1: "Sim", 0: "Não"},
    "cli_cicatr": {1: "Sim", 0: "Não"},
    "cli_cutane": {1: "Sim", 0: "Não"},
    "evolucao": {1: "Cura", 2: "Abandono", 3: "Óbito LTA", 4: "Óbito outras", 5: "Transferência", 6: "Mudança dx"},
    "clas_forma": {1: "Cutânea", 2: "Mucosa", 9: "Ignorada"},
    "tra_droga_": {1: "Antimonial", 2: "Anfotericina B", 3: "Pentamidina", 4: "Outras", 5: "Não utilizada"},
}

uf_labels = {
    11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
    21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL",
    28: "SE", 29: "BA", 31: "MG", 32: "ES", 33: "RJ", 35: "SP", 41: "PR",
    42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF",
}
value_labels["sg_uf"] = uf_labels


def print_separator(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def report_continuous(col, label):
    """Report para variáveis contínuas."""
    data = df[col].dropna()
    missing = df[col].isnull().sum()
    miss_pct = missing / len(df) * 100
    print(f"\n--- {label} ({col}) ---")
    print(f"  Válidos: {len(data):,} | Missing: {missing:,} ({miss_pct:.1f}%)")
    if len(data) == 0:
        print("  Sem dados válidos.")
        return
    print(f"  Média:   {data.mean():.1f}")
    print(f"  Mediana: {data.median():.1f}")
    print(f"  DP:      {data.std():.1f}")
    print(f"  Min:     {data.min():.1f}")
    print(f"  P25:     {data.quantile(0.25):.1f}")
    print(f"  P75:     {data.quantile(0.75):.1f}")
    print(f"  Max:     {data.max():.1f}")


def report_categorical(col, label, top_n=None):
    """Report para variáveis categóricas."""
    data = df[col]
    missing = data.isnull().sum()
    miss_pct = missing / len(df) * 100
    counts = data.dropna().value_counts().sort_index()
    total_valid = counts.sum()

    print(f"\n--- {label} ({col}) ---")
    print(f"  Válidos: {total_valid:,} | Missing: {missing:,} ({miss_pct:.1f}%)")

    labels = value_labels.get(col, {})
    display = counts.sort_values(ascending=False)
    if top_n:
        display = display.head(top_n)

    for val, count in display.items():
        pct = count / total_valid * 100
        lbl = labels.get(val, labels.get(int(val) if not isinstance(val, str) else val, ""))
        lbl_str = f" ({lbl})" if lbl else ""
        print(f"  {val}{lbl_str:<30} {count:>8,}  ({pct:>5.1f}%)")

    if top_n and len(counts) > top_n:
        print(f"  ... e mais {len(counts) - top_n} categorias")


# =============================================================================
# FEATURES CONTÍNUAS
# =============================================================================
print_separator("FEATURES CONTÍNUAS")
report_continuous("idade", "Idade (anos)")
report_continuous("tempo_tratamento", "Tempo até tratamento (dias)")

# =============================================================================
# FEATURES CATEGÓRICAS
# =============================================================================
print_separator("FEATURES CATEGÓRICAS")
report_categorical("cs_sexo", "Sexo")
report_categorical("cs_gestant", "Gestante")
report_categorical("cs_raca", "Raça/Cor")
report_categorical("cs_escol_n", "Escolaridade")
report_categorical("cli_co_hiv", "Co-infecção HIV")
report_categorical("lab_parasi", "Parasitológico direto")
report_categorical("lab_irm", "IRM (Montenegro)")
report_categorical("lab_histop", "Histopatologia")
report_categorical("criterio", "Critério de confirmação")
report_categorical("con_class_", "Classificação epidemiológica")
report_categorical("tpautocto", "Autóctone de residência")
report_categorical("doenca_tra", "Doença relacionada ao trabalho")
report_categorical("sg_uf", "UF de residência", top_n=10)
report_categorical("nu_ano", "Ano da notificação")

# =============================================================================
# OUTCOMES
# =============================================================================
print_separator("OUTCOMES (DESFECHOS)")

print("\n--- Outcomes primários (binários) ---")
report_categorical("cli_mucosa", "Lesão mucosa")
report_categorical("cli_cicatr", "Cicatrizes cutâneas")

print("\n--- Outcomes secundários ---")
report_categorical("cli_cutane", "Lesão cutânea")
report_categorical("evolucao", "Evolução do caso")
report_categorical("clas_forma", "Forma clínica")
report_categorical("tra_droga_", "Droga inicial")
report_continuous("tra_peso", "Peso (kg)")
report_continuous("tempo_obito", "Tempo até óbito (dias)")

# =============================================================================
# MATRIZ DE MISSING
# =============================================================================
print_separator("RESUMO DE MISSING POR COLUNA")
for col in df.columns:
    miss = df[col].isnull().sum()
    pct = miss / len(df) * 100
    bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
    print(f"  {col:<22} {bar} {pct:>5.1f}% ({miss:,})")
