"""
Configuration for development test environment
"""
from framework.common_env import *

global config
config = get_common_config()

gatekeeper_config = get_default_service_config()
gatekeeper_config.update({
    'scheme': 'https',
    'host': 'app-t01',
    'ip': '10.20.254.142',
    'port': '8070',
    'db_host': '10.20.254.142',
    'db_name': 'gatekeeper',
    'dummyapp_host': 'app-t01',
    'db_type': 'postgresql',
    'db_credentials': 'postgres:postgres'
})

set_gatekeeper_config(config, **gatekeeper_config)

courier_config = get_default_service_config()
courier_config.update({
    'scheme': 'https',
    'host': 'app-t01',
    'ip': '10.20.254.142',
    'port': '10001',
    'db_host': '10.20.254.142',
    'db_name': 'courier',
    'db_type': 'postgresql',
    'db_credentials': 'postgres:postgres'
})
set_courier_config(config, **courier_config)


screenwriter_config = get_default_service_config()
screenwriter_config.update({
    'scheme': 'http',
    'host': '10.0.2.15',
    'ip': '10.0.2.15',
    'port': '8080',
    'db_host': '10.0.2.15',
    'db_name': '/aam-lms/db/cinema_services.db',
    'db_type': 'sqlite:///'
})
set_screenwriter_config(config, **screenwriter_config)