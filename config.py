import ConfigParser

_config = ConfigParser.SafeConfigParser()
_config.read('api-paste.ini')

os_auth_url = _config.get('DEFAULT', 'os_auth_url')
bind_address = _config.get('DEFAULT', 'bind_address')
bind_port = _config.getint('DEFAULT', 'bind_port')
log_path = _config.get('DEFAULT', 'log_path')
admin_user = _config.get('DEFAULT', 'admin_user')
admin_project = _config.get('DEFAULT', 'admin_project')
admin_project_id = _config.get('DEFAULT', 'admin_project_id')
admin_passwd = _config.get('DEFAULT', 'admin_passwd')
admin_role_id = _config.get('DEFAULT', 'admin_role_id')
shadow_user_name = _config.get('DEFAULT', 'shadow_user_name')
member_role_id = _config.get('DEFAULT', 'member_role_id')
enable_ssl = _config.get('DEFAULT', 'enable_ssl')
privatekey_file = _config.get('DEFAULT', 'privatekey_file')
certificate_file = _config.get('DEFAULT', 'certificate_file')
debug = _config.get('DEFAULT', 'debug')

if not _config.has_option('DEFAULT', 'disable_inner_high'):
    disable_inner_high = False
else:
    disable_inner_high = _config.get('DEFAULT', 'disable_inner_high')

#Notification DB
notification_db_config = {}
notification_db_config['db_host'] = _config.get(
    'Notification_DB', 'db_host')
notification_db_config['db_port'] = int(
    _config.get('Notification_DB', 'db_port'))
notification_db_config['db_user'] = _config.get(
    'Notification_DB', 'db_user')
notification_db_config['db_pass'] = _config.get(
    'Notification_DB', 'db_pass')
notification_db_config['db_schema'] = _config.get(
    'Notification_DB', 'db_schema')

devices_db_host = _config.get('devices', 'db_host')
devices_db_port = _config.get('devices', 'db_port')
devices_db_user = _config.get('devices', 'db_user')
devices_db_passwd = _config.get('devices', 'db_passwd')
devices_db = _config.get('devices', 'db_database')

workissue_db_host = _config.get('workissue', 'workissue_db_host')
workissue_db_port = _config.get('workissue', 'workissue_db_port')
workissue_db_user = _config.get('workissue', 'workissue_db_user')
workissue_db_passwd = _config.get('workissue', 'workissue_db_passwd')
workissue_db = _config.get('workissue', 'workissue_db_database')

security_db_host = _config.get('security', 'db_host')
security_db_port = _config.get('security', 'db_port')
security_db_user = _config.get('security', 'db_user')
security_db_passwd = _config.get('security', 'db_passwd')
security_db = _config.get('security', 'db_database')
wafs_server_port = _config.get('security', 'wafs_server_port')
wafs_image_id = _config.get('security', 'wafs_image_id')
enable_daemons = _config.get('security', 'enable_daemons')
daemon_modules =  _config.get('security', 'modules_to_daemon')

sso_login = _config.get('sso', 'sso_login')
