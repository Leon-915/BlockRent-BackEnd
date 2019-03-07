from django.contrib import admin
from api.models import User, Application, Event, Registration


# Register your models here.
admin.site.register(User)
admin.site.register(Application)
admin.site.register(Event)
admin.site.register(Registration)