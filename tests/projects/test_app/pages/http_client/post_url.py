# coding=utf-8

import re

from tornado.escape import utf8
import frontik.handler

FIELDS = {
    'fielda': 'hello',
    'fieldb': '',
    'field3': 'None',
    'field4': '0',
    'field5': 0,
    'field6': False,
    'field7': ['1', '3', 'jiji']
}

FILES = {
    'field9': [{'filename': 'file0', 'body': bytes([10, 20, 30])}],
    'field10': [
        {'filename': 'file1', 'body': bytes([1, 2, 3])},
        {'filename': 'file2', 'body': bytes([4, 5, 6])},
        {'filename': u'файл 01-12_25.abc', 'body': u'Ёконтент 123 !"№;%:?*()_+={}[]'}
    ]
}


class Page(frontik.handler.PageHandler):
    def get_page(self):

        def callback_post(element, response):
            self.doc.put(element.text)

        self_uri = self.request.host + self.request.path
        self.post_url(self_uri, data=FIELDS, files=FILES, callback=callback_post)

    def post_page(self):
        body_parts = self.request.body.split('\r\n--')
        for part in body_parts:
            meaning_fields = re.search('name="(?P<name>.+)"\r\n\r\n(?P<value>.*)', part)
            meaning_files = re.search('name="(?P<name>.+)"; filename="(?P<filename>.+)"\r\n'
                                      'Content-Type: application/octet-stream\r\n\r\n(?P<value>.*)', part)

            if meaning_fields:
                val = meaning_fields.group('value')
                name = meaning_fields.group('name')
                if not ((isinstance(FIELDS[name], list) and val in FIELDS[name]) or (str(FIELDS[name]) == val)):
                    self.doc.put('BAD')

            elif meaning_files:
                val = meaning_files.group('value')
                name = meaning_files.group('name')
                filename = meaning_files.group('filename')
                for file in FILES[name]:
                    if utf8(file['filename']) == filename and utf8(file['body']) != val:
                        self.doc.put('BAD')

            elif re.search('name=', part):
                self.doc.put('BAD')
