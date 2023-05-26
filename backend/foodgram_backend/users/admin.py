from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'email')
    exclude = ('date_joined', 'last_login')
    fieldsets = None
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
            ),
        }),
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'subscriber')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
