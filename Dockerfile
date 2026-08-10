# Usa uma imagem oficial leve do Python
FROM python:3.14.3

# Define o diretório de trabalho dentro do contentor
WORKDIR /app

# Instala as dependências do sistema necessárias para compilar bibliotecas se preciso
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copia o ficheiro de dependências e instala-as
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para dentro do contentor
COPY . .

# Expõe a porta padrão onde o Streamlit corre
EXPOSE 8501

# Comando para iniciar a aplicação quando o contentor arrancar
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]