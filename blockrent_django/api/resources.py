# api/resources.py

from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication
from tastypie import fields
from tastypie.validation import Validation
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from api.models import User
from api.models import Application
from api.models import Event
from api.models import Registration
from api.core.helpers import send_application_confirm_email, send_account_creation_email
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden
import uuid 


"""
user fields:
    user_id
    secret_key
    password
    password_reset_token
    first_name
    last_name
    contact_number
    email
    user_type
    user_status
    user_bsb
    user_account_number
    user_bank_name
    created_at
    verified_at
"""


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'users'
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        filtering = {
            'accountID': 'exact',
            'firstName': 'iexact',
            'lastName': 'iexact',
            'email': 'iexact',
            'accounType': ALL,
            'accountStatus': ALL,
        }

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/login%s$' % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name='api_login'),
            url(r'^(?P<resource_name>%s)/logout%s$' % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
        ]

    def get_api_key_for_user(self, user):
        try:
            return '%s' % (user.api_key.key)
        except:
            return 'Key not found'

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body)
        username = data['email']
        password = data['password']

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True,
                    'username': user.get_username(),
                    'api_key': self.get_api_key_for_user(user)
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                }, HttpForbidden)
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect'
            }, HttpUnauthorized)

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)


"""
Application fields:
    application_id
    internal_id
    tenant_id
    onwer_id
    application_address
    application_start_date
    application_end_date
    application_deposit_amount
    application_deposit_payment_terms
    application_status
    application_deposit_holding
    application_created_date
"""


class ApplicationResource(ModelResource):
    class Meta:
        queryset = Application.objects.all()
        resource_name = 'applications'
        authorization = Authorization()
        filtering = {
            'application_id': 'exact',
            'internal_id': 'iexact',
            'tenant_id': 'exact',
            'onwer_id': 'iexact',
            'application_status': ALL,
            'application_address': ALL,
        }


"""
Application fields:
    application_id
    internal_id
    tenant_id
    onwer_id
    application_address
    application_start_date
    application_end_date
    application_deposit_amount
    application_deposit_payment_terms
    application_status
    application_deposit_holding
    application_created_date
"""

class ApplicationConfirmResource(ModelResource):
    class Meta:
        queryset = Application.objects.all()
        resource_name = 'confirmApplication'
        authorization = Authorization()
        
    def obj_create(self, bundle, request=None, **kwargs):
        
        """
        Updates the status of the Application
        """
        
        applicationID = bundle.data['applicationID']
        userID = bundle.data['userID']
        
        try:
             application_to_confirm = Application.objects.get(internalID=applicationID) ##get application object
             
             tenantID = application_to_confirm.tenantID
             onwerID = application_to_confirm.ownerID
             
             ## Update the Confirmation Field
             if userID == tenantID: 
                 application_to_confirm.isConfirmedByTenant = "YES"
             elif userID == onwerID:
                 application_to_confirm.isConfirmedByOwner = "YES"
                 
             ## Update status of application if both have been confirmed
             if application_to_confirm.isConfirmedByTenant == "YES" and application_to_confirm.isConfirmedByOwner == "YES":
                 application_to_confirm.status = "CONFIRMED"
                 
             application_to_confirm.save()
             
             ##Log the event
             registrationEvent = Event(
                     referenceid=applicationID,
                     what="APPLICATION CONFIRMATION",
                     who=userID,
                     #when=bundle.data['confirmedAt']
                     )
             registrationEvent.save()
             

        except Application.DoesNotExist: ##if doesn't exist create a new object
            pass        


"""
Event fields:
    event_id
    event_type
    user_id
    event_status
    event_occured_at
"""
class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'events'
        authorization = Authorization()
        filtering = {
            'event_id': 'exact',
            'event_type': 'iexact',
            'user_id': 'iexact',
            'email': 'iexact',
            'event_status': ALL,
        }

"""
Registration Handler

"""


