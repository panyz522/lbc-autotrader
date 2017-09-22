from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config

Config.readconfig()
monitor = Monitor()
monitor.start()