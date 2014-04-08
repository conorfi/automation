"""
@summary: Sample Test File
@since: Created on 8th April 2014
@author: Conor Fitzgerald
"""

import requests
from testconfig import config
from nose.plugins.attrib import attr


class TestSample:
    '''A class for API testing the OAuth web service'''

@attr(env=['test'], priority=1)
def test_get_requests():
    server = config['google-server']['host']
    #server = 'http://localhost'
    r = requests.get(server)
    text = r.text
    assert r.status_code == requests.codes.ok

    print r.text
    print r.status_code
