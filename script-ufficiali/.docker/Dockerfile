FROM python:3.12-slim

WORKDIR /app

COPY libraries.txt .
RUN pip install --no-cache-dir -r libraries.txt

COPY .. /app

EXPOSE 8000

RUN python model_base.py

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]