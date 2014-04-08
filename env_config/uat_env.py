"""
uat configuration
"""

from framework.common_env import *

global config
config = get_common_config()

gatekeeper_config = get_default_service_config()
gatekeeper_config.update({
    'scheme': 'https',
    'host':'gatekeeper-uat.artsalliancemedia.com',
    'db_host': 'aam-uat-postgres-1.artsalliancemedia.com',
    'db_name': 'gatekeeper',
    'db_type': 'postgresql',
    'db_credentials': 'postgres:dbUs3r',
    'port': None
})

set_gatekeeper_config(config, **gatekeeper_config)
