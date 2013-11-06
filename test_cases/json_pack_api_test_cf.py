import json
import urllib
import urllib2
import requests
from testconfig import config
from nose.plugins.attrib import attr

from sqlalchemy import create_engine


@attr(env=['test'],priority =1)
def test_pack_test_tms():
	url = 'http://{0}:{1}/{2}'.format('172.28.150.133','8080','core/pack/last_modified')
	
	payload = {
	    'username': 'admin',
	    'password': 'admin'
	}	
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r_last = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_last.status_code
	r_last = json.loads(r_last.text)
	#assert uuid in r_last['data']	

@attr(env=['test'],priority =1)
def test_pack_test_tms_5():
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
		
		
@attr(env=['test'],priority =2)
def test_pack():
		
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
	
	
	#data = json.dumps(data)
	
	#request = urllib2.Request(url, data)
	#request.add_header('Cache-Control', 'no-cache')
	#request.add_header('Content-Type', 'application/json')
	#response = urllib2.urlopen(request, timeout=10)
	
	#response_body = response.read()
	#print json.loads(response_body)
	
	#save a pack
	
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['save'])
	
	payload = {
	    'username': 'admin',
	    'password': 'admin',
	    'packs':[ads]
	}
	
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
    
	
    #last modified (401?)
	
	'''url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['last_modified'])
	
	payload = {
	    'username': 'admin',
	    'password': 'admin'
	}	
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r_last = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_last.status_code
	r_last = json.loads(r_last.text)
	assert uuid in r_last['data']
	'''
	
	
    #pack name exists
	pack_name = 'VM2DB2 - Monsters University'    
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['pack_name_exists'])
	
	payload = {
	    'username': 'admin',
	    'password': 'admin',
		'pack_name': pack_name
	}	
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r_exists = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_exists.status_code
	assert json.loads(r_exists.text)

	#pack name exists(NEGATIVE test)
	pack_name = 'fake pack name'
	payload = {
	    'username': 'admin',
	    'password': 'admin',
		'pack_name': pack_name
	} 
	r_exists = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_exists.status_code
	#possibly add some assert fnctions to framework utilties 
	assert json.loads(r_exists.text) == False
	
		
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
	
	#db - before edit find a real screen(API seems to still work with fake screen ids)
	db = create_engine(config['tms']['db_type'] + config['tms']['db'])	
	connection = db.connect()
	result = connection.execute("select uuid from screen")
	#fetch one - any will do
	row = result.fetchone()
	screen_uuid=row['uuid']
	connection.close()
	
	#edit(i.e. edit associated screens with pack)
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port'],
									config['api']['core']['pack']['edit'])
	
	pack_uuids=[uuid]
	screen_uuids=[screen_uuid]
	payload = {
	    'username': 'admin',
	    'password': 'admin',
	    'pack_uuids':pack_uuids,
	    'screen_uuids': screen_uuids
	    
	}	
	
	headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
	r_edit = requests.post(url, data=json.dumps(payload), headers=headers)
	status = r_edit.status_code
	response_edit = json.loads(r_edit.text)
	assert 'Pack(s) updated' in response_edit['messages'][0]['message']
	assert 'success' in response_edit['messages'][0]['type']
		
	
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


@attr(env=['test'],priority = 2)	
def test_pack_xml():
	
		#create Pack
	
	ads_xml ='''<?xml version="1.0" encoding="UTF-8"?>
	<AAMPack xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="pack_schema.xsd">    
    <AnnotationText>Pack API Test My movie</AnnotationText>
    <IssueDate>2011-08-10T15:00:00Z</IssueDate>
    <Issuer>Karens Ad Agency</Issuer>
    <Placeholder>Silver Screen Ads</Placeholder>
    <Version>1</Version>
    <NotValidBeforeDate>2013-08-01</NotValidBeforeDate>
    <NotValidBeforeTime>10:00:00</NotValidBeforeTime>
    <NotValidAfterDate>2013-08-10</NotValidAfterDate>
    <NotValidAfterTime>15:00:00</NotValidAfterTime>
    <TargetRatingCertificate>PG</TargetRatingCertificate>
    <FilmTitle>My Movie</FilmTitle>
    <ShowAttributes><ShowAttribute>3_D</ShowAttribute><ShowAttribute>Mommie and Me</ShowAttribute></ShowAttributes>
    <ElementList>
        <Element>
            <ContentTitleText>Best ad Ever</ContentTitleText>
            <CplUUID>1f66d340-a648-43c1-bfc6-639185337b28</CplUUID>
        </Element>
        <Element>
            <ContentTitleText>6BIG-BUCK-BUNN_ADV-1_C_EN-XX_INT-TL_2K_20120905_AAM_OV</ContentTitleText>
            <CplUUID>198798f1-f059-4ecb-9695-055432744c53</CplUUID>
        </Element>
        <Element>
            <ContentTitleText>ART-BLACK-LOGO_ADV_178_EN-XX_UK_20_ART_20100420_AAM_OV</ContentTitleText>
            <CplUUID>284930ab-f68a-42e8-8bb1-ae71fdde8e02</CplUUID>
            <Duration>312</Duration>
            <EditRate>24 1</EditRate>
        </Element>
    </ElementList>
</AAMPack>'''
		
	#save an xml pack	
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['add_pack_xml'])
	
	payload = {
	    'username': 'admin',
	    'password': 'admin',
	    'pack':ads_xml
	}
	
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

'''
	url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
	                                       ,config['api']['core']['pack']['last_modified'])
	payload = {
	    'username': 'admin',
	    'password': 'admin'
	}
	
	data = json.dumps(payload)
	
	request = urllib2.Request(url, data)
	request.add_header('Cache-Control', 'no-cache')
	request.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(request, timeout=10)
	
	response_body = response.read()
	print json.loads(response_body)
	'''
	
'''
{"username": "admin", "password": "admin", "screen_uuid":"2b20e3b7-e299-4a6f-ab5d-5b9d35973e6c", "title_uuid":" " , "placeholder_uuid":" " , "print_number";" " , "show_attribute_names":" "}
'''