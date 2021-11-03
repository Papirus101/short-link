from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('redirect_app.api.urls')),
    path('', include('redirect_app.urls')),
]
