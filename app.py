import json
import re
from flask import Flask, request
from flask_cors import CORS
from keras.models import load_model
from PIL import Image, ImageDraw
import cv2
import easyocr
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

app = Flask(__name__)
CORS(app)

# Load the OCR model
reader = easyocr.Reader(['id'])

# Load the KTP detection model
ktp_model = load_model('ktp_detection_model.h5')

# ... (definisikan fungsi CariNIK, CariNama, CariTTL, dan getOCRData seperti pada kode sebelumnya)

reader = easyocr.Reader(['id'])

def CariNIK(X):
    for i in X:
        if re.match(r'\d{10,}', i):
            return i

    return ""

def CariNama(X):
    c = 0
    for i in X:
        if c == 1:
            return i
        if re.match(r'nam[a-z]', i.lower()):
            c = 1

    return ""

def CariTTL(X):
    for i in X:
        match = re.search(r'[a-zA-Z, ]+(\d{2}[- ]{1}\d{2}[- ]{1}\d{4})', i)
        if match:
            extracted_format = match.group(1)
            return extracted_format
    return ""

def getOCRData(file):
    image = Image.open(file)
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    gaussian = cv2.GaussianBlur(src=gray, ksize=(3, 3), sigmaX=0, sigmaY=0)
    clahe = cv2.createCLAHE(clipLimit=2.00, tileGridSize=(12, 12))
    image = clahe.apply(gaussian)
    _, final_image = cv2.threshold(image, thresh=165, maxval=255, type=cv2.THRESH_TRUNC + cv2.THRESH_OTSU)
    border_image = cv2.copyMakeBorder(
        src=final_image,
        top=20,
        bottom=20,
        left=20,
        right=20,
        borderType=cv2.BORDER_CONSTANT,
        value=(255, 255, 255))
    results = reader.readtext(np.array(border_image))
    List = []
    for result in results:
        List.append(result[1])
    return json.dumps({
        'error': 'false',
        'message': 'Data berhasil diterima!',
        'NIK': CariNIK(List),
        'Nama': CariNama(List),
        'Tgl Lahir': CariTTL(List),
        'Link Photo': 'uploaded_image.jpg'
    })

ktp_model = load_model('ktp_detection_model.h5')

@app.route('/masuk/image', methods=['POST'])
def upload_image():
    if 'images' not in request.files:
        return json.dumps({'error': 'true', 'message': 'No file part'})

    uploaded_file = request.files['images']
    
    if uploaded_file.filename == '':
        return json.dumps({'error': 'true', 'message': 'No selected file'})

    # Save the uploaded image to a file
    uploaded_file.save('uploaded_image.jpg')
    # Process the uploaded image
    test_result = getOCRData(uploaded_file)
    return test_result

@app.route('/masuk', methods=['POST'])
def upload_image_old():
    if 'file' not in request.files:
        return json.dumps({'error': 'true', 'message': 'No file part'})

    uploaded_file = request.files['file']
    
    if uploaded_file.filename == '':
        return json.dumps({'error': 'true', 'message': 'No selected file'})

    uploaded_file.save('uploaded_image.jpg')  # Save the uploaded image to a file
    test_result = getOCRData('uploaded_image.jpg')  # Process the uploaded image
    return test_result

@app.route('/')
def home():
    return "Welcome to the home page"

if __name__ == '__main__':
    app.run(debug=True)

