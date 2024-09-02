from flask import Flask, request, jsonify, render_template
import requests
from io import BytesIO
from pyzbar.pyzbar import decode
from PIL import Image
import easyocr
import cv2 as cv
import urllib.request
import numpy as np

reader = easyocr.Reader(['en'])
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
        # Fetch the image from the provided URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for bad HTTP responses

        # Open the image
        img_bytes = BytesIO(response.content)
        img_pil = Image.open(img_bytes)

        # Decode the barcode or QR code
        results = decode(img_pil)

        if not results:
            return jsonify({"error": "No barcodes or QR codes found in the image"}), 200

        # Extract and return the decoded data
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


@app.route('/extract-text', methods=['POST'])
def extract_text():
    data = request.get_json()
    if 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']
    
    try:
        # Download the image
        resp = urllib.request.urlopen(url)
        image_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        im = cv.imdecode(image_array, cv.IMREAD_COLOR)
        
        if im is None:
            return jsonify({'error': 'Unable to decode image from URL'}), 400

        # Preprocess the image
        preprocessed_image = preprocess_image(im)
        
        # Perform OCR on the preprocessed image
        results = reader.readtext(preprocessed_image)
        
        # Collect detected text into a variable
        detected_text = [text for (_, text, _) in results]
        
        # Join all detected text into a single string
        detected_text_str = " ".join(detected_text)
        
        return jsonify({'text': detected_text_str})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def preprocess_image(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    resized = cv.resize(blurred, None, fx=1.0, fy=1.0, interpolation=cv.INTER_CUBIC)
    return resized

if __name__ == "__main__":
    app.run(port = 8000, host = "0.0.0.0", debug=False)


