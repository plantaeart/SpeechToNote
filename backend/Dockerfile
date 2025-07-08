FROM python:3.13.3

WORKDIR /app

# Copy requirements first for better caching
COPY text-to-note-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY . .

# Set working directory to the app
WORKDIR /app/text-to-note-backend

# Set environment variable to use dev config
ENV CONFIG_ENV=dev

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
