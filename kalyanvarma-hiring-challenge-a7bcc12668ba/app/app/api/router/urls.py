from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

# Import all router urlpatterns
from app.api.router import user, scam, search, contact
from app.api.router.user import urlpatterns as userAPI
from app.api.router.scam import urlpatterns as scamAPI
from app.api.router.search import urlpatterns as searchAPI
from app.api.router.contact import urlpatterns as contactAPI

# Combine all API URLs
api_urls = [
    *userAPI,
    *scamAPI,
    *searchAPI,
    *contactAPI,
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include((user.urlpatterns, 'user'))), 
    path('api/scam/', include((scam.urlpatterns, 'scam'))),
    path('api/search/', include((search.urlpatterns, 'search'))),
    # path('api/contact/', include((contact.urlpatterns, 'contact'))),
    path('api/contact/', include('app.api.router.contact')),
    path('', RedirectView.as_view(url='/api/user/login/', permanent=False)),
]