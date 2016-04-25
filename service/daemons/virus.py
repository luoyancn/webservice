import time
import config
import threading
import requests
import pymysql
import log
import common_api as api


class daemon_virus(threading.Thread):
    def __init__(self, interval=300):
        threading.Thread.__init__(self)
        self.interval = interval
        self.thread_stop = False
        self.db_table_name = 'virus'
        self.timeout = (3, 9)
        self.image_id = config.virus_image_id
        self.API = '/api/virus/'

    #Overwrite run() method
    def run(self):
        while not self.thread_stop:
            try:
                #self.fetch_data()
                pass
            except Exception, e:
                log.error('Something wrong in running virus daemon')
                log.exception(e)
            time.sleep(self.interval)

    def stop(self):
        self.thread_stop = True

    def fetch_data(self):
        virus_servers = api.get_servers_all_regions(
            image_id=self.image_id)
        tenants_id_name_dict = api.get_tenants_id_name_dict()
        try:
            conn = api.get_database_conn()
            cursor = conn.cursor()
            current_virus_ids = api.get_ids_from_db(
                cursor, db_table=self.db_table_name)
        except Exception, e:
            log.error('Error occured while connecting to security db')
            return

        for virus_server in virus_servers:
            virus_id = virus_server['id']
            ip_addr = api.get_address(virus_server)
            tenant_id = virus_server['tenant_id']
            tenant_name = tenants_id_name_dict.get('tenant_id', '')
            data = {'id': virus_id,
                    'name': virus_server['name'],
                    'tenant_id': tenant_id,
                    'tenant_name': tenant_name,
                    'user_id': 'a5982c0ae54a4b9693b2f0f3cc630edf',
                    'user_name': config.admin_user,
                    'ip_address': ip_addr,
                    'region': server.get('region', '')}
            virus_port = config.virus_server_port
            uri = 'https://%s:%s' % (ip_addr, virus_port)

            try:
                data_virus = self.get_virus(virus_server['id'], uri)
            except Exception, e:
                log.error('Failed to fetch virus with id %s: %s' % (virus_id, str(e)))
                continue
            for key in data.keys():
                if key not in data_virus.keys():
                    continue
                data_virus.pop(key)
            data.update(data_virus)

            if virus_id in current_virus_ids:
                sql = api.get_update_sql(self.db_table_name, data)
            else:
                sql = api.get_insert_sql(self.db_table_name, data)
            try:
                cursor.execute(sql)
                log.info('Wrote virus with id %s to database successfully' % virus_id)
            except Exception as e:
                log.error('Failed to write virus with id %s to db: %s' % (virus_id, str(e)))

        cursor.close()
        conn.commit()
        conn.close()

    def get_virus(self, virus_id, uri):
        virus_url = api.get_resource_url(ID=virus_id, API=self.API)
        virus_url = uri + virus_url
        kwargs = {'headers': {}}
        kwargs['timeout'] = self.timeout
        content_type = 'application/json;charset=utf-8'
        kwargs['headers']['Content-Type'] = content_type
        https = requests.Session()
        https.verify = False
        resp = https.request('GET', virus_url, **kwargs)
        return resp.json()['virus']

    def get_virus_list(self, virus_id, uri):
        virus_url = api.get_resource_url(ID=virus_id, API=self.API)
        virus_url = uri + virus_url
        kwargs = {'headers': {}}
        kwargs['timeout'] = self.timeout
        content_type = 'application/json;charset=utf-8'
        kwargs['headers']['Content-Type'] = content_type
        https = requests.Session()
        https.verify = False
        resp = https.request('GET', virus_url, **kwargs)
        return resp.json()['virus']