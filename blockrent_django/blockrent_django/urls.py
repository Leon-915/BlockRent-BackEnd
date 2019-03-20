"""blockrent_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin
#from django.urls import path

#urlpatterns = [
#    path('admin/', admin.site.urls),
#]

from django.conf.urls import url, include
from django.contrib import admin
from tastypie.api import Api
from api.resources import UserResource, ApplicationResource, EventResource, RegistrationResource, \
    ApplicationConfirmResource, FilterResource, ApplicationDetailResource
from api.views import activate

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(ApplicationResource())
v1_api.register(ApplicationDetailResource())
v1_api.register(EventResource())
v1_api.register(RegistrationResource())
v1_api.register(ApplicationConfirmResource())
v1_api.register(FilterResource())

user_resource = UserResource()
application_resource = ApplicationResource()
event_resource = EventResource()


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(v1_api.urls)),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate')
]



