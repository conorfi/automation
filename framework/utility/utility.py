"""
@summary: A class for simple utility functions. Larger utility
functionality/areas should be created
as separate classes
@since: Created on December 3rd 2013
@author: Conor Fitzgerald
"""

import random
import string


class Utility(object):

    def random_str(self, n):
        return "".join(random.choice(
            string.ascii_lowercase) for x in xrange(n)
        )

    def random_email(self, len):
        email = self.random_str(len) + '@' + self.random_str(len) + '.com'
        return email
