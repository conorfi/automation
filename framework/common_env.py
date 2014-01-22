"""
Base configuration for all automation tests
"""
SERVICE_NAME_GATEKEEPER = 'gatekeeper'
SERVICE_NAME_COURIER = 'courier'


def get_common_config():
    """
    Returns the common configuration options that never change.
    """
    config = {'api': {}}
    set_google_config(config)
    set_tms_config(config)
    return config


def get_default_service_config():
    """
    Returns the default service configuration options.
    """
    return {
        'host': 'localhost',
        'ip': '127.0.0.1',
        'port': '8070',
        'db_host': 'localhost',
        'db_port': '5432',
        'db_name': 'test',
    }


def set_google_config(config):
    """
    Sets the Google configuration.

    :param config:
    """
    config['google-server'] = {}
    config['google-server']['host'] = "https://google.ca"


def set_base_service_config(config, name, **kwargs):
    """
    Sets the base configuration for a named service, using the given
    configuration defined as a base.

    :param config:
    :param name:
    :param kwargs:
    """
    db_credentials = 'postgres:postgres'
    config[name] = {}
    config[name]['scheme'] = 'https'
    config[name]['host'] = kwargs['host']
    config[name]['ip'] = kwargs['ip']
    config[name]['port'] = kwargs['port']
    config[name]['credentials'] = {
        'username': 'admin',
        'password': 'admin'
    }
    config[name]['db'] = {}
    config[name]['db']['type'] = 'postgresql'
    config[name]['db']['credentials'] = db_credentials
    config[name]['db']['host'] = kwargs['db_host']
    config[name]['db']['port'] = kwargs['db_port']
    config[name]['db']['db_name'] = kwargs['db_name']
    config[name]['db']['connection'] = "postgresql://%s@%s:%s/%s" % \
        (db_credentials, kwargs['db_host'], kwargs['db_port'],
         kwargs['db_name'])


def set_tms_config(config):
    """
    Sets the configuration for TMS

    :param config:
    """
    config['tms'] = {}
    config['tms']['ip'] = '172.17.115.14'
    config['tms']['port'] = 8080
    config['tms']['db'] = 'C:\\aam-lms\\db\\cinema_services.db'
    config['tms']['db_type'] = 'sqlite:///'
    config['tms']['credentials'] = {'username': 'admin', 'password': 'admin'}

    config['api']['core'] = {}
    config['api']['core']['pack'] = {}
    config['api']['core']['pack']['save'] = 'core/pack/save'
    config['api']['core']['pack']['find_pack'] = 'core/pack/find_pack'
    config['api']['core']['pack']['packs'] = 'core/pack/packs'
    config['api']['core']['pack']['edit'] = 'core/pack/edit'
    config['api']['core']['pack']['delete'] = 'core/pack/delete'
    config['api']['core']['pack']['edit'] = 'core/pack/edit'
    config['api']['core']['pack']['last_modified'] = 'core/pack/last_modified'
    config['api']['core']['pack']['pack_name_exists'] = \
        "core/pack/pack_name_exists"
    config['api']['core']['pack']['add_pack_xml'] = 'core/pack/add_pack_xml'


