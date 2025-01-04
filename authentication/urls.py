from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('contact', views.contact, name='contact'),
    path('cours', views.cours, name='cours'),
    path('formation', views.formation, name='formation'),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('math', views.math, name='math'),
    path('Physique', views.Physique, name='Physique'),
    path('Chimie', views.Chimie, name='Chimie'),
    path('Si', views.Si, name='Si'),
    path('Fr', views.Fr, name='Fr'),
    path('An', views.An, name='An'),
    path('Info', views.Info,name='Info'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)