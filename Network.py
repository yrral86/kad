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
    currentBase = ""

    def __init__(self):
        super(network, self).__init__()

    def stopLoading(self):
        self.loadingFlag = False
        print("JSON search thread stopped")

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
                        
        print(self.janCategoryList)     
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
            traceback.print_stack
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
            time.sleep(1)

    def saveToFile(self):
        
        try:
            path=self.currentBase
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(path+"new_jans"):
                os.makedirs(path + "new_jans")
                os.makedirs(path + "marked_up_jans")
            netx.write_gpickle(self.janGraph,path + "network")  
            handle = open(path + "lists.dat", 'w')  
            json.dump(self.janCategoryList,handle)
            handle.write("\n")
            json.dump(self.janIDs,handle)
            handle.write("\n")
            json.dump(self.janKeywordList,handle)
            handle.write("\n")
            json.dump(self.janMetaList,handle)
            handle.close()
            with open(path + "jans",'w') as janHandle:
                keyz = self.janDict.keys();
                for key in keyz:
                    janHandle.write(key + "||" + json.dumps(self.janDict[key]) + "\n")
        except:
            print("error writing network data")
            traceback.print_exc()
            
    def loadFromFile(self,baseName):
        try:
            if baseName:
                path = os.path.dirname(os.path.abspath(__file__)) + "/data/"+baseName + "/"
            else:
                path = os.path.dirname(os.path.abspath(__file__)) + "/data/Default/" 
            print(path)
            
            self.janDict = {}
            self.janKeywordList = []
            self.janCategoryList = []
            self.janIDs = []
            self.janMetaList = []            
            
            self.currentBase = path  #saves current path for later access
            self.janGraph = netx.read_gpickle(path+"network")
            with open(path+"lists.dat", 'r') as handle:
                self.janCategoryList = handle.readline().strip()
                self.janCategoryList = self.janCategoryList[1:-1].replace("\"","").replace(',',"").split()
                self.janIDs = handle.readline().strip()
                self.janIDs = self.janIDs[1:-1].replace("\"","").replace(',',"").split()
                self.janKeywordList = handle.readline().strip()
                self.janKeywordList= self.janKeywordList[1:-1].replace("\"","").replace(',',"").split()
                self.janMetaList = handle.readline().strip()
                self.janMetaList=self.janMetaList[1:-1].replace("\"","").replace(',',"").split()
                handle.close()
            with open(path + "jans", 'r') as janHandle:
                for line in janHandle:                                 
                    fields = line.split("||")
                    self.janDict[fields[0]] = json.loads(fields[1].strip())
            print(baseName)
        except:
            print("error reading network datafile or file missing")
            traceback.print_exc()
    def clearMarkupFolder(self):
        path = self.currentBase;
        files = glob.glob(path + "marked_up_jan/*.jan")
        for eachFile in files:
            os.remove(eachFile)
            print(eachFile + " processed & deleted")
            
    def mergeNetworks(self,base1,base2):  #merge 2 into 1
        path2 = os.path.dirname(os.path.abspath(__file__)) + base2 + "/";        
        self.loadNetworkBase(base1)
        
        janGraph2 = netx.read_gpickle(path2+"network")
        janDict2 = []        
        with open(path2+"lists.dat", 'r') as handle:
            janCategoryList2 = handle.readline().strip()
            janCategoryList2 = janCategoryList2[1:-1].replace("\"","").replace(',',"").split()
            janIDs2 = handle.readline().strip()
            janIDs2 = janIDs2[1:-1].replace("\"","").replace(',',"").split()
            janKeywordList2 = handle.readline().strip()
            janKeywordList2= janKeywordList2[1:-1].replace("\"","").replace(',',"").split()
            janMetaList2 = handle.readline().strip()
            janMetaList2 =janMetaList2[1:-1].replace("\"","").replace(',',"").split()
            handle.close()
        with open(path2 + "jans", 'r') as janHandle:
            for line in janHandle:                                 
                fields = line.split("||")
                self.janDict2[fields[0]] = json.loads(fields[1].strip())        
        
        self.janGraph = netx.compose(self.janGraph,janGraph2)
        for cata in janCategoryList2:
            if cata not in self.janCategoryList:
                self.janCategoryList2.append(cata)
                
        for id in janIDs2:
            if id not in self.janIDs:
                self.janIDs.append(id)
                
        for kw in janKeywordList2:
            if kw not in self.janKeywordList:
                self.janKeywordList.append(kw)
                
        for ml in janMetaList2:
            if ml not in self.janMetaList:
                self.janMetaList.append(ml)
                
        for keys in janDict2.keys():
            if keys not in self.janDict:
                self.janDict[keys]= janDict2[keys]
                
                
        self.saveToFile()
    
    
    def loadNetworkBase(self,networkBase):
        self.saveToFile()            
        self.G=netx.Graph()
        self.loadFromFile(networkBase)
        
    
    def createNetworkBase(self,networkBase):
        path = os.path.dirname(os.path.abspath(__file__)) + "/data/"+ networkBase + "/"
        self.currentBase = path
        self.janGraph = netx.Graph()
        self.janDict = {}
        self.janKeywordList = []
        self.janCategoryList = []
        self.janIDs = []
        self.janMetaList = []
        self.saveToFile()
        
    def deleteNetworkBase(self,networkBase):
        if networkBase == "Default":
            return
        #delete base!
            
    def getNetworkBases(self):
        networkBases = list()
        path = os.path.dirname(os.path.abspath(__file__));
        path += ("/data")
        for folders in os.walk(path):
            for base in folders[1]:
                networkBases.append(base)
            break
        return networkBases
        
    def run(self):
        self.loadFromFile(None)
        path = self.currentBase;
        print("JSON search thread started")
        while self.loadingFlag:
            #print("searching for jsons")
            files = glob.glob(path + "marked_up_jan/*.jan")
            #print(files)
            for eachfile in files:
                try:
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

                except:
                    print("Error reading in from marked_up_jans")
                self.saveToFile()
            self.startFlag = True
            self.clearMarkupFolder()
            time.sleep(10)
