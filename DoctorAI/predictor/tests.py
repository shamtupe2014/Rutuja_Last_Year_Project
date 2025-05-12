from django.test import TestCase
import pickle
import os

class ModelPredictionTest(TestCase):
    def test_model_prediction(self):
        model_path = r'D:\my-model\model.pkl'
        self.assertTrue(os.path.exists(model_path), "Model file not found.")

        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        sample_input = [0, 1, 0, 1, 0, 1, 0, 0]
        result = model.predict([sample_input])[0]
        self.assertIn(result, ['Healthy', 'Infected', 'Risky'])  # Modify labels accordingly
