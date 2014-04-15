import requests
from testconfig import config

class SampleTest2:
    server = config['google-server']['host']
    response = requests.get(url=server)
    text = response.text
    status = response.status_code
    assert status == requests.codes.ok