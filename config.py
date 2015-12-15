import ConfigParser

_config = ConfigParser.SafeConfigParser()
_config.read('api-paste.ini')

os_auth_url = _config.get('DEFAULT', 'os_auth_url')
bind_address = _config.get('DEFAULT', 'bind_address')
bind_port = _config.getint('DEFAULT', 'bind_port')
log_path = _config.get('DEFAULT', 'log_path')
admin_user = _config.get('DEFAULT', 'admin_user')
admin_project = _config.get('DEFAULT', 'admin_project')
admin_passwd = _config.get('DEFAULT', 'admin_passwd')
admin_role_id = _config.get('DEFAULT', 'admin_role_id')
enable_ssl = _config.get('DEFAULT', 'enable_ssl')
privatekey_file = _config.get('DEFAULT', 'privatekey_file')
certificate_file = _config.get('DEFAULT', 'certificate_file')
debug = _config.get('DEFAULT', 'debug')

#Notification DB
notification_db_config={}
notification_db_config["db_host"]=_config.get('Notification_DB','db_host')
notification_db_config["db_port"]=int(_config.get('Notification_DB','db_port'))
notification_db_config["db_user"]=_config.get('Notification_DB','db_user')
notification_db_config["db_pass"]=_config.get('Notification_DB','db_pass')
notification_db_config["db_schema"]=_config.get('Notification_DB','db_schema')

devices_db_host = _config.get('devices', 'db_host')
devices_db_port = _config.get('devices', 'db_port')
devices_db_user = _config.get('devices', 'db_user')
devices_db_passwd = _config.get('devices', 'db_passwd')
devices_db = _config.get('devices', 'db_database')
