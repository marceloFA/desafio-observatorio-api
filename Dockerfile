FROM python:3.7-slim
RUN pip install -r requirements.txt
RUN python data_extraction.py
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app:app
