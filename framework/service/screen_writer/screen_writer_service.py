import requests
from testconfig import config
import json
from framework.common_env import SERVICE_NAME_SCREEN_WRITER as SERVICE_NAME


class Messages(object):
    saved_msg = "Saved"
    deleted_msg = "Deleted"

class PackService(object):

    def save_pack_json(self,url=None,pack=None):
        if(url==None):
            url = 'http://{0}:{1}/{2}'.format(config[SERVICE_NAME]['ip'],config[SERVICE_NAME]['port']
                                           ,config['api'][SERVICE_NAME]['pack']['save'])
        
        #create dict with credentials  
        payload = config[SERVICE_NAME]['credentials']
        if pack is None:
            pack = self.create_dict_pack()
        #update paylaod with pack info
        payload.update(pack)
        headers = {'content-type': 'application/json','Cache-Control':'no-cache'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response

    @staticmethod
    def create_dict_pack(
            clips=1,
            packs=1,
            cpl_id="abb5f47f-014d-4a11-8d1e-a820470f01a7",
            text="16554TPG1799UN_ADV_F_EN-XX_AU_51_2K_20130111_DAU_OV",
            duration_in_frames=1080,
            edit_rate="24 1",
            placeholder_name="place holder name",
            name="pack name",
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
        for clip in range(clips):
            clip_dict = {"cpl_id": cpl_id,
                         "text": text,
                         "edit_rate": edit_rate
            }
            #if duration_in_seconds, use instead of duration_in_frames
            if "duration_in_seconds" in kwargs:
                clip_dict["duration_in_seconds"] = kwargs["duration_in_seconds"]
            else:
                clip_dict["duration_in_frames"]= duration_in_frames

            clip_list.append(clip_dict)

        pack_dict={}
        pack_dict["clips"] = clip_list

        pack_dict["name"]= name

        #if placeholder_uuid, use instead of placeholder_name
        if "placeholder_uuid" in kwargs:
            pack_dict["placeholder_uuid"] = kwargs["placeholder_uuid"]
        else:
            pack_dict["placeholder_name"] = placeholder_name

        # if key word arguments are provided then merge with the exisiting dict
        if len(kwargs)>0:
            pack_dict.update(kwargs)

        packs_list=[]
        for pack in range(packs):
            packs_list.append(pack_dict)

        packs_dict = {'packs': packs_list}
        print "pack"
        print packs_dict
        print "pack"

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