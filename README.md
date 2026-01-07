# Desafio Técnico – Backend & Data Analytics

Este repositório contém os insumos para o desafio técnico. O objetivo é avaliar sua capacidade de engenharia de software e análise de dados, cobrindo todo o fluxo: ingestão, tratamento (data cleaning), extração de inteligência e disponibilização via API RESTful.

---

## 1. Contexto do Projeto

Você deve desenvolver uma solução backend que processe um dataset de saúde e estilo de vida, realize a higienização desses dados (tratando tipagens e inconsistências de categorias) e exponha funcionalidades operacionais e analíticas.

### O Dataset

O arquivo `Sleep_health_and_lifestyle_dataset.csv` está na raiz do projeto. Ele contém dados reais sobre o sono e hábitos diários de indivíduos, abrangendo métricas cardiovasculares e distúrbios do sono.

**Dicionário de Dados:**
| Coluna | Descrição |
| :--- | :--- |
| `Person ID` | Identificador único do paciente |
| `Gender` | Gênero |
| `Age` | Idade |
| `Occupation` | Profissão / Ocupação |
| `Sleep Duration` | Duração do sono (horas/dia) |
| `Quality of Sleep` | Avaliação subjetiva da qualidade do sono (1-10) |
| `Physical Activity Level` | Minutos de atividade física diária |
| `Stress Level` | Nível de estresse (1-10) |
| `BMI Category` | Categoria de IMC (ex: Normal, Overweight) |
| `Blood Pressure` | Pressão Arterial (formato "126/83") |
| `Heart Rate` | Frequência cardíaca em repouso (BPM) |
| `Daily Steps` | Passos diários |
| `Sleep Disorder` | Distúrbio diagnosticado (None, Insomnia, Sleep Apnea) |

---

## 2. Escopo Técnico

### A. Análise e Engenharia de Dados (Notebook)

Antes de iniciar a API, você deve atuar na preparação dos dados. Crie um notebook (`analysis/data_engineering.ipynb`) que execute:

1. **Auditoria e Limpeza:**
* Identifique e trate inconsistências no dataset (ex: padronização de categorias de IMC, tratamento de colunas compostas como *Blood Pressure* para cálculos numéricos e tratamento de nulos em *Sleep Disorder*).
* Gere um arquivo final confiável chamado `cleaned_health_data.csv`.
* *Nota:* A estratégia de tratamento (remoção, imputação, correção) fica a seu critério, mas deve ser justificada.


2. **Extração de Insights:**
* Explore os dados para encontrar padrões relevantes.
* Produza pelo menos **3 insights analíticos**, como relacionar a *Ocupação* com a qualidade do sono ou a *Pressão Arterial* com o nível de estresse.


3. **Modelagem Preditiva:**
* Crie um modelo simplificado (ou regra lógica robusta) para prever a presença de **Distúrbio do Sono** (`Sleep Disorder`) baseando-se nas métricas de estilo de vida e saúde.



### B. Desenvolvimento da API RESTful

**Stack Tecnológico:**
Para este desafio, utilize frameworks modernos e eficientes. Escolha uma das opções abaixo:

* **Python:** FastAPI ou Flask.
* **Java:** Quarkus.

A aplicação deve ser autocontida, utilizando um **Banco de Dados em Memória** (SQLite ou H2).

**Requisitos de Inicialização:**

* A aplicação deve ler o arquivo `cleaned_health_data.csv` no startup e popular o banco de dados.

**Endpoints Obrigatórios:**

* **Operacional (CRUD):**
* `POST /patients`: Inserir novo paciente. Deve conter validações (ex: não permitir *Sleep Duration* > 24 horas).
* `GET /patients/{id}`: Detalhes do paciente.
* `DELETE /patients/{id}`: Remoção de dados.


* **Analítico (Dashboard):**
* `GET /analytics/insights`: Este endpoint deve retornar um JSON contendo os dados sumarizados que fundamentam os insights que você descobriu no notebook.
* *Exemplo:* Retornar a média de qualidade de sono agrupada por profissão.


* **Predição (ML Integration):**
* `POST /predict/sleep-disorder`:
* **Input:** JSON com métricas de saúde (Idade, IMC, Tempo de Sono, Estresse, etc.).
* **Processamento:** Aplica o modelo/regra criado no notebook.
* **Output:** Probabilidade ou indicação de risco de distúrbio do sono (Insônia/Apneia).





### C. Infraestrutura

1. **Dockerfile:** A imagem deve conter a aplicação e o dataset processado.
2. **Execução:** A aplicação deve ser capaz de rodar via CLI do Docker padrão (sem necessidade de orquestração externa).

---

## 3. Estrutura Sugerida

```
.
├── Sleep_health_and_lifestyle_dataset.csv            # Dataset Original
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
2. **Relatório de Data Quality:** Quais problemas foram encontrados no dataset (ex: coluna de Pressão Arterial) e como foram resolvidos.
3. **Insights de Negócio:** Explicação dos padrões encontrados e como eles foram traduzidos para o endpoint `/analytics/insights`.
4. **Decisões Técnicas:** Frameworks escolhidos, arquitetura e estratégia de deploy.

### Fluxo de Submissão

1. Faça o fork do repositório.
2. Desenvolva em uma branch com seu nome (`feature/nome-sobrenome`).
3. Abra um Pull Request para a `main` (sem realizar o merge).
4. Notifique a conclusão.
