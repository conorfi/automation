"""
@summary: A class for simple and samll utility functions. Larger utility
functionality/areas should be created
as separate classes
@since: Created on December 3rd 2013
@author: Conor Fitzgerald
"""
import uuid
import random
import string


class Utility(object):

    def random_str(self, n=5):
        return "".join(random.choice(
            string.ascii_lowercase) for x in xrange(n)
        )

    def random_uuid(self):
        uuid = self.random_str(8)+'-'+ self.random_str(4)+'-'+self.random_str(4)+'-'+ self.random_str(4)+'-'+ self.random_str(12)
        return uuid

    def random_email(self, len=None):
        if(len is None):
            len = 5
        email = self.random_str(len) + '@' + self.random_str(len) + '.com'
        return email

    def random_url(self, len=5):
        url = 'http://www.' + self.random_str(len) + '.com'
        return url

    def random_int(self, lower=None, upper=None):
        if(lower is not None and upper is not None):
            rand_int = random.randint(lower, upper)
        else:
            rand_int = random.randint(10000000, 100000000)
        return rand_int

    def phone_number(self):
        phone = "+44 123 456 789123"
        return phone

    def random_screen_uuid (self):
        uuid = self.random_str(8)+'-'+ self.random_str(4)+'-'+self.random_str(4)+'-'+ self.random_str(4)+'-'+ self.random_str(12)
        return uuid
