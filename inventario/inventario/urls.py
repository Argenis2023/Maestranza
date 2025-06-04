from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # <- Esta línea es fundamental para login/logout/reset
    path('', include('productos.urls')),                     # <- Tu app principal
]
