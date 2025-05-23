import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

# File paths (as per your instructions)
dataset_file = 'd:/Rani-Final-Project/DoctorAI/Dataset/symbipredict_2022.csv'
input_file = 'd:/Rani-Final-Project/DoctorAI/Dataset/test_file.csv'
model_dir = 'd:/Rani-Final-Project/DoctorAI/Dataset'

# Load training dataset
df = pd.read_csv(dataset_file)
print("Training data preview:\n", df.head())

# Separate features and target
X = df.drop('prognosis', axis=1)
y = df['prognosis']

# Encode target labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Split data for evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {acc * 100:.2f}%")
print("Classification Report:\n", classification_report(y_test, y_pred, target_names=le.classes_))

# Save model and label encoder
with open(os.path.join(model_dir, 'model.pkl'), 'wb') as f:
    pickle.dump(model, f)

with open(os.path.join(model_dir, 'label_encoder.pkl'), 'wb') as f:
    pickle.dump(le, f)

print("✅ Model and label encoder saved successfully.")

# ---- Prediction Function ----

def predict_disease(input_csv):
    # Load saved model and label encoder
    with open(os.path.join(model_dir, 'ls'), 'rb') as f:
        loaded_model = pickle.load(f)
    with open(os.path.join(model_dir, 'label_encoder.pkl'), 'rb') as f:
        loaded_le = pickle.load(f)

    # Load user input
    user_data = pd.read_csv(input_csv)

    # Align user input with training columns
    user_data_aligned = user_data.reindex(columns=X.columns, fill_value=0)

    # Predict disease
    predictions = loaded_model.predict(user_data_aligned)
    predicted_labels = loaded_le.inverse_transform(predictions)

    return predicted_labels

# ---- Run prediction using test_file.csv ----
if __name__ == "__main__":
    result = predict_disease(input_file)
    print("🩺 Predicted Disease(s):", result)
