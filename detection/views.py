from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import requests
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from accounts.models import UserProfile

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


# views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Detection
from accounts.models import Account
import os
from django.core.files.base import ContentFile
import mimetypes


def get_file_type(file_path):
    # Get MIME type based on file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type


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

            mime_type = get_file_type(file_path)

            if mime_type:
                if mime_type.startswith('image/'):
                    file_type = 'image'
                elif mime_type.startswith('video/'):
                    file_type = 'video'
                elif mime_type.startswith('audio/'):
                    file_type = 'audio'
                else:
                    file_type = 'unknown'
            else:
                file_type = 'unknown'
            
            # Create a Detection record
            detection = Detection(
                user=request.user,
                file_path=file_url,
                image_is_ai_generated=False,  # You can set these based on your logic
                video_is_ai_generated=False,
                audio_is_ai_generated=False
            )
            detection.save()
             # Store dummy data in session
            request.session['dummy_data'] = {
                'labels': ['Ai', 'Not Ai'],
                'values': [ 20, 30]
            }
            return redirect('home')  # Redirect to a success page or any other page
            
    return redirect( 'home')  # Render the upload form template