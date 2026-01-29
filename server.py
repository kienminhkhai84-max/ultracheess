import os
import cv2
import numpy as np
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from stockfish import Stockfish

app = Flask(__name__)
CORS(app)

# 1. Khởi tạo Stockfish với cấu hình tối ưu cho Cloud
try:
    # Trên Linux Railway, stockfish nằm ở đường dẫn này sau khi cài bằng apt
    stockfish = Stockfish(path="/usr/games/stockfish", parameters={"Threads": 2, "Minimum Thinking Time": 30})
except Exception as e:
    print(f"Lỗi khởi tạo Stockfish: {e}")
    stockfish = None

def get_fen_from_image(img):
    """
    Logic MartinDuck: Phân tích lưới 8x8 để tạo chuỗi FEN động
    """
    height, width = img.shape[:2]
    cell_h, cell_w = height // 8, width // 8
    
    fen_rows = []
    for y in range(8):
        row = ""
        empty_count = 0
        for x in range(8):
            # Cắt từng ô nhỏ từ bàn cờ
            cell = img[y*cell_h:(y+1)*cell_h, x*cell_w:(x+1)*cell_w]
            
            # Chuyển sang ảnh xám để tính toán mật độ chi tiết (Variance)
            gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            variance = np.var(gray_cell)
            avg_brightness = np.mean(gray_cell)

            # Nếu ô có mật độ chi tiết cao (>100), nghĩa là có quân cờ
            if variance > 100: 
                if empty_count > 0:
                    row += str(empty_count)
                    empty_count = 0
                
                # Nhận diện màu quân dựa trên độ sáng
                # Quân Trắng thường sáng hơn (P), quân Đen tối hơn (p)
                if avg_brightness > 165:
                    row += "P"  # Tạm thời coi là Pawn trắng
                else:
                    row += "p"  # Tạm thời coi là Pawn đen
            else:
                empty_count += 1
                
        if empty_count > 0:
            row += str(empty_count)
        fen_rows.append(row)
    
    # Kết hợp các hàng lại thành chuỗi FEN hoàn chỉnh
    # 'w' nghĩa là lượt đi của quân Trắng (đại ca đang cầm trắng)
    return "/".join(fen_rows) + " w - - 0 1"

@app.route('/process-board', methods=['POST'])
def process():
    if not stockfish:
        return jsonify({"error": "Engine Stockfish chưa được cài đặt đúng"}), 500
        
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({"error": "Thiếu dữ liệu hình ảnh"}), 400

        # Giải mã ảnh Base64 từ trình duyệt gửi lên
        img_b64 = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Không thể giải mã hình ảnh"}), 400

        # Trích xuất FEN thực tế từ ảnh chụp bàn cờ
        current_fen = get_fen_from_image(img)
        
        # Đưa FEN vào Stockfish để tính toán nước đi tốt nhất
        stockfish.set_fen_position(current_fen)
        best_move = stockfish.get_best_move()
        
        return jsonify({
            "bestMove": best_move,
            "fen": current_fen,
            "engine": "Stockfish 16.1"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Railway yêu cầu lắng nghe trên port được cấp phát
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
