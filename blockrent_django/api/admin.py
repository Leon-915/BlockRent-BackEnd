from django.contrib import admin
from api.models import User, Application, Event, Registration, AppFilter


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'account_status', 'account_type', 'is_active')
    search_fields = ('email', 'username')
    list_filter = ('account_status', 'account_type')


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ejari_no', 'status', 'is_confirmed_by_tenant', 'is_confirmed_by_owner')
    list_filter = ('status', )


admin.site.register(User, UserAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Event)
admin.site.register(Registration)
admin.site.register(AppFilter)