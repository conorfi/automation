"""
Service functionality for working with Courier APIs and remote interfaces.
"""
import requests
from testconfig import config

from framework.utility.utility import Utility
from framework.common_env import SERVICE_NAME_COURIER as SERVICE_NAME


class CourierService(object):

    def __init__(self):
        # initialize utility class
        self.util = Utility()
