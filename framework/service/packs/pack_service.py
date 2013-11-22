import requests
from testconfig import config
import json

class PackService(object):

    def save_pack_json(self,url=None):
        
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
    
        if(url==None):
            url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
                                           ,config['api']['core']['pack']['save'])
        
        #create dict with credentials  
        payload = config['tms']['credentials']     
        #update dict with a dict 'packs' and the json payload 'ads'   
        payload.update({'packs':[ads]}) 
        
    
        headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response
    
    def save_pack_xml(self,url=None):
        
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
        return r

        '''
        #save an xml pack    
        url = 'http://{0}:{1}/{2}'.format(config['tms']['ip'],config['tms']['port']
                                               ,config['api']['core']['pack']['add_pack_xml'])
        #create dict with credentials  
        payload = config['tms']['credentials']     
        #update dict with a dict 'packs' and the json payload 'ads'   
        payload.update({'pack':[ads_xml]}) 
            
        
        headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
       '''