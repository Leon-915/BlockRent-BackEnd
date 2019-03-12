from django.contrib import admin
from api.models import User, Application, Event, Registration


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'accountStatus', 'accountType', 'is_active')
    search_fields = ('email', 'username')
    list_filter = ('accountStatus', 'accountType')


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ejariNo', 'status', 'isConfirmedByTenant', 'isConfirmedByOwner')
    list_filter = ('status', )


admin.site.register(User, UserAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Event)
admin.site.register(Registration)