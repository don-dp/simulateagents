"""
URL configuration for simulateagents project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from base.views import handler400, handler403, handler404, handler500, CustomLoginView

admin.site.login = CustomLoginView.as_view(
    template_name='registration/login.html',
    next_page='admin:index'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('', include('main.urls')),
]

handler400 = 'base.views.handler400'
handler403 = 'base.views.handler403'
handler404 = 'base.views.handler404'
handler500 = 'base.views.handler500'
