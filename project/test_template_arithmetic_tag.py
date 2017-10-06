from .templatetags.template_arithmetic_tag import *

from unittest import TestCase

class Template_Arithmetic_Tag_Test(TestCase):
    def test_Percent_Zero(self):
        self.assertEqual( percent(0, 0), 0 )

    def test_Percent_50(self):
        self.assertEqual( percent(5, 10), 50 )
        
    def test_Percent_100(self):
        self.assertEqual( percent(3, 3), 100 )
