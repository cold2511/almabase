from django.db import models
from app.mixins import TimeStampModelMixin
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create(self, password, **extra_fields):
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save()
        return user

class User(TimeStampModelMixin, AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True,default=None)
    # last_name = models.CharField(max_length=30, blank=True,null=True,default=None)
    phone_number = models.CharField(max_length=10, unique=True, blank=True, null=True)

    USERNAME_FIELD = 'phone_number'

    objects = CustomUserManager()

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()
    