def set_gatekeeper_config(config, **kwargs):
    """
    Sets the Gatekeeper service configuration.

    :param config:
    :param kwargs:
    """
    name = SERVICE_NAME_GATEKEEPER
    set_base_service_config(config, name, **kwargs)

    config[name]['redirect'] = '?redirect=http%3A%2F%2Fwww.example.com'
    config[name]['admin_endpoint'] = 'admin'
    config[name]['dummy'] = {}
    config[name]['dummy']['host'] = kwargs.get('dummyapp_host', 'localhost')
    config[name]['dummy']['port'] = '8001'
    config[name]['dummy']['port2'] = '8002'
    config[name]['dummy']['user_endpoint'] = 'user'
    config[name]['dummy']['admin_endpoint'] = 'admin'

    config['api'][name] = {}
    config['api'][name]['session'] = {}
    # trailing / required for login
    config['api'][name]['session']['create_v1'] = 'login/'
    config['api'][name]['session']['validate_v1'] = 'api/v1/user/session'
    # trailing / required for logout
    config['api'][name]['session']['logout_v1'] = 'logout/'

    config['api'][name]['session']['user_info_v1'] = \
        'api/v1/user/%s/application/%s'
    config['api'][name]['session']['submit_verification_v1'] = \
        'login/?step=verification_code'
    config['api'][name]['application_v1'] = {}
    config['api'][name]['application_v1']['post'] = 'api/v1/application/'
    config['api'][name]['application_v1']['id'] = 'api/v1/application/%s'
    config['api'][name]['applications_v1'] = 'api/v1/applications/'
    config['api'][name]['user_v1'] = {}
    config['api'][name]['user_v1']['post'] = 'api/v1/user/'
    config['api'][name]['user_v1']['id'] = 'api/v1/user/%s'
    config['api'][name]['users_v1'] = 'api/v1/users/'
    config['api'][name]['org_v1'] = {}
    config['api'][name]['org_v1']['post'] = 'api/v1/organization/'
    config['api'][name]['org_v1']['id'] = 'api/v1/organization/%s'
    config['api'][name]['orgs_v1'] = 'api/v1/organizations/'
    config['api'][name]['group_v1'] = {}
    config['api'][name]['group_v1']['post'] = 'api/v1/group/'
    config['api'][name]['group_v1']['id'] = 'api/v1/group/%s'
    config['api'][name]['groups_v1'] = 'api/v1/groups/'
    config['api'][name]['permission_v1'] = {}
    config['api'][name]['permission_v1']['post'] = 'api/v1/permission/'
    config['api'][name]['permission_v1']['id'] = 'api/v1/permission/%s'
    config['api'][name]['permissions_v1'] = 'api/v1/permissions/'
    config['api'][name]['user_app_v1'] = {}
    config['api'][name]['user_app_v1']['post'] = 'api/v1/userapplication/'
    config['api'][name]['user_app_v1']['id'] = 'api/v1/userapplication/%s/%s'
    config['api'][name]['user_apps_v1'] = 'api/v1/userapplications/'
    config['api'][name]['user_grp_v1'] = {}
    config['api'][name]['user_grp_v1']['post'] = 'api/v1/usergroup/'
    config['api'][name]['user_grp_v1']['id'] = 'api/v1/usergroup/%s/%s'
    config['api'][name]['user_grps_v1'] = 'api/v1/usergroups/'
    config['api'][name]['user_org_v1'] = {}
    config['api'][name]['user_org_v1']['post'] = 'api/v1/userorganization/'
    config['api'][name]['user_org_v1']['id'] = 'api/v1/userorganization/%s/%s'
    config['api'][name]['user_orgs_v1'] = 'api/v1/userorganizations/'
    config['api'][name]['grp_perm_v1'] = {}
    config['api'][name]['grp_perm_v1']['post'] = 'api/v1/grouppermission/'
    config['api'][name]['grp_perm_v1']['id'] = 'api/v1/grouppermission/%s/%s'
    config['api'][name]['grp_perms_v1'] = 'api/v1/grouppermissions/'
    config['api'][name]['user_perm_v1'] = {}
    config['api'][name]['user_perm_v1']['post'] = 'api/v1/userpermission/'
    config['api'][name]['user_perm_v1']['id'] = 'api/v1/userpermission/%s/%s'
    config['api'][name]['user_perms_v1'] = 'api/v1/userpermissions/'
    config['api'][name]['grp_app_v1'] = {}
    config['api'][name]['grp_app_v1']['post'] = 'api/v1/groupapplication/'
    config['api'][name]['grp_app_v1']['id'] = 'api/v1/groupapplication/%s/%s'
    config['api'][name]['grp_apps_v1'] = 'api/v1/groupapplications/'
    config['api'][name]['recover_account_v1'] = {}
    config['api'][name]['recover_account_v1']['post'] = 'recoveraccount'
    config['api'][name]['recover_account_v1']['param'] = \
        "recoveraccount?style=gatekeeper&check_email=True"
    config['api'][name]['change_password_v1'] = {}
    config['api'][name]['change_password_v1']['post'] = 'changepassword/%s'


def set_courier_config(config, **kwargs):
    """
    Sets the Courier service configuration.

    :param config:
    :param kwargs:
    """
    name = SERVICE_NAME_COURIER
    set_base_service_config(config, name, **kwargs)

    config['api'][name] = {}
    config['api'][name]['authenticate_v1'] = {}
    config['api'][name]['authenticate_v1']['post'] = 'authenticate/'
    config['api'][name]['group_v1'] = {}
    config['api'][name]['group_v1']['get'] = 'rest/group/'
