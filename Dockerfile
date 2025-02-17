# 1. Choose a lightweight Python base image
FROM python:3.10-slim

# 2. Set environment variables to minimize Python memory usage & logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Create a working directory inside the container
WORKDIR /app

# 4. Copy requirements first for efficient caching
COPY requirements.txt /app/

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your source code into the container
COPY . /app/

# 7. Expose the port the FastAPI app will run on (default 80 or 8000)
EXPOSE 8000

# 8. Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 