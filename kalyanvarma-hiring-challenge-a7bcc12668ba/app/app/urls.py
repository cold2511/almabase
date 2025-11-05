"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from app.api.router.urls import api_urls

api_urls = [
    path('api/' + url.pattern._route, url.callback)
    for url in api_urls
]

urlpatterns = [
    path('admin/', admin.site.urls),
    *api_urls
]
# # from django.contrib import admin
# # from django.urls import path, include
# # from django.views.generic import RedirectView

# # urlpatterns = [
# #     path('admin/', admin.site.urls),

# #     # Include each router directly — no flattening
# #     path('api/user/', include('app.api.router.user')),
# #     path('api/scam/', include('app.api.router.scam')),
# #     path('api/search/', include('app.api.router.search')),
# #     path('api/contact/', include('app.api.router.contact')),

# #     # Default redirect (optional)
# #     path('', RedirectView.as_view(url='/api/user/login/', permanent=False)),
# # ]
# from django.contrib import admin
# from django.urls import path, include
# from django.views.generic import RedirectView

# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # Include each router
#     path('api/user/', include('app.api.router.user')),      # signup/login
#     path('api/scam/', include('app.api.router.scam')),      # scam reporting
#     path('api/search/', include('app.api.router.search')),  # search
#     path('api/contact/', include('app.api.router.contact')),# contacts

#     # Default redirect (optional)
#     path('', RedirectView.as_view(url='/api/user/login/', permanent=False)),
# ]