"""phlcouncilwatch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from legistar.views import legislation, person, index
from django.conf.urls.static import static

urlpatterns = [
    path("ht/", include("health_check.urls")),
    path("admin/", admin.site.urls),
    path("legislation/<str:file_number>/", legislation),
    path("people/<int:id_>/", person),
    path("", index),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
