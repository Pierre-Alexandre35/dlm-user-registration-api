docker build -t fastapi-hello:latest .

docker run --rm -p 8000:8000 fastapi-hello:latest \
 gunicorn app.main:app -k uvicorn.workers.UvicornWorker \
 --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 60

or

docker compose --profile dev up --build
