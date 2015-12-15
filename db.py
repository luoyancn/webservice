import config
import log
import pymysql

def getDevicesConn():
    conn = pymysql.connect(host=config.devices_db_host,
                           port=int(config.devices_db_port),
                           user=config.devices_db_user,
                           passwd=config.devices_db_passwd,
                           db=config.devices_db,
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    return conn