class RegistrationResource(ModelResource):
    
    class Meta:
        queryset = Registration.objects.all()
        resource_name = 'registerApplication'
        authorization = Authorization()
        allowed_methods = ['post']
        
    def obj_create(self, bundle, request=None, **kwargs):
        registrationForm = bundle.data['registrationForm']
        tenantDetails = registrationForm['personalDetails']
        ownerDetails = registrationForm['otherParty']
        leaseApplicationDetails = registrationForm['leaseApplicationDetails']
        tenant_first_name = tenantDetails['firstName']
        tenant_last_name = tenantDetails['lastName']
        owner_first_name = ownerDetails['firstName']
        owner_last_name = ownerDetails['lastName']

        try: ##try to find if registrant user exist
             tenant = User.objects.get(email=tenantDetails['email'])
             generated_tenant_id = tenant.accountID 
        except User.DoesNotExist: ##if doesn't exist create a new object
            
            ##excuse my shit way of doing this, randomly generating user_id
            random_uid = str(uuid.uuid4())
            generated_tenant_id = str(tenant_first_name)[0] + str(tenant_last_name)[0] + random_uid[0] + random_uid[1] + random_uid[2] + random_uid[3]
            generated_tenant_password = random_uid[4] + random_uid[5] + random_uid[6] + random_uid[7] + str(tenant_first_name)[0] + str(tenant_last_name)[0]
            print('tenant password: ' + generated_tenant_password)
            
            tenant = User(
                     accountID=generated_tenant_id,
                     accountType="TENANT",
                     firstName=tenant_first_name,
                     lastName=tenant_last_name,
                     contactNumber=tenantDetails['phoneNumber'],
                     email=tenantDetails['email'])
            tenant.set_password(generated_tenant_password)
            tenant.save()

            send_account_creation_email(tenant, generated_tenant_password)
            
            ##Log the event
            registrationEvent = Event(
                     referenceid=generated_tenant_id,
                     what="TENANT REGISTRATION",
                     who=generated_tenant_id,
                     #when=bundle.data['createdAt']
                     )
            registrationEvent.save()

        try: ##try to find if owner user exist
             owner = User.objects.get(email=ownerDetails['email'])
             
             generated_owner_id = owner.accountID 
        except User.DoesNotExist: ##if doesn't exist create a new object
            
            random_uid = str(uuid.uuid4())
            generated_owner_id = str(owner_first_name)[0] + str(owner_last_name)[0] + random_uid[0] + random_uid[1] + random_uid[2] + random_uid[3]
            generated_owner_password = random_uid[4] + random_uid[5] + random_uid[6] + random_uid[7] + str(owner_first_name)[0] + str(owner_last_name)[0]
            print('owner password: ' + generated_owner_password)
            
            owner = User(
                     accountID=generated_owner_id,
                     accountType="OWNER",
                     firstName=ownerDetails['firstName'],
                     lastName=ownerDetails['lastName'],
                     contactNumber=ownerDetails['phoneNumber'],
                     email=ownerDetails['email'])
            owner.set_password(generated_owner_password)
            owner.save()
            send_account_creation_email(owner, generated_owner_password)
            
            ##Log the event
            registrationEvent = Event(
                     referenceid=generated_owner_id,
                     what="OWNER REGISTRATION",
                     who=generated_owner_id,
                     #when=bundle.data['createdAt']
                     )
            registrationEvent.save()
            
        try: ##try to find if application allready exist
             owner = Application.objects.get(ejariNo=leaseApplicationDetails['contractNo'])
        except Application.DoesNotExist: ##if doesn't exist create a new object
            random_uid = str(uuid.uuid4())
            generated_application_id = str(owner_first_name)[0] + str(tenant_first_name)[0] + \
                                       random_uid[0] + random_uid[1] + random_uid[2] + random_uid[3]
            print(generated_application_id)
            new_application = Application(
                     ejariNo=leaseApplicationDetails['contractNo'],
                     premisNo=leaseApplicationDetails['premiseNo'],
                     internalID=generated_application_id,
                     tenantID=generated_tenant_id,
                     ownerID=generated_owner_id,
                     depositAmount=leaseApplicationDetails['securityDepositAmount'],
                     address=leaseApplicationDetails['address'],
                     statDate=leaseApplicationDetails['contractStartDate'],
                     endDate=leaseApplicationDetails['contractEndDate']
                     )
            new_application.save()

            ##Log the event
            registrationEvent = Event(
                     referenceid=generated_application_id,
                     what="APPLICATION REGISTRATION",
                     who=generated_tenant_id,
                     #when=bundle.data['createdAt']
                     )
            registrationEvent.save()
            send_application_confirm_email(tenant, owner, new_application)
