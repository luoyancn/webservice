import time
import config
import threading
import requests
import pymysql
import log
import common_api as api


class daemon_ips(threading.Thread):
    def __init__(self, interval=300):
        threading.Thread.__init__(self)
        self.interval = interval
        self.thread_stop = False
        self.db_table_name = 'ips'
        self.timeout = (3, 9)
        self.ips_server_port = config.daemon_server_port
        self.image_id = config.ips_image_id
        self.API = '/api/ips/'

    #Overwrite run() method
    def run(self):
        while not self.thread_stop:
            try:
                self.fetch_data()
            except Exception, e:
                log.error('Something wrong in running ips daemon: %r' % e)
            time.sleep(self.interval)

    def stop(self):
        self.thread_stop = True

    def fetch_data(self):
        ips_servers = api.get_servers_all_regions(
            image_id=self.image_id)
        tenants_id_name_dict = api.get_tenants_id_name_dict()
        conn = api.get_database_conn()
        try:
            conn = api.get_database_conn()
            cursor = conn.cursor()
            current_ips_ids = api.get_ids_from_db(
                cursor, db_table=self.db_table_name)
        except Exception, e:
            log.error('Error occured while connecting to security db')
            return
        for ips_server in ips_servers:
            ips_id = ips_server['id']
            ip_addr = api.get_address(ips_server)
            tenant_id = ips_server['tenant_id']
            tenant_name = tenants_id_name_dict.get(tenant_id, '')
            data = {'id': ips_id,
                    'name': ips_server['name'],
                    'tenant_id': tenant_id,
                    'tenant_name': tenant_name,
                    'user_id': 'a5982c0ae54a4b9693b2f0f3cc630edf',
                    'user_name': config.admin_user,
                    'ip_address': ip_addr,
                    'region': ips_server.get('region', '')}
            uri = 'http://%s:%s' % (ip_addr, self.ips_server_port)
            try:
                data_ips = self.get_ips(ips_server['id'], uri)
                protected_objects = data_ips['protected_object']
                protected_object_new = ''
                for protected_object in protected_objects:
                    protected_object_new += protected_object + ','
                data_ips['protected_object'] = protected_object_new[0:-1]
            except Exception, e:
                log.error('Failed to fetch ips with id %s: %r' % (ips_id, e))
                continue
            for key in data.keys():
                if key not in data_ips.keys():
                    continue
                data_ips.pop(key)
            data.update(data_ips)

            if ips_id in current_ips_ids:
                sql = api.get_update_sql(self.db_table_name, data)
            else:
                sql = api.get_insert_sql(self.db_table_name, data)
            try:
                cursor.execute(sql)
                log.info('Wrote ips of id %s to database successfully' % ips_id)
            except Exception as e:
                log.error('Something wrong when execute sql: %s' % sql)
                log.error('Failed to write ips with id %s to db: %r' % (ips_id, e))

        cursor.close()
        conn.commit()
        conn.close()

    def get_ips(self, ips_id, uri):
        ips_url = api.get_resource_url(ID=ips_id, API=self.API)
        ips_url = uri + ips_url
        kwargs = {'headers': {}}
        kwargs['timeout'] = self.timeout
        content_type = 'application/json;charset=utf-8'
        kwargs['headers']['Content-Type'] = content_type
        http = requests.Session()
        resp = http.request('GET', ips_url, **kwargs).json()
        if resp.get('result') == False:
            raise Exception(resp.get('errmsg', 'unknown error'))
        return resp['ips']