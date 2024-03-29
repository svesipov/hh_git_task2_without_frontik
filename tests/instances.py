# coding=utf-8

from functools import partial
import json
import os
import socket
import time

import requests
from lxml import etree

import tornado.options
import tornado_util.supervisor as supervisor

try:
    import sys
    import coverage
    USE_COVERAGE = '--with-coverage' in sys.argv
except ImportError:
    USE_COVERAGE = False


class FrontikTestInstance(object):
    def __init__(self, app, config):
        tornado.options.parse_config_file(config)
        self.app = app
        self.config = config
        self.port = None
        self.supervisor = supervisor

    def start(self):
        for port in xrange(9000, 10000):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', port))
                s.close()
                break
            except:
                pass
        else:
            raise AssertionError('No empty port in range 9000..10000 for frontik test instance')

        if USE_COVERAGE:
            script = 'coverage run -p --branch --source=frontik ./frontik-test'
        else:
            script = './frontik-test'

        supervisor.start_worker(script, app=self.app, config=self.config, port=port)
        self.wait_for(lambda: supervisor.is_running(port))
        self.port = port

    def stop(self):
        if self.port is not None:
            self.supervisor.stop_worker(self.port)
            self.wait_for(lambda: not(self.supervisor.is_running(self.port)))
            self.supervisor.rm_pidfile(self.port)

    @staticmethod
    def wait_for(fun, n=100):
        for i in xrange(n):
            if fun():
                return
            time.sleep(0.01)
        assert fun()

    def get_page(self, page, notpl=False, method=requests.get, **kwargs):
        if not self.port:
            self.start()

        url = 'http://localhost:{port}/{page}{notpl}'.format(
            port=self.port,
            page=page.format(port=self.port),
            notpl=('?' if '?' not in page else '&') + 'notpl' if notpl else ''
        )

        # workaround for different versions of requests library
        if 'auth' in kwargs and requests.__version__ > '1.0':
            from requests.auth import HTTPBasicAuth
            auth = kwargs['auth']
            kwargs['auth'] = HTTPBasicAuth(auth[1], auth[2])

        return method(url, **kwargs)

    def get_page_xml(self, page, notpl=False):
        content = self.get_page_text(page, notpl)

        try:
            return etree.fromstring(content.encode('utf-8'))
        except Exception as e:
            raise Exception('failed to parse xml ({}): "{}"'.format(e, content))

    def get_page_json(self, page, notpl=False):
        content = self.get_page_text(page, notpl)

        try:
            return json.loads(content.encode('utf-8'))
        except Exception as e:
            raise Exception('failed to parse json ({}): "{}"'.format(e, content))

    def get_page_text(self, page, notpl=False):
        return self.get_page(page, notpl).content

join_projects_dir = partial(os.path.join, os.path.dirname(__file__), 'projects')

frontik_broken = FrontikTestInstance(join_projects_dir('broken_app'), join_projects_dir('frontik_debug.cfg'))
frontik_test_app = FrontikTestInstance(join_projects_dir('test_app'), join_projects_dir('frontik_debug.cfg'))
frontik_re_app = FrontikTestInstance(join_projects_dir('re_app'), join_projects_dir('frontik_debug.cfg'))
frontik_non_debug = FrontikTestInstance(join_projects_dir('test_app'), join_projects_dir('frontik_non_debug.cfg'))
