"""
Preparação de Features — LTA (Leishmaniose Tegumentar Americana)

Este script realiza a limpeza e preparação do dataset do SINAN para análise
de sobrevivência. As etapas incluem:
  1. Remoção de duplicidades e filtros de inclusão
  2. Seleção de colunas relevantes (features e outcomes)
  3. Decodificação da idade (codificação SINAN)
  4. Derivação de variáveis temporais (tempo até tratamento, encerramento, óbito)
  5. Reclassificação de valores ignorados (cli_co_hiv)
  6. Recodificação de outcomes binários para 0/1
  7. Preenchimento de dados faltantes (ver docs/missing_data_strategy.md)

Entrada: dataset_lta0725/dataset_main.csv
Saída:   dataset_lta0725/dataset_prepared.csv
"""
import pandas as pd
import numpy as np

# =============================================================================
# LOAD
# =============================================================================
df = pd.read_csv("dataset_lta0725/dataset_main.csv", low_memory=False)
print(f"[0] Dataset carregado: {len(df):,} registros\n")

# =============================================================================
# LIMPEZA BASE (mesma do data_cleaning.py)
# =============================================================================
df = df[df["nduplic_n"] != 2]
print(f"[1] Remover duplicidades: {len(df):,}")

# tp_not: manter apenas 1 (Negativa) e 2 (Individual)
df = df[df["tp_not"].isin([1, 2])]
print(f"[2] Filtrar tp_not (1,2): {len(df):,}")

# Casos novos apenas
df = df[df["cla_tipo_n"] == 1]
print(f"[3] Apenas casos novos: {len(df):,}")

# Critério laboratorial apenas
df = df[df["criterio"] == 1]
print(f"[4] Critério laboratorial: {len(df):,}")

# =============================================================================
# SELECIONAR COLUNAS RELEVANTES
# =============================================================================
features = [
    "nu_idade_n", "cs_sexo", "cs_gestant", "cs_raca", "cs_escol_n",
    "cli_co_hiv",
    "lab_parasi", "lab_irm", "lab_histop",
    "criterio", "con_class_", "tpautocto", "doenca_tra",
    "nu_ano", "sg_uf", "dt_notific", "dt_inic_tr",
]
outcomes = [
    "cli_mucosa", "cli_cicatr", "cli_cutane",
    "clas_forma", "evolucao", "dt_obito", "dt_encerra",
    "cla_tipo_n", "tra_droga_", "tra_peso",
]

keep = features + outcomes
df = df[[c for c in keep if c in df.columns]]
print(f"[5] Colunas selecionadas: {df.shape[1]}")

# =============================================================================
# DECODIFICAR IDADE (nu_idade_n)
# =============================================================================
def decode_age(val):
    """Decodifica idade SINAN: 1o dígito = unidade (4=anos, 3=meses, 2=dias, 1=horas)."""
    if pd.isna(val):
        return np.nan
    val = int(val)
    unit = val // 1000
    age = val % 1000
    if unit == 4:
        return age            # anos
    elif unit == 3:
        return age / 12       # meses -> anos
    elif unit == 2:
        return age / 365      # dias -> anos
    elif unit == 1:
        return age / 8760     # horas -> anos
    return np.nan

df["idade"] = df["nu_idade_n"].apply(decode_age)
df = df.drop(columns=["nu_idade_n"])
print(f"[6] Idade decodificada: min={df['idade'].min():.1f}, max={df['idade'].max():.1f}, "
      f"mediana={df['idade'].median():.1f}")

# Remover idades implausíveis (0 ou >120 anos)
before = len(df)
df = df[(df["idade"] > 0) & (df["idade"] <= 120)]
print(f"[7] Remover idade <= 0 ou > 120: {len(df):,} (removidos: {before - len(df)})")

# =============================================================================
# DERIVAR TEMPO ATÉ TRATAMENTO
# =============================================================================
df["dt_notific"] = pd.to_datetime(df["dt_notific"], errors="coerce")
df["dt_inic_tr"] = pd.to_datetime(df["dt_inic_tr"], errors="coerce")
df["dt_obito"] = pd.to_datetime(df["dt_obito"], errors="coerce")
df["dt_encerra"] = pd.to_datetime(df["dt_encerra"], errors="coerce")

df["tempo_tratamento"] = (df["dt_inic_tr"] - df["dt_notific"]).dt.days
df["tempo_obito"] = (df["dt_obito"] - df["dt_notific"]).dt.days
df["tempo_encerramento"] = (df["dt_encerra"] - df["dt_notific"]).dt.days

