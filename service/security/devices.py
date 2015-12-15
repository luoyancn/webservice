import json
from flask import Blueprint

import request as httprequest
from service.openstack.keystone import commonfun
from service.openstack.keystone import make_response


devicemod = Blueprint('devicemod', __name__)


@devicemod.route('/v1/wafs', methods=['GET'])
@commonfun
def list_wafs(auth, region):
    _wafs = {
        'service_type': 'TYPE_WAF',
        'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
        'name': 'web security',
        'site_domain': '10.0.0.3',
        'site_ip': '172.24.4.228',
        'port': 8080,
        'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7'}
    _wafs_plus = {
        'service_type': 'TYPE_WAF_PLUS',
        'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
        'name': 'web security',
        'site_domain': '10.0.0.3',
        'site_ip': '172.24.4.228',
        'port': 8080,
        'web_page_path': '/ss/dd.xhtml',
        'exclude_process': '123' }

    body = {'waf':[_wafs, _wafs_plus]}
    return make_response(json.dumps(body), 200)


@devicemod.route('/v1/wafs/<wafs_id>', methods=['GET'])
@commonfun
def get_waf(auth, region, wafs_id):
    _wafs = {
        'service_type': 'TYPE_WAF',
        'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
        'name': 'web security',
        'site_domain': '10.0.0.3',
        'site_ip': '172.24.4.228',
        'port': 8080,
        'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7'}

    body = {'waf':_wafs}
    return make_response(json.dumps(body), 200)


@devicemod.route('/v1/ips', methods=['GET'])
@commonfun
def list_ips(auth, region):
    ips = {
        'tenant_id': '4969c491a3c74ee4af974e6d8dsfdsee',
        'name': 'web security',
        'description': 'xxxx',
        'protected_object': ['os', 'device', 'software', 'database'],
        'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
    }


    body = {'ips': [ips]}
    return make_response(json.dumps(body), 200)


@devicemod.route('/v1/ips/<ips_id>', methods=['GET'])
@commonfun
def get_ips(auth, region, ips_id):
    ips = {
        'tenant_id': '4969c491a3c74ee4af974e6d8dsfdsee',
        'name': 'web security',
        'description': 'xxxx',
        'protected_object': ['os', 'device', 'software', 'database'],
        'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
    }


    body = {'ips': ips}
    return make_response(json.dumps(body), 200)


@devicemod.route('/v1/virus', methods=['GET'])
@commonfun
def list_virus(auth, region):
    virus = {
        'service_type': 'WEB',
        'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
        'name': 'web security',
        'description': 'xxxxx',
        'protocol': 'HTTP',
        'upload': True,
        'download': True,
        'operation': 'ALARM',
        'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
    }

    body = {'virus': [virus]}
    return make_response(json.dumps(body), 200)


@devicemod.route('/v1/virus/<virus_id>', methods=['GET'])
@commonfun
def get_virus(auth, region, virus_id):
    virus = {
        'service_type': 'WEB',
        'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
        'name': 'web security',
        'description': 'xxxxx',
        'protocol': 'HTTP',
        'upload': True,
        'download': True,
        'operation': 'ALARM',
        'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
    }

    body = {'virus': virus}
    return make_response(json.dumps(body), 200)


@devicemod.route('/v1/security/physical_devices', methods=['GET'])
@commonfun
def list_devices(auth, region):
    device = {
        'id': '9ad5a7e0-6dac-41b4-b20d-a7b8645fddf1',
        'type': 'WAF',
        'name': 'buildin',
        'description': '',
        'service_ip_list': ['10.0.0.11'],
        'mgmt_ip': '172.10.0.11',
    }

    body = {'physical_devices': [device]}
    return make_response(json.dumps(body), 200)


@devicemod.route('/v1/security/physical_devices/<device_id>', methods=['GET'])
@commonfun
def get_devices(auth, region, device_id):
    device = {
        'id': '9ad5a7e0-6dac-41b4-b20d-a7b8645fddf1',
        'type': 'WAF',
        'name': 'buildin',
        'description': '',
        'service_ip_list': ['10.0.0.11'],
        'mgmt_ip': '172.10.0.11',
    }

    body = {'physical_devices': device}
    return make_response(json.dumps(body), 200)
