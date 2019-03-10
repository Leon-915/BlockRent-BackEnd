from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db.models import Model


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(email=self.normalize_email(email),)

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

"""
User Model, there are three types of users:
    1. Tenant
    2. Landlord
    3. Property Agent
"""




"""
Registration Model, model used for handling registration
"""


class Registration(models.Model):
    USER_TYPE_CHOICES = (
        ('TENANT', 'TENANT'),
        ('LANDLORD', 'LANDLORD'),
        ('AGENT', 'AGENT'),
        ('ADMIN', 'ADMIN'),
        ('TEST', 'TEST')
    )

    registrant_type = models.CharField(max_length=64, choices=USER_TYPE_CHOICES, default='TEST')
    registrant_first_name = models.DateTimeField(blank=True)
    registrant_last_name = models.DateTimeField(blank=True)
    registrant_phone = models.DateTimeField(blank=True)
    registrant_email = models.DateTimeField(blank=True)


"""
Application Model, model used for security deposits 
"""


    
    
"""
Event Model, model used for recording Events
"""


class Event(models.Model):
    
    EVENT_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('HANDLED', 'HANDLED'),
        ('IGNORED', 'IGNORED'),
    )
    
    status  = models.CharField(max_length=512,choices=EVENT_STATUS_CHOICES,default='NEW')
    
    referenceid = models.CharField(max_length=128, blank=True)
    what = models.CharField(max_length=64)
    who  = models.CharField(max_length=512)
    when  = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.referenceid
