global config    
config = {}

config['google-server'] = {}
config['google-server']['host'] = "https://google.ca"

config['tms'] = {}
config['tms']['ip'] = '172.17.115.14'
config['tms']['port'] = 8080
config['tms']['db'] = 'C:\\aam-lms\\db\\cinema_services.db'
config['tms']['db_type'] = 'sqlite:///'
config['tms']['credentials'] = {'username': 'admin','password': 'admin'}

config['gatekeeper'] ={}
config['gatekeeper']['host'] = 'localhost'
config['gatekeeper']['ip'] = '127.0.0.1'
config['gatekeeper']['port'] = '8070'
config['gatekeeper']['credentials'] = {'username': 'admin','password': 'admin'}                                    
config['gatekeeper']['db'] ={}
config['gatekeeper']['db']['type'] = 'postgresql'
config['gatekeeper']['db']['credentials'] = 'postgres:postgres'
config['gatekeeper']['db']['host'] = 'localhost'
config['gatekeeper']['db']['port'] = '5432'
config['gatekeeper']['db']['db_name'] = 'gatekeeper'
config['gatekeeper']['db']['connection'] = \
    'postgresql://postgres:postgres@localhost:5432/gatekeeper'
config['gatekeeper']['redirect'] = '?redirect=http%3A%2F%2Fwww.example.com'
config['gatekeeper']['dummy'] = {}
config['gatekeeper']['dummy']['host'] = 'localhost'
config['gatekeeper']['dummy']['port'] = '8001'
config['gatekeeper']['dummy']['user_endpoint'] = 'user'
config['gatekeeper']['dummy']['admin_endpoint'] = 'admin'
config['api'] = {}
config['api']['core'] = {}
config['api']['core']['pack'] = {}
config['api']['core']['pack']['save'] = 'core/pack/save'
config['api']['core']['pack']['find_pack'] = 'core/pack/find_pack'
config['api']['core']['pack']['packs'] = 'core/pack/packs'
config['api']['core']['pack']['edit'] = 'core/pack/edit'
config['api']['core']['pack']['delete'] = 'core/pack/delete'
config['api']['core']['pack']['edit'] =  'core/pack/edit'
config['api']['core']['pack']['last_modified'] = 'core/pack/last_modified'
config['api']['core']['pack']['pack_name_exists'] = 'core/pack/pack_name_exists'
config['api']['core']['pack']['add_pack_xml'] = 'core/pack/add_pack_xml'
config['api']['user'] = {}
config['api']['user']['session'] = {}
#trailing / required for login
config['api']['user']['session']['create_v1'] = 'login/'
config['api']['user']['session']['validate_v1'] = 'api/v1/user/session'
#trailing / required for logout
config['api']['user']['session']['delete_v1'] = 'logout/'
config['api']['user']['session']['user_info_v1'] = 'api/v1/user'
