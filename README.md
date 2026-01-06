# Desafio Técnico – Backend & Data Analytics

Este repositório contém os insumos para o desafio técnico. O objetivo é avaliar sua capacidade de engenharia de software e análise de dados, cobrindo todo o fluxo: ingestão, tratamento (data cleaning), extração de inteligência e disponibilização via API RESTful.

---

## 1. Contexto do Projeto

Você deve desenvolver uma solução backend que processe um dataset de saúde "sujo" (raw data), realize a higienização desses dados e exponha funcionalidades operacionais e analíticas.

### O Dataset

O arquivo `unclean_smartwatch_health_data.csv` está na raiz do projeto. Ele simula dados de coleta de sensores de smartwatches e contém inconsistências propositais de diversas naturezas (sintáticas, semânticas e lógicas).

**Dicionário de Dados:**
| Coluna | Descrição |
| :--- | :--- |
| `User ID` | Identificador único do usuário |
| `Heart Rate (BPM)` | Batimentos por minuto |
| `Blood Oxygen Level (%)` | Saturação de oxigênio no sangue |
| `Step Count` | Contagem de passos do dia |
| `Sleep Duration (hours)` | Horas de sono |
| `Activity Level` | Categoria de atividade (ex: Sedentary, Active) |
| `Stress Level` | Nível de estresse relatado (Escala numérica) |

---

## 2. Escopo Técnico

### A. Análise e Engenharia de Dados (Notebook)

Antes de iniciar a API, você deve atuar na preparação dos dados. Crie um notebook (`analysis/data_engineering.ipynb`) que execute:

1. **Auditoria e Limpeza:**
* Identifique e trate as anomalias do dataset.
* Gere um arquivo final confiável chamado `cleaned_data.csv`.
* *Nota:* A estratégia de tratamento (remoção, imputação, correção) fica a seu critério, mas deve ser justificada.


2. **Extração de Insights:**
* Explore os dados para encontrar padrões relevantes.
* Produza pelo menos **3 insights analíticos**, relacionando o *Nível de Estresse* com outras variáveis de saúde.


3. **Modelagem Preditiva:**
* Crie um modelo simplificado (ou regra lógica robusta) para prever o `Stress Level` baseando-se nas métricas fisiológicas disponíveis.



### B. Desenvolvimento da API RESTful

**Stack Tecnológico:**
Para este desafio, utilize frameworks modernos e eficientes. Escolha uma das opções abaixo:

* **Python:** FastAPI ou Flask.
* **Java:** Quarkus.

A aplicação deve ser autocontida, utilizando um **Banco de Dados em Memória** (SQLite).

**Requisitos de Inicialização:**

* A aplicação deve ler o arquivo `cleaned_data.csv` no startup e popular o banco de dados.

**Endpoints Obrigatórios:**

* **Operacional (CRUD):**
* `POST /records`: Inserir novo registro. Deve conter validações baseadas nas regras que você descobriu na fase de limpeza (ex: rejeitar dados fisiologicamente impossíveis).
* `GET /records/{userId}`: Histórico do usuário.
* `DELETE /records/{userId}`: Remoção de dados.


* **Analítico (Dashboard):**
* `GET /analytics/insights`: Este endpoint deve retornar um JSON contendo os dados sumarizados que fundamentam os insights que você descobriu no notebook.
* *Exemplo:* Se você descobriu que "X causa Y", este endpoint deve devolver os números que provam isso.


* **Predição (ML Integration):**
* `POST /predict/stress`:
* **Input:** JSON com métricas de saúde (Passos, Sono, BPM, Oxigenação).
* **Processamento:** Aplica o modelo/regra criado no notebook.
* **Output:** O nível de estresse previsto.





### C. Infraestrutura

1. **Dockerfile:** A imagem deve conter a aplicação e o dataset processado.
2. **Execução:** A aplicação deve ser capaz de rodar via CLI do Docker padrão (sem necessidade de orquestração externa).

---

## 3. Estrutura Sugerida

```
.
├── unclean_smartwatch_health_data.csv  # Dataset Original
├── analysis/
│   └── data_engineering.ipynb          # Notebook (Limpeza + Insights + Modelo)
├── src/                                # Código Fonte da API
├── Dockerfile                          # Instruções de build
└── README.md

```

---

## 4. Critérios de Avaliação e Entrega

### Validação do Ambiente

A solução será validada executando os comandos básicos do Docker. Certifique-se de que sua documentação especifique a porta correta. O avaliador executará:

```bash
# Exemplo de execução
docker build -t health-api .
docker run -p 8080:8080 health-api

```

### Documentação (`DOCS.md`)

Além do código, entregue um documento explicando:

1. **Guia de Execução:** O comando exato `docker run` necessário para rodar seu projeto (incluindo mapeamento de portas).
2. **Relatório de Data Quality:** Quais problemas foram encontrados no dataset e como foram resolvidos.
3. **Insights de Negócio:** Explicação dos padrões encontrados e como eles foram traduzidos para o endpoint `/analytics/insights`.
4. **Decisões Técnicas:** Frameworks escolhidos, arquitetura e estratégia de deploy.

### Fluxo de Submissão

1. Faça o fork do repositório.
2. Desenvolva em uma branch com seu nome (`feature/nome-sobrenome`).
3. Abra um Pull Request para a `main` (sem realizar o merge).
4. Notifique a conclusão.
