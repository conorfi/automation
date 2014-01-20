"""
Configuration for development test environment
"""
from framework.common_env import *

global config
config = get_common_config()

gatekeeper_config = get_default_service_config()
gatekeeper_config.update({
    'host': 'app-t01',
    'ip': '10.20.254.142',
    'port': '8070',
    'db_host': '10.20.254.142',
    'db_name': 'gatekeeper',
    'dummyapp_host': 'app-t01'
})
set_gatekeeper_config(**gatekeeper_config)

courier_config = get_default_service_config()
courier_config.update({
    'host': 'app-t01',
    'ip': '10.20.254.142',
    'port': '10001',
    'db_host': '10.20.254.142',
    'db_name': 'courier'
})
set_courier_config(**courier_config)
