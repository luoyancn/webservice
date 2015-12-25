import json
from flask import Blueprint

import log
import request as httprequest
from keystone import commonfun, make_response

neutronmod = Blueprint('neutronmod', __name__)


@neutronmod.route('/v2.0/networks', methods=['GET'])
@neutronmod.route('/v2.0/networks/<tenant_id>', methods=['GET'])
@commonfun
def network_resrc(auth, region, tenant_id=None):
    res_url = get_url(auth, 'networks', tenant_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/subnets', methods=['GET'])
@neutronmod.route('/v2.0/subnets/<tenant_id>', methods=['GET'])
@commonfun
def subnet_resrc(auth, region, tenant_id=None):
    res_url = get_url(auth, 'subnets', tenant_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/ports', methods=['GET'])
@neutronmod.route('/v2.0/ports/<tenant_id>', methods=['GET'])
@commonfun
def port_resrc(auth, region, tenant_id=None):
    res_url = get_url(auth, 'ports', tenant_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/routers', methods=['GET'])
@neutronmod.route('/v2.0/routers/<tenant_id>', methods=['GET'])
@commonfun
def router_resrc(auth, region, tenant_id=None):
    res_url = get_url(auth, 'routers', tenant_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/security-groups', methods=['GET'])
@neutronmod.route('/v2.0/security-groups/<tenant_id>',
                  methods=['GET'])
@commonfun
def security_group_resrc(auth, region, tenant_id=None):
    res_url = get_url(auth, 'security-groups', tenant_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/floatingips', methods=['GET'])
@neutronmod.route('/v2.0/floatingips/<tenant_id>', methods=['GET'])
@commonfun
def floatingip_resrc(auth, region, tenant_id=None):
    res_url = get_url(auth, 'floatingips', tenant_id)
    resp = httprequest.httpclient(
        'GET', res_url, auth[0])
    log.info('RESP:' + str(resp.json()))
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/lb/<sub_res>', methods=['GET'])
@neutronmod.route('/v2.0/lb/<sub_res>/<tenant_id>', methods=['GET'])
@commonfun
def loadbalance_resrc(auth, region, sub_res, tenant_id=None):
    res_url = get_url(auth, 'lb', sub_res, tenant_id)
    try:
        resp = httprequest.httpclient(
            'GET', res_url, auth[0])
        log.info('RESP:' + str(resp.json()))
    except Exception:
        resp = {'code': 404, 'message': 'RESOURCE NOT FOUND'}
        return make_response(str(resp), 404)
    return make_response(json.dumps(resp.json()),
                         resp.status_code)


@neutronmod.route('/v2.0/fw/<sub_res>', methods=['GET'])
@neutronmod.route('/v2.0/fw/<sub_res>/<tenant_id>', methods=['GET'])
@commonfun
def firewall_resrc(auth, region, sub_res, tenant_id=None):
    sub_resources = ('firewall_policies',
                     'firewalls', 'firewall_rules')
    if sub_res not in sub_resources:
        resp = {'code': 404, 'message': 'RESOURCE NOT FOUND'}
        return make_response(str(resp), 404)

    res_url = get_url(auth, 'fw', sub_res, tenant_id)
    try:
        resp = httprequest.httpclient(
            'GET', res_url, auth[0])
        log.info('RESP:' + str(resp.json()))
        return make_response(json.dumps(resp.json()),
                             resp.status_code)
    except Exception:
        if not tenant_id:
            resp = firewall_default_data(sub_res, is_list=True)
        else:
            resp = firewall_default_data(sub_res, is_list=False)
        return make_response(str(resp), 200)


@neutronmod.route('/v2.0/vpn/<sub_res>', methods=['GET'])
@neutronmod.route('/v2.0/vpn/<sub_res>/<tenant_id>', methods=['GET'])
@commonfun
def vpn_resrc(auth, region, sub_res, tenant_id=None):
    sub_resources = ('vpnservices', 'ipsecpolicies',
                     'ikepolicies', 'ipsec-site-connections')
    if sub_res not in sub_resources:
        resp = {'code': 404, 'message': 'RESOURCE NOT FOUND'}
        return make_response(str(resp), 404)

    res_url = get_url(auth, 'vpn', sub_res, tenant_id)
    try:
        resp = httprequest.httpclient(
            'GET', res_url, auth[0])
        log.info('RESP:' + str(resp.json()))
        return make_response(json.dumps(resp.json()),
                             resp.status_code)
    except Exception:
        if not tenant_id:
            resp = vpn_default_data(sub_res, is_list=True)
        else:
            resp = vpn_default_data(sub_res, is_list=False)
        return make_response(str(resp), 200)


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


def vpn_default_data(sub_res, is_list=True):
    data = {}
    sub_resource = {'vpnservices': 'vpnservice',
                    'ikepolicies': 'ikepolicy',
                    'ipsecpolicies': 'ipsecpolicy',
                    'ipsec-site-connections': 'ipsec_site_connection'}
    sub_resources = {'vpnservices': 'vpnservices',
                     'ikepolicies': 'ikepolicies',
                     'ipsecpolicies': 'ipsecpolicies',
                     'ipsec-site-connections': 'ipsec_site_connections'}

    data['vpnservices'] = dict(router_id='', status='',
                               name='', admin_state_up='',
                               subnet_id='', tenant_id='',
                               id='', description='')
    data['ikepolicies'] = dict(name='', tenant_id='', id='',
                               auth_algorithm='', pfs='',
                               encryption_algorithm='',
                               phase1_negotiation_mode='',
                               lifetime=dict(units='', value=''),
                               ike_version='', description='')
    data['ipsecpolicies'] = dict(name='', transform_protocol='',
                                 auth_algorithm='', pfs='',
                                 encapsulation_mode='', id='',
                                 encryption_algorithm='',
                                 tenant_id='', description='',
                                 lifetime=dict(units='', value=''))

    data['ipsec-site-connections'] = dict(status='', initiator='',
                                          name='', admin_state_up='',
                                          tenant_id='', auth_mode='',
                                          peer_cidrs='', psk='', mtu='',
                                          ikepolicy_id='', id='',
                                          dpd=dict(action='', interval='',
                                                   timeout=''),
                                          route_mode='', ipsecpolicy_id='',
                                          peer_address='', peer_id='',
                                          description='', vpnservice_id='',
                                          )

    if is_list:
        return {sub_resource[sub_res]: [data[sub_res]]}
    else:
        return {sub_resources[sub_res]: data[sub_res]}


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
