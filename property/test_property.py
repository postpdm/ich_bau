from django.contrib.auth.models import AnonymousUser
from .models import *

from django.test import TestCase

from django.db import transaction

import reversion

TEST_USER_NAME_CREATOR = 'test project creator'
TEST_QUANTITY_NAME = 'Mass'

class Property_Test(TestCase):

    def test_Quantity(self):
        q = Quantity( fullname = TEST_QUANTITY_NAME )
        q.save()
        self.assertEqual( Quantity.objects.count(), 1 )
        self.assertEqual( str( q ), TEST_QUANTITY_NAME )