from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import io
import os
import cv2
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
# Base directory set to the folder containing this app.py file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, 'skin_model.keras')
JSON_PATH = os.path.join(BASE_DIR, 'recommendations.json')

# Email Config
SENDER_EMAIL = "glowskinapp02@gmail.com"
SENDER_PASSWORD = "qlti dyaf kyfd rbgz"

# Initialize App (No templates/uploads folder needed)
app = Flask(__name__, template_folder=BASE_DIR, static_folder=BASE_DIR, static_url_path='/assets')
app.config['SECRET_KEY'] = 'glowskin-secret-key'

CORS(app)

# --- LOAD AI RESOURCES ---
try:
    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False
    )
    print("✅ Model loaded.")

except Exception as e:
    model = None
    print("❌ Model failed to load.")
    print("ERROR DETAILS:")
    print(e)
    
# Face Detection Model
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


# Load the read-only dictionary of recommendations
try:
    with open(JSON_PATH, 'r') as f:
        recommendations_db = json.load(f)
except:
    recommendations_db = {}

class_names = ['Dry Skin', 'Oily Skin', 'Normal Skin']

# --- ROUTES ---

@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact_page():
    return render_template('contact.html')

@app.route('/skin-analysis.html')
def analysis_page():
    return render_template('skin-analysis.html')

# --- FUNCTIONALITY ROUTES ---

@app.route('/analyze', methods=['POST'])
def analyze_skin():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    file_content = file.read()

    try:
        # 1. Process Image directly in memory
        image = Image.open(io.BytesIO(file_content)).convert('RGB')
        
        # Safely handle rotation (prevents crashes on mobile selfies)
        try:
            image = ImageOps.exif_transpose(image) 
        except:
            pass 
        
        # Explicitly convert to uint8 to prevent OpenCV silent failures
        img_array = np.array(image, dtype=np.uint8) 
        
        # 2. FACE DETECTION (WARNING MODE)
        # We scan for a face, but we do not block the AI if it fails.
        try:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)) 
            
            if len(faces) == 0:
                print("⚠️ WARNING: No face detected by OpenCV, but proceeding to AI model anyway.")
            elif len(faces) > 1:
                print(f"⚠️ WARNING: {len(faces)} faces detected, but proceeding to AI model anyway.")
                
        except Exception as face_err:
            print(f"⚠️ Face detection skipped due to error: {face_err}")

        # 3. AI Prediction (Runs no matter what)
        image = image.resize((180, 180)) 
        image_array = np.expand_dims(np.array(image), axis=0)
        
        print("🧠 Running AI prediction...")
        prediction = model.predict(image_array)
        score = tf.nn.softmax(prediction[0])
        predicted_class = class_names[np.argmax(score)]
        confidence = f"{100 * np.max(score):.2f}%"
        print(f"✅ Prediction complete: {predicted_class}")

        # 4. Fetch Recommendations
        rec_data = recommendations_db.get(predicted_class, {})

        # 5. Return JSON to front-end
        return jsonify({
            'result': predicted_class,
            'confidence': confidence,
            'description': rec_data.get('description', 'No description available.'),
            'remedies': rec_data.get('remedies', []),
            'products': rec_data.get('products', [])
        })

    except Exception as e:
        # Prints exact crash reason to your terminal for easy debugging
        print("\n❌ CRITICAL ANALYSIS ERROR:", str(e), "\n")
        return jsonify({'error': f"Server Error: {str(e)}"}), 500

@app.route('/send_email', methods=['POST'])
def send_email():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    try:

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # ==========================
        # MAIL TO YOU
        # ==========================
        admin_msg = MIMEMultipart()
        admin_msg['From'] = SENDER_EMAIL
        admin_msg['To'] = "abhiranjansingh7255@gmail.com"
        admin_msg['Subject'] = f"New GlowSkin Query - {name}"

        admin_body = f"""
New Contact Form Submission

Name: {name}
Email: {email}

Message:
{message}
"""

        admin_msg.attach(MIMEText(admin_body, 'plain'))
        server.send_message(admin_msg)

        # ==========================
        # CONFIRMATION TO USER
        # ==========================
        user_msg = MIMEMultipart()
        user_msg['From'] = SENDER_EMAIL
        user_msg['To'] = email
        user_msg['Subject'] = "GlowSkin - We Received Your Message"

        user_body = f"""
Hello {name},

Thank you for contacting GlowSkin.

We have received your message:

{message}

Our team will contact you soon.

Regards,
GlowSkin Team
"""

        user_msg.attach(MIMEText(user_body, 'plain'))
        server.send_message(user_msg)

        server.quit()

        return jsonify({
            'success': 'Message sent successfully! Check your email.'
        })

    except Exception as e:
        print("Email Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Changed host to 0.0.0.0 and port to 7860 for deployment
    app.run(host='0.0.0.0', port=7860)