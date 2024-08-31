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
# processor = AutoImageProcessor.from_pretrained("D:/DJANGO/New folder (2)/New folder/sdxl-detector")

# classifier = AutoModelForImageClassification.from_pretrained("D:/DJANGO/New folder (2)/New folder/sdxl-detector")
 
classifier = pipeline("image-classification", model="Organika/sdxl-detector")   
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
            return redirect('login')

        uploaded_file = request.FILES.get('file')

        if uploaded_file:
            file_path = os.path.join('uploads', uploaded_file.name)
            file_content = ContentFile(uploaded_file.read())
            file_url = default_storage.save(file_path, file_content)

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
                with default_storage.open(file_url, 'rb') as file:
                    image = Image.open(file).convert("RGB")
                    predictions = classifier(image)
                    print(predictions)

                    predicted_class = predictions[0]['label']
                    predicted_probability = predictions[0]['score']
                    predicted_probability2 = predictions[1]['score']

                    print(f"probabillity{predicted_probability}")

                   
                    lab1=""
                    lab2=""
                    if predictions[0]['label']=='artificial':
                        lab1='Fake'
                        lab2='Real'
                    else:
                        lab1='Real'
                        lab2='Fake'
                    is_ai_generated = lab1

                    detection = Detection(
                        user=request.user,
                        file_path=file_url,
                        image_is_ai_generated=is_ai_generated,
                        video_is_ai_generated=False,
                        audio_is_ai_generated=False
                    )
                    
                    detection.save()  

                    request.session['dummy_data'] = {
                        'labels': [lab1,lab2],
                        'values': [(predicted_probability * 100),(predicted_probability2*100)]
                    }

            elif file_type == 'video':
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_file.write(default_storage.open(file_url, 'rb').read())
                temp_file.close()

                is_ai_generated = analyze_video(temp_file.name, classifier)

                if is_ai_generated is not None:
                    label0, score0, label1, score1 = is_ai_generated
                else:
                    label0, score0, label1, score1 = 'unknown', 0, 'unknown', 0

                detection = Detection(
                    user=request.user,
                    file_path=file_url,
                    image_is_ai_generated=False,
                    video_is_ai_generated=(label0),
                    audio_is_ai_generated=False
                )
                
                detection.save()
                

                request.session['dummy_data'] = {
                    'labels': [label0, label1],
                    'values': [score0 * 100, score1 * 100]
                }

            elif file_type == 'audio':
                with default_storage.open(file_url, 'rb') as file:
                    audio = file.read()

                    predictions = audio_classifier(audio)
                    predicted_class = predictions[0]['label']
                    predicted_class1 = predictions[1]['label']
                    print(predictions)

                    # is_ai_generated = (predicted_class == 'AI')
                    predicted_probability = predictions[0]['score']
                    predicted_probability2 = predictions[1]['score']

                    
                    lab1=""
                    lab2=""
                    if predictions[0]['label']=='fake':
                        lab1='Fake'
                        lab2='Real'
                    else:
                        lab1='Real'
                        lab2='Fake'
                    is_ai_generated=lab1    
                    detection = Detection(
                        user=request.user,
                        file_path=file_url,
                        image_is_ai_generated=False,
                        video_is_ai_generated=False,
                        audio_is_ai_generated=is_ai_generated
                    )
                    
                    detection.save()  
                    

                    request.session['dummy_data'] = {
                        'labels': [lab1,lab2],
                        'values': [predictions[0]['score'] * 100, predictions[1]['score'] * 100]
                    }

            else:
                detection = Detection(
                    user=request.user,
                    file_path=file_url,
                    image_is_ai_generated=False,
                    video_is_ai_generated=file_type == 'video',
                    audio_is_ai_generated=file_type == 'audio'
                )
                detection.save()

            return redirect('home')

    return redirect('home')


def home(request):
    total_fake=[]
    total_real=[]
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
    current_user = request.user

    user_detections = Detection.objects.filter(user=current_user)
    fake_counts = {
        'image': user_detections.filter(user=user, image_is_ai_generated='Fake').count(),
        'video': user_detections.filter(user=user, video_is_ai_generated='Fake').count(),
        'audio': user_detections.filter(user=user, audio_is_ai_generated='Fake').count(),
    }
    real_counts = {
        'image': user_detections.filter(user=user, image_is_ai_generated='Real').count(),
        'video': user_detections.filter(user=user, video_is_ai_generated='Real').count(),
        'audio': user_detections.filter(user=user, audio_is_ai_generated='Real').count(),
    }
    print(f"fake counts{fake_counts}")
    print(f"real counts{real_counts}")

    # Prepare context with profile picture URL and dummy data
    context = {
        'profile_picture_url': profile_picture_url,
        'dummy_data': dummy_data,
        'fake_list':fake_counts,
        'real_list':real_counts

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
    ai_count, human_count = 0, 0
    ai_score, human_score = 0, 0

    for frame in frames:
        predictions = classify_frame(frame, classifier)
        print(predictions)
        if not predictions:
            continue
        label = predictions[0]['label']
        score = predictions[0]['score']

        if label == "artificial":
            ai_count += 1
            ai_score += score
        else:
            human_count += 1
            human_score += score

    # Determine final classification
    if ai_count >= human_count:
        return ["Fake", ai_score / len(frames) * 100, "Real", human_score / len(frames) * 100]
    else:
        return [ "Real", human_score / len(frames) * 100,"Fake", ai_score / len(frames) * 100]

