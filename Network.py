import threading
import networkx as netx
import time
import json
import glob
import os
import traceback
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
    janMetaList = []

    def __init__(self):
        super(network, self).__init__()

    def stopLoading(self):
        self.loadingFlag = False

    def loadJAN(self, janjson):
        self.janDict[janjson["uuid"]] = janjson
        self.janGraph.add_node(janjson["uuid"])

        for field in janjson.keys():
            if field not in self.janCategoryList:
                self.janCategoryList.append(field)
                self.janGraph.add_node("Category:" + field)
            if janjson[field] not in self.janIDs and not isinstance(janjson[field],list):
                self.janIDs.append(janjson[field])
                self.janGraph.add_node("Id:" + janjson[field])
            if  not isinstance(janjson[field],list):
                self.janGraph.add_edge("Id:" + janjson[field], "Category:" + field)
                self.janGraph.add_edge(janjson["uuid"],"Id:" + janjson[field])
            else:
                for dictList in janjson[field]:
                    for meta in dictList.keys(): #name value name value
                        if dictList["name"] not in self.janMetaList:
                            self.janMetaList.append(dictList[meta])
                            self.janGraph.add_node("MetaField:" + dictList[meta])
                            self.janGraph.add_edge("MetaField:" + dictList[meta], "Category:" + field)
                        if dictList["value"] not in self.janKeywordList:
                            self.janKeywordList.append(dictList["value"])
                            self.janGraph.add_node("Meta:" + dictList["value"])
                            self.janGraph.add_edge("Meta:" + dictList["value"],"MetaField:" + dictList[meta])
                        
                        self.janGraph.add_edge(janjson["uuid"], "Meta:" + dictList["value"])
                        
                
    def getJansFromKeyword(self, keyword):
        try:
            neighborlist = netx.all_neighbors(self.janGraph, "Meta:"+keyword)
            
            jsonlist = list()
            for neigh in neighborlist:
                #print(neigh)
                if not neigh.startswith("MetaField:"):
                    jsonlist.append(self.janDict[neigh])
            return jsonlist
        except netx.NetworkXError:
            return ""

    def getCategories(self):
        return self.janCategoryList

    def getKeywords(self):
        return self.janKeywordList
        
    def getKeywordCategories(self):
        return self.janMetaList
        
    def getKeywordsFromKeywordCategory(self,metafield):
        try:
            neighborlist = netx.all_neighbors(self.janGraph, "MetaField:"+ metafield)
            jsonlist = list()
            for neigh in neighborlist:
                if not neigh.startswith("Category:"):
                    jsonlist.append(neigh)
            return jsonlist
        except netx.NetworkXError:
            return ""
        return

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
            time.sleep(1);

    def run(self):
        #This thread looks for a directory jsons under the location of this script and pulls json files from it
        #it runs until stopLoading() is called
        path = os.path.dirname(os.path.abspath(__file__));
        loadedFileList = list()
        while self.loadingFlag:
            print("searching for jsons")
            files = glob.glob(path + "/new_jan/*.jan")
            #print(files)
            for eachfile in files:
                if eachfile not in loadedFileList:
                    #print(eachfile)
                    with open(eachfile) as handle:
                        for eachJan in handle:
                            #print(eachJan)
                            try:
                                janjson = json.loads(eachJan)
                                #print(janjson["uuid"])
                                self.loadJAN(janjson)
                            except:
                                print("error loading jan")
                                traceback.print_exc()
                        handle.close();
                    loadedFileList.append(eachfile)
            self.startFlag = True
            time.sleep(10)
