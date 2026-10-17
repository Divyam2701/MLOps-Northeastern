from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import os
import joblib
import numpy as np

app = Flask(__name__, static_folder='statics')

# Paths and port come from environment variables set in the Dockerfile / docker-compose.yml
MODEL_PATH = os.environ.get('MODEL_PATH', 'my_model.keras')
SCALER_PATH = os.environ.get('SCALER_PATH', 'scaler.pkl')
PORT = int(os.environ.get('PORT', 4000))

# Load the TensorFlow model and the scaler used during training
model = tf.keras.models.load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
class_labels = ['Setosa', 'Versicolor', 'Virginica']


@app.route('/')
def home():
    return "Welcome to the Iris Classifier API!"

@app.route('/health')
def health():
    # Used by the Docker HEALTHCHECK and docker-compose healthcheck
    return jsonify({"status": "ok", "model": MODEL_PATH})

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            data = request.form
            sepal_length = float(data['sepal_length'])
            sepal_width = float(data['sepal_width'])
            petal_length = float(data['petal_length'])
            petal_width = float(data['petal_width'])

            # Perform the prediction
            input_data = np.array([sepal_length, sepal_width, petal_length, petal_width])[np.newaxis, ]
            prediction = model.predict(scaler.transform(input_data), verbose=0)
            predicted_class = class_labels[np.argmax(prediction)]

            # Return the predicted class in the response
            # Use jsonify() instead of json.dumps() in Flask
            return jsonify({"predicted_class": predicted_class})
        except Exception as e:
            return jsonify({"error": str(e)})
    elif request.method == 'GET':
        return render_template('predict.html')
    else:
        return "Unsupported HTTP method"

if __name__ == "__main__":
    # Local development only; inside Docker the app is served by Gunicorn
    app.run(debug=True, host='0.0.0.0', port=PORT)
