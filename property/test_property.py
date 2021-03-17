from django.contrib.auth.models import AnonymousUser
from .models import *

from django.test import TestCase

from django.db import transaction

import reversion

TEST_QUANTITY_NAME = 'Mass'
TEST_MEASUREMENTUNITS_NAME_GR = 'Gram'

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
        q = Quantity( fullname = TEST_QUANTITY_NAME )
        q.save()
        self.assertEqual( Quantity.objects.count(), 1 )
        self.assertEqual( str( q ), TEST_QUANTITY_NAME )

    def test_MeasurementUnits(self):
        q = Quantity( fullname = TEST_QUANTITY_NAME )
        q.save()

        mu = MeasurementUnits( fullname = TEST_MEASUREMENTUNITS_NAME_GR, quantity = q, factor = 1 )
        mu.save()

        self.assertEqual( MeasurementUnits.objects.count(), 1 )
        self.assertEqual( str( mu ), TEST_MEASUREMENTUNITS_NAME_GR )

        self.assertIsNone( mu.calc_factored(None) )
        self.assertEqual( mu.calc_factored( 15 ), 15 )
