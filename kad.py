#!/usr/bin/env python

import json
import os
import signal
import sys
import Network

from dir_watcher import DirWatcher
from pdf_watcher import PDFWatcher
from file_utils import F
from jan import JAN
from markup import MarkUpHandler
from sync_mail import SyncMail
from ui import UI

class KAD:
    G = Network.network()
    def __init__(self):
        self.pdf_watcher = DirWatcher("pdf", "pdf", PDFWatcher)
        self.pdf_watcher.start()
        self.new_watcher = DirWatcher("jan", JAN.NewDir, MarkUpHandler)
        self.new_watcher.start()

        # self.sync_mail = SyncMail("pop.gmail.com", "houshifu1234@gmail.com", "hsf12345")
        # self.sync_mail.start()

        self.filename = ""

        self.ui = UI(self, "ui.glade")
        self.ui.prepare()

        # magic to make control-c work
        # http://stackoverflow.com/questions/16410852/keyboard-interrupt-with-with-python-gtk
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        #self.G.begin()

    def current_uri(self):
        return F.uri_from_path(self.filename)

    def load_file(self, filename):
        filename = F.path_from_uri(filename)
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

    def render_pdf(self):
        dir = F.dir_from_uri(self.current_uri())
        file = F.file_basename_from_uri(self.current_uri())
        print "dir = " + dir
        print "file = " + file
        print os.popen("cd " + dir + "; pdflatex -interaction nonstopmode " + file).read()
        self.ui.open_uri(F.uri_from_path(dir + "/" + file + ".pdf"))

    def reload_kad(self, *args):
        self.ensure_saved()
        os.execl("./kad.py", "./kad.py")

    def main(self, args):
        if len(args) > 1:
            self.ui.select_tab(args[1])
        self.ui.main()

    def shutdown(self):
        self.ensure_saved()
        self.pdf_watcher.stop = True
        self.new_watcher.stop = True
        self.sync_mail.stop = True
        self.G.stopLoading()

    # javascript bridge functions
    def js_function(self, function, param):
        self.ui.visualizer_view.run_javascript(function +"(" + json.dumps(param) + ")", None, None)

    def get_janbases(self):
        return self.G.getNetworkBases()

    def create_janbase(self, base_name):
        self.G.createNetworkBase(base_name)
    def load_janbase(self, base_name):
        self.G.loadNetworkBase(base_name)
        self.ui.V.janBaseReady();

    def merge_janbases(self, base1, base2):
        self.G.mergeNetworks(base1,base2)


    def delete_janbase(self, base):
        self.G.deleteNetworkBase(base)


kad = KAD()
kad.main(sys.argv)
