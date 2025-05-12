import joblib
import os

def predict_disease(file_path, symptoms):
    model_path = r"D:\\my-model\\model.pkl"
    model = joblib.load(model_path)

    # Example: preprocess file and symptoms before feeding to model
    # You can replace with your actual logic
    genome_data = open(file_path).read()  # dummy read
    feature_vector = [len(genome_data)] + [len(symptoms)]
    prediction = model.predict([feature_vector])
    return prediction[0]