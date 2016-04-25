import time
import threading
import requests
import pymysql

import log
import config
import common_api as api


class daemon_wafs(threading.Thread):
    def __init__(self, interval=300):
        threading.Thread.__init__(self)
        self.interval = interval
        self.thread_stop = False
        session, catalog = api.get_admin_session()
        self.session = session
        self.catalog = catalog
        self.db_table_name = 'wafs'
        #timeout = (connect_timeout, read_timeout)
        self.timeout = (3, 8)
        self.image_id = config.wafs_image_id
        self.API = '/api/wafs/'

    #Overwrite run() method
    def run(self):
        while not self.thread_stop:
            try:
                self.fetch_data()
                pass
            except Exception, e:
                log.error('Something wrong in running wafs daemon: %r' % e)
            time.sleep(self.interval)

    def stop(self):
        self.thread_stop = True

    def fetch_data(self):
        waf_servers = api.get_servers_all_regions(
            image_id=self.image_id)
        tenants_id_name_dict = api.get_tenants_id_name_dict()
        try:
            conn = api.get_database_conn()
            cursor = conn.cursor()
            current_wafs_ids = api.get_ids_from_db(
                cursor, db_table=self.db_table_name)
        except Exception, e:
            log.error('Error occured while connecting to security db')
            return
        for waf_server in waf_servers:
            if self.thread_stop:
                return
            waf_id = waf_server['id']
            tenant_id = waf_server['tenant_id']
            tenant_name = tenants_id_name_dict.get('tenant_id', '')
            ip_addr = api.get_address(waf_server)
            data = {'id': waf_id,
                    'name': waf_server['name'],
                    'tenant_id': tenant_id,
                    'tenant_name': tenant_name,
                    'user_id': 'a5982c0ae54a4b9693b2f0f3cc630edf',
                    'user_name': config.admin_user,
                    'ip_address': ip_addr}
            wafs_port = config.wafs_server_port
            uri = 'http://%s:%s' % (ip_addr, wafs_port)

            try:
                data_waf = self.get_waf(waf_server['id'], uri)
            except Exception, e:
                log.error('Failed to fetch waf with id %s: %r' % (waf_id, e))
                continue
            for key in data.keys():
                if key not in data_waf.keys():
                    continue
                data_waf.pop(key)
            data.update(data_waf)

            if waf_id in current_wafs_ids:
                sql = api.get_update_sql(self.db_table_name, data)
            else:
                sql = api.get_insert_sql(self.db_table_name, data)
            try:
                cursor.execute(sql)
                log.info('Wrote waf of id %s to database successfully' % waf_id)
            except Exception as e:
                log.error('Failed to write waf with id %s to db: %r' % (waf_id, e))

        cursor.close()
        conn.commit()
        conn.close()

    def get_waf(self, waf_id, uri):
        waf_url = api.get_resource_url(ID=waf_id, API=self.API)
        waf_url = uri + waf_url
        kwargs = {'headers': {}}
        kwargs['timeout'] = self.timeout
        content_type = 'application/json;charset=utf-8'
        kwargs['headers']['Content-Type'] = content_type
        http = requests.Session()
        resp = http.request('GET', waf_url, **kwargs)
        return resp.json()['wafs']
