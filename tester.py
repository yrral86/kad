import Network;




G = Network.network()
G.begin()
#G.loadFromFile()
#print(G.getCategories())
#G.saveToFile()

list = G.getNetworkBases();
print(list[2])
G.loadNetworkBase(list[2])
y=G.getKeywordCategories()
print(y)


categoryList = G.getCategories()  #returns a list of strings

for x in categoryList:      #this loop runs through all categories and prints all IDs associated
    y = G.getIdsFromCategory(x)     #returns a list of strings
    for z in y:
        print("List for " + x + ": " + z)
print("\n")

"""
y=G.getKeywordCategories()
print(y)

for z in y:
    print(z)
    #print (G.getKeywordsFromKeywordCategory(z))
print("\n")
"""
"""
y = G.getKeywords()     #returns a list of strings
for z in y:         #this loop prints each keyword and the jans associated with it
    print("Keyword:" + z)
    #print(G.getJansFromKeyword(z))
"""
#print(G.getJansFromKeyword("page"))
G.stopLoading()

#print(G.getJansFromId("Google")) #returns list of json

#print(G.getJansFromKeyword("video"))  #returns list of json

#print(G.getKeywordsFromJan("id5"))  #returns a list of strings

#G.getIdsFromCategory("empty")
#print(G.getJANsFromKeyword("empty"))   #this value is not in the samples
#print(G.getRelatedKeywords("empty"))   #this value is not in the samples
