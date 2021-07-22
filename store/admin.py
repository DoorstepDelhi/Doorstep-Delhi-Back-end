from django.contrib import admin
import nested_admin

from .models import Store, ShippingZone, ShippingMethod, BankAccount


class StoreAdmin(nested_admin.NestedModelAdmin):
    model = Store
    # inlines = [WholesaleProductVariantInline]


class ShippingMethodInlineAdmin(nested_admin.NestedTabularInline):
    model = ShippingMethod
    extra = 0
    min_num = 1


class ShippingZoneAdmin(nested_admin.NestedModelAdmin):
    inline = [ShippingMethodInlineAdmin]


class BankAccountAdmin(admin.ModelAdmin):
    fields = ['store', 'holder_name', 'account_number', 'bank_name', 'ifsc', 'account_type']


admin.site.register(Store, StoreAdmin)
admin.site.register(ShippingZone, ShippingZoneAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
