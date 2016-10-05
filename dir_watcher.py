import glob
import os
import threading
import time

class DirWatcher(threading.Thread):
    def __init__(self, directory, responder):
        self.directory = directory
        self.responder = responder
        self.stop = False
        super(DirWatcher, self).__init__()
        self.daemon = True

    def run(self):
        path = os.path.abspath(self.directory)
        while not(self.stop):
            files = glob.glob(path + "/*.jan")
            for file in files:
                if self.responder != None:
                    self.responder.new_file(file)
            # sleep for 10 seconds, checking if stopped frequently
            for i in range(100):
                if not(self.stop):
                    time.sleep(0.1)