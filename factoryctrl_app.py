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

"""This module controls the Alarm Light and Reset button.
"""

from distutils.util import strtobool
import json
import os
import sys
import eis.msgbus as mb
from eis.env_config import EnvConfig
from eis.config_manager import ConfigManager
from util.util import Util
from util.log import configure_logging
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

CONFIG_KEY_PATH = "/config"


class FactoryControlApp:
    '''This Class controls the AlarmLight'''

    def __init__(self, dev_mode, config_client, log):
        ''' Reads the config file and connects
        to the io_module

        :param dev_mode: indicates whether it's dev or prod mode
        :type dev_mode: bool
        :param config_client: distributed store config client
        :type config_client: config client object
        '''
        self.dev_mode = dev_mode
        self.config_client = config_client
        self.log = log
        self.app_name = os.environ.get("AppName")
        cfg = self.config_client.GetConfig("/{0}{1}"
                                           .format(self.app_name,
                                                   CONFIG_KEY_PATH))
        # Validating config against schema
        with open('./schema.json', "rb") as infile:
            schema = infile.read()
            if (Util.validate_json(schema, cfg)) is not True:
                sys.exit(1)
        self.config = json.loads(cfg)
        host = self.config["io_module_ip"]
        port = self.config["io_module_port"]
        self.ip_address = host + ":" + str(port)
        self.modbus_client = ModbusClient(host, port, timeout=1,
                                          retry_on_empty=True)

    def light_ctrl_cb(self, metadata):
        '''Controls the Alarm Light, i.e., alarm light turns on
        if there are any defects in the classified results

        :param metadata:  classified results metadata
        :type metadata: dict
        '''
        defect_types = []
        if 'defects' in metadata:
            if metadata['defects']:
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
                    except Exception as ex:
                        self.log.error(ex, exc_info=True)
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
            self.log.info("Modbus connecting on %s", self.ip_address)
            ret = self.modbus_client.connect()
            if not ret:
                self.log.error("Modbus Connection failed")
                sys.exit(-1)
            self.log.info("Modbus connected")
            topics = os.environ.get("SubTopics").split(",")
            if len(topics) > 1:
                raise Exception("Multiple SubTopics are not supported")

            self.log.info("Subscribing on topic: %s", topics[0])
            publisher, topic = topics[0].split("/")
            msgbus_cfg = EnvConfig.get_messagebus_config(
                topic, "sub", publisher, self.config_client, self.dev_mode)
            topic = topic.strip()
            mode_address = os.environ[topic + "_cfg"].split(",")
            mode = mode_address[0].strip()
            if (not self.dev_mode and mode == "zmq_tcp"):
                for key in msgbus_cfg[topic]:
                    if msgbus_cfg[topic][key] is None:
                        raise ValueError("Invalid Config")

            msgbus = mb.MsgbusContext(msgbus_cfg)
            subscriber = msgbus.new_subscriber(topic)
            while True:
                metadata, _ = subscriber.recv()
                if metadata is None:
                    raise Exception("Received None as metadata")
                self.light_ctrl_cb(metadata)
        except KeyboardInterrupt:
            self.log.error(' keyboard interrupt occurred Quitting...')
        except Exception as ex:
            self.log.exception(ex)
        finally:
            if subscriber is not None:
                subscriber.close()


def main():
    """Main method to FactoryControl App
    """

    dev_mode = bool(strtobool(os.environ["DEV_MODE"]))

    app_name = os.environ["AppName"]
    conf = Util.get_crypto_dict(app_name)

    cfg_mgr = ConfigManager()
    config_client = cfg_mgr.get_config_client("etcd", conf)

    log = configure_logging(os.environ['PY_LOG_LEVEL'].upper(),
                            __name__, dev_mode)
    log.info("=============== STARTING factoryctrl_app ===============")
    try:
        factory_control_app = FactoryControlApp(dev_mode, config_client, log)
        factory_control_app.main()
    except Exception as ex:
        log.exception(ex)


if __name__ == "__main__":
    main()
