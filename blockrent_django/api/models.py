from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db.models import Model
from tastypie.models import create_api_key

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, username=None, password=None):
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        """

        user = self.model(username=username,)

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password)
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
    
    account_type = models.CharField(max_length=64, choices=USER_TYPE_CHOICES, default=TEST)
    
    USER_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('VERIFIED', 'VERIFIED'),
        ('SUSPENDED', 'SUSPENDED'),
    )
    
    account_status = models.CharField(max_length=64, choices=USER_STATUS_CHOICES, default='NEW')
    
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    
    contact_number = models.CharField(max_length=64, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=128, unique=True)
    username = models.CharField(max_length=255, unique=True)
    
    account_id = models.CharField(max_length=256, default="FFFF", unique=True)
    password = models.CharField(max_length=256, default="FFFF")
    secret_key = models.CharField(max_length=64, blank=True)
    password_reset_token = models.CharField(max_length=512, blank=True)
    bank_bsb = models.CharField(max_length=64, blank=True)
    bank_no = models.CharField(max_length=128, blank=True)
    bank_name = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'auth_user'
    
    def __str__(self):
        return '%s %s %s %s %s %s %s' % (self.account_id, self.account_type, self.account_status, self.first_name,
                                         self.last_name, self.contact_number, self.email)

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    
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

    APPLICATION_PROPERTY_USAGE = (
        ('Residential', 'Residential'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial')
    )

    APPLICATION_DEPOSIT_TERMS = (
        ('Fixed Amount', 'Fixed Amount'),
        ('% of Contract Value', '% of Contract Value')
    )

    CURRENCY_TYPE = (
        ('AED', 'AED'),
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('AUD', 'AUD')
    )
    
    status = models.CharField(max_length=64, choices=APPLICATION_STATUS_CHOICES, default='NEW')
    is_confirmed_by_tenant = models.CharField(max_length=64, default="NO")
    is_confirmed_by_owner = models.CharField(max_length=64, default="NO")
    
    ejari_no = models.CharField(max_length=128)  #contractNo
    premis_no = models.CharField(max_length=128)  #premiseNo
    internal_id = models.CharField(max_length=128)
    tenant_id = models.CharField(max_length=512)
    owner_id = models.CharField(max_length=512)
    
    address = models.CharField(max_length=256)  #address
    total_contract_value = models.CharField(max_length=128,  blank=True)
    property_usage = models.CharField(max_length=64, choices=APPLICATION_PROPERTY_USAGE, default='RESIDENTIAL')
    annual_rent = models.CharField(max_length=64, blank=True)
    property_size = models.CharField(max_length=64, blank=True)
    currency_type = models.CharField(max_length=32, choices=CURRENCY_TYPE, blank=True)
    
    start_date = models.DateField(blank=True)  #contractStartDate
    end_date = models.DateField(blank=True)  #contractEndDate
    
    deposit_holding = models.CharField(max_length=64, blank=True)

    #deposit Details
    deposit_term = models.CharField(max_length=64, choices=APPLICATION_DEPOSIT_TERMS, default='Fixed Amount')
    deposit_amount = models.CharField(max_length=128, blank=True)
    term_percent = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    tenant_dispute_claim = models.CharField(max_length=2048, blank=True)
    owner_dispute_claim = models.CharField(max_length=2048, blank=True)
    
    def __str__(self):
        return self.ejari_no
    
    
"""
Event Model, model used for recording Events
"""


class Event(models.Model):
    
    EVENT_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('HANDLED', 'HANDLED'),
        ('IGNORED', 'IGNORED'),
    )
    
    status = models.CharField(max_length=512, choices=EVENT_STATUS_CHOICES, default='NEW')
    
    referenceid = models.CharField(max_length=128, blank=True)
    what = models.CharField(max_length=64)
    who = models.CharField(max_length=512)
    when = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id', )
    
    def __str__(self):
        return self.referenceid


class AppFilter(models.Model):
    APPLICATION_PROPERTY_USAGE = (
        ('', ''),
        ('Residential', 'Residential'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial')
    )

    filter_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    filter_name = models.CharField(max_length=64, blank=True)
    property_type = models.CharField(max_length=64, choices=APPLICATION_PROPERTY_USAGE, blank=True)
    property_size_name = models.CharField(max_length=64, blank=True)
    property_size_level = models.IntegerField(default=0)
    property_size_from = models.IntegerField(default=0)
    property_size_to = models.IntegerField(default=0)
    tenant_name = models.CharField(max_length=64, blank=True)
    owner_name = models.CharField(max_length=64, blank=True)
    start_date = models.CharField(max_length=64, blank=True)
    end_date = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return self.filter_name


models.signals.post_save.connect(create_api_key, sender=User)