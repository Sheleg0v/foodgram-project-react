from django.contrib import admin

from .models import User, Subscription


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'subscriber')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
