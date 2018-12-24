#!/usr/bin/env python

import socket
import time
import json
from . import args


class Network:
    def __init__(self,
                 ip=args["roborio_ip"],
                 port=int(args["roborio_port"]),
                 verbose=args["verbose"]):
        self.ip = ip
        self.port = port
        self.verbose = verbose

        self.prev_message = {}
        self.prev_recipient = ()
        self.prev_time = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message, recipient=False):
        """
        Sends a packet to the specified recipient. For broadcasts, IP should be
        10.25.21.255, with a port in range of 5800-5810. In most cases, the recipient
        should be the roboRIO.

        :param message: the dict to send as a message (will be converted to JSON and
                        a timestamp will be added)
        :param recipient: the recipient of the packet
        """
        message["time"] = int(time.time() * 1000)

        try:
            self.sock.sendto(json.dumps(message, separators=(",", ":")).encode(),
                             recipient if recipient else (self.ip, self.port))
        except:
            print("Network error...")
            pass

    def send_new(self, message, recipient=False):
        """
        Sends a packet to the specified recipient if either the message or the
        recipient has changed from the last call of this method, or if 500ms have
        passed since the last time a message has been sent.

        :param message: the dict to send as a message (will be converted to JSON and
                        a timestamp will be added)
        :param recipient: the recipient of the packet
        """
        timeout = int(time.time() * 1000) - self.prev_time > 500
        if message != self.prev_message or recipient != self.prev_recipient or timeout:
            self.prev_message = dict(message)
            self.prev_recipient = recipient
            self.prev_time = int(time.time() * 1000)

            self.send(message, recipient)
