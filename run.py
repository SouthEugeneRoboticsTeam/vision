#!/usr/bin/env python

import threading

from appJar import gui

from gui import Gui
from vision.app import Vision

app = gui("Vision")
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


def runVision():
    vision = Vision(app)
    vision.run()


def runGui():
    gui = Gui(app)
    gui.run()


if __name__ == '__main__':
    visionThread = threading.Thread(target=runVision)
    visionThread.start()

    guiThread = threading.Thread(target=runGui)
    guiThread.start()

    app.go()
