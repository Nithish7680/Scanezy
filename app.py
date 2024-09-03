from flask import Flask, request, jsonify, render_template
import requests
from io import BytesIO
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route('/decode-barcode', methods=['POST'])
def decode_barcode():
    """Decode barcode or QR code from an image URL."""
    data = request.get_json()

    if 'url' not in data:
        return jsonify({"error": "Missing 'url' key in JSON body"}), 400

    image_url = data['url']

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img_bytes = BytesIO(response.content)
        img_pil = Image.open(img_bytes)
        results = decode(img_pil)

        if not results:
            return jsonify({"error": "No barcodes or QR codes found in the image"}), 200

        barcode = results[0]
        decoded_data = {
            "Code": barcode.data.decode('utf-8'),
            "type": barcode.type
        }
        return jsonify(decoded_data)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port = 8000, host = "0.0.0.0", debug=True)


