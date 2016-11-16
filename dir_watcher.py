import glob
import os
import threading
import time

from config import Config
from file_utils import F

class DirWatcher(threading.Thread):
    def __init__(self, directory, responder):
        self.directory = directory
        self.responder = responder
        self.stop = False
        super(DirWatcher, self).__init__()
        self.daemon = True

    def run(self):
        while not(self.stop):
            path = os.path.abspath(Config.current_janbase_dir() + self.directory)
            F.ensure_directory(path)
            files = glob.glob(path + "/*.jan")
            for file in files:
                if self.responder != None:
                    self.responder.new_file(file)
            time.sleep(1)