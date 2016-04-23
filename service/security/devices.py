import json
import pymysql
import log
import config
from flask import Blueprint

from service.openstack.keystone import commonfun
from service.openstack.keystone import make_response


devicemod = Blueprint('devicemod', __name__)

TABLE_NAME_WAFS = 'wafs'
TABLE_NAME_IPS = 'ips'
TABLE_NAME_VIRUS = 'virus'
TABLE_NAME_PHYSICAL_DEVICES = 'physical_devices'


def get_database_conn():
    conn = pymysql.connect(
        host=config.security_db_host,
        port=config.security_db_port,
        user=config.security_db_user,
        passwd=config.security_db_passwd,
        db=config.security_db,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)
    return conn


@devicemod.route('/v1/wafs', methods=['GET'])
@commonfun
def list_wafs(auth, region, project_id):
    wafs = []
    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_WAFS + \
                ' where tenant_id=\'' + project_id + '\''
            result_num = cursor.execute(sql)
            for result in cursor:
                wafs.append(result)
    except Exception as e:
        log.error(e)
        response = {'code': 500, 'message': str(e)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'wafs': wafs}
        return make_response(json.dumps(body), 200)

 
@devicemod.route('/v1/wafs/<wafs_id>', methods=['GET'])
@commonfun
def get_waf(auth, region, project_id, wafs_id): 
    wafs = {}
    if not verify_id(wafs_id):
        message = 'Invalid wafs id! Please check it.'
        response = {'code': 403, 'message': message}
        return make_response(json.dumps(response), 403)

    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_WAFS + \
                ' where id=\'' + wafs_id + '\''
            result_num = cursor.execute(sql)
            if result_num == 1:
                wafs = cursor.fetchone()
            elif result_num == 0:
                message = 'Unable to find ips with id ' + wafs_id
                log.debug(message)
                response = {'code': 404, 'message': message}
                return make_response(json.dumps(message), 200)
            else:
                message = 'Unknown error.'
                log.error(message)
                response = {'code': 500, 'message': message}
                return make_response(json.dumps(message), 500)

    except Exception as e:
        log.error(e)
        error_message = str(e)
        return make_response(json.dumps(body), 500)
    else:
        body = {'wafs': wafs}
        return make_response(json.dumps(body), 200)


@devicemod.route('/v1/ips', methods=['GET'])
@commonfun
def list_ips(auth, region, project_id):
    ips = []
    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_IPS + \
                ' where tenant_id=\'' + project_id + '\''
            result_num = cursor.execute(sql)
            for result in cursor:
                ips.append(result)
    except Exception as e:
        log.error(e)
        response = {'code': 500, 'message': str(e)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'ips': ips}
        return make_response(json.dumps(body), 200)


@devicemod.route('/v1/ips/<ips_id>', methods=['GET'])
@commonfun
def get_ips(auth, region, project_id, ips_id):
    ips = {}
    if not verify_id(ips_id):
        message = 'Invalid ips id! Please check it.'
        response = {'code': 403, 'message': message}
        return make_response(json.dumps(response), 403)

    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_IPS + \
                ' where id=\'' + ips_id + '\''
            result_num = cursor.execute(sql)
            if result_num == 1:
                ips = cursor.fetchone()
            elif result_num == 0:
                message = 'Unable to find ips with id ' + ips_id
                log.debug(message)
                response = {'code': 404, 'message': message}
                return make_response(json.dumps(message), 200)
            else:
                message = 'Unknown error.'
                log.error(message)
                response = {'code': 500, 'message': message}
                return make_response(json.dumps(message), 500)

    except Exception as e:
        log.error(e)
        response = {'code': 500, 'message': str(e)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'ips': ips}
        return make_response(json.dumps(body), 200)


@devicemod.route('/v1/virus', methods=['GET'])
@commonfun
def list_virus(auth, region, project_id):
    virus = []
    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_VIRUS + \
                ' where tenant_id=\'' + project_id + '\''
            result_num = cursor.execute(sql)
            for result in cursor:
                virus.append(result)
    except Exception as e:
        log.error(e)
        response = {'code': 500, 'message': str(e)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'virus': virus}
        return make_response(json.dumps(body), 200)


@devicemod.route('/v1/virus/<virus_id>', methods=['GET'])
@commonfun
def get_virus(auth, region, project_id, virus_id):
    virus = {}
    if not verify_id(virus_id):
        message = 'Invalid virus id! Please check it.'
        response = {'code': 403, 'message': message}
        return make_response(json.dumps(response), 403)

    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_VIRUS + \
                ' where id=\'' + virus_id + '\''
            result_num = cursor.execute(sql)
            if result_num == 1:
                virus = cursor.fetchone()
            elif result_num == 0:
                message = 'Unable to find virus with id ' + virus_id
                log.debug(message)
                response = {'code': 404, 'message': message}
                return make_response(json.dumps(message), 200)
            else:
                message = 'Unknown error.'
                log.error(message)
                response = {'code': 500, 'message': message}
                return make_response(json.dumps(message), 500)

    except Exception as e:
        log.error(e)
        response = {'code': 500, 'message': str(e)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'virus': virus}
        return make_response(json.dumps(body), 200)


@devicemod.route('/v1/security/physical_devices', methods=['GET'])
@commonfun
def list_devices(auth, region, project_id):
    physical_devices = []
 
    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_PHYSICAL_DEVICES + \
                ' where tenant_id=\'' + project_id + '\''
            result_num = cursor.execute(sql)
            for result in cursor:
                physical_devices.append(result)
    except Exception as e:
        log.error(e)
        response = {'code': 500, 'message': str(e)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'physical_devices': physical_devices}
        return make_response(json.dumps(body), 200)


@devicemod.route('/v1/security/physical_devices/<device_id>', methods=['GET'])
@commonfun
def get_devices(auth, region, project_id, device_id):
    physical_devices = {}
    if not verify_id(device_id):
        message = 'Invalid device_id! Please check it.'
        response = {'code': 403, 'message': message}
        return make_response(json.dumps(response), 403)

    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + TABLE_NAME_PHYSICAL_DEVICES + \
                ' where id=\'' + device_id + '\''
            result_num = cursor.execute(sql)
            if result_num == 1:
                physical_devices = cursor.fetchone()
            elif result_num == 0:
                message = 'Unable to find physical device with id ' + device_id
                log.debug(message)
                response = {'code': 404, 'message': message}
                return make_response(json.dumps(message), 200)
            else:
                message = 'Unknown error.'
                log.error(message)
                response = {'code': 500, 'message': message}
                return make_response(json.dumps(message), 500)

    except Exception as e:
        log.error(e)
        response = {'code': 500, 'message': str(e)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'physical_devices': physical_devices}
        return make_response(json.dumps(body), 200)


def verify_id(resource_id):
    for char in resource_id:
        if char <= 9 and char >= 0 or char == '-':
            continue
        elif char.lower() <= 'z' and char.lower() >= 'a':
            continue
        else:
            break
    else:
        return True
    return False
