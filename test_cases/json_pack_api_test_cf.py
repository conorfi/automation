import json
import urllib
import urllib2
import requests

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
	
	url = 'http://{0}:{1}/core/{2}'.format('172.28.150.114',
	                                       '8080', 'pack/save'
	                                      )
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
	
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	status= r.status_code
	response = json.loads(r.text)
	assert 'Saved' in response['messages'][0]['message']
	
	database = 'C:\\aam-lms\\db\\cinema_services.db'	
	db = create_engine('sqlite:///' + database)	
	connection = db.connect()
	result = connection.execute("select uuid from pack")
	row = result.fetchone()
	uuid=row['uuid']
	connection.close()
    
    #find a pack
	url = 'http://{0}:{1}/core/{2}'.format('172.28.150.114','8080', 'pack/find_pack')
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
	
	#delete a pack
	url = 'http://{0}:{1}/core/{2}'.format('172.28.150.114','8080', '/pack/delete')
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
	

	
	