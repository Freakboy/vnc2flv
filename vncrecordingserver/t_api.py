# coding=utf-8

import glob
import re
import time, threading

from flask import Flask, request, current_app, Response
import json, os
from vncrecordingserver.tt1 import Recorder, RecorderActiveError
from vncrecordingserver.util.demo import get_info

app = Flask(__name__)


@app.route("/info", methods=["GET"])
def show_info():
    # 默认返回内容
    return_dict = {'host_ip': '',
                   'host_port': '',
                   'type': 'VNC',
                   'username': 'visitor',
                   'password': '',
                   }
    # 判断入参是否为空
    if request.get_data() is None:
        return_dict['return_code'] = '504'
        return_dict['return_info'] = '请求参数为空'
        return json.dumps(return_dict, ensure_ascii=False)
    # 获取传入的参数
    get_Data = request.args.to_dict()
    id = get_Data.get('id')
    res = get_info(id)
    return_dict['host_ip'] = res.get('host')
    return_dict['host_port'] = str(res.get('port'))
    return_dict['password'] = res.get('password')
    return json.dumps(return_dict, ensure_ascii=False)


@app.route("/start", methods=["POST"])
def check():
    # 默认返回内容
    data = request.get_json()
    downloadpath = data.get('downloadpath')
    filename = data.get('filename')
    filepath = data.get('filepath')
    foldername = data.get('foldername')
    globalconfigdbid = data.get('globalconfigdbid')
    projectdbid = data.get('projectdbid')
    vminstancedbid = data.get('vminstancedbid')
    id = data.get('instanceName')
    print('id==================', id)
    return_dict = {'return_code': '200',
                   'return_info': '处理成功',
                   'result': False}
    try:
        # 对参数进行操作d
        return_dict['result'] = start(id)
    except Exception as e:
        print('error', e)
    if re.match(r'^i-', id):
        return json.dumps(return_dict, ensure_ascii=False)
    else:
        return json.dumps({"return_code": "500", 'success': False, "message": 'instanceid error'})


def asy(f):
    def wrapper(*args, **kwargs):
        thr = threading.Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


@asy
def start(id):
    r = Recorder(id)
    r.start()
    f = open('%s.lock' % (id), 'w')
    f.close()
    while True:
        time.sleep(1)
        if os.path.exists('%s.lock' % (id)) == False:
            break
    r.stop()
    # res = req()
    # filePath = os.getcwd()
    return r.ins


@app.route("/stop", methods=["GET"])
def judge():
    # 默认返回内容
    return_dict = {'return_code': '200', 'return_info': '处理成功', 'result': False}
    get_Data = request.args.to_dict()
    id = get_Data.get('id')
    # 对参数进行操作
    return_dict['result'] = stop(id)
    if '{}.lock'.format(id):

        return json.dumps(return_dict, ensure_ascii=False)
    else:
        return json.dumps({"return_code": "500", 'success': False, "message": "No start recording!"})


def stop(id):
    # r = Recorder(id)
    os.remove('%s.lock' % (id))
    # filename =
    msg = "{}:is stop!".format(id)
    return msg


@app.route("/trance", methods=["GET"])
# def despose():
#     msg = {'return_code': '200', 'return_info': '处理成功', 'result': False}
#     msg['result'] = trance()
#     return json.dumps(msg,ensure_ascii=False)
# @asy
def trance():
    # r = Recorder(id)

    path = '/home/zeel/Desktop/vnc2flv/vncrecordingserver'
    # path = os.getcwd()
    # print(path)
    li = []
    for infile in glob.glob(os.path.join(path, '*.flv')):
        filename = infile.split('/')[6]
        li.append(filename)

    try:
        for l in li:
            l1 = l.split('f')[0]
            # print(l1)
            if os.path.exists('%smp4' % (l1)) == False:
                os.system('ffmpeg -i {} {}mp4'.format(l, l1))
        # path = os.getcwd()
    except Exception as e:
        raise e
    msg = {'return_code': '200', 'return_info': '处理成功', 'result': False}
    #     msg['result'] = trance()
    return json.dumps(msg, ensure_ascii=False)
    # for infile in glob.glob(os.path.join(path, '*.flv')):
    # # os.popen('cd {}'.format(path))
    #     os.popen('ffmpeg -i {} output.mp4'.format(infile))


'''
{
  "downloadpath": "resources/recFiles/192.168.1.78_5904_20190916192831.mp4", 
  "filename": "192.168.1.78_5904_20190916192831.mp4", 
  "filepath": "resources", 
  "foldername": "recFiles", 
  "globalconfigdbid": "1adabeb5-151b-49b6-8c0d-cccd382cb6dc", 
  "projectdbid": "P55a5fd90-6b18-47cc-b1ce-b53b37a3c3e8", 
  "vminstancedbid": "2cd07460-fbb8-4214-9353-f61d6cca8dd4"
}
'''
if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0', threaded=True)
