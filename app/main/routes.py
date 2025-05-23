
from flask import render_template, request, send_file, Response, redirect, url_for, jsonify
from . import main
from app.models import User
from .. import db
import os
from flask import current_app
import requests
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
from collections import Counter
from flask_wtf import FlaskForm
from wtforms import StringField ,SubmitField, PasswordField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO

import jwt
from datetime import datetime, timedelta
from functools import wraps

# === Token Helpers ===

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# === Decorator to protect endpoints ===

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated


# Create a form to login existing users
class LoginForm(FlaskForm):
    phone_no = StringField("Phone Number", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")

file_path = ""

@main.route("/", methods = ["POST", "GET"])
def home():
    global file_path
    if request.method == "POST":
        # logic to upload files.
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        print(file_path)
        file.save(file_path)

        # Convert to relative URL so frontend can load it
        uploaded_image_url = url_for('static', filename=f'uploads/{file.filename}')

        # logic to read image
        # Step 1: Load and downsample image
        img = Image.open(file_path)
        img_small = img.resize((img.width // 4, img.height // 4))  # Downsample

        # Step 2: Convert to NumPy
        pixels = np.array(img_small).reshape(-1, 3)

        # Step 3: Apply faster clustering
        k = 10
        kmeans = MiniBatchKMeans(n_clusters=k, random_state=0, batch_size=1000)
        kmeans.fit(pixels)

        # Step 4: Analyze results
        counts = Counter(kmeans.labels_)
        total_pixels = len(kmeans.labels_)
        # Print clusters sorted from most to least dominant
        color_data = []

        for cluster_idx, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            percent = (count / total_pixels) * 100
            color = kmeans.cluster_centers_[cluster_idx].astype(np.uint8)
            hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
            color_data.append({
                "hex": hex_color,
                "percent": round(percent, 2)
            })
        return render_template("index.html", color_data=color_data, uploaded_image=uploaded_image_url)

    # logic to read image
    # Step 1: Load and downsample image
    image_path = os.path.join(current_app.root_path, 'main', 'static', 'demo.jpg')
    img = Image.open(image_path)
    img_small = img.resize((img.width // 4, img.height // 4))  # Downsample

    # Step 2: Convert to NumPy
    pixels = np.array(img_small).reshape(-1, 3)

    # Step 3: Apply faster clustering
    k = 10
    kmeans = MiniBatchKMeans(n_clusters=k, random_state=0, batch_size=1000)
    kmeans.fit(pixels)

    # Step 4: Analyze results
    counts = Counter(kmeans.labels_)
    total_pixels = len(kmeans.labels_)
    # Print clusters sorted from most to least dominant
    color_data = []

    for cluster_idx, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        percent = (count / total_pixels) * 100
        color = kmeans.cluster_centers_[cluster_idx].astype(np.uint8)
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        color_data.append({
            "hex": hex_color,
            "percent": round(percent, 2)
        })
    return render_template("index.html", color_data=color_data)

@main.route("/api", methods= ["POST"])
@token_required
def api():
    # Check if file is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Open image directly from memory using BytesIO
    img = Image.open(BytesIO(file.read()))
    img_small = img.resize((img.width // 4, img.height // 4))  # Downsample
    pixels = np.array(img_small).reshape(-1, 3)

    # Step 2: Convert to NumPy
    pixels = np.array(img_small).reshape(-1, 3)

    # Step 3: Apply faster clustering
    k = 10
    kmeans = MiniBatchKMeans(n_clusters=k, random_state=0, batch_size=1000)
    kmeans.fit(pixels)

    # Step 4: Analyze results
    counts = Counter(kmeans.labels_)
    total_pixels = len(kmeans.labels_)
    # Print clusters sorted from most to least dominant
    color_data = []

    for cluster_idx, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        percent = (count / total_pixels) * 100
        color = kmeans.cluster_centers_[cluster_idx].astype(np.uint8)
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        color_data.append({
            "hex": hex_color,
            "percent": round(percent, 2)
        })
    return jsonify(color_data)


@main.route("/registration", methods= ["POST", "GET"])
def registration():
    form = LoginForm()
    if form.validate_on_submit():
        phone_no = form.phone_no.data
        password = form.password.data
        if not phone_no or not password:
            return jsonify({'error': 'Name and password required'}), 400

        existing_user = db.session.execute(db.select(User).where(User.phone_no == phone_no)).scalar()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(phone_no=phone_no,
                        password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        token = create_token(new_user.id)
        return jsonify({'message': 'User registered', 'token': token})

    return  render_template("registration.html", form= form)
