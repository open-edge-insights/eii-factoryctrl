# Copyright (c) 2019 Intel Corporation.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from libs.log import configure_logging, LOG_LEVELS
from distutils.util import strtobool
import logging
import argparse
import ast
import json
import os
import datetime
import eis.msgbus as mb
from libs.ConfigManager import ConfigManager
from libs.common.py.util import Util
import queue

CONFIG_KEY_PATH = "/config"


class FactoryControlApp:
    '''This Class controls the AlarmLight'''

    def __init__(self, args, log):
        ''' Reads the config file and connects
        to the io_module'''
        self.args = args
        self.log = log
        self.dev_mode = bool(strtobool(os.environ["DEV_MODE"]))
        conf = {
            "certFile": "",
            "keyFile": "",
            "trustFile": ""
        }
        self.app_name = os.environ.get("AppName")
        cfg_mgr = ConfigManager()
        self.config_client = cfg_mgr.get_config_client("etcd", conf)
        cfg = self.config_client.GetConfig("/{0}{1}"
                                           .format(self.app_name,
                                                   CONFIG_KEY_PATH))
        self.config = json.loads(cfg)
        self.ip = self.config["io_module_ip"]
        self.port = self.config["io_module_port"]
        self.modbus_client = ModbusClient(
            self.ip, self.port, timeout=1, retry_on_empty=True)

    def light_ctrl_cb(self, metadata):
        ''' Controls the Alarm Light, i.e., alarm light turns on
        if there are any defects in the classified results
        Argument: metadata from influxdb
        Output: Turns on the Alarm Light
        '''
        defect_types = []
        if 'defects' in metadata:
            if metadata['defects']:
                metadata['defects'] = ast.literal_eval(
                    metadata['defects'])

                for i in metadata['defects']:
                    defect_types.append(i['type'])

                if (1 in defect_types) or (2 in defect_types) or \
                   (3 in defect_types) or (0 in defect_types):
                    # write_coil(regester address, bit value)
                    # bit value will be stored in the register address
                    # bit value is either 1 or 0
                    # 1 is on and 0 is off
                    try:
                        self.modbus_client.write_coil(
                            self.config["green_bit_register"], 0)
                        self.modbus_client.write_coil(
                            self.config["red_bit_register"], 1)
                        self.log.info("AlarmLight Triggered")
                    except Exception as e:
                        self.log.error(e, exc_info=True)
                else:
                    self.modbus_client.write_coil(
                        self.config["red_bit_register"], 0)
                    self.modbus_client.write_coil(
                        self.config["green_bit_register"], 1)
            else:
                self.modbus_client.write_coil(
                    self.config["red_bit_register"], 0)
                self.modbus_client.write_coil(
                    self.config["green_bit_register"], 1)

    def main(self):
        ''' FactoryControl app to subscribe to topics published by
            VideoAnalytics and control the red/green lights based on the
            classified metadata
        '''
        subscriber = None
        try:
            self.log.info("Modbus connecting on %s:%s" % (self.ip, self.port))
            ret = self.modbus_client.connect()
            if not ret:
                self.log.error("Modbus Connection failed")
                exit(-1)
            self.log.info("Modbus connected")
            topics = os.environ.get("SubTopics").split(",")
            if len(topics) > 1:
                raise Exception("Multiple SubTopics are not supported")

            self.log.info("Subscribing on topic: {}".format(topics[0]))
            publisher, topic = topics[0].split("/")
            msgbus_cfg = Util.get_messagebus_config(topic, "sub",
                                                    publisher,
                                                    self.config_client,
                                                    self.dev_mode)
            msgbus = mb.MsgbusContext(msgbus_cfg)
            subscriber = msgbus.new_subscriber(topic)
            while True:
                metadata, _ = subscriber.recv()
                if metadata is None:
                    raise Exception("Received None as metadata")
                self.light_ctrl_cb(metadata)
        except KeyboardInterrupt:
            self.log.error(' keyboard interrupt occurred Quitting...')
        except Exception as e:
            self.log.exception(e)
        finally:
            if subscriber is not None:
                subscriber.close()


def parse_args():
    '''Parse command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', dest='log', choices=LOG_LEVELS.keys(),
                        default='DEBUG', help='Logging level (df: DEFAULT)')

    parser.add_argument('--log-name', dest='log_name',
                        default='factoryctrl_app_logs', help='Logfile name')

    parser.add_argument('--log-dir', dest='log_dir', default='logs',
                        help='Directory to for log files')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(args.log_dir):
        os.mkdir(args.log_dir)

    currentDateTime = str(datetime.datetime.now())
    listDateTime = currentDateTime.split(" ")
    currentDateTime = "_".join(listDateTime)
    logFileName = 'factoryCtrlApp_' + currentDateTime + '.log'

    log = configure_logging(args.log.upper(), logFileName,
                            args.log_dir, __name__)
    log.info("=============== STARTING factoryctrl_app ===============")
    try:
        factoryCtrlApp = FactoryControlApp(args, log)
        factoryCtrlApp.main()
    except Exception as e:
        log.exception(e)
