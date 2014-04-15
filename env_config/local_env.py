"""
Local development configuration
"""
from framework.common_env import *

global config
config = get_common_config()

gatekeeper_config = get_default_service_config()
gatekeeper_config.update({
    'scheme': 'https',
    'port': 443,
    'db_name': 'gatekeeper',
    'db_type': 'postgresql',
    'db_credentials': 'postgres:postgres'
})
set_gatekeeper_config(config, **gatekeeper_config)

courier_config = get_default_service_config()
courier_config.update({
    'scheme': 'https',
    'port': '10001',
    'db_name': 'courier',
    'db_type': 'postgresql',
    'db_credentials': 'postgres:postgres'
})
set_courier_config(config, **courier_config)

screenwriter_config = get_default_service_config()
screenwriter_config.update({
    'scheme': 'http',
    'port': '8080',
    'db_name': '/aam-lms/db/cinema_services.db',
    'db_type': 'sqlite'
})
set_screenwriter_config(config, **screenwriter_config)

producer_config = get_default_service_config()
producer_config.update({
    'scheme': 'http',
    'port': '8080',
    'db_name': 'yes',
    'db_type': 'postgresql',
    'db_credentials': 'postgres:postgres'
})
set_producer_config(config, **producer_config)