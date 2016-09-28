import poplib
import string, random
import StringIO, rfc822
import logging

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
# download the first message in the list
for i in range(0, ret[0]):
    id, size = string.split(items[i])
    resp, text, octets = server.retr(id)

    # convert list to Message object
    text = string.join(text, "\n")
    file = StringIO.StringIO(text)
    message = rfc822.Message(file)

    # output message
    print(message['From']),
    print(message['Subject']),
    print(message['Date']),
    print('\n'),
    print(message.fp.read()),
    print('\n')