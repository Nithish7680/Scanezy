FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3-dev \
    build-essential \
    libzbar0 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN git clone --branch master https://github.com/Nithish7680/Scanezy.git
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
RUN chmod +x /app/startup.sh
CMD ["python", "/app/app.py"]