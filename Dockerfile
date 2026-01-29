FROM python:3.9-slim

# Cài đặt Stockfish và các thư viện cần thiết cho OpenCV xử lý ảnh
RUN apt-get update && apt-get install -y \
    stockfish \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy toàn bộ code vào container
COPY . .

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Railway sẽ gán cổng qua biến $PORT
CMD gunicorn --bind 0.0.0.0:$PORT server:app
