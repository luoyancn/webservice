import requests


def httpclient(method, url, token, kwargs={}):
    kwargs.setdefault('headers', kwargs.get('headers', {}))
    kwargs['params'] = kwargs.get('params', {})
    kwargs['headers']['X-Auth-Token'] = token
    kwargs['headers']['Content-Type'] = 'application/json'
    http = requests.Session()
    resp = http.request(method, url, **kwargs)
    return resp
