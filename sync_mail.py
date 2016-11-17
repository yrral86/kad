import poplib
import string
import threading
import time

from config import Config
from file_utils import F
from jan import JAN

MAILBOX_DIR = "mailbox"

class SyncMail(threading.Thread):
    def __init__(self, server, user, password):
        self.pop3 = poplib.POP3_SSL(server)
        self.pop3.user(user)
        self.pop3.pass_(password)
        self.stop = False
        super(SyncMail, self).__init__()
        self.daemon = True

    def get_ids(self):
        resp, items, octets = self.pop3.list()
        return map(lambda x : string.split(x)[0], items)

    def filename_from_id(self, id):
        directory = Config.current_janbase_dir() + MAILBOX_DIR
        F.ensure_directory(directory)
        return directory + "/" + id + ".mbox"

    def sync(self):
        ids = self.get_ids()
        for message_id in ids:
            filename = self.filename_from_id(message_id)
            if not(F.file_exists(filename)):
                resp, text, octets = self.pop3.retr(message_id)
                text = string.join(text, "\n")
                F.dump(filename, text)
                uri = F.uri_from_path(filename)
                jan = JAN.new_from_uri_and_type(uri, "email")
                jan.add_new()

    def run(self):
        while not(self.stop):
            self.sync()
            time.sleep(60)