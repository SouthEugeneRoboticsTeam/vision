#!/usr/bin/env python

import threading

from appJar import gui

from gui import Gui
from vision import args
from vision.app import Vision

app = None


def create_gui():
    global app

    app = gui("Vision", handleArgs=False)
    app.setSize(800, 480)
    app.setSize("fullscreen")
    app.setGuiPadding(0, 0)
    app.hideTitleBar()

    app.setBg("yellow")

    app.setFont(size=64, family="Verdana", underline=False, slant="roman")

    app.addLabel("title", "VISION SYSTEM")
    app.getLabelWidget("title").config(font="Verdana 64 underline")

    app.addLabel("radio", "RADIO: DOWN")
    app.addLabel("robot", "ROBOT: DOWN")
    app.addLabel("ntabl", "NTABL: DOWN")
    app.getLabelWidget("radio").config(font="Courier 64 bold", bg="red")
    app.getLabelWidget("robot").config(font="Courier 64 bold", bg="red")
    app.getLabelWidget("ntabl").config(font="Courier 64 bold", bg="red")


def run_vision():
    vision = Vision(app)
    vision.run()


def run_gui():
    gui = Gui(app)
    gui.run()


if __name__ == '__main__':
    vision_thread = threading.Thread(target=run_vision)
    vision_thread.start()

    if not args["no_gui"]:
        create_gui()

        gui_thread = threading.Thread(target=run_gui)
        gui_thread.start()

        app.go()
