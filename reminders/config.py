from ConfigParser import ConfigParser
import logging

config = ConfigParser()
config.readfp(open('config.ini'))

logger = logging.getLogger('Reminder Bot')
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)

logger.addHandler(sh)