valid_te = df["tempo_encerramento"].dropna()
print(f"[8a] Tempo até encerramento: mediana={valid_te.median():.0f} dias, "
      f"disponível em {len(valid_te):,}/{len(df):,} registros")

valid_tt = df["tempo_tratamento"].dropna()
print(f"[8] Tempo até tratamento: mediana={valid_tt.median():.0f} dias, "
      f"disponível em {len(valid_tt):,}/{len(df):,} registros")

# Remover tempo_tratamento negativo (datas inconsistentes)
neg_tt = (df["tempo_tratamento"] < 0).sum()
df.loc[df["tempo_tratamento"] < 0, "tempo_tratamento"] = np.nan
print(f"[8b] Tempo tratamento negativo → NaN: {neg_tt:,} registros")

# =============================================================================
# cli_co_hiv: Ignorado (9) → NaN
# =============================================================================
hiv_ignored = (df["cli_co_hiv"] == 9).sum()
df.loc[df["cli_co_hiv"] == 9, "cli_co_hiv"] = np.nan
print(f"[8c] cli_co_hiv ignorado (9) → NaN: {hiv_ignored:,} registros")

# =============================================================================
# RECODIFICAR OUTCOMES PARA 0/1
# =============================================================================
# cli_mucosa: 1=Sim -> 1, 2=Não -> 0
df["cli_mucosa"] = df["cli_mucosa"].map({1: 1, 2: 0})

# cli_cicatr: 1=Sim -> 1, 2=Não -> 0
df["cli_cicatr"] = df["cli_cicatr"].map({1: 1, 2: 0})

# cli_cutane: 1=Sim -> 1, 2=Não -> 0
df["cli_cutane"] = df["cli_cutane"].map({1: 1, 2: 0})

print(f"[9] Outcomes recodificados (0/1):")
print(f"    cli_mucosa: {df['cli_mucosa'].sum():,} positivos / {df['cli_mucosa'].count():,} válidos "
      f"({df['cli_mucosa'].mean()*100:.1f}%)")
print(f"    cli_cicatr: {df['cli_cicatr'].sum():,} positivos / {df['cli_cicatr'].count():,} válidos "
      f"({df['cli_cicatr'].mean()*100:.1f}%)")
print(f"    cli_cutane: {df['cli_cutane'].sum():,} positivos / {df['cli_cutane'].count():,} válidos "
      f"({df['cli_cutane'].mean()*100:.1f}%)")

# =============================================================================
# PREENCHIMENTO DE MISSING (ver docs/missing_data_strategy.md)
# =============================================================================
print(f"\n[10] Preenchimento de missing:")

# Categóricas → categoria "Desconhecido" (valor 0)
cat_fill_cols = ["cs_raca", "cs_escol_n", "cli_co_hiv", "con_class_", "doenca_tra", "sg_uf"]
for col in cat_fill_cols:
    n_miss = df[col].isnull().sum()
    if n_miss > 0:
        df[col] = df[col].fillna(0)
        print(f"     {col:<18} {n_miss:>6,} NaN → 0 (Desconhecido)")

# Contínuas → mediana
tt_median = df["tempo_tratamento"].median()
n_miss_tt = df["tempo_tratamento"].isnull().sum()
df["tempo_tratamento"] = df["tempo_tratamento"].fillna(tt_median)
print(f"     {'tempo_tratamento':<18} {n_miss_tt:>6,} NaN → {tt_median:.0f} (mediana)")

# =============================================================================
# RESUMO FINAL
# =============================================================================
print(f"\n{'='*60}")
print(f"Dataset preparado: {len(df):,} registros x {df.shape[1]} colunas")
print(f"\nFeatures ({len(features) - 1} + 2 derivadas):")
feat_cols = [c for c in df.columns if c not in outcomes]
for c in feat_cols:
    miss = df[c].isnull().sum() / len(df) * 100
    print(f"  {c:<22} missing={miss:.1f}%")

print(f"\nOutcomes:")
for c in outcomes:
    if c in df.columns:
        miss = df[c].isnull().sum() / len(df) * 100
        print(f"  {c:<22} missing={miss:.1f}%")

# =============================================================================
# SALVAR
# =============================================================================
output_path = "dataset_lta0725/dataset_prepared.csv"
df.to_csv(output_path, index=False)
print(f"\nSalvo em: {output_path}")
