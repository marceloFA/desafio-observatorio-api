# usando esquema de construção da imagem em vários passos
# para garantir uma imagem final limpa e de deploy rápido
FROM python:3.9-slim as base

# Imagem de peso leve oficial Python 3.9
FROM base as builder

# Permite logs aparecerem imediatamente durante a implantação
ENV PYTHONUNBUFFERED True

COPY . ./src

# instala os pacotes requeridos
RUN pip install --user -r src/requirements.txt

# faz o scraping dos dados que são servidos na API
#RUN python app/data_extraction.py

FROM base as app
# se pip não instalar os pacotes como ==user,
# esse dir não será criado
COPY --from=builder /root/.local /root/.local
COPY --from=builder /src .

# path precisa ser especificado para 
# execução de scripts em /root/.local
ENV PATH=/root/.local:$PATH

# Entra no diretório do pacote
ENV APP_HOME app/
WORKDIR $APP_HOME

# Executa o servidor web
ENV PORT 8000
EXPOSE $PORT
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker app.app:main
