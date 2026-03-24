from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
from PIL import Image
from io import BytesIO
import math

app = Flask(__name__)
CORS(app)  # ✅ FIXED POSITION

API_KEY = "wvmj9BF2deJP95SddKbfGBKp"


@app.route('/passport', methods=['POST'])
def create_passport():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "Empty file"}), 400

        pieces = int(request.form.get("pieces", 4))

        # ===== GRID =====
        cols = math.ceil(math.sqrt(pieces))
        rows = math.ceil(pieces / cols)

        # ===== REMOVE BG =====
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': file},  # ✅ FIXED
            data={'size': 'auto'},
            headers={'X-Api-Key': API_KEY},
        )

        print("STATUS:", response.status_code)

        if response.status_code != 200:
            return jsonify({
                "error": "remove.bg failed",
                "details": response.text
            }), 500

        # ===== IMAGE LOAD =====
        img = Image.open(BytesIO(response.content)).convert("RGBA")

        # ===== WHITE BG =====
        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, (0, 0), img)
        img = white_bg

        # ===== PASSPORT SIZE =====
        passport_w, passport_h = 413, 531
        passport = img.resize((passport_w, passport_h))

        # ===== A4 =====
        a4_width, a4_height = 2480, 3508
        canvas = Image.new("RGB", (a4_width, a4_height), "white")

        x_gap, y_gap = 40, 40

        total_width = cols * passport_w + (cols - 1) * x_gap
        total_height = rows * passport_h + (rows - 1) * y_gap

        x_offset = (a4_width - total_width) // 2
        y_offset = (a4_height - total_height) // 2

        count = 0
        for row in range(rows):
            for col in range(cols):
                if count >= pieces:
                    break

                x = x_offset + col * (passport_w + x_gap)
                y = y_offset + row * (passport_h + y_gap)

                canvas.paste(passport, (x, y))
                count += 1

        # ===== RETURN =====
        img_io = BytesIO()
        canvas.save(img_io, 'JPEG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)