# Import SDK packages
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException
import time
import managers
import uuid
import json
import random
import pandas as pd
import numpy as np
from common import *

class MQTTClient:

    def __init__(self, thing_num, topic='device/data'):
        self.topic = topic
        # For certificate based connection
        self.ch = managers.CertsHelper()
        cert, key = self.ch.get_cert_paths(thing_num)
        self.cert = cert
        self.key = key
        self.ca_cert = self.ch.root_ca_path
        self.device_id = get_name(thing_num)
        self.state = 0
        self.discovered = False
        self.connected = False
        self.endpoint_url = 'a1kof1gm996y1o-ats.iot.us-east-1.amazonaws.com'
        self.coreInfo, self.group_ca = self.discover()
        self.client = AWSIoTMQTTClient(self.device_id)
        #TODO 2: modify your broker address

        #self.client.configureEndpoint(self.endpoint_url, 8883)
        self.client.configureCredentials(self.group_ca, key, cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client.onMessage = self.customOnMessage

        self.data = get_data(thing_num).to_dict(orient='records')
        self.data_idx = 0

    def connect_endpoint(self):
        for connectivityInfo in self.coreInfo.connectivityInfoList:
            currentHost = connectivityInfo.host
            currentPort = connectivityInfo.port
            debug("Trying to connect to core at %s:%d" % (currentHost, currentPort))
            self.client.configureEndpoint(currentHost, currentPort)
            try:
                self.client.connect()
                self.connected = True
                break
            except BaseException as e:
                debug("Error in connect!")
                debug("Type: %s" % str(type(e)))
                debug("Error message: %s" % str(e))

    def discover(self):
        # Progressive back off core
        backOffCore = ProgressiveBackOffCore()

        # Discover GGCs
        discoveryInfoProvider = DiscoveryInfoProvider()
        discoveryInfoProvider.configureEndpoint(self.endpoint_url)
        discoveryInfoProvider.configureCredentials(self.ca_cert, self.cert, self.key)
        discoveryInfoProvider.configureTimeout(10)  # 10 sec

        retryCount = MAX_DISCOVERY_RETRIES
        while retryCount != 0:
            try:
                discoveryInfo = discoveryInfoProvider.discover(self.device_id)
                caList = discoveryInfo.getAllCas()
                coreList = discoveryInfo.getAllCores()

                # We only pick the first ca and core info
                groupId, ca = caList[0]
                coreInfo = coreList[0]
                debug("Discovered GGC: %s from Group: %s" % (coreInfo.coreThingArn, groupId))

                debug("Now we persist the connectivity/identity information...")
                group_ca = self.ch.save_cert_file(grp_cert_format.format(groupId), ca)

                self.discovered = True
                debug("Now proceed to the connecting flow...")
                return coreInfo, group_ca
            except DiscoveryInvalidRequestException as e:
                debug("Invalid discovery request detected!")
                debug("Type: %s" % str(type(e)))
                debug("Error message: %s" % str(e))
                debug("Stopping...")
                break
            except BaseException as e:
                debug("Error in discovery!")
                debug("Type: %s" % str(type(e)))
                debug("Error message: %s" % str(e))
                retryCount -= 1
                debug("\n%d/%d retries left\n" % (retryCount, MAX_DISCOVERY_RETRIES))
                debug("Backing off...\n")
                backOffCore.backOff()

    def customOnMessage(self, message):
        #TODO 3: fill in the function to show your received message
        info("{} received {} from topic {}"
             .format(self.device_id, message.payload, message.topic))

    # Suback callback
    def customSubackCallback(self,mid, data):
        #You don't need to write anything here
        pass

    # Puback callback
    def customPubackCallback(self,mid):
        #You don't need to write anything here
        pass

    def publish(self, Payload="payload"):
        #TODO 4: fill in this function for your publish
        #self.client.subscribeAsync("myTopic", 0, ackCallback=self.customSubackCallback)
        if self.data_idx >= len(self.data):
            info(f"No more data to publish for {self.device_id}.")
            return
        record = self.data[self.data_idx]
        record['device_id'] = self.device_id
        self.data_idx += 1

        info(json.dumps(record))

        self.client.publishAsync(self.topic, json.dumps(record), 0,
                                 ackCallback=self.customPubackCallback)


print("Initializing MQTTClients...")
clients = []
for sq in NUM_SEQ:
    client = MQTTClient(sq)
    client.connect_endpoint()
    clients.append(client)

print("start?")
input()

try:
    while True:
        for c in clients:
            time.sleep(random.randint(0, 1))
            c.publish()
        time.sleep(random.randint(0, 1))
except KeyboardInterrupt:
    info("Program was interrupted by the user")

for c in clients:
    c.client.disconnect()

print("All devices disconnected")