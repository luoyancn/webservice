import copy
import json
import uuid
from flask import Blueprint
from flask import request as frequest
from werkzeug.exceptions import BadRequest

import request as httprequest
from service.openstack.keystone import commonfun
from service.openstack.keystone import make_response
import db
import log


workissuelogmod = Blueprint('workissuelogmod', __name__)

REQ_ITEM = ('tenant_id', 'user_id', 'title', 'content', 'status')

def decode_datetime(datetime_struct):
    if not datetime_struct:
        return ''
    else:
        return datetime_struct.strftime(
            '%Y-%m-%d %H:%M:%S')


@workissuelogmod.route('/v1/workissue/<workissue_id>', methods=['GET'])
@commonfun
def get_workissue(auth, region, workissue_id):
    conn = db.getWorkIssueConn()
    try:
        with conn.cursor() as cursor:
            sql = 'SELECT id, tenant_id, user_id, title,'\
                  ' content, status, user_email,'\
                  ' user_tel, created_time, response_time, fix_time'\
                  ' FROM workissue'\
                  ' WHERE region = %s and id = %s'
            cursor.execute(sql, (region, workissue_id))
            res = cursor.fetchone()
            copy_res = copy.deepcopy(res)
            if res:
                res['created_time'] = decode_datetime(
                    copy_res['created_time'])
                res['response_time'] = decode_datetime(
                    copy_res.get('response_time', ''))
                res['fix_time'] = decode_datetime(
                    copy_res.get('response_time', ''))
                result = {'workissue': res}
                return make_response(json.dumps(result), 200)
            else:
                msg = 'The workissue %s cannot be found' % workissue_id
                return make_response(msg, 404)
    except Exception as exc:
        log.error(exc)
        return make_response(json.dumps(exc.message), 500)
    finally:
        conn.close()


@workissuelogmod.route('/v1/workissue', methods=['POST'])
@commonfun
def create_workissue(auth, region):
    try:
        req_body = json.loads(frequest.data)['workissue']
    except KeyError as err:
        raise BadRequest(description='Invalid request body')
    except Exception as exc:
        log.error(exc)
    if not set(REQ_ITEM).issubset(set(req_body.keys())):
        msg = 'You should provide requried all params in (%s)' % ','.join(REQ_ITEM)
        raise BadRequest(description=msg)
    conn = db.getWorkIssueConn()
    try:
        uuid_str = str(uuid.uuid4())
        with conn.cursor() as cursor:
            sql = 'insert into workissue('\
                ' `id`,`tenant_id`, `user_id`, `title`, `content`,'\
                ' `status`, `user_email`, `user_tel`, `region`, `created_time`)'\
                ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, Now())'
            cursor.execute(sql, (uuid_str, req_body['tenant_id'],
                                 req_body['user_id'],
                                 req_body['title'], req_body['content'],
                                 req_body['status'], req_body.get('user_email', ''),
                                 req_body.get('user_tel', ''), region))
            conn.commit()
        result = {'workissue': {'id': uuid_str}}
        return make_response(json.dumps(result), 201)
    except Exception as exc:
        log.error(exc)
        return make_response(exc, 500)
    finally:
        conn.close()
