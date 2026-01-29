import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from stockfish import Stockfish

app = Flask(__name__)
CORS(app)

# Railway sẽ cài stockfish vào đường dẫn mặc định này
try:
    stockfish = Stockfish(path="/usr/games/stockfish")
except:
    stockfish = None

@app.route('/process-board', methods=['POST'])
def process():
    if not stockfish:
        return jsonify({"error": "Engine chưa sẵn sàng"}), 500
        
    data = request.json
    # Giải mã ảnh từ Tampermonkey gửi lên
    img_b64 = data['image'].split(',')[1]
    img_data = base64.b64decode(img_b64)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Logic xử lý ảnh 8x8 theo phong cách MartinDuck
    # Tạm thời dùng FEN mặc định để đại ca test đường truyền Cloud
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" 
    
    stockfish.set_fen_position(fen)
    best_move = stockfish.get_best_move()
    
    return jsonify({
        "bestMove": best_move,
        "fen": fen,
        "status": "Railway Cloud Active"
    })

if __name__ == '__main__':
    # Railway tự cấp port qua biến môi trường PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
