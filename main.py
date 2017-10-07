from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config
from lbcmain.cmdcontrol import Command
import os

Config.setpath(os.path.dirname(os.path.abspath(__file__)))
Config.readconfig()
monitor = Monitor()
monitor.start()
cmd = Command(monitor)
cmd.activate()