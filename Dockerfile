FROM python:3.11-slim

WORKDIR /app

# Зависимости устанавливаем отдельным слоем — кешируются при неизменном requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# gunicorn вместо Flask dev-сервера
CMD ["gunicorn", "main:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
