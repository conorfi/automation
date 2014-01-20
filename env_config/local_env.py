"""
Local development configuration
"""
from framework.common_env import *

global config
config = get_common_config()

gatekeeper_config = get_default_service_config()
gatekeeper_config.update({
    'port': '8070',
    'db_name': 'gatekeeper'
})
set_gatekeeper_config(config, **gatekeeper_config)

courier_config = get_default_service_config()
courier_config.update({
    'port': '10001',
    'db_name': 'courier'
})
set_courier_config(config, **courier_config)
