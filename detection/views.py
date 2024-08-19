import json
import subprocess
from django.shortcuts import render, redirect
from django.http import JsonResponse
from transformers import pipeline
from .models import Detection
from accounts.models import UserProfile
import os
import numpy as np
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import mimetypes
from PIL import Image
import tensorflow as tf

# from transformers import TFVideoClassifier

# model = TFVideoClassifier.from_pretrained("DaMsTaR/Detecto-DeepFake_Video_Detector")

 
	
# Replace 'path_to_saved_model' with your actual SavedModel path
classifier = pipeline("image-classification", "umm-maybe/AI-image-detector")
audio_classifier = pipeline("audio-classification", model="motheecreator/Deepfake-audio-detection")

def get_file_type(file_path):
    # Get MIME type based on file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type
def extract_frames_from_video(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    command = [
        'ffmpeg', '-i', video_path, '-vf', 'fps=1', 
        os.path.join(output_folder, 'frame_%04d.jpg')
    ]
    
    subprocess.run(command, check=True)

def upload_file(request):
    if request.method == 'POST':
        # Get the file from the request
        uploaded_file = request.FILES.get('file')
        
        if uploaded_file:
            # Define the file path where you want to save the file
            file_path = os.path.join('uploads', uploaded_file.name)
            
            # Save the file to the default storage
            file_content = ContentFile(uploaded_file.read())
            file_url = default_storage.save(file_path, file_content)
            print(file_path)
            mime_type = get_file_type(file_path)
            file_type = 'unknown'

            if mime_type:
                if mime_type.startswith('image/'):
                    file_type = 'image'
                elif mime_type.startswith('video/'):
                    file_type = 'video'
                elif mime_type.startswith('audio/'):
                    file_type = 'audio'

            if file_type == 'image':
                # Load and preprocess the image
                with default_storage.open(file_url, 'rb') as file:
                    image = Image.open(file)
                    image = image.convert("RGB")  # Ensure the image is in RGB format
                    image = image.resize((224, 224))  # Resize if necessary

                    # Make prediction
                    predictions = classifier(image)
                    
                    # Extract the predicted class and score
                    predicted_class = predictions[0]['label']
                    predicted_score = predictions[0]['score']
                    print(f"class is{predicted_class}")
                    print(f"score is {predicted_score}")

                    # Determine if the image is AI generated based on the label
                    is_ai_generated = (predicted_class == 'AI')  # Adjust based on actual labels
                    
                    # Create a Detection record
                    detection = Detection(
                        user=request.user,
                        file_path=file_url,
                        image_is_ai_generated=is_ai_generated,
                        video_is_ai_generated=False,
                        audio_is_ai_generated=False
                    )
                    detection.save()
                    
                    # Store prediction data in session
                    request.session['dummy_data'] = {
                        'labels': [predictions[0]['label'], predictions[1]['label']],
                        'values': [predictions[0]['score'], predictions[1]['score']]}
                    
            elif file_type == 'audio':
                # Load and preprocess the audio file
                with default_storage.open(file_url, 'rb') as file:
                    audio = file.read()
                    
                    # Make prediction
                    predictions = audio_classifier(audio)
                    
                    # Extract prediction results
                    predicted_class = predictions[0]['label']
                    is_ai_generated = (predicted_class == 'AI') 
                    predicted_score = predictions[0]['score']

                     # Adjust based on actual labels
                    print(f"score is {predicted_score}")

                    print(f"class is{predicted_class}")
                    # Create a Detection record
                    detection = Detection(
                        user=request.user,
                        file_path=file_url,
                        image_is_ai_generated=False,
                        video_is_ai_generated=False,
                        audio_is_ai_generated=is_ai_generated
                    )
                    detection.save()
                    
                    # Store prediction data in session
                    request.session['dummy_data'] = {
                        'labels': [predictions[0]['label'], predictions[1]['label']],
                        'values': [predictions[0]['score'], predictions[1]['score']]}
            # elif file_type == 'video':
            #     frames_folder = 'uploads/frames'
                
            #     # Extract frames from the video
            #     extract_frames_from_video(file_url, frames_folder)
                
            #     frame_predictions = []
            #     for frame_file in os.listdir(frames_folder):
            #         frame_path = os.path.join(frames_folder, frame_file)
            #         image = Image.open(frame_path)
            #         image = image.resize((224, 224))
            #         image_array = np.array(image) / 255.0  # Normalize the image
            #         image_array = np.expand_dims(image_array, axis=0)
                    
            #         # Make prediction
            #         predictions = model.predict(image_array)
            #         frame_predictions.append(predictions)
                
            #     # Process frame predictions
            #     # Aggregate or average predictions for final video prediction
            #     is_deepfake = np.mean(frame_predictions) > 0.5  # Example threshold
            #     print(is_deepfake)
            #     # Create a Detection record
            #     detection = Detection(
            #         user=request.user,
            #         file_path=file_url,
            #         image_is_ai_generated=False,
            #         video_is_ai_generated=is_deepfake,
            #         audio_is_ai_generated=False
            #     )
            #     detection.save()
                
            #     # Store prediction data in session
            #     request.session['dummy_data'] = {
            #         'labels': ['deepfake', 'real'],
            #         'values': [np.mean(frame_predictions), 1 - np.mean(frame_predictions)]
            #     }
     
            else:
                # For non-image and non-audio files, handle accordingly
                detection = Detection(
                    user=request.user,
                    file_path=file_url,
                    image_is_ai_generated=False,
                    video_is_ai_generated=file_type == 'video',
                    audio_is_ai_generated=file_type == 'audio'
                )
                detection.save()
            return redirect('home')  # Redirect to a success page or any other page
            
    return redirect('home')
def home(request):
    # Retrieve dummy data from session
    dummy_data = request.session.get('dummy_data', {})
    user = request.user
    profile_picture_url = None

    # Check if user is authenticated and get profile picture URL
    if user.is_authenticated:
        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile and user_profile.profile_picture:
            profile_picture_url = user_profile.profile_picture.url
        else:
            profile_picture_url = "https://icon-library.com/images/avatar-icon-images/avatar-icon-images-4.jpg"

    # Prepare context with profile picture URL and dummy data
    context = {
        'profile_picture_url': profile_picture_url,
        'dummy_data': dummy_data
    }

    # Clear the session data if needed
    if 'dummy_data' in request.session:
        del request.session['dummy_data']
    
    return render(request, 'index.html', context)
