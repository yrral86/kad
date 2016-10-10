import Network;




G = Network.network()
G.begin()

print(G.getCategories())

categoryList = G.getCategories()  #returns a list of strings

for x in categoryList:      #this loop runs through all categories and prints all IDs associated
    y = G.getIdsFromCategory(x)     #returns a list of strings
    for z in y:
        print("List for " + x + ": " + z)
print("\n")

y=G.getKeywordCategories()

for z in y:
    print ("KeywordCategory:" + z) #
    print (G.getKeywordsFromKeywordCategory(z))
print("\n")

y = G.getKeywords()     #returns a list of strings
for z in y:         #this loop prints each keyword and the jans associated with it
    print("Keyword:" + z)
    print(G.getJansFromKeyword(z))

G.stopLoading()
#print(G.getJansFromId("Google")) #returns list of json

#print(G.getJansFromKeyword("video"))  #returns list of json

#print(G.getKeywordsFromJan("id5"))  #returns a list of strings

#G.getIdsFromCategory("empty")
#print(G.getJANsFromKeyword("empty"))   #this value is not in the samples
#print(G.getRelatedKeywords("empty"))   #this value is not in the samples
