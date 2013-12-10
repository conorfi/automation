import requests
from testconfig import config


class SampleTest:
    '''A class for API testing the OAuth web service'''


def test_get_requests():
    import requests
    server = config['google-server']['host']
    r = requests.get(server)
    text = r.text
    status = r.status_code
    assert status == 200
