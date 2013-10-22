global config    
config = {}

config['google-server'] = {}
config['google-server']['host'] = "https://google.ca"

config['tms'] = {}
config['tms']['ip'] = '172.28.150.133'
config['tms']['port'] = 8080
config['tms']['db'] = 'C:\\aam-lms\\db\\cinema_services.db'
config['tms']['db_type'] = 'sqlite:///'

config['api'] = {}
config['api']['core'] = {}
config['api']['core']['pack'] = {}
config['api']['core']['pack']['save'] = 'core/pack/save'
config['api']['core']['pack']['find_pack'] = 'core/pack/find_pack'
config['api']['core']['pack']['packs'] = 'core/pack/packs'
config['api']['core']['pack']['edit'] = 'core/pack/edit'
config['api']['core']['pack']['delete'] = 'core/pack/delete'