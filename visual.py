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

        #initiatial title dictionary and keyword_list to avoid they are not in the metadata


        #make json as the format of [{"uuid":"", "type":"","time":"","link":"","keywords":["",""],"author":"","metadata",""}]
        for d in self.jsonList:
            title_dic = ""
            time_dic = ""
            keyword_list = []
            for key,value in d.iteritems():
                if key == "metadata":
                    for md in value:
                        for key_m, value_m in md.iteritems():
                            if value_m == "page title":
                                title_dic = md["value"]
                            if value_m == "keyword":
                                keyword_list.append(md["value"])
                            if value_m == "retrieval time":
                                time_dic = md["value"][0:4]
            d["keywords"]=keyword_list #append list of keywords to jan from metadata
            d["title"]= title_dic #append jan title to jan from metadata
            d["time"] = time_dic

        # print(self.jsonList)
        json_context = json.dumps(self.jsonList)
        # print(json.loads(json_context))

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

    def getCategory(self,janbase):
        category = ["type","time"]
        #category would not show link, uuid and metadata
        # if('link' in category):
        #     category.remove('link')
        # if('uuid' in category):
        #     category.remove('uuid')
        # if('metadata' in category):
        #     category.remove('metadata')
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


