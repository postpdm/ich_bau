from django.db import models

#from ybase.avatars import enumerable_variant_upload
enumerable_variant_upload = ''

# Create your models here.

# Enumerable

class EnumerableProperty(models.Model):
    fullname = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['fullname']

    def __str__(self):
        return self.fullname

    # def get_absolute_url(self):
        # return "/property/enum/%i/" % self.id

#Простой вызов `from product.models import Product` выдает ошибку, вилимо получается циклическая связь. Поэтому - трюк ForeignKey( 'product.Product' )

class EnumerableVariants(models.Model):
    enumerable_property = models.ForeignKey(EnumerableProperty, on_delete=models.PROTECT, blank=False, null=False )
    fullname = models.CharField(max_length=255)
    #clarifying_product=models.ForeignKey( 'product.Product', on_delete=models.PROTECT, blank=True, null=True )
    avatar = models.ImageField(upload_to=enumerable_variant_upload, blank=True, null=True )

    class Meta:
        ordering = ['fullname']

    def __str__(self):
        return self.fullname

    # def get_absolute_url(self):
        # return "/property/enum/var/%i/" % self.id

# Physical

class Quantity(models.Model):
    fullname = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['fullname']

    def __str__(self):
        return self.fullname
    # def get_absolute_url(self):
        # return "/property/quantity/%i/" % self.id

class MeasurementUnits(models.Model):
    quantity = models.ForeignKey(Quantity, on_delete=models.PROTECT)
    shortname = models.CharField(max_length=25)
    fullname = models.CharField(max_length=255)
    factor = models.FloatField()
    shift_scale = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.fullname

    # def get_absolute_url(self):
        # return "/property/quantity/unit/%i/" % self.id

    # пересчитывает в базовые, с учетом factor и shift_scale
    def calc_factored( self, a_amount ):
        if ( a_amount is None ):
            return None
        else:
            r = a_amount
            if not( self.shift_scale is None ):
                r = r + self.shift_scale
            if self.factor != 0:
                r = r * self.factor
            return r

class PhysicalProperty(models.Model):
    quantity = models.ForeignKey(Quantity, on_delete=models.PROTECT)
    fullname = models.CharField(max_length=255)
    default_unit = models.ForeignKey(MeasurementUnits, on_delete=models.PROTECT)

    class Meta:
        ordering = ['fullname']

    def __str__(self):
        return self.fullname

    # def get_absolute_url(self):
        # return "/property/quantity/pp/%i/" % self.id

    # получить список допустимых единиц
    def linked_mu(self):
        return MeasurementUnits.objects.filter( quantity = self.quantity )

    # проверки перед сохранением
    def save(self, *args, **kwargs):
        # проверить - есть ли данная величина у указанной единицы?
        if self.default_unit.quantity == self.quantity:
            super(PhysicalProperty, self).save(*args, **kwargs) # Call the "real" save() method.
        else:
            raise Exception("Wrong measure unit!")

# условия измерения
class PPMeasurementCondition(models.Model):
    measured_pp = models.ForeignKey(PhysicalProperty, on_delete=models.PROTECT, related_name = 'measured_pp' )
    # для измерения measured_pp нужно зафиксировать значение fixed_pp.
    fixed_pp = models.ForeignKey(PhysicalProperty, on_delete=models.PROTECT, related_name = 'fixed_pp' )
    amount=models.FloatField()
    amount_based=models.FloatField() # значение пересчитанное в базовые единицы
    amount_unit=models.ForeignKey(MeasurementUnits, on_delete=models.PROTECT)

    class Meta:
        ordering = ['measured_pp', 'amount_based']

    # def get_absolute_url(self):
        # return "/property/quantity/pp/mc/%i/" % self.id

    def __str__(self):
        return str( self.fixed_pp ) + " " + str( self.amount ) + " " + str( self.amount_unit )

    def save(self, *args, **kwargs):
        # проверки
        if self.measured_pp == self.fixed_pp:
            # нельзя связывать сам с собой
            raise Exception( "Can't set measurement condition to itself!" )
        if self.amount_unit.quantity != self.fixed_pp.quantity:
            raise Exception( "Wrong unit!" )

        self.amount_based = self.amount_unit.calc_factored( self.amount )
        super(PPMeasurementCondition, self).save(*args, **kwargs) # Call the "real" save() method.
