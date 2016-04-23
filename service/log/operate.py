import json
import log
import config
import pymysql
from flask import Blueprint

from service.openstack.keystone import commonfun
from service.openstack.keystone import make_response


logmod = Blueprint('logmod', __name__)

DB_TABLE_NAME_LOGS = 'logs'

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


@logmod.route('/v2.1/operation_log', methods=['GET'])
@commonfun
def get_logs(auth, region):
    operation_logs = []
    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + DB_TABLE_NAME_LOGS
            result_num = cursor.execute(sql)
            for result in cursor:
                create_time = result.pop('created_time')
                operate_time = result.pop('operate_time')
                result['created_time'] = str(create_time.isoformat())
                result['operate_time'] = str(operate_time.isoformat())
                operation_logs.append(result)
    except Exception as e:
        message = 'Failed to get logs : %r' % e
        log.error(message)
        response = {'code': 500, 'message': message)}
        return make_response(json.dumps(response), 500)
    else:
        body = {'operation_logs': operation_logs}
        return make_response(json.dumps(body), 200)
