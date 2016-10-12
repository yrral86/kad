import poplib

from file_utils import F

class SyncMail
    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password
        self.pop3 = poplib.POP3_SSL(self.server)

    def get_items(self)
        resp, items, octets = self.pop3.list()
        return items
        
    def sync(self):
        items = self.get_items()
        for item in items:
            

SERVER = "pop.gmail.com"
USER  = "houshifu1234@gmail.com"
PASSWORD = "hsf12345"


# connect to server
logging.debug('connecting to ' + SERVER)
server = poplib.POP3_SSL(SERVER)
#server = poplib.POP3(SERVER)

# login
logging.debug('logging in')
server.user(USER)
server.pass_(PASSWORD)

# list items on server
logging.debug('listing emails')
resp, items, octets = server.list()
ret = server.stat()
print "ret:\n"
print ret
print "resp:\n"
print resp
print "items:\n"
print items
print "octets:\n"
print octets
# download the first message in the list
if False:
    for i in range(0, ret[0]):
        id, size = string.split(items[i])
        resp, text, octets = server.retr(id)

        # convert list to Message object
        text = string.join(text, "\n")
        file = StringIO.StringIO(text)
        message = rfc822.Message(file)

        # output message
        print text
        print "\n\n"