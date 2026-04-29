# lta-survival-models

Comparação de modelos estatísticos tradicionais e de aprendizado de máquina na
identificação de fatores de risco para óbito e abandono de tratamento em
pacientes com Leishmaniose Tegumentar Americana (LTA) no Brasil (2007–2025).

## Autores

- Guto Leoni Santos (gutoleo@amazon.com)
- Vanderson Sampaio (vanderson.sampaio@itps.org.br)

## Estrutura do Projeto

```
├── README.md
├── requirements.txt
├── .gitignore
│
├── scripts/                      # Scripts Python
│   ├── feature_preparation.py    # Limpeza e preparação do dataset
│   ├── feature_analysis.py       # Análise exploratória de features
│   ├── distribution_report.py    # Relatório de distribuição das variáveis
│   ├── kaplan_meier.py           # Curvas de KM (análise exploratória completa)
│   ├── kaplan_meier_paper.py     # Curvas de KM (figuras para o paper)
│   └── survival_models.py        # Treinamento e comparação dos modelos
│
├── docs/                         # Documentação
│   ├── data_dictionary.md        # Dicionário de dados (todas as variáveis)
│   └── missing_data_strategy.md  # Estratégia de tratamento de dados faltantes
│
└── outputs/                      # Saídas geradas pelos scripts
```

## Dados

O dataset utilizado é proveniente do SINAN (Sistema de Informação de Agravos
de Notificação), contendo 351.267 notificações de LTA (CID-10: B55.1) no
Brasil entre 2007 e 2025.

**Os dados não estão incluídos no repositório.** Para reproduzir as análises,
crie uma pasta `dataset_lta0725/` na raiz do projeto com os seguintes arquivos:

- `dataset_main.csv` — dataset original do SINAN
- `value_labels.csv` — rótulos dos valores categóricos
- `variable_labels.csv` — rótulos das variáveis

## Como Executar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Preparar o dataset

```bash
python scripts/feature_preparation.py
```

Gera o arquivo `dataset_lta0725/dataset_prepared.csv` com os dados limpos.

### 3. Análise exploratória

```bash
python scripts/distribution_report.py
python scripts/kaplan_meier.py
```

### 4. Treinar modelos de sobrevivência

```bash
python scripts/survival_models.py
```

## Modelos Avaliados

| Tipo | Modelo | Biblioteca |
|---|---|---|
| Estatístico | Cox PH | scikit-survival |
| Estatístico | Cox Elastic Net | scikit-survival |
| Árvore única | Survival Tree | scikit-survival |
| Árvore única | Extra Survival Tree | scikit-survival |
| Ensemble | Random Survival Forest | scikit-survival |
| Ensemble | Extra Survival Trees | scikit-survival |

## Resultados Principais

### Óbito (C-index no test set)

| Modelo | C-index |
|---|---|
| **Cox PH** | **0,8965** |
| Random Survival Forest | 0,8946 |
| Extra Survival Trees | 0,8945 |
| Cox Elastic Net | 0,8913 |
| Extra Survival Tree | 0,8314 |
| Survival Tree | 0,7956 |

### Abandono de Tratamento (C-index no test set)

| Modelo | C-index |
|---|---|
| **Random Survival Forest** | **0,6697** |
| Extra Survival Trees | 0,6663 |
| Cox PH | 0,6599 |
| Extra Survival Tree | 0,6225 |
| Survival Tree | 0,6171 |
| Cox Elastic Net | 0,5117 |

## Documentação

- [Dicionário de Dados](docs/data_dictionary.md) — descrição de todas as variáveis do dataset
- [Estratégia de Dados Faltantes](docs/missing_data_strategy.md) — regras de preenchimento e justificativas

## Licença

Este projeto tem propósito acadêmico e é distribuído sob a licença [Apache 2.0](LICENSE).
