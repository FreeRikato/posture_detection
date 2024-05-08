from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import base64
import cv2
import numpy as np
import pandas as pd

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Posture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coordinates = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Posture {self.id} {self.status}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Decode the image from Base64
    data = request.get_json()
    encoded_data = data['image'].split(',')[1]
    binary_data = base64.b64decode(encoded_data)
    image = np.frombuffer(binary_data, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Process image with OpenPose
    coordinates = get_pose(image)

    # Analyze posture and determine status
    posture = analyze_posture(coordinates)

    # Log to SQLite and CSV
    log_coordinates(coordinates, posture)

    return jsonify(status="success", posture=posture)

def get_pose(image):
    # Implement your logic here to extract pose coordinates from OpenPose
    return np.random.rand(25, 2)  # Random coordinates for 25 keypoints

def analyze_posture(coordinates):
    quality = ["Good", "Slight Sluggish", "Very Sluggish", "Bad"]
    return np.random.choice(quality)

def log_coordinates(coordinates, posture):
    # Convert coordinates to a string for storage
    coordinates_str = ','.join([f'{x},{y}' for x, y in coordinates])
    new_posture = Posture(coordinates=coordinates_str, status=posture)
    db.session.add(new_posture)
    db.session.commit()

    # Log to CSV using pandas
    df = pd.DataFrame([{
        'id': new_posture.id,
        'coordinates': coordinates_str,
        'status': posture
    }])
    df.to_csv('postures.csv', mode='a', header=not os.path.exists('postures.csv'), index=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables within application context
    app.run(debug=True)
