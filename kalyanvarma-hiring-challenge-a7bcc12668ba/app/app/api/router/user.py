from django.urls import path
from app.api.viewsets.user import CreateUser, LoginUser

urlpatterns = [
    path('user/signup/', CreateUser.as_view(), name='user-create'),
    path('user/login/', LoginUser.as_view(), name='user-login'),
]
