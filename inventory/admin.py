"""Inventory App Admin Functionality"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from inventory.models import User, Item, Provision
from inventory.forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    """Admin Panel for custom user model"""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('other info', {'fields': ('phone', 'address',
                                   'id_number', 'is_admin', 'image')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_admin',
        'is_superuser',
        'phone',
        'address',
        'id_number'
    )

    list_filter = (
        'is_superuser',
        'is_admin'
    )

    search_fields = (
        'first_name',
        'last_name',
        'email'
    )

    ordering = (
        'email',
    )

    filter_horizontal = ()


class ItemAdmin(admin.ModelAdmin):
    """Admin Panel for Items"""
    list_display = (
        'name',
        'description',
        'returnable',
        'quantity'
    )


class ProvisionAdmin(admin.ModelAdmin):
    """Admin Panel for Provisions"""
    list_display = (
        'item',
        'user',
        'timestamp',
        'approved',
        'approved_on',
        'return_by',
        'quantity',
        'returned',
        'returned_on'
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Provision, ProvisionAdmin)

admin.site.unregister(Group)
admin.site.unregister(Site)
