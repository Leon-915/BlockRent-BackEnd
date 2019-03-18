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
from django.db.models import Q
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden
import uuid
from django.core.exceptions import (
    ObjectDoesNotExist, MultipleObjectsReturned, ValidationError, FieldDoesNotExist
)
from tastypie import http


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
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        filtering = {
            'account_id': 'exact',
            'first_name': 'iexact',
            'last_name': 'iexact',
            'email': 'iexact',
            'accounType': ALL,
            'account_status': ALL,
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
        if request.user and request.user.is_authenticated:
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
        authentication = ApiKeyAuthentication()
        filtering = {
            'application_id': 'exact',
            'internal_id': 'iexact',
            'tenant_id': 'exact',
            'onwer_id': 'iexact',
            'application_status': ALL,
            'application_address': ALL,
        }

    def dehydrate(self, bundle):
        tenant = User.objects.get(account_id=bundle.data['tenant_id'])
        owner = User.objects.get(account_id=bundle.data['owner_id'])
        bundle.data['tenant_name'] = tenant.username
        bundle.data['tenant_first_name'] = tenant.first_name
        bundle.data['tenant_last_name'] = tenant.last_name
        bundle.data['tenant_phone_number'] = tenant.contact_number
        bundle.data['tenant_email'] = tenant.email

        bundle.data['owner_name'] = owner.username
        bundle.data['owner_first_name'] = owner.first_name
        bundle.data['owner_last_name'] = owner.last_name
        bundle.data['owner_phone_number'] = owner.contact_number
        bundle.data['owner_email'] = owner.email
        return super(ApplicationResource, self).dehydrate(bundle)

    def get_list(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(),
                                               limit=self._meta.limit, max_limit=self._meta.max_limit,
                                               collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = [
            self.full_dehydrate(self.build_bundle(obj=obj, request=request), for_list=True)
            for obj in to_be_serialized[self._meta.collection_name]
        ]

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)

        return self.create_response(request, to_be_serialized)

    def get_detail(self, request, **kwargs):
        #applications = super(ApplicationResource, self).get_object_list(request)
        #return applications.filter(Q(tenant_id=request.user.account_id) | Q(owner_id=request.user.account_id))
        basic_bundle = self.build_bundle(request=request)

        try:
            obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)
        return self.create_response(request, bundle)


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
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        
    def obj_create(self, bundle, request=None, **kwargs):
        
        """
        Updates the status of the Application
        """
        applicationID = bundle.data['applicationID']
        userID = bundle.data['userID']
        
        try:
             application_to_confirm = Application.objects.get(internal_id=applicationID) ##get application object
             
             tenant_id = application_to_confirm.tenant_id
             owner_id = application_to_confirm.owner_id
             
             ## Update the Confirmation Field
             if userID == tenant_id:
                 application_to_confirm.is_confirmed_by_tenant = "YES"
             elif userID == owner_id:
                 application_to_confirm.is_confirmed_by_owner = "YES"
                 
             ## Update status of application if both have been confirmed
             if application_to_confirm.is_confirmed_by_tenant == "YES" and application_to_confirm.is_confirmed_by_owner == "YES":
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
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
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
        depositDetails = registrationForm['depositDetails']

        tenant_first_name = tenantDetails['firstName']
        tenant_last_name = tenantDetails['lastName']
        owner_first_name = ownerDetails['firstName']
        owner_last_name = ownerDetails['lastName']

        try: ##try to find if registrant user exist
             tenant = User.objects.get(email=tenantDetails['email'])
             generated_tenant_id = tenant.account_id
        except User.DoesNotExist: ##if doesn't exist create a new object
            
            ##excuse my shit way of doing this, randomly generating user_id
            random_uid = str(uuid.uuid4().hex)
            generated_tenant_id = random_uid
            #generated_tenant_id = str(tenant_first_name)[0] + str(tenant_last_name)[0] + random_uid[0] + random_uid[1] + random_uid[2] + random_uid[3]
            generated_tenant_password = random_uid[4] + random_uid[5] + random_uid[6] + random_uid[7] + str(tenant_first_name)[0] + str(tenant_last_name)[0]
            print('tenant password: ' + generated_tenant_password)

            tenant = User(
                     account_id=generated_tenant_id,
                     account_type="TENANT",
                     first_name=tenant_first_name,
                     last_name=tenant_last_name,
                     contact_number=tenantDetails['phoneNumber'],
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
             
             generated_owner_id = owner.account_id
        except User.DoesNotExist: ##if doesn't exist create a new object
            
            random_uid = str(uuid.uuid4().hex)
            generated_owner_id = random_uid
            #generated_owner_id = str(owner_first_name)[0] + str(owner_last_name)[0] + random_uid[0] + random_uid[1] + random_uid[2] + random_uid[3]
            generated_owner_password = random_uid[4] + random_uid[5] + random_uid[6] + random_uid[7] + str(owner_first_name)[0] + str(owner_last_name)[0]
            print('owner password: ' + generated_owner_password)
            
            owner = User(
                account_id=generated_owner_id,
                account_type="OWNER",
                first_name=ownerDetails['firstName'],
                last_name=ownerDetails['lastName'],
                contact_number=ownerDetails['phoneNumber'],
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
             owner = Application.objects.get(ejari_no=leaseApplicationDetails['contractNo'])
        except Application.DoesNotExist: ##if doesn't exist create a new object
            random_uid = str(uuid.uuid4().hex)
            #generated_application_id = str(owner_first_name)[0] + str(tenant_first_name)[0] + \
            #                           random_uid[0] + random_uid[1] + random_uid[2] + random_uid[3]
            generated_application_id = random_uid
            new_application = Application(
                ejari_no=leaseApplicationDetails['contractNo'],
                premis_no=leaseApplicationDetails['premiseNo'],
                total_contract_value=leaseApplicationDetails['securityDepositAmount'],
                address=leaseApplicationDetails['address'],
                start_date=leaseApplicationDetails['contractStartDate'],
                end_date=leaseApplicationDetails['contractEndDate'],
                annual_rent=leaseApplicationDetails['annualRent'],
                property_size=leaseApplicationDetails['propertySize'],
                property_usage=leaseApplicationDetails['propertyUsage'],
                deposit_term=depositDetails['term'],
                deposit_amount=depositDetails['amount'],
                term_percent=depositDetails['termPercent'],
                internal_id=generated_application_id,
                tenant_id=generated_tenant_id,
                owner_id=generated_owner_id
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
