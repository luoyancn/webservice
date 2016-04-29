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
        self.virus_port = config.daemon_server_port
        self.API = '/v1/virus'

    #Overwrite run() method
    def run(self):
        while not self.thread_stop:
            try:
                self.fetch_data()
            except Exception, e:
                log.error('Something wrong in running virus daemon: %r' % e)
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
        all_virus_data = []
        for virus_server in virus_servers:
            ip_addr = api.get_address(virus_server)
            tenant_id = virus_server['tenant_id']
            tenant_name = tenants_id_name_dict.get(tenant_id, '')
            data = {'server_id': virus_server['id'],
                    'tenant_id': tenant_id,
                    'tenant_name': tenant_name,
                    'user_id': 'a5982c0ae54a4b9693b2f0f3cc630edf',
                    'user_name': config.admin_user,
                    'ip_address': ip_addr,
                    'region': server.get('region', '')}
            
            num_once = 500
            num_total = 0
            len_response = 500
            error_occured = False
            data_virus = []
            date = str(int(time.time()))
            sign_text = date + self.API + api.USER + api.md5(api.PASSWORD)
            sign = api.USER + ':' + api.md5(sign_text)
            # Get virus list from current server
            while len_response == num_once and not error_occured:
                virus_port = self.virus_port
                virus_url = 'http://%s:%s%s?date=%s&sign=%s&from=%d&size=%d' \
                    % (ip_addr, virus_port, self.API, date, sign, num_total, num_once)
                try:
                    data_virus = self.get_virus_list(virus_url)
                    len_response = len(data_virus)
                    num_total += len_response
                    all_virus_data.extend(data_virus)
                except Exception, e:
                    error_occured = True
                    log.error('Failed to fetch virus list for server %s from %s: %r' \
                        % (virus_server['id'], ip_addr, e))
                    break
            if error_occured:
                continue

            for virus in data_virus:
                for key in data.keys():
                    if key not in virus.keys():
                        continue
                    virus.pop(key)
                virus.update(data_virus)
                if virus.get('upload'):
                    virus['upload'] = 1
                else:
                    virus['upload'] = 0
                if virus.get('download'):
                    virus['download'] = 1
                else:
                    virus['download'] = 0

                if virus['id'] in current_virus_ids:
                    sql = api.get_update_sql(self.db_table_name, data)
                else:
                    sql = api.get_insert_sql(self.db_table_name, data)
                try:
                    cursor.execute(sql)
                    log.info('Wrote virus of id %s to database successfully' % virus_id)
                except Exception as e:
                    log.error('Something wrong when execute sql: %s' % sql)
                    log.error('Failed to write virus with id %s to db: %s' % (virus_id, str(e)))

        cursor.close()
        conn.commit()
        conn.close()


    def get_virus_list(self, virus_url):
        kwargs = {'headers': {}}
        kwargs['timeout'] = self.timeout
        content_type = 'application/json;charset=utf-8'
        kwargs['headers']['Content-Type'] = content_type
        https = requests.Session()
        https.verify = False
        resp = https.request('GET', virus_url, **kwargs).json()
        if resp.get('result') == False:
            raise Exception(resp.get('errmsg', 'unknown error'))
        return resp['virus']


    def get_virus_by_id(self, virus_id, uri):
        virus_url = api.get_resource_url(ID=virus_id, API=self.API + '/')
        virus_url = uri + virus_url
        kwargs = {'headers': {}}
        kwargs['timeout'] = self.timeout
        content_type = 'application/json;charset=utf-8'
        kwargs['headers']['Content-Type'] = content_type
        https = requests.Session()
        https.verify = False
        resp = https.request('GET', virus_url, **kwargs).json()
        if resp.get('result') == False:
            raise Exception(resp.get('errmsg', 'unknown error'))
        return resp['virus']