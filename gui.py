import time
from platform import system
from subprocess import call

from vision import args, network_utils


class Gui:
    def __init__(self, app):
        self.app = app

        self.radio_address = '10.{}.{}.1'.format(int(args['team'] / 100), int(args['team'] % 100))
        self.robot_address = '10.{}.{}.2'.format(int(args['team'] / 100), int(args['team'] % 100))

        network_utils.initConnectionListener(self._listener)

    def run(self):
        while True:
            self.update()
            time.sleep(2)

    def update(self):
        radio_good = self._ping(self.radio_address)
        robot_good = self._ping(self.robot_address)
        ntabl_good = network_utils.nt.isConnected()

        self.app.queueFunction(self._update_gui, radio_good, robot_good, ntabl_good)

    def _update_gui(self, radio_good, robot_good, ntabl_good):
        if radio_good and robot_good and ntabl_good:
            self.app.setBg("green")
        elif not radio_good and not robot_good and not ntabl_good:
            self.app.setBg("red")
        else:
            self.app.setBg("yellow")

        self._update_state("radio", radio_good)
        self._update_state("robot", robot_good)
        self._update_state("ntabl", ntabl_good)

    def _update_state(self, element, good):
        self.app.setLabelBg(element, "green" if good else "red")
        self.app.setLabel(element, "{}: {}".format(element.upper(), "GOOD" if good else "DOWN"))

    def _ping(self, host):
        param = '-n' if system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-w', '1', host]

        return call(command) == 0

    def _listener(self, connected, _):
        self.app.queueFunction(self._update_state, "ntabl", connected)
        self.update()
