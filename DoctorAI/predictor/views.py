from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, GenomeForm
from .models import GenomeUpload, Profile
from .ml_model import predict_disease
from .forms import CustomUserCreationForm
from django.http import HttpResponse
from .models import PredictionResult
#---New
import os
import pandas as pd
import joblib
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage



def upload_file(request):
    return render(request, 'upload.html')

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pandas as pd
import joblib

# Load the model and label encoder once globally, outside the request handling
model = joblib.load('d:/Rani-Final-Project/DoctorAI/Dataset/model.pkl')
label_encoder = joblib.load('d:/Rani-Final-Project/DoctorAI/Dataset/label_encoder.pkl')


def predict_result(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

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

            df['Predicted Disease'] = diseases  # Append predictions to original data

            # Save merged result to a new CSV file
            result_filename = 'result_' + filename
            result_path = fs.path(result_filename)
            df.to_csv(result_path, index=False)

            # Provide predictions and download link to template
            return render(request, 'result.html', {
                'predictions': diseases.tolist(),
                'download_url': fs.url(result_filename)
            })

        except Exception as e:
            return render(request, 'upload.html', {'error': 'Prediction error: ' + str(e)})

        fs.delete(filename)

    return render(request, 'upload.html')


def download_csv(request, prediction_id):
    # Get the prediction from the database
    prediction_result = PredictionResult.objects.get(id=prediction_id)
    
    # Get the file path
    csv_file_path = prediction_result.result_file.path  # Adjust this based on your model
    print(f"CSV file path: {csv_file_path}")

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={prediction_result.result_file.name}'
            return response
    else:
        print("File does not exist!")
        return HttpResponse("File not found.", status=404)

#---New End
def homepage(request):
    return render(request, 'homepage.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user to the database
            return redirect('login')  # Redirect to login page after successful registration
        else:
            # If form is invalid, print the errors and send back the form
            print(form.errors)
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

            # Predict disease using ML model
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