import Network
import json



G = Network.network()
G.begin()

print(G.getCategories())
categoryList = G.getCategories()  #returns a list of strings
for x in categoryList:
    y = G.getIdsFromCategory(x)     #returns a list of strings
    for z in y:
        print("List for " + x + ": " + z)

print(G.getJansFromId("Google")) #returns list of json

print(G.getJANsFromKeyword("video"))  #returns list of json

print(G.getKeywordsFromJan("id5"))  #returns a list of strings

#G.getIdsFromCategory("empty")
#print(G.getJANsFromKeyword("empty"))   #this value is not in the samples
#print(G.getRelatedKeywords("empty"))   #this value is not in the samples
