import threading
import time
from platform import system
from subprocess import call, DEVNULL

from appJar import gui
from networktables import NetworkTablesInstance

# TODO: Get this number from config
team = 2521

up_color = "green"
down_color = "red"
warn_color = "yellow"

up_text = " UP "
down_text = "DOWN"


class ConnectionGui:
    def __init__(self, app):
        app.setSize(800, 480)
        app.setSize("fullscreen")
        app.setGuiPadding(0, 0)

        app.setBg(warn_color)

        app.setFont(size=64, family="Ubuntu", underline=False, slant="roman")

        app.addLabel("title", "VISION SYSTEM")
        app.getLabelWidget("title").config(font="Ubuntu 64 underline")

        app.addLabel("radio", "RADIO: {}".format(down_text))
        app.addLabel("robot", "ROBOT: {}".format(down_text))
        app.addLabel("ntabl", "NTABL: {}".format(down_text))
        app.getLabelWidget("radio").config(font="Ubuntu\ Mono 64 bold", bg="red")
        app.getLabelWidget("robot").config(font="Ubuntu\ Mono 64 bold", bg="red")
        app.getLabelWidget("ntabl").config(font="Ubuntu\ Mono 64 bold", bg="red")

        self.app = app

        self.radio_address = '10.{}.{}.1'.format(int(team / 100), int(team % 100))
        self.robot_address = '10.{}.{}.2'.format(int(team / 100), int(team % 100))

        self.nt = NetworkTablesInstance.getDefault()
        self.nt.startClientTeam(team)
        self.nt.addConnectionListener(self._listener, immediateNotify=True)

    def run(self):
        while True:
            self.update()
            time.sleep(2)

    def update(self):
        radio_good = self._ping(self.radio_address)
        robot_good = self._ping(self.robot_address)
        ntabl_good = self.nt.isConnected()

        self.app.queueFunction(self._update_gui, radio_good, robot_good, ntabl_good)

    def _update_gui(self, radio_good, robot_good, ntabl_good):
        if radio_good and robot_good and ntabl_good:
            self.app.setBg(up_color)
        elif not radio_good and not robot_good and not ntabl_good:
            self.app.setBg(down_color)
        else:
            self.app.setBg(warn_color)

        self._update_state("radio", radio_good)
        self._update_state("robot", robot_good)
        self._update_state("ntabl", ntabl_good)

    def _update_state(self, element, good):
        self.app.setLabelBg(element, up_color if good else down_color)
        self.app.setLabel(element, "{}: {}".format(element.upper(), up_text if good else down_text))

    def _ping(self, host):
        param = '-n' if system().lower() == 'windows' else '-c'
        interval = '1' if system().lower() == 'windows' else '0.2'

        command = ['ping', param, '3', '-W', '1', '-i', interval, host]

        return call(command, stdout=DEVNULL) == 0

    def _listener(self, connected, _):
        self.app.queueFunction(self._update_state, "ntabl", connected)
        self.update()


if __name__ == "__main__":
    app = gui("Vision")

    interface = ConnectionGui(app)

    gui_thread = threading.Thread(target=interface.run)
    gui_thread.start()

    app.go()
