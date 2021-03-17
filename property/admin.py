from django.contrib import admin

# Register your models here.

from property.models import Quantity, MeasurementUnits, PhysicalProperty, EnumerableProperty, EnumerableVariants

class MeasurementUnitsInline(admin.TabularInline):
    model = MeasurementUnits
    fieldsets = [
        (None,               {'fields': ['shortname','fullname','factor', 'shift_scale']}),
    ]
    extra = 2

class QuantityAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['fullname', 'description']}),        
    ]
    inlines = [MeasurementUnitsInline]
    search_fields = ['fullname']
	
from django import forms
    
class PhysicalPropertyInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PhysicalPropertyInlineForm, self).__init__(*args, **kwargs)
        try:
            self.fields['default_unit'].queryset = MeasurementUnits.objects.filter(quantity=self.instance.quantity)            
        except:
            self.fields['default_unit'].queryset = MeasurementUnits.objects
         
	
class PhysicalPropertyAdmin(admin.ModelAdmin):
    list_display = ['fullname','quantity','default_unit']
    form = PhysicalPropertyInlineForm	
    
admin.site.register(Quantity, QuantityAdmin)
admin.site.register(PhysicalProperty, PhysicalPropertyAdmin)

class EnumerableVariantsInline(admin.TabularInline):
    model = EnumerableVariants
    fieldsets = [
        (None,               {'fields': ['fullname']}),        
    ]
    extra = 2

class EnumerablePropertyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['fullname']}),        
    ]
    inlines = [EnumerableVariantsInline]
    search_fields = ['fullname']

admin.site.register(EnumerableProperty, EnumerablePropertyAdmin)