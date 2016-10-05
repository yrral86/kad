#!/usr/bin/env python

import json
import sys
import uuid

from file_utils import F

class JAN:
    @staticmethod
    def new_from_json(json_string):
        jan = JAN()
        jan.map = json.loads(json_string)
        return jan

    @staticmethod
    def new_from_uri_and_type(uri, type):
        jan = JAN()
        jan.map = {
                'type': type,
                'link': uri,
                'uuid': str(uuid.uuid5(uuid.NAMESPACE_URL, uri)),
                'metadata': []
                }
        return jan

    def __getattr__(self, name):
        return self.map[name]

    def add_metadata(self, key, value):
        self.metadata.append({'name': key, 'value': value})

    def deduplicate_metadata(self):
        names = {}
        for meta in self.metadata:
            name, value = meta['name'], meta['value']
            if not(name in names):
                names[name] = {}
            names[name][value] = None
        self.map['metadata'] = []
        for name in names:
            for value in names[name].keys():
                self.add_metadata(name, value)

    def to_json(self):
        self.deduplicate_metadata()
        return json.dumps(self.map)

    def to_pretty_json(self, indent):
        return json.dumps(self.map, indent=indent)


if len(sys.argv) == 2 and "jan.py" in sys.argv[0]:
    print JAN.new_from_json(F.slurp(sys.argv[1])).to_pretty_json(2)