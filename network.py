# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 13:34:07 2016

@author: baronzaaz
"""
import json
import networkx as network
import jan as Jan

#creating some sample JANs

samplejn1 = "[{\"uuid\": \"id1\", \"type\": \"URL\", \"link\": \"http://www.google.com\"}]"
samplejn2 = "[{\"uuid\": \"id2\", \"type\": \"URL\", \"link\": \"http://www.wikipedia.com\"}]"
samplejn3 = "[{\"uuid\": \"id3\", \"type\": \"URL\", \"link\": \"http://www.amazon.com\"}]"
samplejn4 = "[{\"uuid\": \"id4\", \"type\": \"URL\", \"link\": \"http://www.facebook.com\"}]"
samplejn5 = "[{\"uuid\": \"id5\", \"type\": \"URL\", \"link\": \"http://www.youtube.com\"}]"

#turning JANs into json objects

jan1 = json.loads(samplejn1)
jan2 = json.loads(samplejn2)
jan3 = json.loads(samplejn3)
jan4 = json.loads(samplejn4)
jan5 = json.loads(samplejn5) 

#create a list of janjsons and print out the 'link' field
janjsons = (jan1,jan2,jan3,jan4,jan5)
for i in janjsons:
    for j in i:
        print(j['link'])

#create a dictinoary of class JANs by converting janjsons to a class
#networkx would not allow the use of json objects so converting to class
janDict = dict()
for i in janjsons:
    for j in i:
        temp = Jan.Jan(j["uuid"], j["type"], j["link"])
        print(temp.uuid)
        janDict[temp.uuid] = temp


#create a new network graph
G = network.Graph()

#read through the dictionary and add the key as a network node on the graph
for key in janDict.keys():
    G.add_node(key)

#add edges between the nodes using the key names aka uuid
G.add_edge("id1","id2")
G.add_edge("id2","id3")
G.add_edge("id3","id4")
G.add_edge("id4","id5")
G.add_edge("id5","id1")

#test the graph by printing out neighbords of id1
print("\nNeighbors of id1")
neighborz = G.neighbors("id1")
for i in neighborz:
    print(i)


print("\nShortest path to all from id5")
pathDict = network.single_source_shortest_path(G,"id5")

#get all the jan keys and use them to access the dictionarys (it2) nodelist for each key
for key in janDict.keys():
    print("-----------------------------------")
    print("From id5 to :" + key)
    print("current key's link value=" + janDict[key].link)
    for i in pathDict[key]:  #it2[key] looks up the specific list of return values for each key
        print(i)
    

