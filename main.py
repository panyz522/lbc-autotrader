from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config
import os

Config.readconfig()
Config.path = os.path.dirname(os.path.abspath(__file__))
monitor = Monitor()
monitor.start()