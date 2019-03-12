from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db.models import Model
from tastypie.models import create_api_key

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


class User(AbstractBaseUser):
    
    TENANT = 'TENANT'
    OWNER = 'OWNER'
    ADMIN = 'ADMIN'
    TEST = 'TEST'
    
    USER_TYPE_CHOICES = (
        (TENANT, 'TENANT'),
        (OWNER, 'OWNER'),
        (ADMIN, 'ADMIN'),
        (TEST, 'TEST')
    )
    
    accountType = models.CharField(max_length=64, choices=USER_TYPE_CHOICES, default=TEST)
    
    USER_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('VERIFIED', 'VERIFIED'),
        ('SUSPENDED', 'SUSPENDED'),
    )
    
    accountStatus = models.CharField(max_length=64, choices=USER_STATUS_CHOICES, default='NEW')
    
    firstName = models.CharField(max_length=256, blank=True)
    lastName = models.CharField(max_length=256, blank=True)
    
    contactNumber = models.CharField(max_length=64, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=128, unique=True)
    
    accountID = models.CharField(max_length=256, default="FFFF", unique=True)
    password = models.CharField(max_length=256, default="FFFF")
    secret_key = models.CharField(max_length=64, blank=True)
    password_reset_token = models.CharField(max_length=512, blank=True)
    bankBSB = models.CharField(max_length=64, blank=True)
    bankNo = models.CharField(max_length=128, blank=True)
    bankName = models.CharField(max_length=256, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    class Meta:
        db_table = 'auth_user'
    
    def __str__(self):
        return '%s %s %s %s %s %s %s' % (self.accountID, self.accountType, self.accountStatus, self.firstName,
                                         self.lastName, self.contactNumber, self.email)

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def username(self):
        return '%s %s' % (self.firstName, self.lastName)
    
    def has_module_perms(self, app_label):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin


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


class Application(models.Model):

    APPLICATION_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('CONFIRMED', 'CONFIRMED'),
        ('ACTIVE', 'ACTIVE'),
        ('SUSPENDED', 'SUSPENDED'),
        ('DISPUTE', 'DISPUTE'),
        ('COMPLETE', 'COMPLETE'),
    )
    
    status = models.CharField(max_length=64, choices=APPLICATION_STATUS_CHOICES, default='NEW')
    isConfirmedByTenant = models.CharField(max_length=64, default="NO")
    isConfirmedByOwner = models.CharField(max_length=64, default="NO")
    
    ejariNo = models.CharField(max_length=128)
    premisNo = models.CharField(max_length=128)
    internalID = models.CharField(max_length=128)
    tenantID = models.CharField(max_length=512)
    ownerID = models.CharField(max_length=512)
    
    address = models.CharField(max_length=256)
    
    statDate = models.DateTimeField(blank=True)
    endDate = models.DateTimeField(blank=True)
    
    depositAmount = models.CharField(max_length=128,  blank=True)
    depositHolding = models.CharField(max_length=64, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    
    tenantDisputeClaim = models.CharField(max_length=2048, blank=True)
    ownerDisputeClaim = models.CharField(max_length=2048, blank=True)
    
    def __str__(self):
        return self.ejariNo
    
    
"""
Event Model, model used for recording Events
"""


class Event(models.Model):
    
    EVENT_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('HANDLED', 'HANDLED'),
        ('IGNORED', 'IGNORED'),
    )
    
    status = models.CharField(max_length=512,choices=EVENT_STATUS_CHOICES,default='NEW')
    
    referenceid = models.CharField(max_length=128, blank=True)
    what = models.CharField(max_length=64)
    who = models.CharField(max_length=512)
    when = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.referenceid


models.signals.post_save.connect(create_api_key, sender=User)