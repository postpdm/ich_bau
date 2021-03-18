from django.contrib.auth.models import AnonymousUser
from .models import *

from django.test import TestCase

from django.db import transaction

import reversion

TEST_QUANTITY_MASS_NAME = 'Mass'
TEST_MEASUREMENTUNITS_NAME_GR = 'Gram'
TEST_PHYSICALPROPERTY_MASS_NETTO_NAME = 'Mass netto'

TEST_QUANTITY_LENGHT_NAME = 'Lenght'
TEST_MEASUREMENTUNITS_NAME_M = 'Metr'
TEST_PHYSICALPROPERTY_LENGHT_NAME = 'Lenght'

TEST_ENUMERABLEPROPERTY_NAME = 'Type'
TEST_ENUMERABLEVARIANTS_NAME = 'Aero'

class Property_Test(TestCase):

    def test_EnumerableProperty(self):
        ep = EnumerableProperty( fullname = TEST_ENUMERABLEPROPERTY_NAME )
        ep.save()
        self.assertEqual( EnumerableProperty.objects.count(), 1 )
        self.assertEqual( str( ep ), TEST_ENUMERABLEPROPERTY_NAME )

    def test_EnumerableVariants(self):
        ep = EnumerableProperty( fullname = TEST_ENUMERABLEPROPERTY_NAME )
        ep.save()

        ev = EnumerableVariants( fullname = TEST_ENUMERABLEVARIANTS_NAME, enumerable_property = ep )
        ev.save()
        self.assertEqual( EnumerableVariants.objects.count(), 1 )
        self.assertEqual( str( ev ), TEST_ENUMERABLEVARIANTS_NAME )
        self.assertEqual( str( ev.enumerable_property ), TEST_ENUMERABLEPROPERTY_NAME )

    def test_Quantity(self):
        q = Quantity( fullname = TEST_QUANTITY_MASS_NAME )
        q.save()
        self.assertEqual( Quantity.objects.count(), 1 )
        self.assertEqual( str( q ), TEST_QUANTITY_MASS_NAME )

    def test_MeasurementUnits(self):
        q = Quantity( fullname = TEST_QUANTITY_MASS_NAME )
        q.save()

        mu = MeasurementUnits( fullname = TEST_MEASUREMENTUNITS_NAME_GR, quantity = q, factor = 1 )
        mu.save()

        self.assertEqual( MeasurementUnits.objects.count(), 1 )
        self.assertEqual( str( mu ), TEST_MEASUREMENTUNITS_NAME_GR )

        self.assertIsNone( mu.calc_factored(None) )
        self.assertEqual( mu.calc_factored( 15 ), 15 )

    def test_PhysicalProperty(self):
        q = Quantity( fullname = TEST_QUANTITY_MASS_NAME )
        q.save()

        mu = MeasurementUnits( fullname = TEST_MEASUREMENTUNITS_NAME_GR, quantity = q, factor = 1 )
        mu.save()

        pp = PhysicalProperty( fullname = TEST_PHYSICALPROPERTY_MASS_NETTO_NAME, quantity = q, default_unit = mu )
        pp.save()

        self.assertEqual( PhysicalProperty.objects.count(), 1 )
        self.assertEqual( str( pp ), TEST_PHYSICALPROPERTY_MASS_NETTO_NAME )

        self.assertEqual( pp.linked_mu().count(), 1 )

        self.assertEqual( pp.linked_mu()[0], mu )

    def test_wrong_mu(self):
        q_mass = Quantity( fullname = TEST_QUANTITY_MASS_NAME )
        q_mass.save()

        mu_gr = MeasurementUnits( fullname = TEST_MEASUREMENTUNITS_NAME_GR, quantity = q_mass, factor = 1 )
        mu_gr.save()

        pp_mn = PhysicalProperty( fullname = TEST_PHYSICALPROPERTY_MASS_NETTO_NAME, quantity = q_mass, default_unit = mu_gr )
        pp_mn.save()

        q_lenght = Quantity( fullname = TEST_QUANTITY_LENGHT_NAME )
        q_lenght.save()

        mu_m = MeasurementUnits( fullname = TEST_MEASUREMENTUNITS_NAME_M, quantity = q_lenght, factor = 1 )
        mu_m.save()

        #raise
        with self.assertRaises(Exception) as cm:
            pp_l = PhysicalProperty( fullname = TEST_PHYSICALPROPERTY_LENGHT_NAME, quantity = q_lenght, default_unit = mu_gr )
            pp_l.save()

        the_exception = cm.exception
        self.assertEqual( str( the_exception ), 'Wrong measure unit!' )

        pp_l = PhysicalProperty( fullname = TEST_PHYSICALPROPERTY_LENGHT_NAME, quantity = q_lenght, default_unit = mu_m )
        pp_l.save()
        self.assertEqual( pp_l.fullname, TEST_PHYSICALPROPERTY_LENGHT_NAME )
        self.assertEqual( pp_l.quantity, pp_l.default_unit.quantity )
