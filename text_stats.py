import re

class TextStats:
    def __init__(self, text):
        self.raw_text = text
        self.clean_text()
        self.build_dictionary()

    def clean_text(self):
        # remove characters that are not alphabetic or whitespace
        stripped = re.sub("[^a-z\s]", "", self.raw_text.lower())
        # replace all whitespace with a single space
        self.text = re.sub("\s+", " ", stripped)

    def build_dictionary(self):
        self.dictionary = {}
        for word in self.text.split():
            if not(self.dictionary.has_key(word)):
                self.dictionary[word] = 1
            else:
                self.dictionary[word] += 1

    def print_summary(self):
        total = 0
        for word in self.dictionary:
            total += self.dictionary[word]
        print total, " total words"
        top = sorted(self.dictionary, key=self.dictionary.get, reverse=True)
        print "Top 4 words: ", top[:4]