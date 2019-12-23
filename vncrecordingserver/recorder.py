#!/usr/bin/env python
import time
import socket
import threading
import os
import errno
import logging

from vnc2flv.flv import FLVWriter
from vnc2flv.rfb import RFBNetworkClient, RFBError
from vnc2flv.video import FLVVideoSink
import xml.dom.minidom as xmldom
from util import cloudutil

from vncrecordingserver.util.demo import get_info

logger = logging.getLogger(__name__)


class RecorderActiveError(Exception):
    pass


class MemoryPWD(object):
    def __init__(self, password=None):
        self.p = password

    def getpass(self):
        if not self.p:
            return ''
        return self.p


class RecordingStatus(object):
    STATUS_IDLE = "idle"
    STATUS_RUNNING = "recording"
    STATUS_ERROR = "error"

    def __init__(self):
        self.status = RecordingStatus.STATUS_IDLE
        self.error = ""

    def stop(self):
        self.status = RecordingStatus.STATUS_IDLE
        self.error = ""

    def running(self):
        self.status = RecordingStatus.STATUS_RUNNING
        self.error = ""

    def raise_error(self, message=""):
        self.status = RecordingStatus.STATUS_ERROR
        self.error = message

    def current_status(self):
        return self.status


class RecordingThread(threading.Thread):

    def __init__(self, status, fp, writer, client):
        threading.Thread.__init__(self)
        self.fp = fp
        self.writer = writer
        self.client = client
        self.status = status

    def run(self):
        Recorder.run(self.status, self.fp, self.writer, self.client)

    def stop(self):
        self.status.stop()

    def get_status(self):
        return self.status




class Recorder(object):
    # def getinfo(self):

    _config = {
        'filename': 'out%s.flv' % time.strftime('%Y%m%d%H%M'),
        'output_path': os.curdir,
        'password': '',
        'host': '',
        'port': 5900,
        'framerate': 12,
        'keyframe': 120,
        'preferred_encoding': (0,),
        'blocksize': 32,
        'clipping': None,
        'debug': False
    }

    def __init__(self, config):
        self._config.update(config)
        self._recording_thread = None

    def stop(self):
        if self._recording_thread is not None:
            self._recording_thread.stop()
            self._recording_thread.join()
            self._recording_thread = None

    def start(self, config_override):
        if self.is_active():
            raise RecorderActiveError
        status = RecordingStatus()
        self._config.update(config_override)
        fp, writer, client = Recorder.client_from_config(self._config)
        self._recording_thread = RecordingThread(status, fp, writer, client)
        self._recording_thread.start()

    def get_status(self):
        status = {
            'config': self._config,
            'active': False
        }

        if self._recording_thread is not None:
            status['active'] = self._recording_thread.isAlive()
            if self._recording_thread.status.current_status() \
                    == RecordingStatus.STATUS_ERROR:
                status['error'] = self._recording_thread.status.error

        return status

    def is_active(self):
        if self._recording_thread is not None:
            return self._recording_thread.isAlive()
        return False

    @staticmethod
    def client_from_config(config):
        password = config.get('password')
        filename = config.get('filename')
        host = config.get('host')
        port = config.get('port')
        output_path = config.get('output_path')
        framerate = config.get('framerate')
        keyframe = config.get('keyframe')
        preferred_encoding = config.get('preferred_encoding')
        blocksize = config.get('blocksize')
        clipping = config.get('clipping')
        debug = config.get('debug')

        pwdcache = MemoryPWD(password)

        try:
            os.makedirs(output_path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(output_path):
                pass
            else:
                raise
        fp = open(os.path.join(output_path, filename), 'wb')

        writer = FLVWriter(
            fp,
            framerate=framerate,
            debug=debug
        )
        sink = FLVVideoSink(
            writer,
            blocksize=blocksize,
            framerate=framerate,
            keyframe=keyframe,
            clipping=clipping,
            debug=debug
        )
        client = RFBNetworkClient(
            host,
            port,
            sink,
            timeout=500 / framerate,
            pwdcache=pwdcache,
            preferred_encoding=preferred_encoding,
            debug=debug
        )

        return fp, writer, client

    @staticmethod
    def run(status, fp, writer, client):
        status.running()
        try:
            client.open()
            try:
                while status.current_status() \
                        == RecordingStatus.STATUS_RUNNING:
                    client.idle()

            finally:
                client.close()
        except socket.error as e:
            logger.error('Socket error:' + str(e))
            status.raise_error('Socket error ' + str(e))
        except RFBError as e:
            logger.error('RFB error:' + str(e))
            status.raise_error('RFB error: ' + str(e))
        except Exception as e:
            logger.error('Unknown error:' + str(e))
            status.raise_error('Unknown error ' + str(e))
        writer.close()
        fp.close()


if __name__ == '__main__':
    pass
    # ins = 'i-5EB0E5CB'
    # info = getInfo(ins)
    # print(info)
    # con={
    #         'filename': '{}-out%s.flv'.format(ins,time.strftime('%Y%m%d%H%M')),
    #         'password': info[2],
    #         'host': info[0],
    #         'port': int(info[1]),
    #     }
    # r = Recorder(con)
    # r.start(config_override=con)
    # # print(123123)
    # time.sleep(10)
    # r.stop()


# class VncInfo():
#     def __init__(self, ins):
#         self.ins = ins
#
#     def trans(self):
#         pass
