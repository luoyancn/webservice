import json
from flask import Blueprint

import request as httprequest
from .keystone import commonfun
from .keystone import make_response

from flask import request
novamod = Blueprint('novamod', __name__)


@novamod.route('/v2.1/<project_id>/servers/<server_id>', methods=['GET'])
@commonfun
def get_server(auth, region, project_id, server_id):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    resp = httprequest.httpclient(
        'GET', auth[1][0] + '/servers/%s' % server_id,
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)


@novamod.route('/v2.1/<project_id>/servers/detail', methods=['GET'])
@commonfun
def list_servers(auth, region, project_id):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    kwargs['params'] = request.args
    resp = httprequest.httpclient(
        'GET', auth[1][0] + '/servers/detail',
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)


@novamod.route('/v2.1/<project_id>/flavors/detail', methods=['GET'])
@commonfun
def list_flavors(auth, region, project_id):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    resp = httprequest.httpclient(
        'GET', auth[1][0] + '/flavors/detail',
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)


@novamod.route('/v2/<project_id>/volumes/<volume_id>', methods=['GET'])
@commonfun
def get_volume(auth, region, project_id, volume_id):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    kwargs['params'] = request.args
    resp = httprequest.httpclient(
        'GET', auth[3][0] + '/volumes/%s' % volume_id,
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)


@novamod.route('/v2/<project_id>/volumes/detail', methods=['GET'])
@commonfun
def list_volumes(auth, region, project_id):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    resp = httprequest.httpclient(
        'GET', auth[3][0] + '/volumes/detail',
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)


@novamod.route('/v2/<project_id>/snapshots/detail', methods=['GET'])
@commonfun
def list_snapshots(auth, region, project_id):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    resp = httprequest.httpclient(
        'GET', auth[3][0] + '/snapshots/detail',
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)


@novamod.route('/v2/images', methods=['GET'])
@commonfun
def list_images(auth, region):
    kwargs = {'headers': {'X-Openstack-Region': region}}
    resp = httprequest.httpclient(
        'GET', auth[4][0] + '/images',
        auth[0], kwargs=kwargs)
    return make_response(json.dumps(resp.json()), resp.status_code)
