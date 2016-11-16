# javascript bridge functions
import json
import urllib
import os

from gi.repository import Gio
from itertools import groupby 
from file_utils import F

class V:
    jsonList = [];
    authorList = [];
    timeList = [];
    typeList = [];
    def __init__ (self, ui):
        self.ui = ui
        self.kad = ui.kad

    def visualizer_request(self, request, *args):
        request.finish(Gio.MemoryInputStream(), 0, "text/html")
        eval("self." + request.get_path())

    def getJansFromKeyword(self, keyword):
        json_author = [];
        json_time = [];
        json_type = [];

        json_context = F.slurp(F.uri_from_path("hardcode/" + keyword + ".json"))
        self.jsonList = json.loads(json_context)
        self.kad.js_function("getJansFromKeyword",json_context)

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
        self.kad.js_function("getIdsFromCategory", json.dumps(showList))

    def showJansUrl(self, jan_url):
        decode_url = urllib.unquote(jan_url) #to avoid unread the content after the question mark
        self.ui.open_uri(decode_url)

    def showJansPdf(self, title):
        self.ui.open_uri(F.uri_from_path("pdf/" + title +".pdf"))

    def showJansPic(self, jan_url):
        self.ui.open_uri(os.path.abspath("pic/" + jan_url))


