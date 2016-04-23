import json
import pymysql
from flask import Blueprint

import log
import config
import request as httprequest
from keystone import commonfun, make_response

neutronmod = Blueprint('neutronmod', __name__)


@neutronmod.route('/v2.0/networks', methods=['GET'])
@neutronmod.route('/v2.0/networks/<resource_id>', methods=['GET'])
@commonfun
def network_resrc(auth, region, resource_id=None):
    res_url = get_url(auth, 'networks', resource_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/subnets', methods=['GET'])
@neutronmod.route('/v2.0/subnets/<resource_id>', methods=['GET'])
@commonfun
def subnet_resrc(auth, region, resource_id=None):
    res_url = get_url(auth, 'subnets', resource_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/ports', methods=['GET'])
@neutronmod.route('/v2.0/ports/<resource_id>', methods=['GET'])
@commonfun
def port_resrc(auth, region, resource_id=None):
    res_url = get_url(auth, 'ports', resource_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/routers', methods=['GET'])
@neutronmod.route('/v2.0/routers/<resource_id>', methods=['GET'])
@commonfun
def router_resrc(auth, region, resource_id=None):
    res_url = get_url(auth, 'routers', resource_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/security-groups', methods=['GET'])
@neutronmod.route('/v2.0/security-groups/<resource_id>',
                  methods=['GET'])
@commonfun
def security_group_resrc(auth, region, resource_id=None):
    res_url = get_url(auth, 'security-groups', resource_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/floatingips', methods=['GET'])
@neutronmod.route('/v2.0/floatingips/<resource_id>', methods=['GET'])
@commonfun
def floatingip_resrc(auth, region, resource_id=None):
    res_url = get_url(auth, 'floatingips', resource_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/lb/<sub_res>', methods=['GET'])
@neutronmod.route('/v2.0/lb/<sub_res>/<resource_id>', methods=['GET'])
@commonfun
def loadbalance_resrc(auth, region, sub_res, resource_id=None):
    res_url = get_url(auth, 'lb', sub_res, resource_id)
    try:
        resp = httprequest.httpclient(
            'GET', res_url, auth[0])
        log.info('RESP:' + str(resp.json()))
    except Exception as e:
        log(e)
        resp = {'code': 404, 'message': 'RESOURCE NOT FOUND'}
        return make_response(json.dumps(resp), 404)
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/fw/<sub_res>', methods=['GET'])
@neutronmod.route('/v2.0/fw/<sub_res>/<resource_id>', methods=['GET'])
@commonfun
def firewall_resrc(auth, region, sub_res, resource_id=None):
    sub_resources = ('firewall_policies',
                     'firewalls', 'firewall_rules')
    if sub_res not in sub_resources:
        resp = {'code': 404, 'message': 'RESOURCE NOT FOUND'}
        return make_response(json.dumps(resp), 404)

    res_url = get_url(auth, 'fw', sub_res, resource_id)
    try:
        resp = httprequest.httpclient(
            'GET', res_url, auth[0])
        log.info('RESP:' + str(resp.json()))
	if resp.status_code == 404:
	    raise Exception('RESOURCE NOT FOUND')
        return make_response(json.dumps(resp.json()),
                             resp.status_code)
    except Exception:
        if not resource_id:
            resp = firewall_default_data(sub_res, is_list=True)
        else:
            resp = firewall_default_data(sub_res, is_list=False)
        return make_response(json.dumps(resp), 200)


VPN_DB_TABLE_DICT = {'ikepolicies': 'vpn_ikes',
                     'ipsecpolicies': 'vpn_ipsecs',
                     'vpnservices': 'vpn_services',
                     'ipsec-site-connections': 'vpn_site_conns'}


@neutronmod.route('/v2.0/vpn/<sub_res>', methods=['GET'])
@commonfun
def vpn_res_list(auth, region, project_id, sub_res):
    vpn_resources = []
    sub_resources = {'vpnservices': 'vpnservices',
                     'ikepolicies': 'ikepolicies',
                     'ipsecpolicies': 'ipsecpolicies',
                     'ipsec-site-connections': 'ipsec_site_connections'}
    if sub_res not in sub_resources.keys():
        resp = {'code': 404, 'message': 'RESOURCE NOT FOUND'}
        return make_response(json.dumps(resp), 404)

    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + VPN_DB_TABLE_DICT[sub_res] + \
                ' where tenant_id=\'%s\'' % project_id
            result_num = cursor.execute(sql)
            for result in cursor:
                if sub_res in ['ikepolicies', 'ipsecpolicies']:
                    units = result.pop('lifetime_units')
                    value = result.pop('lifetime_value')
                    result['lifetime'] = {'units': units,
                                          'value': value}
                if sub_res == 'ipsec-site-connections':
                    action = result.pop('dpd_action')
                    interval = result.pop('dpd_interval')
                    timeout = result.pop('dpd_timeout')
                    result['dpd'] = {'action': action,
                                     'interval': interval,
                                     'timeout': timeout}
                    result['peer_cidrs'] = result['peer_cidrs'].split(',')
                vpn_resources.append(result)
    except Exception as e:
        message = 'Failed to get %s list: %r': % (sub_res, e)
        log.error(message)
        response = {'code': 500, 'message': message)}
        return make_response(json.dumps(response), 500)
    else:
        body = {sub_resources[sub_res]: vpn_resources}
        return make_response(json.dumps(body), 200)


@neutronmod.route('/v2.0/vpn/<sub_res>/<resource_id>', methods=['GET'])
@commonfun
def vpn_res_get(auth, region, project, sub_res, resource_id):
    vpn_resource = {}
    sub_resources = {'vpnservices': 'vpnservice',
                     'ikepolicies': 'ikepolicy',
                     'ipsecpolicies': 'ipsecpolicy',
                     'ipsec-site-connections': 'ipsec_site_connection'}
    if sub_res not in sub_resources.keys():
        resp = {'code': 404, 'message': 'RESOURCE NOT FOUND'}
        return make_response(json.dumps(resp), 404)
    if not verify_id(resource_id):
        message = 'Invalid %s id %s! Please check it.'\
            % (sub_res, resource_id)
        response = {'code': 401, 'message': message}
        return make_response(json.dumps(message), 401)

    try:
        conn = get_database_conn()
        with conn.cursor() as cursor:
            sql = 'select * from ' + VPN_DB_TABLE_DICT[sub_res] + \
                ' where id=\'%s\'' % resource_id
            result_num = cursor.execute(sql)
            if result_num == 1:
                result = cursor.fetchone()
                if sub_res in ['ikepolicies', 'ipsecpolicies']:
                    units = result.pop('lifetime_units')
                    value = result.pop('lifetime_value')
                    result['lifetime'] = {'units': units,
                                          'value': value}
                if sub_res == 'ipsec-site-connections':
                    action = result.pop('dpd_action')
                    interval = result.pop('dpd_interval')
                    timeout = result.pop('dpd_timeout')
                    result['dpd'] = {'action': action,
                                     'interval': interval,
                                     'timeout': timeout}
                    result['peer_cidrs'] = result['peer_cidrs'].split(',')
                vpn_resource = result
            elif result_num == 0:
                message = 'Unable to find ' + sub_res + \
                    ' with id ' + resource_id
                log.debug(message)
                response = {'code': 404, 'message': message}
                return make_response(json.dumps(message), 200)
            else:
                message = 'Unknown error.'
                log.error(message)
                response = {'code': 500, 'message': message}
                return make_response(json.dumps(message), 500)

    except Exception as e:
        message = 'Failed to get %s by id %s: %r:' \
            % (sub_res, resource_id, e)
        log.error(message)
        response = {'code': 500, 'message': message)}
        return make_response(json.dumps(response), 500)
    else:
        body = {sub_resources[sub_res]: vpn_resource}
        return make_response(json.dumps(body), 200)


def get_url(auth_list, resource_name,
            tenantid_or_subres=None,
            sub_res_tenant_id=None):
    neutron_url = auth_list[2][0]
    res_url = neutron_url + '/' + resource_name
    if tenantid_or_subres:
        res_url += '/' + tenantid_or_subres
        if sub_res_tenant_id:
            res_url += '/' + sub_res_tenant_id
    log.info('REQ BEGIN(neutron): ' + 'GET ' + res_url)
    return res_url


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


def firewall_default_data(sub_res, is_list):
    data = {}
    sub_resource = {'firewall_policies': 'firewall_policy',
                    'firewalls': 'firewall',
                    'firewall_rules': 'firewall_rule'}
    sub_resources = {'firewall_policies': 'firewall_policies',
                     'firewalls': 'firewalls',
                     'firewall_rules': 'firewall_rules'}

    data['firewall_policies'] = dict(name='', id='',
                                     tenant_id='', shared='',
                                     audited='', status='',
                                     description='',
                                     firewall_rules='')
    data['firewalls'] = dict(id='', admin_state_up='',
                             description='', name='',
                             tenant_id='', status='',
                             firewall_policy_id='')
    data['firewall_rules'] = dict(id='', firewall_policy_id='',
                                  tenant_id='', ip_version='',
                                  enabled='', protocol='',
                                  action='', description='',
                                  shared='', position='', name='',
                                  source_port='', source_ip_address='',
                                  destination_port='',
                                  destination_ip_address='')

    if is_list:
        return {sub_resource[sub_res]: [data[sub_res]]}
    else:
        return {sub_resources[sub_res]: data[sub_res]}
