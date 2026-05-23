from django import views
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from accounts.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='home'),
    path('landing/', landing, name='landing'),
    path('login/', user_login, name='login'),
    path('signup/', signup, name='signup'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('logout/', user_logout, name='logout'),
    path('cinnamon/', cinnamon, name='cinnamon'),
    path('burnout/', burnout, name='burnout'),
    path('AI/', AI, name='AI'),
]

# Media files (VERY important)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)