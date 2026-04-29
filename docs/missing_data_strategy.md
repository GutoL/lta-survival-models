# Estratégia de Dados Faltantes — LTA

## Regra Geral

- **Feature com > 50% missing**: remover como feature (manter no arquivo original)
- **Feature com < 50% missing**: aplicar estratégia de preenchimento
- **Outcomes**: nunca preencher — missing no outcome = excluir a linha daquela análise

---

## Features — Estratégias de Preenchimento

### Categóricas → Nova categoria "Desconhecido"

Justificativa: no SINAN, o dado faltante geralmente não é aleatório (MNAR — Missing Not At Random). Criar uma categoria própria preserva essa informação, que pode ser preditiva.

| Coluna | Missing | Estratégia | Valor atribuído |
|---|---|---|---|
| cs_raca | 1.1% | Categoria "Desconhecido" | 0 |
| cs_escol_n | 9.6% | Categoria "Desconhecido" | 0 |
| cli_co_hiv | 44.3% | Categoria "Desconhecido" | 0 |
| con_class_ | 13.6% | Categoria "Desconhecido" | 0 |
| doenca_tra | 16.2% | Categoria "Desconhecido" | 0 |
| sg_uf | 0.4% | Categoria "Desconhecido" | 0 |

Nota: `cli_co_hiv` já teve os valores "Ignorado" (9) convertidos para NaN na etapa de limpeza. O missing aqui inclui tanto os originalmente ausentes quanto os ex-ignorados.

### Contínuas → Mediana

| Coluna | Missing | Estratégia | Justificativa |
|---|---|---|---|
| tempo_tratamento | 15.0% | Mediana | Robusta a outliers, preserva tendência central |

### Sem preenchimento (poucos missing, dropar linhas)

| Coluna | Missing | Estratégia |
|---|---|---|
| cs_gestant | 0.0% | Nenhuma ação |
| lab_parasi | 0.0% | Nenhuma ação |
| lab_irm | 0.0% | Nenhuma ação |
| lab_histop | 0.0% | Nenhuma ação |
| idade | 0.0% | Nenhuma ação |

---

## Outcomes — Sem Preenchimento

Missing no outcome significa que o dado não foi registrado. Preencher introduziria viés no desfecho.

| Coluna | Missing | Ação |
|---|---|---|
| cli_mucosa | 0.0% | Nenhuma |
| cli_cicatr | 95.1% | Nenhuma — amostra reduzida (~13k registros válidos) |
| cli_cutane | 0.0% | Nenhuma |
| evolucao | 22.7% | Nenhuma — excluir linhas sem desfecho na análise |
| dt_obito / tempo_obito | 99.5% | Nenhuma — apenas para survival analysis |
| tra_droga_ | 10.4% | Nenhuma |
| tra_peso | 7.4% | Nenhuma |

---

## Observações

1. `cli_cicatr` como outcome terá amostra muito menor (~13k vs ~268k). Modelos para esse desfecho devem ser interpretados com cautela.
2. `cli_co_hiv` é clinicamente importante apesar do alto missing. A categoria "Desconhecido" permite que o modelo aprenda se a ausência do dado está associada ao desfecho.
3. Outcomes nunca são preenchidos — cada análise usa apenas os registros com outcome válido.
4. O arquivo original (`dataset_main.csv`) nunca é modificado. Todas as transformações são aplicadas em memória e salvas em `dataset_prepared.csv`.
