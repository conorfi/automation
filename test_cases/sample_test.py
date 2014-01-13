import requests
from testconfig import config


class SampleTest:
    '''A class for API testing the OAuth web service'''


def test_get_requests():
    server = config['google-server']['host']
    r = requests.get(server)
    text = r.text
    assert r.status_code == requests.codes.ok

    print r.text
    print r.status_code