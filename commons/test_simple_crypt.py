from .simple_crypt import *

from unittest import TestCase

class Simple_Crypt_Test(TestCase):
    def test_Simple_Crypt(self):
        s = '12345'
        p = 'udp3-wxwex4'
        self.assertEqual( DeCrypt_Str( EnCrypt_Str( s, p ) , p ), s )