import json
from flask import Blueprint

import request as httprequest
from service.openstack.keystone import commonfun
from service.openstack.keystone import make_response


logmod = Blueprint('logmod', __name__)


@logmod.route('/v2.1/operation_log', methods=['GET'])
@commonfun
def get_logs(auth, region):
    _log = {'tenant_id': '',
            'user_id': '',
            'id': '',
            'action': '',
            'object': '',
            'msg': '',
            'level': 'info',
            'run_time': '',
            'created_time': '',
            'operator': 'admin',
            'operator_ip': '127.0.0.1',
            'operate_result': 'success'}

    body = {'operation_logs':[_log]}
    return make_response(json.dumps(body), 200)
