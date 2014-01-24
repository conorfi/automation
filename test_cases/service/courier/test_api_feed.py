"""
Integration tests for group API
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase
from framework.db.model.courier import Feed

class FeedApiTestCase(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_create_success(self):
        """
        COURIER_FEED_API_001 test_create_success

        Successful test when creating feed via API
        """
        user, session = self.login_random_user()
        feed = self.service.generate_feed()
        print feed
        response = self.service.resource_request(
            'feed', method='post', data=feed.to_request_data(),
            session=session)
        self.assertResponseSuccess(response)
        json_data = response.json()
        group_data = json_data.get('data')
        self.assertGroupData(group.to_request_data(), group_data)

        self.service.remove_user(user)
        self.service.remove_group(group)