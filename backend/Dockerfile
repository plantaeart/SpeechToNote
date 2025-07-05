FROM python:3.13.3
WORKDIR /app
COPY text-to-note-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/text-to-note-backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
