import subprocess
import threading


class TimedCommand(object):

    def __init__(self, prog, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, timeout=None):




