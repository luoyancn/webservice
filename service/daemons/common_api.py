import time
import config
import requests
import md5 as _md5
import pymysql
import log

from keystoneclient.auth.identity.generic.password\
    import Password as auth_plugin
from keystoneclient import session as osc_session
from keystoneclient.v3 import client

REGIONS = ['inner', 'external']
if not config.disable_inner_high:
    REGIONS.append('inner_high')
USER = 'virtual.user'
PASSWORD = 'virtual.pass'

def get_database_conn():
    conn = pymysql.connect(
        host=config.security_db_host,
        port=int(config.security_db_port),
        user=config.security_db_user,
        passwd=config.security_db_passwd,
        db=config.security_db,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)
    return conn

def get_resource_url(ID, API):
    date = str(int(time.time()))
    sign_text = date + API + ID + USER + md5(PASSWORD)
    sign = md5(sign_text)
    res_url = API + ID + '?date=%s&sign=%s:%s' % (date, USER, sign)
    return res_url


def get_servers_all_regions(image_id=None, all_tenants=True):
    servers = []
    try:
        session, catalog = get_admin_session()
        token = session.get_token()
    except Exception as e:
        log.exception('Failed to get token from keystone: %s' % str(e))
        return []
    
    kwargs = {'headers': {}, 'params': {}}
    if all_tenants:
        kwargs['params']['all_tenants'] = True
    if image_id:
        kwargs['params']['image_id'] = image_id
    kwargs['headers']['X-Auth-Token'] = token
    kwargs['headers']['Content-Type'] = 'application/json'
    http = requests.Session()

    for region in REGIONS:
        nova_url = ''
        nova_catalog = [res for res in catalog
                        if res['type'] == 'compute'
                        and res['endpoints'][0]['region'] == region]
        for res in nova_catalog:
            for r in res['endpoints']:
                if r['interface'] == 'public':
                    nova_url = r['url']
                    break
        if not nova_url:
            return {'servers': {}}
        try:
            kwargs['headers']['X-Openstack-Region'] = region
            resp = http.request('GET', nova_url + \
                '/servers/detail', **kwargs)
            for server in resp.json()['servers']:
                servers.append(server)
        except Exception, e:
            log.error('Failed to get servers in region of %s' % region)
            continue
    if not servers:
        log.debug('There is no server fetched')
    return servers


def get_insert_sql(db_table, data):
    values = '('
    sql = 'INSERT INTO %s (' % db_table
    value_id = data.pop('id')
    for key in data.keys():
        sql +=  '%s, ' % key
        if isinstance(data[key], int):
            values += "%d, " % data[key]
        else:
            values += "'%s', " % data[key]
    values += "'%s')" % value_id
    sql += 'id) VALUE %s;' % values
    return sql


def get_update_sql(db_table, data):
    sql = 'UPDATE ' + db_table + ' SET '
    value_id = data.pop('id')
    for key in data.keys():
        if isinstance(data[key], int):
            sql += '%s=%d,' % (key, data[key])
        else:
            sql += '%s=\'%s\',' % (key, data[key])
    sql += 'id=\'%s\' WHERE id=\'%s\';' % (value_id, value_id)
    return sql


def get_ids_from_db(cursor, db_table):
    ids = []
    if not cursor or not db_table:
        return []
    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from %s;' % db_table
            result_num = cursor.execute(sql)
            for result in cursor:
                ids.append(result['id'])
    except Exception as e:
        log.error(e)
    return ids


def get_tenants_id_name_dict():
    id_name_dict = {}
    session, catalog = get_admin_session()
    token = session.get_token()
    url = config.os_auth_url + '/v3/projects'
    kwargs = {'headers': {}, 'params': {}}
    kwargs['headers']['X-Auth-Token'] = token
    kwargs['headers']['Content-Type'] = 'application/json'
    try:
        http = requests.Session()
        projects = http.request('GET', url, **kwargs).json()['projects']
    except Exception as e:
        log.error(e)
        return {}

    for project in projects:
        id_name_dict[project['id']] = project['name']
    return id_name_dict


def get_address(server):
    ip_addr_float = ''
    ip_addr_fixed = ''
    interfaces = server['addresses']
    for interface in interfaces:
        ports = interface
        for port in ports:
            if port.get('OS-EXT-IPS:type') == 'floating':
                ip_addr_float = port['addr']
                break
            else:
                ip_addr_fixed = port['addr']
        if ip_addr_float:
            return ip_addr_float
    else:
        return ip_addr_fixed


def md5(text):
    md5_instance = _md5.new()
    md5_instance.update(text)
    return md5_instance.hexdigest()


def get_admin_session():
    params_no_version = {
        'username': config.admin_user,
        'project_name': config.admin_project,
        'auth_url': config.os_auth_url,
        'user_domain_id': 'default',
        'tenant_name': config.admin_project,
        'password': config.admin_passwd,
        'project_domain_id': 'default'}

    request_session = requests.session()
    auth = auth_plugin.load_from_options(**params_no_version)
    session = osc_session.Session(
        auth=auth,
        session=request_session,
        verify=True)
    catalog = auth.get_auth_ref(session)['catalog']
    #ks = client.Client(session=session)
    return session, catalog
