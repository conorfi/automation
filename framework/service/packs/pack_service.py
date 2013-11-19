import requests
from testconfig import config
import json

class PackService(object):

    def save_pack(self,url=None):
        
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