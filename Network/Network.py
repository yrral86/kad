import threading
import networkx as netx
import time
import json
import glob
import os
"""
Every unique field type in the json has a category master node, stored as Category:field
Each unique entry is referred to as either and Id unless its a Keyword
Each jan is connected to its Ids and its Keywords, which are connected to their master categories
Ids and Keywords are basically the same logically and might be merged together later if it seems a good idea
"""
class network (threading.Thread):
    loadingFlag = True
    janGraph = netx.Graph()
    janDict = {}
    janKeywordList = []
    janCategoryList = []
    janIDs = []
    startFlag = False

    def __init__(self):
        super(network, self).__init__()

    def stopLoading(self):
        self.loadingFlag = False

    def loadJAN(self, JAN):
        self.janDict[JAN[0]["uuid"]] = JAN
        self.janGraph.add_node(JAN[0]["uuid"])

        for line in JAN:
            for x in line:
                if x not in self.janCategoryList:
                    self.janCategoryList.append(x)
                    self.janGraph.add_node("Category:" + x)
                if x not in self.janIDs:
                    self.janIDs.append(x)
                    self.janGraph.add_node("Id:" + JAN[0][x])
                if x != "keywords":
                    self.janGraph.add_edge("Id:" + JAN[0][x], "Category:" + x)
                    self.janGraph.add_edge(JAN[0]["uuid"],"Id:" + JAN[0][x])
                else:
                    keywords = JAN[0]["keywords"].replace('[','').replace(']','').split(",")
                    for x in keywords:
                        if x not in self.janKeywordList:
                            self.janKeywordList.append(x)
                            self.janGraph.add_node("Key:" + x)
                            self.janGraph.add_edge("Key:" + x, "Category:keywords")
                        self.janGraph.add_edge(JAN[0]["uuid"],"Key:"+ x)

    def getJANsFromKeyword(self, keyword):
        try:
            neighborlist = netx.all_neighbors(self.janGraph, "Key:"+keyword)
            jsonlist = list()
            for neigh in neighborlist:
                if not neigh.startswith("Category:"):
                    jsonlist.append(self.janDict[neigh])
            return jsonlist
        except netx.NetworkXError:
            return ""

    def getCategories(self):
        return self.janCategoryList

    def getJansFromId(self,id):
        try:
            neighborlist = netx.all_neighbors(self.janGraph, "Id:"+ id)
            jsonlist = list()
            for neigh in neighborlist:
                if not neigh.startswith("Category:"):
                    jsonlist.append(self.janDict[neigh])
            return jsonlist
        except netx.NetworkXError:
            return ""


    def getKeywordsFromJan(self, JANid):
        try:
            neighborlist = netx.all_neighbors(self.janGraph, JANid)
            keywordList = list()
            for neigh in neighborlist:
                if neigh not in keywordList:
                    if neigh.startswith("Key:"):
                        keywordList.append(neigh[4:])
            return keywordList
        except netx.NetworkXError:
            return ""

    def getIdsFromCategory(self,category):
        try:
            neighborlist = netx.all_neighbors(self.janGraph, "Category:" + category)
            keywordList = list()
            for neigh in neighborlist:
                if neigh not in keywordList:
                    if neigh.startswith("Id:"):
                        keywordList.append(neigh[3:])
            return keywordList
        except netx.NetworkXError:
            return ""
    #this method starts the thread, but does not return control until all jans have been loaded
    def begin(self):
        self.start()
        while not self.startFlag:
            pass

    def run(self):
        #This thread looks for a directory jsons under the location of this script and pulls json files from it
        #it runs until stopLoading() is called
        path = os.path.dirname(os.path.abspath(__file__))
        loadedFileList = list()
        while self.loadingFlag:
            print("searching for jsons")
            files = glob.glob(path + "\\jsons\\*.json")
            for eachfile in files:
                if eachfile not in loadedFileList:
                    print(eachfile)
                    with open(eachfile) as handle:
                        for eachJan in handle:
                            self.loadJAN(json.loads(eachJan))
                        handle.close()
                    loadedFileList.append(eachfile)
            self.startFlag = True
            time.sleep(10)
