import os
import joblib
import tensorflow as tf
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

if __name__ == '__main__': 
    # Load the Iris dataset
    iris = datasets.load_iris()
    X, y = iris.data, iris.target

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize features
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    # Build a simple TensorFlow model
    
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(8, input_shape=(4,), activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test))

    # Output location is configurable so Docker Compose can write to a shared volume
    model_dir = os.environ.get('MODEL_DIR', '.')
    os.makedirs(model_dir, exist_ok=True)
    model.save(os.path.join(model_dir, 'my_model.keras'))
    # Save the scaler too, so the server applies the same preprocessing
    joblib.dump(sc, os.path.join(model_dir, 'scaler.pkl'))
    print(f"Model and scaler were trained and saved to {model_dir}")
