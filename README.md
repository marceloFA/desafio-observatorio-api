# desafio-observatorio-api
API em FastAPI que serve dados do dashboard para o desafio técnico do Observatório da Indústria.
O dataset é carregado unicamente ao início do servidor uvicorn e consutlado por demanda quando os endpoints recebem requisições.
Idealmente, deveríamos salvas os dados em um banco postgresql e não em memória, mas não tive tempo de implementar isso ;)

### Como executar localmente
- 1. Instalar os pacotes requeridos com `pip3 install -r requirements.txt`
- 2. Executar o servidor com `uvicorn app:app`
- 3. Consultar a documentação dos endpoints e fazer consutlas teste é possível em `http://localhost:8000/`

