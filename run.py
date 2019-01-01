#!/usr/bin/env python

import threading

from appJar import gui

from gui import ConnectionGui
from vision import args
from vision.app import Vision


def run_vision():
    vision = Vision()
    vision.run()


def run_gui(app):
    interface = ConnectionGui(app)
    interface.run()


if __name__ == '__main__':
    vision_thread = threading.Thread(target=run_vision)
    vision_thread.start()

    if not args["no_gui"]:
        app = gui("Vision", handleArgs=False)

        gui_thread = threading.Thread(target=lambda: run_gui(app))
        gui_thread.start()

        app.go()
