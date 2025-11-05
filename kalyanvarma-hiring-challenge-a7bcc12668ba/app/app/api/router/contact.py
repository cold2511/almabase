# from django.urls import path
# from app.api.viewsets.contact import CreateContact

# urlpatterns = [
#     path('contact', CreateContact.as_view(), name='contact-create'),
# ]
# app/api/router/contact.py
from django.urls import path
from app.api.viewsets.contact import CreateContact
app_name='contact'

urlpatterns = [
    path('', CreateContact.as_view(), name='contact-create'),
]