
from flask import render_template, request, send_file, Response, redirect, url_for
from . import main
import os
from flask import current_app
import requests
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
from collections import Counter

@main.route("/", methods = ["POST", "GET"])
def home():
    if request.method == "POST":
        # logic to upload files.
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
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