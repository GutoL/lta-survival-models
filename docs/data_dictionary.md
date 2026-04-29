# Dicionário de Dados — LTA (Leishmaniose Tegumentar Americana)

Dataset: `dataset_lta0725/dataset_main.csv`
Fonte: SINAN (Sistema de Informação de Agravos de Notificação)
Agravo: B55.1 — Leishmaniose Tegumentar Americana
Período: 2007–2025
Registros: 351.267

---

## Classificação das Variáveis

### Outcomes (Desfechos)

| Coluna | Descrição | Tipo | Valores |
|---|---|---|---|
| cli_mucosa | Presença de lesão mucosa | Binária | 1=Sim, 2=Não |
| cli_cicatr | Presença de cicatrizes cutâneas | Binária | 1=Sim, 2=Não |
| cli_cutane | Presença de lesão cutânea | Binária | 1=Sim, 2=Não |
| clas_forma | Forma clínica | Categórica | 1=Cutânea, 2=Mucosa, 9=Ignorada |
| evolucao | Evolução do caso | Categórica | 1=Cura, 2=Abandono, 3=Óbito LTA, 4=Óbito outras causas, 5=Transferência, 6=Mudança de diagnóstico |
| dt_obito | Data do óbito | Data | Para derivar tempo até evento (dt_obito - dt_notific) |
| cla_tipo_n | Tipo de entrada (recidiva como outcome) | Categórica | 1=Caso novo, 2=Recidiva, 3=Transferência, 9=Ignorado |
| tra_droga_ | Droga inicial (outcome futuro) | Categórica | 1=Antimonial pentavalente, 2=Anfotericina B, 3=Pentamidina, 4=Outras, 5=Não utilizada |
| tra_peso | Peso do paciente (outcome futuro) | Numérica | kg |

### Variáveis Derivadas (a criar)

| Variável | Fórmula | Descrição |
|---|---|---|
| idade | Decodificar nu_idade_n | Idade em anos (contínua) |
| tempo_tratamento | dt_inic_tr - dt_notific | Dias entre notificação e início do tratamento |
| tempo_obito | dt_obito - dt_notific | Dias entre notificação e óbito (survival) |

### Features (Preditores)

#### Demográficas

| Coluna | Descrição | Tipo | Valores / Observações |
|---|---|---|---|
| nu_idade_n | Idade (codificação SINAN) | Numérica | Primeiro dígito = unidade (4=anos, 3=meses, 2=dias, 1=horas). Ex: 4045 = 45 anos. Decodificar para idade em anos. |
| cs_sexo | Sexo | Categórica | M=Masculino, F=Feminino, I=Ignorado |
| cs_gestant | Gestante | Categórica | 1=1ºtri, 2=2ºtri, 3=3ºtri, 4=IG ignorada, 5=Não, 6=Não se aplica, 9=Ignorado |
| cs_raca | Raça/Cor | Categórica | 1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indígena, 9=Ignorado |
| cs_escol_n | Escolaridade | Categórica | 43=Analfabeto, 1=1ª-4ª inc., 2=4ª comp., 3=5ª-8ª inc., 4=EF comp., 5=EM inc., 6=EM comp., 7=ES inc., 8=ES comp., 9=Ignorado, 10=N/A |

#### Clínicas

| Coluna | Descrição | Tipo | Valores |
|---|---|---|---|
| cli_co_hiv | Co-infecção HIV | Categórica | 1=Sim, 2=Não, 9=Ignorado |

#### Laboratoriais

| Coluna | Descrição | Tipo | Valores |
|---|---|---|---|
| lab_parasi | Parasitológico direto | Categórica | 1=Positivo, 2=Negativo, 3=Não realizado |
| lab_irm | IRM (Montenegro) | Categórica | 1=Positivo, 2=Negativo, 3=Não realizado |
| lab_histop | Histopatologia | Categórica | 1=Encontro do parasita, 2=Compatível, 3=Não compatível, 4=Não realizado |

#### Epidemiológicas

| Coluna | Descrição | Tipo | Valores |
|---|---|---|---|
| criterio | Critério de confirmação | Categórica | 1=Laboratorial, 2=Clínico epidemiológico |
| con_class_ | Classificação epidemiológica | Categórica | 1=Autóctone, 2=Importado, 3=Indeterminado |
| tpautocto | Caso autóctone de residência? | Categórica | 1=Sim, 2=Não, 3=Indeterminado |
| doenca_tra | Doença relacionada ao trabalho | Categórica | 1=Sim, 2=Não, 9=Ignorado |

#### Geográficas / Temporais

| Coluna | Descrição | Tipo | Valores |
|---|---|---|---|
| nu_ano | Ano da notificação | Inteiro | 2007–2025 |
| sg_uf | UF de residência | Código IBGE | 11=RO ... 53=DF |
| dt_notific | Data da notificação | Data | Para derivar variáveis temporais |
| dt_inic_tr | Data do início do tratamento | Data | Para derivar tempo_tratamento |

### Colunas Removidas

#### Por ausência ≥ 90%

migrado_w, flxrecebi, mun_des1, mun_des2, mun_des3, co_uf_des1, co_uf_des2, co_uf_des3,
dt_desc1, dt_desc2, dt_desc3, cs_flxret, nu_lote_v, nu_lote_h, dt_transrm, sem_diag,
sem_not, dt_transdm, dt_transse, dt_transrs, dt_transus, nduplic_n

#### Por predominância ≥ 95% ou valor único

tp_not (100% Individual), id_agravo (100% B551), id_pais (99.6% Brasil),
nu_lote_i (100% zero), pa_des1/2/3 (100% zero), copaisinf (91.6% Brasil)

#### Identificadores / Administrativos sem valor analítico

id_unidade, id_regiona, id_rg_resi, id_municip, id_mn_resi, id_pais,
dt_digita, dt_transsm, dt_invest, dt_encerra, titulo, ano_nasc,
id_ocupa_n, tra_dose, tra_ampola, tra_outr_n, coufinf, comuninf
