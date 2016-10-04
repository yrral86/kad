import re

STOP_WORDS = {
    'english': ["a", "about", "all", "also", "an", "and",
                "any", "are", "as",
                "by", "etc", "for", "from", "had",
                "have", "has", "in", "is", "isnt",
                "it", "its", "not", "of", "on", "or",
                "than", "that", "the", "they",
                "their", "then", "this", "to", "which",
                "will", "with"],
    'python':  ["class", "def", "for", "if", "in", "not", "self"]
    }

class TextStats:
    def __init__(self, text, lang):
        self.raw_text = text
        self.language = lang
        self.clean_text()
        self.build_dictionary()

    def clean_text(self):
        # replace -\n with empty to concatenate line breaks
        concatenated = re.sub("-\n", "", self.raw_text.lower())
        # remove characters that are not alphabetic or whitespace
        stripped = re.sub("[^a-z\s]", "", concatenated)
        # replace all whitespace with a single space
        cleaned = re.sub("\s+", " ", stripped)
        # remove stop words
        words = []
        for word in cleaned.split():
            if word not in STOP_WORDS[self.language]:
                words.append(word)
        self.text = " ".join(words)

    def build_dictionary(self):
        self.dictionary = {}
        for word in self.text.split():
            if not(self.dictionary.has_key(word)):
                self.dictionary[word] = 1
            else:
                self.dictionary[word] += 1

    def top_words(self, limit):
        top = sorted(self.dictionary, key=self.dictionary.get, reverse=True)
        return top[:limit]

    def print_summary(self):
        total = 0
        for word in self.dictionary:
            total += self.dictionary[word]
        #print "Raw text: ", self.raw_text
        #print "Cleaned text: ", self.text
        print "Total words: ", total
        top = sorted(self.dictionary, key=self.dictionary.get, reverse=True)
        print "Top 10 words: ", top[:10]
