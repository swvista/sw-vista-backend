from django.contrib import admin

from .models import Permission, Role, User

# Register your models here.


admin.site.register(User)
admin.site.register(Role)
admin.site.register(Permission)
