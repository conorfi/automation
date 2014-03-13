"""
@summary: Contains a set of test cases for screen_writer(tms) packs API
@since: Created on October 31st 2013
@author: Conor Fitzgerald
"""
from nose.plugins.attrib import attr
from . import ApiTestCase
import requests


class ScreenWriterPacksAPI(ApiTestCase):
    @attr(env=['test'], priority=1)
    def test_save_pack_required_params(self):
        """
        SW_PACK_API_001 test_save_pack_required_params
        Ensure save API works correctly when required fields are provided
        Json request and response
        """
        response = self.packs_service.test_pack_api("save_pack_json")
        self.assertResponse(response, message=self.msgs.saved_msg)
        self.packs_service.pack_clean_up(response)

    @attr(env=['test'], priority=1)
    def test_save_pack_required_params_none(self):
        """
        SW_PACK_API_002 test_save_pack_required_params_none
        Ensure save API returns an error when required fields are None
        Json request and response
        """
        # list of date that can not be null
        list_none = [
            {'placeholder_name': None},
            {'name': None},
            {'placeholder_uuid': None},
            {'placeholder_uuid': None, 'placeholder_name': None}
        ]

        for none_dict in list_none:
            ads = self.packs_service.create_dict_pack(
                required_fields=False,
                **none_dict
            )
            #response = self.packs_service.save_pack_json(pack=ads)
            response = self.packs_service.test_pack_api(
                "save_pack_json",
                p_data=ads
            )
            self.assertResponse(response, message=self.msgs.missing_msg)

    @attr(env=['test'], priority=1)
    def test_save_pack_required_params_no_clip(self):
        """
        SW_PACK_API_003 test_save_pack_required_params_no_clip
        Ensure save API returns an error when no clips is provided
        Json request and response
        """
        #create a pack dict with no clips
        ads = self.packs_service.create_dict_pack(clips=0)
        response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=ads
        )
        self.assertResponse(response, message=self.msgs.missing_msg)

    @attr(env=['test'], priority=1)
    def test_save_pack_required_params_invalid_title_uuid(self):
        """
        SW_PACK_API_004 test_save_pack_required_params_invalid_title_uuid
        Ensure save API returns an error when an invalid titleuuid
        is provided
        Json request and response
        """
        invalid_title = {'title_uuid': 'could_not_exist'}
        ads = self.packs_service.create_dict_pack(**invalid_title)
        response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=ads
        )
        self.assertResponse(response, message=self.msgs.not_exist_msg)

    @attr(env=['test'], priority=1)
    def test_save_pack_required_params_edit_rate_none(self):
        """
        SW_PACK_API_005 test_save_pack_required_params_edit_rate_none
        Ensure save API sets the edit rate if None
        The default required test  data contains no clip data
        Json request and response
        """
        create_response = self.packs_service.test_pack_api(
            "save_pack_json"
        )
        self.assertResponse(create_response, message=self.msgs.saved_msg)

        pack_uuids = create_response.json()['messages'][0]['uuid']
        pack_dict = {'pack_uuids': [pack_uuids]}
        response = self.packs_service.test_pack_api(
            "packs",
            p_data=pack_dict
        )
        #simple assertion that edit rate is not none
        self.assertTrue(
            response.json()['data'][pack_uuids]['clips'][0]['edit_rate']
        )
        self.packs_service.pack_clean_up(create_response)

    @attr(env=['test'], priority=1)
    def test_save_json_pack_optional_parms(self):
        """
        SW_PACK_API_006 test_save_json_pack_optional_parms
        Ensure save API works correctly with all optional fields are provided
        Json request and response
        """
        option_dict = self.optional_dict
        ads = self.packs_service.create_dict_pack(**option_dict)
        create_response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=ads
        )
        self.assertResponse(create_response, message=self.msgs.saved_msg)

        # verify using the packs API
        pack_uuids = create_response.json()['messages'][0]['uuid']
        pack_dict = {'pack_uuids': [pack_uuids]}
        response = self.packs_service.test_pack_api(
            "packs",
            p_data=pack_dict
        )
        print ""
        self.assert_packs_data(response, **pack_dict)

        self.packs_service.pack_clean_up(create_response)

    @attr(env=['test'], priority=1)
    def test_save_json_pack_optional_parms_individually(self):
        """
        SW_PACK_API_007 test_save_json_pack_optional_parms_individually
        Ensure save API works correctly with option fields created individually
        Json request and response
        """
        option_dict = self.optional_dict
        for k, v in option_dict.iteritems():
            ads = self.packs_service.create_dict_pack(**{k: v})
            response = self.packs_service.test_pack_api(
                "save_pack_json",
                p_data=ads
            )
            self.assertResponse(response, message=self.msgs.saved_msg)
            self.packs_service.pack_clean_up(response)

    @attr(env=['test'], priority=1)
    def test_save_pack_optional_params_invalid(self):
        """
        SW_PACK_API_008 test_save_pack_optional_params_invalid
        Ensure save API returns an error when optional fields have
        invalid values
        Json request and response
        """
        # list of date that can not be null
        list_invalid = [
            {'date_from': "fake_date"},
            {'date_to': "fake_date"},
            {'time_from': "fake_date"},
            {'time_to': "fake_date"}
        ]

        for invalid_dict in list_invalid:
            ads = self.packs_service.create_dict_pack(
                **invalid_dict
            )
            response = self.packs_service.test_pack_api(
                "save_pack_json",
                p_data=ads
            )
            # TODO: re-add the assertion if BUG is resolved
            # BUG: https://www.pivotaltracker.com/story/show/66166264
            #self.assertResponse(response, message=self.msgs.missing_msg)

    @attr(env=['test'], priority=1)
    def test_pack_name_exists(self):
        """
        SW_PACK_API_009 test_pack_name_exists
        Ensure test_pack_name_exists API works correctly
        Json request and response
        """
        req_dict = self.packs_service.create_dict_pack()
        create_response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=req_dict
        )
        self.assertResponse(create_response, message=self.msgs.saved_msg)

        pack_name = str(req_dict['packs'][0]['name'])
        response = self.packs_service.test_pack_api(
            "pack_name_exists",
            p_data=pack_name
        )
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(response.text, 'true')

        self.packs_service.pack_clean_up(create_response)


    @attr(env=['test'], priority=1)
    def test_pack_name_exists_invalid(self):
        """
        SW_PACK_API_010 test_pack_name_exists
        Ensure test_pack_name_exists API returns errors when fake
        packname is provided
        Json request and response
        """
        pack_name = "fakey_fakey"
        response = self.packs_service.test_pack_api(
            "pack_name_exists",
            p_data=pack_name
        )
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertEqual(response.text, 'false')

    @attr(env=['test'], priority=1)
    def test_find_pack(self):
        """
        SW_PACK_API_011 test_find_pack
        Ensure save API works correctly with option fields
        Json request and response
        """
        uuid = self.util.random_uuid()
        cpl_dict = {
            'cpl_id': uuid,
            'name': self.util.random_str(8),
            'uuid': self.util.random_uuid(),
            'placeholder_uuid': self.placeholder_uuid
        }

        find_cpl_dict = {'cpl_uuid': uuid}

        req_dict = self.packs_service.create_dict_pack(
            **cpl_dict
        )

        create_response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=req_dict
        )
        self.assertResponse(create_response, message=self.msgs.saved_msg)

        response = self.packs_service.test_pack_api(
            "find_pack",
            p_data=find_cpl_dict
        )

        self.assert_find_pack_data(response, **cpl_dict)
        self.packs_service.pack_clean_up(create_response)

    @attr(env=['test'], priority=1)
    def test_find_pack_invalid(self):
        """
        SW_PACK_API_012 test_find_pack_invalid
        Ensure save API works correctly with option fields
        Json request and response
        """
        find_cpl_dict = {'cpl_uuid': "fake_fake_fake"}

        response = self.packs_service.test_pack_api(
            "find_pack",
            p_data=find_cpl_dict
        )
        self.assertResponse(response)

    @attr(env=['test'], priority=1)
    def test_packs(self):
        """
        SW_PACK_API_013 test_packs
        Ensure "packs" API returns the correct information when
        a packs is created through "save" API with required data
        Json request and response
        """

        req_dict = self.packs_service.create_dict_pack()
        create_response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=req_dict
        )
        self.assertResponse(create_response, message=self.msgs.saved_msg)

        pack_uuids = create_response.json()['messages'][0]['uuid']
        pack_dict = {'pack_uuids': [pack_uuids]}
        response = self.packs_service.test_pack_api(
            "packs",
            p_data=pack_dict
        )
        self.assert_packs_data(response, **pack_dict)
        self.packs_service.pack_clean_up(create_response)

    @attr(env=['test'], priority=1)
    def test_edit(self):
        """
        SW_PACK_API_009 test_edit
        Ensure edit  API works correctly three available options
        A)placeholder_uuid
        b)screen_uuids
        C)placeholder_uuid and screen_uuids
        Json request and response
        """

        req_dict = self.packs_service.create_dict_pack()
        create_response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=req_dict
        )

        self.assertResponse(create_response, message=self.msgs.saved_msg)
        pack_uuids = create_response.json()['messages'][0]['uuid']

        edit_dict_list = [
            {
                'pack_uuids': [pack_uuids],
                'placeholder_uuid': self.placeholder_uuid
            },
            {
                'pack_uuids': [pack_uuids],
                'screen_uuids': [self.screen_uuid]
            },
            {
                'pack_uuids': [pack_uuids],
                'placeholder_uuid': self.placeholder_uuid,
                'screen_uuids': [self.screen_uuid]
            }
        ]
        for edit_dict in edit_dict_list:
            response = self.packs_service.test_pack_api(
                "edit",
                p_data=edit_dict
            )
            self.assertResponse(response, message=self.msgs.updated_msg)
            #assert using the packs API
            pack_dict = {'pack_uuids': [pack_uuids]}
            response = self.packs_service.test_pack_api(
                "packs",
                p_data=pack_dict
            )
            self.assert_packs_data(response, **pack_dict)

        #self.packs_service.pack_clean_up(create_response)

    @attr(env=['test'], priority=1)
    def test_edit_invalid(self):
        """
        SW_PACK_API_009 test_edit
        Ensure edit API returns error when the placeholder and/or screen ids
        do not exist in the system
        Json request and response
        """

        req_dict = self.packs_service.create_dict_pack()
        create_response = self.packs_service.test_pack_api(
            "save_pack_json",
            p_data=req_dict
        )

        self.assertResponse(create_response, message=self.msgs.saved_msg)
        pack_uuids = create_response.json()['messages'][0]['uuid']

        edit_dict_list = [
            {
                'pack_uuids': [pack_uuids],
                'placeholder_uuid': self.util.random_uuid()
            },
            {
                'pack_uuids': [self.util.random_uuid()],
                'screen_uuids': [self.util.random_uuid()]
            },
            {
                'pack_uuids': [pack_uuids],
                'placeholder_uuid': self.util.random_uuid(),
                'screen_uuids': [self.util.random_uuid()]
            }
        ]
        for edit_dict in edit_dict_list:
            response = self.packs_service.test_pack_api(
                "edit",
                p_data=edit_dict
            )
            # :TODO Add verification if BUG is resolved
            # :BUG https://www.pivotaltracker.com/story/show/66321080

        self.packs_service.pack_clean_up(create_response)

    @attr(env=['test'], priority=1)
    def test_pack_delete(self):
        """
        SW_PACK_API_010 test_pack_delete
        Ensure save API works correctly when it deletes
        Json request and response
        """
        response = self.packs_service.test_pack_api("save_pack_json")
        self.assertResponse(response, message=self.msgs.saved_msg)
        pack_uuid = str(response.json()['messages'][0]['uuid'])
        response = self.packs_service.test_pack_api(
            "delete_pack",
            p_data=[pack_uuid]
        )
        self.assertResponse(response, message=self.msgs.deleted_msg)