## Desafio Assobio

1. **Guia de execução**:
Abrir o Docker Desktop e em seguida executar os comandos:


    docker build -t health-api .


    docker run -p 8080:8080 health-api

2. **Relatório de Data Quality**:


- A coluna *Sleep Disorder* tinha muitos valores ausentes, porém isso significava apenas que aquela pessoa não possuia distúrbios do sono. A solução foi preencher todos esses valores com a string "No".
- Na coluna *BMI* havia uma falta de padronização, onde "Normal" e "Normal Weight" têm o mesmo significado. Além disso, havia uma falta de representação na categoria "Obese", então as categorias "Obese" e "Overweight" foram unidas, tendo agora apenas duas categorias, "Normal" e "Above Normal".
- A coluna "Occupation" tinha algumas profissões que não eram muito bem representadas, então as profissões foram agrupadas em 3 grandes grupos, "STEM_Education", "Healthcare" e "Corporate_Sales".
- A coluna "Blood Pressure" tinha o formato em string "120/80", dificultando cálculos posteriores. Então essa coluna foi dividida em duas outras, "Systolic_BP" e "Diastolic_BP".
- O dataset possui muitas linhas repetidas, gerando problemas na análise dos dados e no modelo preditivo, como erros estatísticos e um score muito alto do modelo(que engana), porque o modelo estaria apenas revendo dados que ele apenas decorou. Todos os dados repetidos foram removidos.


3. **Insights de Negócio**:


    Insights:
    1. A correlação entre a pressão sistólica e a pressão diastólica é muito próxima de 1, então eles carregam a mesma informação.
    2. A pressão alta está ligada a um alto nível de estresse.
    3. Em geral, as mulheres tem uma qualidade do sono maior que os homens.
    4. Existe uma tendência da qualidade do sono melhorar com a idade.
    5. Pessoas com pressão alta tem grandes chances de ter algum distúrbio do sono.
    6. Problemas no sono tendem a aparecer nos mais velhos.
    7. Pessoas com Apneia tem, em média, um maior nível de atividade física, enquanto pessoas com insônia tem a menor média.


    Eles foram extraídos a partir de observações na matriz de correlação e em gráficos gerados no arquivo "data_engineering.ipynb".


    Para demonstrar cada insight, é retornado as seguintes informações:
    1. Essa informação é melhor vista na matriz de correlação, então não foi representada aqui.
    2. A média de pressão sistólica por nível de estresse, e é possível notar médias mais altas em níveis mais altos de estresse, sendo a maior média do maior nível registrado.
    3. A média da qualidade do sono por gênero, evidenciando uma média superior entre as mulheres.
    4. A média da qualidade do sono por idade, mostrando a tendência de melhora em idades mais avançadas.
    5. Aqui mostramos a média de pressão sistólica agrupada pelo tipo de distúrbio, sendo possível notar que pessoas com distúrbios do sono possuem, em média, uma pressão mais alta.
    6. Média de idade para cada categoria de disturbio do sono, mostrando médias mais altas em distúrbios.
    7. A média do nível de atividade física por categoria de distúrbio, mostrando que pessoas com apneia tem um nível maior de atividade física, enquanto pessoas com insônia são menos ativas, e no meio termo temos as pessoas sem distúrbios.


4. **Decisões técnicas**:


    **FastAPI**: Foi escolhido pela sua alta performance, validação automática de tipos de dados(via Pydantic) e geração automática de documentação (Swagger UI).


    **Scikit-learn e joblib**: O Scikit-learn foi usado para treinar o RandomForestClassifier devido à sua robustez para dados tabulares. Como o dataset é simples, a floresta foi configurada para ter árvores pequenas, onde cada uma vai olhar apenas para pequenos padrões, evitando overfitting. O joblib foi a escolha para serialização (salvar/carregar) do modelo.


    **Pandas**: Utilizado tanto na engenharia de dados (notebook) para limpeza quanto na API (main.py) para realizar agregações analíticas em tempo real (ex: df.groupby).


    **SQLite**: Base de dados relacional leve e sem servidor (serverless). Ideal para armazenar dados da aplicação sem a complexidade de gerir um servidor PostgreSQL ou MySQL separado neste estágio.

    **Pipeline de treino (offline)**: Executado no Jupyter Notebook (data_engineering.ipynb). Gera dois arquivos importantes: o modelo treinado (model_health.pkl) e o conjunto de dados limpo (cleaned_health_data.csv).


    **Pipeline de inferência (online)**: A API (main.py) não treina o modelo. Ela apenas carrega os artefatos gerados anteriormente. Gestão de Ciclo de Vida (Lifespan): Uma decisão arquitetural importante foi usar o @asynccontextmanager. O modelo pesado é carregado na memória RAM apenas uma vez quando a API inicia (startup), e não a cada requisição do utilizador. Isso garante respostas rápidas (baixa latência).


    **Estratégia de deploy**:


        Docker: Garante que a solução vai rodar em outros ambientes, preservando as dependências matemáticas e a estrutura de arquivos que o código Python exige.

        Gestão de caminhos: O uso da biblioteca pathlib (BASE_DIR / "data") torna o código agnóstico ao sistema operativo. A API consegue localizar os ficheiros .pkl e .csv independentemente de estar a rodar no Windows, Linux ou dentro do Docker, desde que a estrutura de pastas seja mantida.

        Resiliência: O código implementa verificações de segurança no arranque (if not MODEL_PATH.exists()). Se os arquivos essenciais não estiverem presentes no deploy, a API recusa-se a iniciar, prevenindo erros em tempo de execução.