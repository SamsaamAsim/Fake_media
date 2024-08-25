import json
import subprocess
import tempfile
from django.shortcuts import render, redirect
from django.http import JsonResponse
from torchvision import transforms
import torch
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

from transformers import AutoImageProcessor, AutoModelForImageClassification

# model = TFVideoClassifier.from_pretrained("DaMsTaR/Detecto-DeepFake_Video_Detector")
processor = AutoImageProcessor.from_pretrained("D:/DJANGO/New folder (2)/New folder/sdxl-detector")

classifier = AutoModelForImageClassification.from_pretrained("D:/DJANGO/New folder (2)/New folder/sdxl-detector")
 
# classifier = pipeline("image-classification", model="Organika/sdxl-detector")   
# Replace 'path_to_saved_model' with your actual SavedModel path
# classifier = pipeline("image-classification", "umm-maybe/AI-image-detector")
audio_classifier = pipeline("audio-classification", model="motheecreator/Deepfake-audio-detection")

def get_file_type(file_path):
    # Get MIME type based on file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type
# def extract_frames_from_video(video_path, output_folder):
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
    
#     command = [
#         'ffmpeg', '-i', video_path, '-vf', 'fps=1', 
#         os.path.join(output_folder, 'frame_%04d.jpg')
#     ]
    
#     subprocess.run(command, check=True)

def upload_file(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Redirect to login page if user is not authenticated
            return redirect('login')

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
                    image = Image.open(file).convert("RGB")  # Ensure the image is in RGB format

                    # Define the image transformation pipeline (resize, normalize, etc.)
                    transform = transforms.Compose([
                        transforms.Resize((224, 224)),  # Resize the image to the expected input size
                        transforms.ToTensor(),          # Convert image to Tensor
                        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize with ImageNet mean and std
                    ])

                    # Apply transformations and add batch dimension
                    image = transform(image).unsqueeze(0)

                    # Model inference
                    with torch.no_grad():  # Disable gradient computation for faster inference
                        outputs = classifier(image)  # Get the raw model outputs

                    # Apply softmax to convert logits to probabilities
                    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

                    # Get the predicted class
                    predicted_class = torch.argmax(probabilities, dim=1).item()

                    # Get the probability of the predicted class
                    predicted_probability = probabilities[0][predicted_class].item()

                    # Determine if the image is AI-generated based on the predicted class
                    is_ai_generated = (predicted_class == 1)  # Assuming '1' corresponds to AI-generated in your labels

                    # Print the predicted class and the corresponding probability
                    print(f"Predicted class: {predicted_class}")
                    print(f"Probability: {predicted_probability:.4f}")

                    # Create and save a Detection record
                    detection = Detection(
                        user=request.user,
                        file_path=file_url,
                        image_is_ai_generated=is_ai_generated,
                        video_is_ai_generated=False,
                        audio_is_ai_generated=False
                    )
                    detection.save()

                    # Store prediction data in the session (optional)
                    request.session['dummy_data'] = {
                        'labels': [predicted_class],
                        'values': [predicted_probability * 100]
                    }
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

                    print(f"Score: {predicted_score}")
                    print(f"Class: {predicted_class}")

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
                        'values': [predictions[0]['score'] * 100, predictions[1]['score'] * 100]}
                    
            elif file_type == 'video':
                print("Video section")
                # Save the video file to a temporary location
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_file.write(default_storage.open(file_url, 'rb').read())
                temp_file.close()
                
                # Extract frames from the video
                is_ai_generated = analyze_video(temp_file.name, classifier)
                print(f"is ai generated: {is_ai_generated}")

                # Assuming is_ai_generated is a tuple: (label0, score0, label1, score1)
                if is_ai_generated is not None:
                    label0, score0, label1, score1 = is_ai_generated
                else:
                    label0, score0, label1, score1 = 'unknown', 0, 'unknown', 0
                
                # Create a Detection record
                detection = Detection(
                    user=request.user,
                    file_path=file_url,
                    image_is_ai_generated=False,  # Not applicable for videos
                    video_is_ai_generated=(label0 == 'Artificial' or label1 == 'Artificial'),
                    audio_is_ai_generated=False  # Not implemented in this example
                )
                detection.save()
                
                # Store prediction data in session
                request.session['dummy_data'] = {
                    'labels': [label0, label1],
                    'values': [score0 * 100, score1 * 100]
                }
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
            profile_picture_url = "c:/Users/samsaam/Downloads/WhatsApp Video 2024-08-21 at 00.28.52_229a2070.mp4"

    # Prepare context with profile picture URL and dummy data
    context = {
        'profile_picture_url': profile_picture_url,
        'dummy_data': dummy_data
    }

    # Clear the session data if needed
    if 'dummy_data' in request.session:
        del request.session['dummy_data']
    
    return render(request, 'index.html', context)

import cv2
import os

def extract_frames(video_path, interval=1):
    frames = []
    # Use absolute path if relative path might cause issues
    # video_path = os.path.abspath(video_path)
    
    # video_path="C:/Users/samsaam/Downloads/WhatsApp Video 2024-08-21 at 00.28.52_229a2070.mp4"
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return frames
    
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(frame_rate * interval)
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval_frames == 0:
            frames.append(frame)
        count += 1

    cap.release()
    print(f"Extracted {len(frames)} frames.")
    return frames


from PIL import Image
import io

def classify_frame(frame, classifier):
    try:
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pil_image = pil_image.resize((224, 224))
        predictions = classifier(pil_image)
        return predictions
    except Exception as e:
        print(f"Error in classify_frame: {e}")
        return []

def analyze_video(video_path, classifier):
    frames = extract_frames(video_path)
    results = []
    airesults = 0
    humresults = 0

    aiocunt=0
    humancount=0
    for frame in frames:
        predictions = classify_frame(frame, classifier)
        if not predictions:
            continue
        predicted_class = predictions[0]['label']
        # predicted_class = predictions[0]['score']
        if predictions[0]['label'] =="artificial":
            aiocunt+=1
            airesults+=predictions[0]['score']
        else:
            humancount+=1
            humresults+=predictions[0]['score']

         

        print(f"Video frame prediction: {predicted_class}")

        # is_ai_generated = (predicted_class == 'AI')  # Adjust based on actual labels
        # results.append(is_ai_generated)
    if aiocunt>=humancount:
            results.append("Artificial")
            results.append((airesults/(len(frames)*100)*100))
            results.append("Human")
            results.append((humresults/(len(frames)*100)*100))    

    else:
            results.append("Human")
            results.append((humresults/(len(frames)*100)*100))  
            results.append("Artificial")
            results.append((airesults/(len(frames)*100)*100)) 
    print(f"Results: {results}")
    # final_result = any(results)  # If any frame is classified as AI-generated, mark the video as AI-generated
    return results


