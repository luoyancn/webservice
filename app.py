from flask import Flask
import config


from service.openstack.keystone import keystonemod
from service.openstack.nova import novamod
from service.notification.monitor import monitormod
from service.node.node import nodemod
from service.log.operate import logmod
from service.openstack.neutron import neutronmod
from service.security.devices import devicemod
from service.tasks.workissue import workissuelogmod
from service.daemons.wafs import daemon_wafs


app = Flask(__name__)
app.register_blueprint(keystonemod)
app.register_blueprint(novamod)
app.register_blueprint(nodemod)
app.register_blueprint(monitormod)
app.register_blueprint(logmod)
app.register_blueprint(neutronmod)
app.register_blueprint(devicemod)
app.register_blueprint(workissuelogmod)
TRUE_STRINGS = ('1', 't', 'true', 'on', 'y', 'yes')


def generate_ssl_context():
    return (config.certificate_file, config.privatekey_file)

def thread_daemons():
    daemons_run = {}
    daemons_run_keys = []
    daemons_all = {'wafs': daemon_wafs}
    daemon_modules = config.daemon_modules.split(',')
    for daemon in daemon_modules:
        if daemon not in daemons_all.keys():
            continue
        daemons_run_keys.append(daemon)

    # Run daemons
    for daemon in daemons_run_keys:
        daemons_run[daemon] = daemons_all[daemon](300)
        daemons_run[daemon].setDaemon(True)
        daemons_run[daemon].start()


if __name__ == '__main__':
    if config.enable_daemons.lower() in TRUE_STRINGS:
        thread_daemons()
    kwargs = dict(host=config.bind_address, port=config.bind_port)
    if config.enable_ssl.lower() in TRUE_STRINGS:
        ssl_context = generate_ssl_context()
        kwargs['ssl_context'] = ssl_context
    if config.debug.lower() in TRUE_STRINGS:
        kwargs['debug'] = True
        # If debug is true, it runs app.py twice by default to auto reload
        kwargs['use_reloader'] = False
    app.run(**kwargs)
