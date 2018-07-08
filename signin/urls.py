"""signin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from signin import settings
from team_signin.views import Events
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth import views as authviews

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^events/', Events.as_view()), 
    url(r'^',include(('register.urls','register'),namespace="register")),
    url(r'^slack/', include('django_slack_oauth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)