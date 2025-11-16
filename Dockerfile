# Step 1: Use official Python 3.12 slim image
FROM python:3.12-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy only dependency files first (for caching)
COPY requirements.txt ./

# Step 4: Install system and Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy the rest of your app
COPY . .

# Step 6: Expose port
EXPOSE 8000

# Step 7: Run FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
