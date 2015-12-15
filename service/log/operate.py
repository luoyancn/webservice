import json
from flask import Blueprint

import request as httprequest
from service.openstack.keystone import commonfun
from service.openstack.keystone import make_response


logmod = Blueprint('logmod', __name__)


@logmod.route('/v2.1/operation_log', methods=['GET'])
@commonfun
def get_logs(auth, region):
    body = {'operation_logs':[]}
    return make_response(json.dumps(body), 200)
