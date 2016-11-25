import os
import re
import StringIO, rfc822

from file_utils import F
from jan import JAN
from text_stats import TextStats

class MarkUpHandler:
    @staticmethod
    def new_file(path):
        json_string = F.slurp(path)
        jan = JAN.new_from_json(json_string)
        type = jan.type
        uri = jan.link
        lang = None
        if type == "py":
            text = F.slurp(uri)
            text = re.sub("[.()\[\]_]", " ", text)
            lang = 'python'
        elif type == "url":
            text = dump_url(uri)
            for link in dump_links(uri):
                jan.add_metadata("link", link)
            lang = 'english'
        elif type == "pdf":
            text = dump_pdf(uri)
            lang = 'english'
        elif type == "email":
            message = parse_email(uri)
            jan.add_metadata("from", message["From"])
            jan.add_metadata("author", message["From"])
            jan.add_metadata("subject", message["Subject"])
            jan.add_metadata("date", message["Date"])
            text = message.fp.read()
            text = re.sub(".*\n\n(.*)", "\g<1>", text)
            lang = 'english'
        else:
            print "type not yet supported:", type
            print uri
        if lang != None:
            ts = TextStats(text, lang)
            top_twenty = ts.top_words(20)
            for word in top_twenty:
                jan.add_metadata("keyword", word)
            jan.promote_new_to_marked_up()

def dump_url(url):
    return os.popen("lynx -dump -nolist " + url).read()

def dump_links(url):
    string = os.popen("lynx -dump -listonly " +url).read()
    links = {}
    lines = string.split("\n")
    for line in lines:
        if re.match(".*http.*", line):
            links[re.sub(".*(http.*)", "\g<1>", line)] = None
    return links.keys()

def dump_pdf(uri):
    path = F.path_from_uri(uri)
    command = "pdftotext '" + path.replace("'", "'\\''") + "' -"
    print command
    return os.popen(command).read()

def parse_email(uri):
    text = F.slurp(uri)
    io = StringIO.StringIO(text)
    return rfc822.Message(io)