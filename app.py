from flask import Flask
import config


from service.openstack.keystone import keystonemod
from service.openstack.nova import novamod
from service.notification.monitor import monitormod
from service.node.node import nodemod
from service.log.operate import logmod
from service.openstack.neutron import neutronmod


app = Flask(__name__)
app.register_blueprint(keystonemod)
app.register_blueprint(novamod)
app.register_blueprint(nodemod)
app.register_blueprint(monitormod)
app.register_blueprint(logmod)
app.register_blueprint(neutronmod)
TRUE_STRINGS = ('1', 't', 'true', 'on', 'y', 'yes')


def generate_ssl_context():
    return (config.certificate_file, config.privatekey_file)


if __name__ == '__main__':
    kwargs = dict(host=config.bind_address, port=config.bind_port)
    if config.enable_ssl.lower() in TRUE_STRINGS:
        ssl_context = generate_ssl_context()
        kwargs['ssl_context'] = ssl_context
    if config.debug.lower() in TRUE_STRINGS:
        kwargs['debug'] = True
    app.run(**kwargs)
