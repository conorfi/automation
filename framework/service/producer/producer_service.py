import requests
from testconfig import config
import json
from framework.common_env import SERVICE_NAME_PRODUCER as SERVICE_NAME


class Messages(object):
    saved_msg = "Saved"
    deleted_msg = "Deleted"
    missing_msg = "missing"
    not_exist_msg = "not exist"
    updated_msg = "updated"


class PackService(object):

    def create_url(self,
                   path,
                   host=config[SERVICE_NAME]['host'],
                   port=config[SERVICE_NAME]['port'],
                   ):
        url ='{0}://{1}:{2}/{3}'.format(
            config[SERVICE_NAME]['scheme'], host, port, path)
        #TODO: improve this line - just a hack for now
        url = url + '?username=admin&password=admin'
        return url

    def test_pack_api(self, resource, url=None, p_data=None):

        headers = {
            'content-type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        temp_dict = {}

        payload = {
            'username': 'admin',
            'password': 'admin',
        }

        if resource is "datatables":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['datatables']
            )
            temp_dict['datatables'] = p_data
            p_data = temp_dict

        elif resource is "packs":
            url = self.create_url(
                config['api'][SERVICE_NAME]['pack']['packs']
            )
            temp_dict['datatables'] = p_data
            p_data = temp_dict

        response = requests.get(url)
        return response


