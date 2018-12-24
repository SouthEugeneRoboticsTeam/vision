#!/usr/bin/env python

import time
import sys
from vision.network_utils import Network
from vision.app import Vision
from threading import Thread


class VisionWorker(Thread):
    def __init__(self):
        Thread.__init__(self, name="VisionWorker")
        self.vision = Vision()

    def run(self):
        self.vision.run()

    def stop(self):
        self.vision.stop()

    @property
    def stopped(self):
        return self.vision.stopped


class HeartbeatWorker(Thread):
    def __init__(self):
        Thread.__init__(self, name="HeartbearWorker")
        self.kill_received = False
        self.network = Network()

    def run(self):
        while not self.kill_received:
            self.heartbeat()

        self.network.send({"alive": False})

    def heartbeat(self):
        self.network.send({"alive": True})
        time.sleep(0.25)

    def stop(self):
        self.kill_received = True

    @property
    def stopped(self):
        return self.kill_received


def main():
    heartbeat = HeartbeatWorker()
    vision = VisionWorker()

    heartbeat.start()
    vision.start()

    while True:
        try:
            # Stop threads if main vision thread dies in a method other than ctrl-c
            # (e.g. hitting q in display mode)
            if vision.stopped:
                heartbeat.stop()
                sys.exit(0)

            time.sleep(0.25)
        except KeyboardInterrupt:
            # Stop running threads
            vision.stop()
            heartbeat.stop()

            # Allow threads to cleanup and die, then exit
            time.sleep(0.25)
            sys.exit(0)


if __name__ == '__main__':
    main()
