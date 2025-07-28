# Use official Python image (3.12 slim for small size)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for npx (Node.js) if needed (for MCP tools)
RUN apt-get update && apt-get install -y curl nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ./src ./src

# Expose port FastAPI will run on
EXPOSE 8000


# Entry point for FastAPI with reload (dev mode)
CMD ["python", "src.api.main:app"]
