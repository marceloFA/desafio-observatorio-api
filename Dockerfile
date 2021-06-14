# Imagem de peso leve oficial Python 3.9
FROM python:3.9-slim

# Permite logs aparecerem imediatamente durante a implantação
ENV PYTHONUNBUFFERED True

# Copia o código do projeto para o container
ENV APP_HOME app/
WORKDIR $APP_HOME
COPY . ./

# instala os pacotes requeridos
RUN pip install -r requirements.txt

# faz o scraping dos dados que são servidos na API
RUN python app/data_extraction.py

# Executa o servidor web
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app.app:main
