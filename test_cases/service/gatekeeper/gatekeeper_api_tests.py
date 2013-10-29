import json
import requests
from testconfig import config
from nose.plugins.attrib import attr
from sqlalchemy import create_engine

@attr(env=['test'],priority =1)
def test_can_create_session_body_json():
    url = 'http://{0}:{1}/{2}'.format(config['gatekeeper']['ip'],config['gatekeeper']['port']
                                           ,config['api']['user']['session']['create_v1'])
    #requests is url-encoded by default
    payload = {
        'username': 'admin',
        'password': 'admin',        
    }    
    r = requests.post(url, data=json.dumps(payload))
    assert r.status_code == requests.codes.ok
    
@attr(env=['test'],priority =2)
def test_can_create_session_body_url_encoded():
    url = 'http://{0}:{1}/{2}'.format(config['gatekeeper']['ip'],config['gatekeeper']['port']
                                           ,config['api']['user']['session']['create_v1'])
    #requests is url-encoded by default
    payload = {
        'username': 'admin',
        'password': 'admin',        
    }
       
    r = requests.post(url, data=payload)
    assert r.status_code == requests.codes.ok
   

@attr(env=['test'],priority =2)    
def test_can_validate_session():
    
    # create sesssion
    url = 'http://{0}:{1}/{2}'.format(config['gatekeeper']['ip'],config['gatekeeper']['port']
                                           ,config['api']['user']['session']['create_v1'])
    #requests is url-encoded by default
    payload = {
        'username': 'admin',
        'password': 'admin',        
    }
       
    r = requests.post(url, data=payload)
    assert r.status_code == requests.codes.ok 
    response = json.loads(r.text)
   
    # validate session    
    url = 'http://{0}:{1}/{2}/{3}'.format(config['gatekeeper']['ip'],config['gatekeeper']['port']
                                           ,config['api']['user']['session']['validate_v1'],response['session_id'])
    r = requests.get(url)
    val_response = json.loads(r.text)
    assert val_response['user_id'] == response['user_id']
    assert val_response['session_id'] == response['session_id']
    