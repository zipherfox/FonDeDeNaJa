# Use official Python image
FROM python:3.11-slim

# Set working directory INSIDE container
WORKDIR /app

# Copy requirements & install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code from app/
COPY . .    

# Expose Streamlit port
EXPOSE 8501

# Env vars
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

# Start Streamlit
CMD ["cd", "/app", "&&", "streamlit", "run", "main.py"]