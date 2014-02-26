import requests
from testconfig import config
import json
from framework.common_env import SERVICE_NAME_SCREEN_WRITER as SERVICE_NAME


class Messages(object):
    saved_msg = "Saved"
    deleted_msg = "Deleted"
    missing_msg = "missing"
    not_exist_msg = "not exist"
    updated_msg =  "updated"

class PackService(object):


    def create_url(self,
                    path,
                    host=config[SERVICE_NAME]['ip'],
                    port=config[SERVICE_NAME]['port']):
        return '{0}://{1}:{2}/{3}'.format(
            config[SERVICE_NAME]['scheme'], host, port, path)


    def test_pack_api(self, resource, url=None, p_data=None):

        headers = {
            'content-type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        #payload = config[SERVICE_NAME]['credentials']
        payload =  {
        'username': 'admin',
        'password': 'admin'
        }
        temp_dict ={}

        if resource is "save_pack_json":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['save']
            )
            if p_data is None:
                p_data = self.create_dict_pack()
        elif resource is "pack_name_exists":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['pack_name_exists']
            )
            temp_dict['pack_name'] = p_data
            p_data = temp_dict
        elif resource is "find_pack":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['find_pack']
            )
            #temp_dict['cpl_uuid'] = p_data
            #p_data = temp_dict
        elif resource is "delete_pack":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['delete']
            )
            temp_dict['pack_uuids'] = p_data
            p_data = temp_dict
        elif resource is "packs":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['packs']
            )
            #temp_dict['pack_uuids'] = p_data
            #p_data = temp_dict

        elif resource is "edit":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['edit']
            )

        payload.update(p_data)
        #print "payload"
        #print payload
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response

    def pack_clean_up(self, response):
        pack_uuid= str(response.json () ['messages'][0]['uuid'])
        response = self.test_pack_api(
            "delete_pack",
            p_data=[pack_uuid]
        )


    @staticmethod
    def create_dict_pack(
            clips=1,
            packs=1,
            required_fields=True,
            **kwargs
    ):
        """
        Creates a dict of pack info
        Positional arguments are for required parameters and key
        word arguments are for optional parameters
        @param clips: number of clips to include in a a pack
        @param cpl_id: CPL UUID
        @param text: CPL content title text
        @param duration_in_frames: Duration in frames
        @param edit_rate: CPL Edit rate
        @param placeholder_name: placeholder name
        @param name: name of pack
        @param **kwargs: optional arguments
        """

        clip_list = []
        clip_dict = {}
        pack_dict = {}

        if required_fields is True:

            pack_dict['name'] = kwargs.get('name', 'pack_name')
            pack_dict['placeholder_name'] = kwargs.get(
                    'placeholder_name',
                    'placeholder_name'
                )

        if clips > 0:
            for clip in range(clips):
                if len(kwargs) > 0:
                    for key, value in kwargs.iteritems():
                        if(
                            'cpl_id' is key
                            or 'text' is key
                            or 'duration_in_frames' is key
                            or 'edit_rate' is key
                            or 'duration_in_seconds' is key
                            or 'duration_in_frames' is key
                            ):
                            clip_dict.update({key:value})
            clip_list.append(clip_dict)
            pack_dict['clips'] = clip_list



        # if key word arguments are provided then set as appropiate
        if len(kwargs) > 0:
            for key, value in kwargs.iteritems():
                if not (
                    'cpl_id' is key
                    or 'text' is key
                    or 'duration_in_frames' is key
                    or 'edit_rate' is key
                    or 'duration_in_seconds' is key
                    or 'duration_in_frames' is key
                ):
                    pack_dict.update({key:value})
        packs_list = []
        for pack in range(packs):
            packs_list.append(pack_dict)
        packs_dict = {'packs': packs_list}
        return packs_dict

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
        url = 'http://{0}:{1}/{2}'.format(config[SERVICE_NAME]['ip'],config[SERVICE_NAME]['port']
                                               ,config['api'][SERVICE_NAME]['pack']['add_pack_xml'])
        
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
        url = 'http://{0}:{1}/{2}'.format(config[SERVICE_NAME]['ip'],config[SERVICE_NAME]['port']
                                               ,config['api'][SERVICE_NAME]['pack']['add_pack_xml'])
        #create dict with credentials  
        payload = config[SERVICE_NAME]['credentials']
        #update dict with a dict 'packs' and the json payload 'ads'   
        payload.update({'pack':[ads_xml]}) 
            
        
        headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
       '''



