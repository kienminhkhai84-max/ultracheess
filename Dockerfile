FROM python:3.9-slim

# Cập nhật và cài đặt Stockfish cùng các thư viện đồ họa mới nhất
RUN apt-get update && apt-get install -y \
    stockfish \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy toàn bộ code vào
COPY . .

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Chạy server
CMD gunicorn --bind 0.0.0.0:$PORT server:app
