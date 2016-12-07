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
    website_flag = False;
    Janbase_flag = False;

    def __init__ (self, ui):
        self.ui = ui
        self.kad = ui.kad
        self.G = self.kad.G

    def visualizer_request(self, request, *args):
        request.finish(Gio.MemoryInputStream(), 0, "text/html")
        eval("self." + request.get_path())

    def websiteReady(self, msg):
        self.website_flag = True
        if(self.Janbase_flag):
            self.getJansFromKeyword()
        

    def janBaseReady(self):
        self.Janbase_flag = True
        if(self.website_flag):
            self.getJansFromKeyword()
        

    def getJansFromKeyword(self):
        json_author = [];
        json_time = [];
        json_type = [];

        # json_context = F.slurp(F.uri_from_path("hardcode/" + keyword + ".json"))
        json_context = json.dumps(self.G.getAllJans())
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

        # print("start test")
        # y=self.G.getKeywordCategories()
        # print(y)

        # categoryList = self.G.getCategories()  #returns a list of strings
        # print(categoryList)
        # for x in categoryList:      #this loop runs through all categories and prints all IDs associated
        #     y = self.G.getIdsFromCategory(x)     #returns a list of strings
        #     for z in y:
        #         print("List for " + x + ": " + z)
        # print("\n")
        # # print(self.G.)
        # print("end of test")

    # def start_visualize(self):

    def getCategory(self,janbase):
        category = self.G.getCategories()
        #category would not show link, uuid and metadata
        if('link' in category):
            category.remove('link')
        if('uuid' in category):
            category.remove('uuid')
        if('metadata' in category):
            category.remove('metadata')
        self.kad.js_function("getCategory", category)


    def getIdsFromCategory(self,category):

        # print("ID:",self.G.getIdsFromCategory(category))
        # showList = self.G.getIdsFromCategory(category)
        if category == "author":
            showList = self.authorList
        elif category == "time":
            showList = self.timeList
        elif category == "type":
            showList = self.typeList
        else:
            showList = ""
        self.kad.js_function("getIdsFromCategory", json.dumps(showList))

    def showJansUrl(self, jan_url):
        decode_url = urllib.unquote(jan_url) #to avoid unread the content after the question mark
        self.ui.open_uri(decode_url)

    def showJansPdf(self, title):
        self.ui.open_uri(F.uri_from_path("pdf/" + title +".pdf"))

    def showJansPic(self, jan_url):
        self.ui.open_uri(os.path.abspath("pic/" + jan_url))


