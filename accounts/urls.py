from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('forgotpassword/', views.forgot_password, name="forgotpassword"),
    path('resetpassword/', views.reset_password, name="resetpassword"),
    
    path('forgotpasswordreset/<uidb64>/<token>', views.forgotpassword_validate, name="forgotpassword_validate"),
    
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
]
