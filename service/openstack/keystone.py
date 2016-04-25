import json
import requests
from flask import Blueprint
from keystoneclient.auth.identity.generic.password\
    import Password as auth_plugin
from keystoneclient import session as osc_session
from keystoneclient.v3 import client
from functools import wraps
import keystoneauth1

import log
import config
import request as httprequest
import flask
from flask import request as frequest
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound


keystonemod = Blueprint('keystonemod', __name__)


def _get_admin_context():
    params_no_version = {
        'username': config.admin_user,
        'project_name': config.admin_project,
        'auth_url': config.os_auth_url,
        'user_domain_id': 'default',
        'tenant_name': config.admin_project,
        'password': config.admin_passwd,
        'project_domain_id': 'default'}

    request_session = requests.session()

    auth = auth_plugin.load_from_options(**params_no_version)
    session = osc_session.Session(
        auth=auth,
        session=request_session,
        verify=True)
    ks = client.Client(session=session)
    return ks


def _get_user_info(user_id):
    ks = _get_admin_context()
    user = ks.users.get(user_id)
    return user.name, user.default_project_id


def check_project(project_id):
    ks = _get_admin_context()
    try:
        ks.projects.get(project_id)
    except Exception:
        msg = 'Project %s cannot be found' % project_id
        raise NotFound(description=msg)


def login(username, project_id, password, region):
    params_no_version = {
        'username': username, 'project_id': project_id,
        'auth_url': config.os_auth_url,
        'user_domain_id': 'default',
        'tenant_name': project_id, 'password': password,
        'project_domain_id': 'default'}

    request_session = requests.session()

    auth = auth_plugin.load_from_options(**params_no_version)
    session = osc_session.Session(
        auth=auth,
        session=request_session,
        verify=True)
    catalog = auth.get_auth_ref(session)['catalog']
    nova_catalog = [res for res in catalog
                    if res['type'] == 'compute'
                    and res['endpoints'][0]['region'] == region]
    neutron_catalog = [res for res in catalog
                       if res['type'] == 'network'
                       and res['endpoints'][0]['region'] == region]
    cinder_catalog = [res for res in catalog
                      if res['type'] == 'volumev2'
                      and res['endpoints'][0]['region'] == region]

    glance_catalog = [res for res in catalog
                      if res['type'] == 'image'
                      and res['endpoints'][0]['region'] == region]

    final_nova_catalog = []
    for res in nova_catalog:
        for r in res['endpoints']:
            if r['interface'] == 'public':
                final_nova_catalog.append(r['url'])

    final_neutron_catalog = []
    for res in neutron_catalog:
        for r in res['endpoints']:
            if r['interface'] == 'public':
                final_neutron_catalog.append(r['url'] + '/v2.0')

    final_cinder_catalog = []
    for res in cinder_catalog:
        for r in res['endpoints']:
            if r['interface'] == 'public':
                final_cinder_catalog.append(r['url'])

    final_glance_catalog = []
    for res in glance_catalog:
        for r in res['endpoints']:
            if r['interface'] == 'public':
                final_glance_catalog.append(r['url'])

    return (session.get_token(), final_nova_catalog,
            final_neutron_catalog, final_cinder_catalog,
            final_glance_catalog)


