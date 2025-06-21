# Dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y pandoc texlive texlive-latex-recommended texlive-xetex
WORKDIR /app
COPY app /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
VOLUME ["/data"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]