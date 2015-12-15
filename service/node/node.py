import json
from flask import Blueprint

import request as httprequest
from service.openstack.keystone import commonfun
from service.openstack.keystone import make_response
import db
import log

nodemod = Blueprint('node', __name__)


@nodemod.route('/v1/host', methods=['GET'])
@commonfun
def get_hosts(auth, region):
    result = {'hosts': []}
    conn = db.getDevicesConn()
    host_sql = 'SELECT t1.id, t1.os_name,t1.hostname,'\
               ' t1.description, t1.ip_address, t1.hypervisor,'\
               ' t1.model, t1.vendor, t1.cpu_count, t1.cpu_model,'\
	       ' t1.cpu_frequence, t1.cpu_socket, t1.cpu_core,'\
               ' t1.memory_size '\
	       ' FROM Host t1'\
               ' WHERE t1.regionname=%s'

    tmp_disk_sql = 'SELECT t1.name,'\
                   ' t1.capacity'\
                   ' FROM Disk t1 WHERE t1.host_id = %s'

    tmp_nic_sql = 'SELECT t1.name,'\
                  ' t1.description,'\
                  ' t1.status,'\
                  ' t1.mac_address'\
                  ' FROM Port t1 WHERE t1.host_id = %s'
    try:
        with conn.cursor() as cursor:
            cursor.execute(host_sql, (region,))
            res = cursor.fetchall()
            for r in res:
                nics = []
                disks = []
                with conn.cursor() as nic_cursor:
                    nic_cursor.execute(tmp_nic_sql, (r['id'],))
                    nic_res = nic_cursor.fetchall()
                    for nic in nic_res:
                        nics.append(nic)
                    r['nics'] = nics

                with conn.cursor() as disk_cursor:
                    disk_cursor.execute(tmp_disk_sql, (r['id'],))
                    disk_res = disk_cursor.fetchall()
                    for disk in disk_res:
                        disks.append(disk)
                    r['disks'] = disks
                result['hosts'].append(r)
    except Exception as exc:
        log.error(exc)
        return make_response(json.dumps(exc.message), 500)
    finally:
        conn.close()
    return make_response(json.dumps(result), 200)


@nodemod.route('/v1/storage_device', methods=['GET'])
@commonfun
def get_storages(auth, region):
    result = {'storage_device': []}
    conn = db.getDevicesConn()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM Storage where regionname=%s"
            cursor.execute(sql, (region,))
            res = cursor.fetchall()
            for r in res:
                tmp = {}
                tmp['id'] = r['id']
                tmp['name'] = r['name']
                tmp['description'] = r.get('description', '')
                tmp['model'] = r.get('model', '')
                tmp['vendor'] = r.get('vendor', '')
                tmp['device_type'] = r.get('device_type', '')
                tmp['capacity'] = r.get('capacity', '')
                tmp['mac_address'] = r.get('mac_address', '')
                tmp['ip_address'] = r.get('ip_address', '')
                result['storage_device'].append(tmp)
    except Exception as exc:
        log.error(exc)
        return make_response(json.dumps(exc.message), 500)
    finally:
        conn.close()
    return make_response(json.dumps(result), 200)


@nodemod.route('/v1/network_device', methods=['GET'])
@commonfun
def get_networks(auth, region):
    result = {'network_device': []}
    conn = db.getDevicesConn()
    try:
        with conn.cursor() as cursor:
            sql = 'SELECT id, name, description, model,'\
                  ' vendor, device_type, port_num,'\
                  ' total_ram FROM Network'\
                  ' WHERE regionname = %s'
            cursor.execute(sql, (region,))
            res = cursor.fetchall()
            for r in res:
                result['network_device'].append(r)
    except Exception as exc:
        log.error(exc)
        return make_response(json.dumps(exc.message), 500)
    finally:
        conn.close()
    return make_response(json.dumps(result), 200)
