from django.contrib import admin
from team_signin.models import AllowedHostsAddress,Eventmesssage,SignInRecords,SlackProfile
# Register your models here.

class AllowedHostsAddressAdmin(admin.ModelAdmin):
    list_details=['ip_addrr']

admin.site.register(AllowedHostsAddress,AllowedHostsAddressAdmin)
