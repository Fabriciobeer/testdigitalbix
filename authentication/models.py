from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
  is_manager =  models.BooleanField('manager status',default=False)
  is_executor =  models.BooleanField('executor status',default=False)
  is_RH =  models.BooleanField('RH status',default=False)
  is_financeiro =  models.BooleanField('financeiro status',default=False)
  is_active = models.BooleanField('active status',default=True)
  #https://stackoverflow.com/questions/11788821/best-way-to-delete-a-django-model-instance-after-a-certain-date