def commonfun(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        log.info('@' * 50)
        log.info('The request headers are follows: %r ' % frequest.headers)
        log.info('The request params are follows: %r' % frequest.args)
        log.info('The request body is follows: %r' % frequest.data)
        log.info('The request url is follows: %s %r' % (frequest.method, frequest.url))
        log.info('The request remote is follows: %r' % frequest.remote_addr)
        log.info('The request values are follows: %r' % frequest.values)
        log.info('@' * 50)

        content_type = frequest.headers.get('Content-Type', None)
        if 'application/json' not in content_type:
            msg = 'Please make sure the request Content-Type '\
                  'is application/json'
            raise BadRequest(description=msg)
        try:
            user_id = frequest.headers['userid']
            password = frequest.headers['password']
            region = frequest.headers['region']
            username = frequest.headers['username']
        except KeyError:
            msg = 'userid, username, password and region must be provided'
            raise BadRequest(description=msg)

        if config.disable_inner_high and region == 'inner_high':
            response = {"message": "Note: inner_high is disabled!"}
            return make_response(json.dumps(response), 200)

        try:
            user, project = _get_user_info(user_id)
        except AttributeError:
            msg = 'Invalid user %s: missing default_project_id' % user_id
            raise BadRequest(description=msg)
        except Exception as exc:
            raise BadRequest(description=exc.message)
        try:
            if username == config.shadow_user_name:
                auth = login(config.admin_user, config.admin_project_id,
                             config.admin_passwd, region)
            else:
                auth = login(user, project, password, region)
        except keystoneauth1.exceptions.http.Unauthorized as exc:
            return make_response(json.dumps(exc.message), 401)
        except Exception as base_exc:
            raise base_exc

        security_api = ['/wafs', '/ips', '/virus', '/vpn', '/fw']
        security_api.append('/physical_devices')
        for api in security_api:
            if api in frequest.path:
                return func(auth, region, project, *args, **kwargs)

        try:
            return func(auth, region, *args, **kwargs)
        except TypeError:
            return func(*args, **kwargs)
    return wrap


def make_response(json_response, statu_code):
    return flask.make_response(
        flask.Response(json_response,
                       headers={'Content-Type':
                                'application/json'}),
        statu_code)


@keystonemod.route('/v3/services')
@commonfun
def get_service(auth, region):

    resp = httprequest.httpclient(
        'GET', config.os_auth_url + '/v3/services', auth[0])
    return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/resources')
@commonfun
def get_resources(auth, region):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    resp = httprequest.httpclient(
        'GET', config.os_auth_url + '/v3/resources',
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/projects', methods=['POST'])
@commonfun
def create_project(auth, region):
    try:
        json_body = json.loads(frequest.data)
        if not json_body.get('project'):
            msg = 'Bad request data in creating v3 project: %r' % frequest.data
            log.error(msg)
            resp = {'code': 400, 'message': msg}
            return make_response(json.dumps(resp), 400)
        kwargs = {'json': json_body}
        resp = httprequest.httpclient(
            'POST', config.os_auth_url + '/v3/projects',
            auth[0], kwargs=kwargs)
    except Exception as e:
        message = 'Failed to create project: %r' % e
        log.error(message)
        resp = {'code': 500, 'messeage': message}
        return make_response(json.dumps(resp), 500)

    return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/projects/<project_id>', methods=['PATCH'])
@commonfun
def update_project(auth, region, project_id):
    try:
        json_body = json.loads(frequest.data)
        if not json_body.get('project'):
            msg = 'Bad request data in update v3 project: %r' % frequest.data
            log.error(msg)
            resp = {'code': 400, 'message': msg}
            return make_response(json.dumps(resp), 400)
        kwargs = {'json': json_body}
        resp = httprequest.httpclient(
            'PATCH', config.os_auth_url + '/v3/projects/%s' % project_id,
            auth[0], kwargs=kwargs)
    except Exception as e:
        message = 'Failed to update project: %r' % e
        log.error(message)
        resp = {'code': 500, 'messeage': message}
        return make_response(json.dumps(resp), 500)

    return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/projects/<project_id>', methods=['DELETE'])
@commonfun
def delete_project(auth, region, project_id):
    resp = httprequest.httpclient(
        'DELETE', config.os_auth_url + '/v3/projects/%s' % project_id,
        auth[0])
    if resp.status_code == 204:
        return make_response('', resp.status_code)
    else:
        return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/projects/<project_id>', methods=['GET'])
@commonfun
def get_project(auth, region, project_id):
    resp = httprequest.httpclient(
        'GET', config.os_auth_url + '/v3/projects/%s' % project_id,
        auth[0])
    return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/users', methods=['POST'])
@commonfun
def create_user(auth, region):
    try:
        json_body = json.loads(frequest.data)
        if not json_body.get('user'):
            msg = 'Bad request data in creating v3 user: %r' % frequest.data
            log.error(msg)
            resp = {'code': 400, 'message': msg}
            return make_response(json.dumps(resp), 400)
        if 'default_project_id' not in json_body['user']:
            msg = 'default_project_id is needed when create user'
            raise BadRequest(description=msg)
        kwargs = {'json': json_body}
        resp = httprequest.httpclient(
            'POST', config.os_auth_url + '/v3/users',
            auth[0], kwargs=kwargs)
        resp_json = resp.json()
        if resp.status_code < 300:
            assignment_resp = httprequest.httpclient(
                'PUT', config.os_auth_url +
                '/v3/projects/%s/users/%s/roles/%s' % (
                    json_body['user']['default_project_id'],
                    resp_json['user']['id'], config.member_role_id),
                auth[0])
            if assignment_resp.status_code > 300:
                resp = httprequest.httpclient(
                    'DELETE', config.os_auth_url +
                    '/v3/users/%s' % resp_json['user']['id'],
                    auth[0])
                msg = 'Fail to create user'
                raise BadRequest(description=msg)
    except Exception as e:
        message = 'Failed to create v3 user: %r' % e
        log.error(message)
        resp = {'code': 500, 'messeage': message}
        return make_response(json.dumps(resp), 500)

    return make_response(json.dumps(resp_json), resp.status_code)


@keystonemod.route('/v3/users/<user_id>', methods=['PATCH'])
@commonfun
def update_user(auth, region, user_id):
    try:
        json_body = json.loads(frequest.data)
        if not json_body.get('user'):
            msg = 'Wrong request data in update v3 user: %r' % frequest.data
            log.error(msg)
            resp = {'code': 400, 'message': msg}
            return make_response(json.dumps(resp), 400)
        kwargs = {'json': json_body}
        resp = httprequest.httpclient(
            'PATCH', config.os_auth_url + '/v3/users/%s' % user_id,
            auth[0], kwargs=kwargs)
    except Exception as e:
        message = 'Failed to update v3 user: %r' % e
        log.error(message)
        resp = {'code': 500, 'messeage': message}
        return make_response(json.dumps(resp), 500)

    return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/users/<user_id>', methods=['GET'])
@commonfun
def get_user(auth, region, user_id):
    resp = httprequest.httpclient(
        'GET', config.os_auth_url + '/v3/users/%s' % user_id,
        auth[0])
    return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/users/<user_id>', methods=['DELETE'])
@commonfun
def delete_user(auth, region, user_id):
    resp = httprequest.httpclient(
        'DELETE', config.os_auth_url + '/v3/users/%s' % user_id,
        auth[0])
    if resp.status_code == 204:
        return make_response('', resp.status_code)
    else:
        return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/v3/<project_id>/quotas', methods=['GET'])
@commonfun
def get_quotas(auth, region, project_id):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    resp = httprequest.httpclient(
        'GET', config.os_auth_url + '/v3/%s/quotas' % project_id,
        auth[0], kwargs=kwargs)
    resp_json = resp.json()
    if resp.status_code < 300:
        resp_json['quota'].update(
            {'wafs': 0, 'ips': 0, 'anti_virus': 0,
             'wafs_used': 0, 'ips_used': 0, 'anti_virus': 0})
    return make_response(json.dumps(resp_json), resp.status_code)


@keystonemod.route('/v3/<project_id>/quotas', methods=['PUT'])
@commonfun
def update_quotas(auth, region, project_id):
    json_body = json.loads(frequest.data)
    kwargs = {'headers': {'X-Openstack-Region': region}}
    kwargs['json'] = json_body
    resp = httprequest.httpclient(
        'PUT', config.os_auth_url + '/v3/%s/quotas' % project_id,
        auth[0], kwargs=kwargs)
    if resp.status_code == 204:
        return make_response('', resp.status_code)
    else:
        return make_response(json.dumps(resp.json()), resp.status_code)


@keystonemod.route('/icp/url', methods=['GET'])
@commonfun
def sso_login(auth, region):
    url = config.sso_login + '?token=%s&region=%s' % (auth[0], region)
    result = {'url': url}
    return make_response(json.dumps(result), 200)
