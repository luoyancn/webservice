import time
import threading
import requests
import pymysql

import log
import config
import common_api as api


class daemon_vpns(threading.Thread):
    def __init__(self, interval=300):
        threading.Thread.__init__(self)
        self.interval = interval
        self.thread_stop = False
        session, catalog = api.get_admin_session()
        self.session = session
        self.catalog = catalog
        self.db_table_name = 'vpns'
        #timeout = (connect_timeout, read_timeout)
        self.timeout = (3, 8)
        self.image_id = config.vpn_image_id
        self.vpn_server_port = config.daemon_server_port
        self.VPN_SERVICE_API = '/api/vpn/ipsecservice/'

    #Overwrite run() method
    def run(self):
        while not self.thread_stop:
            try:
                self.fetch_data()
            except Exception, e:
                log.error('Something wrong in running vpns daemon: %r' % e)
            time.sleep(self.interval)

    def stop(self):
        self.thread_stop = True

    def fetch_data(self):
        vpn_servers = api.get_servers_all_regions(
            image_id=self.image_id)
        tenants_id_name_dict = api.get_tenants_id_name_dict()
        try:
            conn = api.get_database_conn()
            cursor = conn.cursor()
            current_vpns_ids = api.get_ids_from_db(
                cursor, db_table=self.db_table_name)
        except Exception, e:
            log.error('Error occured while connecting to security db')
            return
        for vpn_server in vpn_servers:
            if self.thread_stop:
                return
            vpn_id = vpn_server['id']
            tenant_id = vpn_server['tenant_id']
            tenant_name = tenants_id_name_dict.get(tenant_id, '')
            ip_addr = api.get_address(vpn_server)
            data = {'id': vpn_id,
                    'name': vpn_server['name'],
                    'tenant_id': tenant_id,
                    'tenant_name': tenant_name,
                    'user_id': 'a5982c0ae54a4b9693b2f0f3cc630edf',
                    'user_name': config.admin_user,
                    'ip_address': ip_addr,
                    'region': server.get('region', '')}
            uri = 'http://%s:%s' % (ip_addr, self.vpn_server_port)

            try:
                data_vpn = self.get_vpn_service(vpn_server['id'], uri)
            except Exception, e:
                log.error('Failed to fetch vpn with id %s: %r' % (vpn_id, e))
                continue
            for key in data.keys():
                if key not in data_vpn.keys():
                    continue
                data_vpn.pop(key)
            data.update(data_vpn)

            ike_policies = get_ike_list(uri)
            ipsec_policies = get_ipsec_list(uri)
            vpn_site_conns = get_site_conns_by_vpn_service(uri, vpn_id)

            if vpn_id in current_vpns_ids:
                sql = api.get_update_sql(self.db_table_name, data)
            else:
                sql = api.get_insert_sql(self.db_table_name, data)
            try:
                cursor.execute(sql)
                log.info('Wrote vpn of id %s to database successfully' % vpn_id)
            except Exception as e:
                log.error('Something wrong when execute sql: %s' % sql)
                log.error('Failed to write vpn with id %s to db: %r' % (vpn_id, e))

        cursor.close()
        conn.commit()
        conn.close()

    def get_vpn_service(self, vpn_id, uri):
        vpn_url = get_resource_url(ID=vpn_id, API=self.VPN_SERVICE_API)
        vpn_url = uri + vpn_url
        kwargs = {'headers': {}}
        kwargs['timeout'] = self.timeout
        content_type = 'application/json;charset=utf-8'
        kwargs['headers']['Content-Type'] = content_type
        http = requests.Session()
        resp = http.request('GET', vpn_url, **kwargs).json()
        if resp.get('result') == False:
            raise Exception(resp.get('errmsg', 'unknown error'))
        return resp['ipsecservice']


def get_resource_url(ID, API):
    USER = api.USER
    PASSWORD = api.PASSWORD
    date = str(int(time.time()))
    sign_text = date + API + USER + api.md5(PASSWORD)
    sign = api.md5(sign_text)
    res_url = API + '?id=%sdate=%s&sign=%s:%s' % (ID, date, USER, sign)
    return res_url
