# Use official Python image
FROM python:3.11-slim

# Set working directory INSIDE container
WORKDIR /app
# Install system dependencies needed by Tesseract OCR and other utilities
RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		tesseract-ocr \
		ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirements & install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code from app/
COPY . .    

# Expose Streamlit port
EXPOSE 8501

# Env vars
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

# Start Streamlit
CMD ["streamlit", "run", "app/main.py"]