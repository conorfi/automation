"""
uat configuration
"""
from framework.common_env import *

global config
config = get_common_config()

gatekeeper_config = get_default_service_config()
gatekeeper_config.update({
    'scheme': 'https',
    'host': 'gatekeeper-uat.artsalliancemedia.com',
    'ip': ' 213.161.94.173',
    'port': '8070',
    'db_host': '213.161.94.173',
    'db_name': 'gatekeeper',
    'dummyapp_host': 'gatekeeper-uat.artsalliancemedia.com',
    'db_type': 'postgresql',
    'db_credentials': 'postgres:postgres'
})

set_gatekeeper_config(config, **gatekeeper_config)
