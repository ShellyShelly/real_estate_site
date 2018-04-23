from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import Account


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Номер телефону'


class UserAdmin(BaseUserAdmin):
    inlines = (AccountInline, )
    exclude = (
        'is_active',
        'is_staff',
        'is_superuser',
        'groups',
        'last_login',
        'date_joined',
    )
    fieldsets = (
        (None, {'fields': ('username', )}),
        ('Особиста інформація', {
            'fields': (
                'first_name',
                'last_name',
                'email',
            )
        }),
    )


class AccountAdmin(admin.ModelAdmin):
    readonly_fields = (
        'user',
    )
    fields = (
        'user',
        'mobile_phone_number',
        'is_online',
    )
    list_display = (
        'user',
        'mobile_phone_number',
        'is_online',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    @staticmethod
    def change_status(modeladmin, request, queryset):
        for account in queryset:
            account.is_online = not account.is_online
            account.save()

    def has_change_permission(self, request, obj=None):
        has_class_permission = super(AccountAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.user.id:
            return False
        return True


admin.site.add_action(AccountAdmin.change_status, name='Змінити статус')
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Account, AccountAdmin)


