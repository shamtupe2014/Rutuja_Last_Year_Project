from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, GenomeForm
from .models import GenomeUpload, Profile, PredictionResult
from .ml_model import predict_disease
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import pandas as pd
import joblib
import requests

# Load model and label encoder once globally
model = joblib.load('d:/Rani-Final-Project/DoctorAI/Dataset/model.pkl')
label_encoder = joblib.load('d:/Rani-Final-Project/DoctorAI/Dataset/label_encoder.pkl')

# Disease to keyword mapping for hospital search
DISEASE_TO_KEYWORD = {
    'Acne': 'dermatologist',
    'AIDS': 'infectious disease specialist',
    'Allergy': 'allergist',
    'GERD': 'gastroenterologist',
    'Chronic Cholestasis': 'gastroenterologist',
    'Drug Reaction': 'dermatologist',
    'Peptic Ulcer Disease': 'gastroenterologist',
    'Diabetes': 'endocrinologist',
    'Gastroenteritis': 'gastroenterologist',
    'Bronchial Asthma': 'pulmonologist',
    'Hypertension': 'cardiologist',
    'Migraine': 'neurologist',
    'Cervical Spondylosis': 'orthopedic',
    'Paralysis (brain hemorrhage)': 'neurologist',
    'Jaundice': 'general physician',
    'Malaria': 'general physician',
    'Chickenpox': 'general physician',
    'Dengue': 'general physician',
    'Typhoid': 'general physician',
    'Hepatitis A': 'hepatologist',
    'Hepatitis B': 'hepatologist',
    'Hepatitis C': 'hepatologist',
    'Hepatitis D': 'hepatologist',
    'Hepatitis E': 'hepatologist',
    'Alcoholic Hepatitis': 'hepatologist',
    'Tuberculosis': 'pulmonologist',
    'Common Cold': 'general physician',
    'Pneumonia': 'pulmonologist',
    'Dimorphic Hemmorhoids (piles)': 'proctologist',
    'Heart Attack': 'cardiologist',
    'Varicose Veins': 'vascular surgeon',
    'Hypothyroidism': 'endocrinologist',
    'Hyperthyroidism': 'endocrinologist',
    'Hypoglycemia': 'endocrinologist',
    'Osteoarthritis': 'orthopedic',
    'Arthritis': 'rheumatologist',
    'Vertigo': 'neurologist',
    'Urinary Tract Infection': 'urologist',
    'Psoriasis': 'dermatologist',
    'Impetigo': 'dermatologist',
    'Fungal Infection': 'dermatologist'
}

def fetch_top_hospitals(pincode, disease):
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        return ['Google API Key not set']

    keyword = DISEASE_TO_KEYWORD.get(disease, 'hospital')
    location_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={pincode}&key={api_key}'
    loc_response = requests.get(location_url)
    loc_data = loc_response.json()

    if not loc_data.get('results'):
        return ['Invalid pincode']

    latlng = loc_data['results'][0]['geometry']['location']
    lat, lng = latlng['lat'], latlng['lng']

    places_url = (
        f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
        f'location={lat},{lng}&radius=5000&type=hospital&keyword={keyword}&key={api_key}'
    )
    places_response = requests.get(places_url)
    places_data = places_response.json()

    top_hospitals = []
    for result in places_data.get('results', [])[:5]:
        name = result.get('name')
        rating = result.get('rating', 'No rating')
        address = result.get('vicinity', '')
        top_hospitals.append(f"{name} - {rating}⭐ - {address}")

    return top_hospitals or ['No hospitals found']

def upload_file(request):
    return render(request, 'upload.html')

def predict_result(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        pincode = request.POST.get('pincode')  # Get pin code from form

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_path = fs.path(filename)

        try:
            df = pd.read_csv(uploaded_file_path)
        except Exception as e:
            return render(request, 'upload.html', {'error': 'Error reading file: ' + str(e)})

        if 'prognosis' in df.columns:
            df = df.drop('prognosis', axis=1)

        try:
            predictions = model.predict(df)
            diseases = label_encoder.inverse_transform(predictions)

            df['Predicted Disease'] = diseases
            result_filename = 'result_' + filename
            result_path = fs.path(result_filename)
            df.to_csv(result_path, index=False)

            top_hospitals = fetch_top_hospitals(pincode, diseases[0]) if pincode else []

            return render(request, 'result.html', {
                'predictions': diseases.tolist(),
                'download_url': fs.url(result_filename),
                'top_hospitals': top_hospitals
            })

        except Exception as e:
            return render(request, 'upload.html', {'error': 'Prediction error: ' + str(e)})

        finally:
            fs.delete(filename)

    return render(request, 'upload.html')

def download_csv(request, prediction_id):
    prediction_result = PredictionResult.objects.get(id=prediction_id)
    csv_file_path = prediction_result.result_file.path
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={prediction_result.result_file.name}'
            return response
    return HttpResponse("File not found.", status=404)

def homepage(request):
    return render(request, 'homepage.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'homepage.html')

@login_required
def dashboard(request):
    prediction = None
    if request.method == 'POST':
        form = GenomeForm(request.POST, request.FILES)
        symptoms = request.POST.getlist('symptoms')
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.symptoms = ','.join(symptoms)
            instance.save()
            prediction = predict_disease(instance.genome_file.path, symptoms)
            return render(request, 'result.html', {
                'prediction': prediction,
                'file': instance.genome_file.name,
                'symptoms': symptoms
            })
    else:
        form = GenomeForm()
    return render(request, 'upload.html', {'form': form, 'prediction': prediction})

@login_required
def result(request):
    return render(request, 'result.html')

def logout_view(request):
    logout(request)
    return redirect('login')
