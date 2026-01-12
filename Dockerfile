# Use uma imagem leve
FROM python:3.10-slim

# Diretório de trabalho no container
WORKDIR /app

# Copiar dependências primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o resto (código, modelo, dados)
COPY . .

# Expor a porta que o Uvicorn usará
EXPOSE 8080

# Comando para rodar a aplicação
# Ajuste o caminho 'src.main:app' conforme sua estrutura
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]