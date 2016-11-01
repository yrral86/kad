#!/usr/bin/env python

import json
import os
import signal
import sys

from dir_watcher import DirWatcher
from file_utils import F
from jan import JAN
from markup import MarkUpHandler
from sync_mail import SyncMail
from ui import UI

from gi.repository import Gio
from itertools import groupby 

class KAD:
    def __init__(self):
        self.new_watcher = DirWatcher(JAN.NewDir, MarkUpHandler)
        self.new_watcher.start()

        self.sync_mail = SyncMail("pop.gmail.com", "houshifu1234@gmail.com", "hsf12345")
        self.sync_mail.start()

        self.filename = ""

        self.ui = UI(self, "ui.glade")
        self.ui.prepare()

        # magic to make control-c work
        # http://stackoverflow.com/questions/16410852/keyboard-interrupt-with-with-python-gtk
        signal.signal(signal.SIGINT, signal.SIG_DFL)

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

    def reload_kad(self, *args):
        self.ensure_saved()
        os.execl("./kad.py", "./kad.py")

    def main(self, args):
        if len(args) > 1:
            self.ui.select_tab(args[1])
        self.ui.main()

    def shutdown(self):
        self.ensure_saved()
        self.new_watcher.stop = True
        self.sync_mail.stop = True

    # javascript bridge functions

    jsonList = [];
    authorList = [];
    timeList = [];
    typeList = [];

    def visualizer_request(self, request, *args):
        request.finish(Gio.MemoryInputStream(), 0, "text/html")
        eval("self." + request.get_path())

    def getJansFromKeyword(self, keyword):
        json_author = [];
        json_time = [];
        json_type = [];

        json_context = F.slurp(F.uri_from_path("hardcode/" + keyword + ".json"))
        self.jsonList = json.loads(json_context)
        self.js_function("getJansFromKeyword",json_context)

        #for i in range(0,len(self.jsonList)):
        for d in self.jsonList:
            for key,value in d.iteritems():
                if key == "author":
                    json_author.append(value)
                if key == "time":
                    json_time.append(value)
                if key == "type":
                    json_type.append(value)
        self.authorList = [dict(name = key, value= len(list(group))) for key,group in groupby(sorted(json_author))]
        self.timeList = [dict(name = key, value= len(list(group))) for key,group in groupby(sorted(json_time))]
        self.typeList = [dict(name = key, value= len(list(group))) for key,group in groupby(sorted(json_type))]

    def getIdsFromCategory(self,category):

        if category == "author":
            showList = self.authorList
        elif category == "time":
            showList = self.timeList
        elif category == "type":
            showList = self.typeList
        self.js_function("getIdsFromCategory", json.dumps(showList))

    def js_function(self, function, param):
        self.ui.visualizer_view.run_javascript(function +"(" + json.dumps(param) + ")", None, None)


kad = KAD()
kad.main(sys.argv)
