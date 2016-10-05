#!/usr/bin/env python

import json
import os
import signal
import sys

from dir_watcher import DirWatcher
from file_utils import F
from markup import MarkUpHandler
from ui import UI

class KAD:
    def __init__(self):
        self.new_watcher = DirWatcher("new_jan", MarkUpHandler)
        self.new_watcher.start()

        self.filename = ""

        self.ui = UI(self, "ui.glade")
        self.ui.prepare()

        # magic to make control-c work
        # http://stackoverflow.com/questions/16410852/keyboard-interrupt-with-with-python-gtk
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def add_jan(self, jan):
        F.dump("new_jan/" + jan.uuid + ".jan", jan.to_json())

    def current_uri(self):
        return F.file_uri_from_relative_path(self.filename)

    def load_file(self, filename):
        filename = F.filename_from_fule_uri(filename)
        if self.filename != "":
            self.ensure_saved()
        self.filename = filename
        try:
            self.file_data = F.slurp(self.filename)
        except IOError:
            self.file_data = ""
        self.ui.set_language_from_filename(self.filename)
        self.ui.editor_buffer.set_text(self.file_data)

    def load(self, uri):
        self.ui.browser_view.load_uri(uri)

    def save_file(self, *args):
        self.file_data = self.ui.get_editor_text()
        F.dump(self.filename, self.file_data)

    def ensure_saved(self):
        if self.ui.get_editor_text() != self.file_data:
            self.save_file()

    def reload_kad(self, *args):
        self.ensure_saved()
        os.execl("./kad.py", "./kad.py", self.ui.get_tab())

    def main(self, args):
        if len(args) > 1:
            self.ui.select_tab(args[1])
        self.ui.main()

    def shutdown(self):
        self.ensure_saved()
        self.new_watcher.stop = True

    # javascript bridge functions

    def visualizer_request(self, request, *args):
        eval("self." + request.get_path())

    def trigger_update(self, thing):
       self.js_function("update", {'test': "stuff", 'things': ['one', 2, {'name': "iii"}], "from_js": thing})

    def js_function(self, function, param):
        self.ui.visualizer_view.run_javascript(function + "(" + json.dumps(param) + ")", None, None)


kad = KAD()
kad.main(sys.argv)
