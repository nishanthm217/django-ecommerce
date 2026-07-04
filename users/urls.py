from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/',views.register, name='register'),
    path('email-verfication/<str:uidb64>/<str:token>',views.email_verification, name='email-verification'),
    path('email-verfication-sent/',views.email_verification_sent, name='email-verification-sent'),
    path('email-verfication-success/',views.email_verification_success, name='email-verification-success'),
    path('email-verfication-failed/',views.email_verification_failed, name='email-verification-failed'),
    path('login/',views.loginPage,name='loginPage'),
    path('logout/',views.logoutPage, name="logoutPage"),
    path('profile/',views.profilePage,name="profilePage"),
    
    #password reset functionality
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password-reset.html'), name='password_reset'),
    path('password-reset-sent',auth_views.PasswordResetDoneView.as_view(template_name='users/password-reset-sent.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='users/password-reset-confirm.html'),name="password_reset_confirm"),
    path('password-reset-complete',auth_views.PasswordResetCompleteView.as_view(template_name='users/password-reset-complete.html'),name='password_reset_complete')
]