import json
import urllib
import urllib2
import requests
from testconfig import config

from sqlalchemy import create_engine

def test_pack():
	
	#create Pack
	
	ads = {
		"clips":[
		{
		"cpl_id": "abb5f47f-014d-4a11-8d1e-a820470f01a7",
		"text": "16554TPG1799UN_ADV_F_EN-XX_AU_51_2K_20130111_DAU_OV",
		"duration_in_frames": "1080",
		"edit_rate": "24 1",
		},
		{
		"cpl_id": "60a7ded9-ee81-4c86-b18a-9fb8362ce392",
		"text": "17887TOURISM60_ADV_F_EN-XX_AU-AE_51-EN_2K_VM_20130725_EDP_OV",
		"duration_in_frames": "1080",
		"edit_rate": "24 1",
		},
		{
		"cpl_id": "ab9e2c32-8148-4d8c-9c50-9a73399194ac",
		"text": "16989HOYTSKIOSK41_ADV_F_EN_AU-AE_51_2K_20130305_AUS_OV",
		"duration_in_frames": "1080",
		"edit_rate": "24 1",
		},
		],
		"complex_name":"Hoyts Entertainment Quarter",
		"date_from":"2013-08-22",
		"date_to":"2013-08-28",
		"time_from": "00:00:01",
		"time_to": "11:59:59",
		"issuer":"Val Morgan",
		"placeholder_name":"VM 2D Ad Block 2",
		"title_name":"Monsters University",
		"name":"VM2DB2 - Monsters University",
		"print_no":""
	}
	
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['save'])
	
	payload = {
	    'username': 'admin',
	    'password': 'admin',
	    'packs':[ads]
	}
	
	#data = json.dumps(data)
	
	#request = urllib2.Request(url, data)
	#request.add_header('Cache-Control', 'no-cache')
	#request.add_header('Content-Type', 'application/json')
	#response = urllib2.urlopen(request, timeout=10)
	
	#response_body = response.read()
	#print json.loads(response_body)
	
	#save a pack
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	status= r.status_code
	response = json.loads(r.text)
	assert 'Saved' in response['messages'][0]['message']
	
	#db - find the UUID		
	db = create_engine(config['tms']['db_type'] + config['tms']['db'])	
	connection = db.connect()
	result = connection.execute("select uuid from pack")
	row = result.fetchone()
	uuid=row['uuid']
	connection.close()
    
    #find a pack	
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['find_pack'])
	
	cpls = 'abb5f47f-014d-4a11-8d1e-a820470f01a7'
		
	payload = {
	    'username': 'admin',
	    'password': 'admin',
	    'cpl_uuid':cpls
	}
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r_find = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_find.status_code
	response = json.loads(r_find.text)
	assert 'abb5f47f-014d-4a11-8d1e-a820470f01a7' in  response['data']
	
	#packs
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['packs'])
	
	payload = {
	    'username': 'admin',
	    'password': 'admin'
	}	
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r_packs = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_packs.status_code
	r_packs = json.loads(r_packs.text)
	r_packs_length  =  r_packs['data'].__len__()
	
	#db - find the number of packs that exist and assert	
	db = create_engine(config['tms']['db_type'] + config['tms']['db'])	
	connection = db.connect()
	result = connection.execute("select count(uuid) from pack")
	row = result.fetchone()
	number_of_packs=row._row[0]
	connection.close()
	
	assert number_of_packs == r_packs_length
	
	#delete a pack	
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port'],
									config['api']['core']['pack']['delete'])
	pack_uuids = [uuid]
		
	payload = {
	    'username': 'admin',
	    'password': 'admin',
	    'pack_uuids':pack_uuids
	}	
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r_delete = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_delete.status_code
	response_delete = json.loads(r_delete.text)
	assert 'Deleted' in response_delete['messages'][0]['message']
	

## extra code
'''
	params = {
	    'username': '"admin"',
	    'password': '"admin"',
	    'cpl_uuid':cpls
	}
	
	string_params = str(params)
	special_url='http://{0}:{1}/{2}{3}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['find_pack'],string_params)
	# Send HTTP POST request
	response = urllib2.urlopen(special_url) 
	response = response.read()
	response = json.loads(response)
    
	r_find = requests.get(url,params=params)
	url_request= r_find.url
	status = r_find.status_code
	r_find_text = r_find.text
	response = json.loads(r_find.text)
	assert 'abb5f47f-014d-4a11-8d1e-a820470f01a7' in  response['data']
'''	
	