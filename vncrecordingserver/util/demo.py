from util import cloudutil
import sys, os, base64
from xml.dom.minidom import parse
import xml.dom.minidom as xmldom

from util import cloudutil

sys.path.append(os.path.join(os.path.dirname(__file__), 'util'))


def getvncinfo(client, instanceId):
    params = {"InstanceId": instanceId}
    return client.invoke("GetVncInfo", params)


def get_info(instanceId):
    client = cloudutil.bcclient('cloud', True)
    # instanceId = "i-0D465FA4"

    result = getvncinfo(client, instanceId)
    # print(res)
    # result = getvncinfo(client, instanceId)
    # print(result)
    domobj = xmldom.parseString(result)
    eleobj = domobj.documentElement
    subobj = eleobj.getElementsByTagName('getVncInfoResult')
    for sub in subobj:
        hosts = sub.getElementsByTagName('host')[0].firstChild.data
        # print(hosts)
        ports = sub.getElementsByTagName('port')[0].firstChild.data
        # print(ports)
        passwd = sub.getElementsByTagName('password')[0].firstChild.data
        # print(passwd)
        res = {
            'host':hosts,
            'port':int(ports),
            'password':passwd
        }
        # print(res)
        return res
if __name__ == '__main__':
    get_info("i-0D465FA4")